import geopandas as gpd
import os
import pandas as pd

input_file = 'data/hadong_roads.geojson'
output_file = 'data/hadong_roads_cleaned.geojson'

print("Bước 2/4 : Đang làm sạch và lọc dữ liệu ...")
gdf = gpd.read_file(input_file)
initial_count = len(gdf)

gdf['highway'] = gdf['highway'].astype(str)

target_roads = [
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 
    'unclassified', 'residential', 'service', 'living_street'
]

# Hàm lọc
def filter_highway(val_str):
    val_str = val_str.lower()
    for road in target_roads:
        if road in val_str:
            return road 
    return None

# Ánh xạ và lọc
gdf['highway_clean'] = gdf['highway'].apply(filter_highway)
gdf_cleaned = gdf.dropna(subset=['highway_clean']).copy()

# Giữ lại các cột cần thiết
keep_columns = ['osmid', 'name', 'highway_clean', 'oneway', 'length', 'geometry']
existing_cols = [c for c in keep_columns if c in gdf_cleaned.columns]
gdf_cleaned = gdf_cleaned[existing_cols]

# Kiểm tra tính hợp lệ 
gdf_cleaned = gdf_cleaned[gdf_cleaned.is_valid]

for col in gdf_cleaned.columns:
    if col not in ['geometry', 'geom']:
        gdf_cleaned[col] = gdf_cleaned[col].apply(str)

# Lưu kết quả
if not os.path.exists('data'):
    os.makedirs('data')

gdf_cleaned.to_file(output_file, driver='GeoJSON')

print(f" Số lượng đường ban đầu: {initial_count}")
print(f" Số lượng đường sau khi lọc: {len(gdf_cleaned)}")
if initial_count > 0:
    print(f"Tỷ lệ giữ lại: {(len(gdf_cleaned)/initial_count)*100:.2f}%")