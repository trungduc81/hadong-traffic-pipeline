import geopandas as gpd
import os
import pandas as pd

input_file = 'data/hadong_roads_cleaned.geojson'
output_file = 'data/hadong_roads_normalized.geojson'

print("Bước 3/4: Đang chuẩn hóa cấu trúc dữ liệu...")

gdf = gpd.read_file(input_file)

def clean_osmid(val):
    cleaned_str = str(val).replace('[', '').replace(']', '').replace("'", "")
    first_id = cleaned_str.split(',')[0].strip()
    return str(first_id)

if 'osmid' in gdf.columns:
    gdf['osmid'] = gdf['osmid'].apply(clean_osmid)

gdf = gdf.rename(columns={
    'osmid': 'road_id',
    'name': 'road_name',
    'highway_clean': 'road_type'
})

speed_limit_map = {
    'motorway': 80, 'trunk': 60, 'primary': 50,
    'secondary': 45, 'tertiary': 40, 'unclassified': 30,
    'residential': 30, 'service': 20, 'living_street': 15
}

# Nếu road_type là list, lấy giá trị đầu tiên để map tốc độ
if 'road_type' in gdf.columns:
    gdf['road_type'] = gdf['road_type'].apply(lambda x: x[0] if isinstance(x, list) else x)
    gdf['max_speed'] = gdf['road_type'].map(speed_limit_map).fillna(30).astype(int)
else:
    gdf['max_speed'] = 30

# Nếu road_name là list, lấy tên đầu tiên
if 'road_name' in gdf.columns:
    gdf['road_name'] = gdf['road_name'].apply(lambda x: x[0] if isinstance(x, list) else x).fillna("Đường không tên")

expected_cols = ['road_id', 'road_name', 'road_type', 'max_speed', 'geometry']
available_cols = [col for col in expected_cols if col in gdf.columns]
gdf = gdf[available_cols]

for col in gdf.columns:
    if col not in ['geometry', 'geom', 'max_speed']:
        gdf[col] = gdf[col].apply(lambda x: ', '.join(map(str, x)) if isinstance(x, list) else x)


os.makedirs('data', exist_ok=True)
gdf.to_file(output_file, driver='GeoJSON')
print(f"Chuẩn hóa thành công! Số lượng bản ghi: {len(gdf)}")