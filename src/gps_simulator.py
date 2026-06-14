import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine
from shapely.geometry import Point
from datetime import datetime, timedelta
import random
import os

# Lấy DB_URI từ biến môi trường hoặc sử dụng giá trị mặc định
DB_URI = os.getenv("DB_URI", "postgresql://trung:123456@localhost:5433/hadong_traffic")
engine = create_engine(DB_URI)

def simulate_traffic(num_steps_per_vehicle=500, time_step_sec=5):
    
    # đọc dữ liệu từ db 
    vehicles = pd.read_sql("SELECT vehicle_id FROM vehicle", engine)
    roads = gpd.read_postgis("SELECT road_id, max_speed, geom FROM road_segment", engine, geom_col='geom')
    
    if vehicles.empty or roads.empty:
        print("Không tìm thấy dữ liệu xe hoặc đường trong DB")
        return

    gps_data_list = []
    start_time = datetime.now()

    # lặp giả lập 
    total_v = len(vehicles)
    for idx, v in vehicles.iterrows():
        v_id = int(v['vehicle_id'])
        
        # Chọn con đường ngẫu nhiên để bắt đầu
        current_road = roads.sample(n=1).iloc[0]
        line = current_road.geom
        max_speed = current_road.max_speed
        current_dist_on_road = 0 

        for step in range(num_steps_per_vehicle):
            # Vận tốc ngẫu nhiên từ 70% tới 100% vận tốc tối đa trên quãng đường 
            speed_mps = (max_speed * random.uniform(0.7, 1.0)) / 3.6 
            step_dist_degrees = (speed_mps * time_step_sec) / 111000
            
            #  tọa độ tại vị trí hiện tại
            point = line.interpolate(current_dist_on_road)
            
            # Ghi nhận thời gian và vị trí
            gps_time = start_time + timedelta(seconds=step * time_step_sec)
            gps_data_list.append({
                'vehicle_id': v_id,
                'gps_time': gps_time,
                'speed_kmh': round(speed_mps * 3.6, 2),
                'geom': Point(point.x, point.y).wkt
            })

            current_dist_on_road += step_dist_degrees

            # Nếu đi hết đường, đổi sang đường mới ngay lập tức
            if current_dist_on_road >= line.length:
                current_road = roads.sample(n=1).iloc[0]
                line = current_road.geom
                max_speed = current_road.max_speed
                current_dist_on_road = 0 

    # nạp vào db 
    df_gps = pd.DataFrame(gps_data_list)
    gdf_gps = gpd.GeoDataFrame(df_gps, geometry=gpd.GeoSeries.from_wkt(df_gps['geom']), crs="EPSG:4326")
    gdf_gps = gdf_gps.drop(columns=['geom']).rename_geometry('geom')
    
    gdf_gps.to_postgis('gps_tracking', engine, if_exists='append', index=False)
    
    print("Dữ liệu đã được nạp hoàn tất vào trong bảng gps_tracking")

if __name__ == "__main__":
    simulate_traffic(num_steps_per_vehicle=500, time_step_sec=5)