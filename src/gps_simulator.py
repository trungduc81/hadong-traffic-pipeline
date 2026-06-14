import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine, text
from shapely.geometry import Point
from datetime import datetime, timedelta
import random
import os

DB_URI = os.getenv("DB_URI", "postgresql://trung:123456@hadong_db:5432/hadong_traffic")
engine = create_engine(DB_URI)

def simulate_traffic(num_steps_per_vehicle=500, time_step_sec=5):
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE gps_tracking CASCADE;"))
    
    # Đọc dữ liệu từ DB 
    vehicles = pd.read_sql("SELECT vehicle_code AS vehicle_id FROM vehicle", engine)
    roads = gpd.read_postgis("SELECT road_id, max_speed, geom FROM road_segment", engine, geom_col='geom')
    
    if vehicles.empty or roads.empty:
        print("Không tìm thấy dữ liệu xe hoặc đường trong DB")
        return

    start_time = datetime.now()
    total_v = len(vehicles)
    
    for idx, v in vehicles.iterrows():
        v_id = str(v['vehicle_id'])
        current_road = roads.sample(n=1).iloc[0]
        line = current_road.geom
        
        current_dist_on_road = 0 
        gps_data_list = [] 

        for step in range(num_steps_per_vehicle):
            try:
                speed_limit = float(current_road.max_speed)
            except (ValueError, TypeError):
                speed_limit = 40.0 
                
            speed_mps = (speed_limit * random.uniform(0.7, 1.0)) / 3.6 
            step_dist_degrees = (speed_mps * time_step_sec) / 111000
            
            point = line.interpolate(current_dist_on_road)

            gps_time = start_time + timedelta(seconds=step * time_step_sec)
            gps_data_list.append({
                'vehicle_id': v_id,
                'gps_time': gps_time,
                'speed_kmh': round(speed_mps * 3.6, 2),
                'geom': Point(point.x, point.y).wkt
            })

            current_dist_on_road += step_dist_degrees

            if current_dist_on_road >= line.length:
                current_road = roads.sample(n=1).iloc[0]
                line = current_road.geom
                current_dist_on_road = 0 

        df_gps = pd.DataFrame(gps_data_list)
        gdf_gps = gpd.GeoDataFrame(df_gps, geometry=gpd.GeoSeries.from_wkt(df_gps['geom']), crs="EPSG:4326")
        gdf_gps = gdf_gps.drop(columns=['geom']).rename_geometry('geom')
        
        gdf_gps.to_postgis('gps_tracking', engine, if_exists='append', index=False)
            
        print(f"Đã nạp xong lộ trình cho xe {v_id} ({idx + 1}/{total_v})")
        
    print(" Dữ liệu đã được nạp hoàn tất vào trong bảng gps_tracking")

if __name__ == "__main__":
    try:
        simulate_traffic(num_steps_per_vehicle=500, time_step_sec=5)
    except Exception as e:
        print(f"Lỗi giả lập GPS: {e}")