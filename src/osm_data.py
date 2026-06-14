import osmnx as ox
import geopandas as gpd
import os

place = "Ha Dong District, Hanoi, Vietnam"
print(f"Bước 1/4: Đang tải dữ liệu mạng lưới giao thông khu vực: {place}...")

data = ox.graph_from_place(place, network_type='all')
nodes, edges = ox.graph_to_gdfs(data)

for col in edges.columns:
    if col not in ['geometry', 'geom']:
        edges[col] = edges[col].astype(str)

os.makedirs('data', exist_ok=True)

output_file = 'data/hadong_roads.geojson'
if os.path.exists(output_file):
    os.remove(output_file)

edges.to_file(output_file, driver='GeoJSON')
print(f"Lấy dữ liệu {len(edges)} con đường thành công vào file {output_file}")