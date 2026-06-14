import osmnx 
import os

place = "Ha Dong District, Hanoi, Vietnam"
data = osmnx.graph_from_place(place , network_type = 'all')

nodes , edges = osmnx.graph_to_gdfs(data) 
output_file = 'data/hadong_roads.geojson'
edges.to_file(output_file,driver = 'GeoJSON')
print(f"Lay du lieu {len(edges)} con duong vao file hadong_roads.geojson")