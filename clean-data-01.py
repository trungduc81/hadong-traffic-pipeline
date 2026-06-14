import geopandas as gpd
import os

input_file = 'data/hadong_roads.geojson'
output_file = 'data/hadong_roads_cleaned.geojson'

gdf = gpd.read_file(input_file)
initial_count = len(gdf)

# Chỉ giữ lại các loại đường dành cho phương tiện cơ giới
keep_highways = [
    'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 
    'unclassified', 'residential', 'motorway_link', 'trunk_link', 
    'primary_link', 'secondary_link', 'tertiary_link'
]

# Lọc 
gdf_cleaned = gdf[gdf['highway'].isin(keep_highways)].copy()

# Loại bỏ các cột k cần thiết 
keep_columns = ['osmid', 'name', 'highway_str', 'oneway', 'length', 'geometry']
gdf_cleaned = gdf_cleaned[keep_columns]

# Điền tên cho các con đường không có tên trong OSM
gdf_cleaned['name'] = gdf_cleaned['name'].fillna("Đường không tên")


#Lưu kết quả
if not os.path.exists('data'):
    os.makedirs('data')

gdf_cleaned.to_file(output_file, driver='GeoJSON')

print(f"Số lượng đường ban đầu: {initial_count}")
print(f"Số lượng đường sau khi lọc: {len(gdf_cleaned)}")
print(f"Tỷ lệ giảm tải: {((initial_count - len(gdf_cleaned))/initial_count)*100:.2f}%")
