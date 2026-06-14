import geopandas as gpd
import os

input_file = 'data/hadong_roads_cleaned.geojson'
output_file = 'data/hadong_roads_normalized.geojson'

# Đọc dữ liệu từ bước lọc 
gdf = gpd.read_file(input_file)

# Lấy phần tử đầu tiên trong list để làm id do osm có osm_id dạng list 
gdf['osmid'] = gdf['osmid'].apply(lambda x: x[0] if isinstance(x, list) else x)
gdf['osmid'] = gdf['osmid'].astype(int)

# Khớp cột với sql 
gdf = gdf.rename(columns={
    'osmid': 'osm_id',
    'name': 'road_name',
    'highway_clean': 'road_type',
    'length': 'length_m',
    'geometry' : 'geom'
})

gdf['road_name'] = gdf['road_name'].fillna("Đường không tên")

# Chuẩn hóa thành Boolean 
gdf['oneway'] = gdf['oneway'].apply(lambda x: True if str(x).lower() in ['yes', '1', '-1', 'true'] else False)

# Sinh dữ liệu max_speed
speed_limit_map = {
    'motorway': 80, 
    'trunk': 60, 
    'primary': 50,
    'secondary': 45, 
    'tertiary': 40, 
    'unclassified': 30,
    'residential': 30, 
    'service': 20, 
    'living_street': 15
}
gdf['max_speed'] = gdf['road_type'].map(speed_limit_map).fillna(30).astype(int)

if not os.path.exists('../data'):
    os.makedirs('../data')

gdf.to_file(output_file, driver='GeoJSON')

print(f"Số lượng bản ghi: {len(gdf)}")
print(f"Các cột hiện tại: {gdf.columns.tolist()}")
