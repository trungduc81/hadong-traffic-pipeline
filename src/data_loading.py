import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine, text
import os

csv_input = 'data/vehicle.csv'
geojson_input = 'data/hadong_roads_normalized.geojson'

DB_URI = os.getenv("DB_URI", "postgresql://trung:123456@hadong_db:5432/hadong_traffic")
engine = create_engine(DB_URI)

#Xóa dữ liệu cũ nếu có 
def clean_old_data():
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE vehicle, road_segment CASCADE;"))

def load_vehicles():
    if os.path.exists(csv_input):
        df_vehicles = pd.read_csv(csv_input)
        df_vehicles.to_sql('vehicle', engine, if_exists='append', index=False)
        print(f" Đã load {len(df_vehicles)} xe.")

def load_roads():
    if os.path.exists(geojson_input):
        gdf_roads = gpd.read_file(geojson_input)
            
        if gdf_roads.crs is None or gdf_roads.crs.to_epsg() != 4326:
            gdf_roads = gdf_roads.to_crs(epsg=4326)
            
        if 'geom' in gdf_roads.columns:
            gdf_roads = gdf_roads.set_geometry('geom')
        else:
            gdf_roads = gdf_roads.rename_geometry('geom')
                              
        gdf_roads.to_postgis('road_segment', engine, if_exists='append', index=False)
        print(f" Đã load {len(gdf_roads)} đoạn đường.")

if __name__ == "__main__":
    try:
        clean_old_data()
        load_vehicles()
        load_roads()
        print("Hoàn tất luồng pipeline")
    except Exception as e:
        print(f" Xảy ra lỗi: {e}")