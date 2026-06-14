import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine
import os

csv_input = 'data/vehicle.csv'
geojson_input = 'data/hadong_roads_normalized.geojson'

# Lấy DB_URI từ biến môi trường hoặc sử dụng giá trị mặc định
DB_URI = os.getenv("DB_URI", "postgresql://trung:123456@localhost:5433/hadong_traffic")
engine = create_engine(DB_URI)

def load_vehicles():
    if os.path.exists(csv_input):
        df_vehicles = pd.read_csv(csv_input)
        
        # Nạp vào bảng vehicle
        df_vehicles.to_sql('vehicle', engine, if_exists='append', index=False)
        print(f"Đã nạp {len(df_vehicles)} xe vào bảng 'vehicle'")
    else:
        print(f"Không tìm thấy file {csv_input}")

def load_roads():
    if os.path.exists(geojson_input):
        gdf_roads = gpd.read_file(geojson_input)
        if gdf_roads.crs is None or gdf_roads.crs.to_epsg() != 4326:
            gdf_roads = gdf_roads.to_crs(epsg=4326)
            
        if 'geom' in gdf_roads.columns:
            gdf_roads = gdf_roads.set_geometry('geom')
        else:
            gdf_roads = gdf_roads.rename_geometry('geom')
                                  
        # Nạp vào bảng road_segment
        gdf_roads.to_postgis('road_segment', engine, if_exists='append', index=False)
        print(f"Đã nạp {len(gdf_roads)} đoạn đường vào bảng 'road_segment'")
    else:
        print(f"Không tìm thấy file {geojson_input}")

if __name__ == "__main__":
    load_vehicles()
    load_roads()
    print("Hoàn tất")
