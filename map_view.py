import folium
import geopandas as gpd
from sqlalchemy import create_engine

# 1. Kết nối DB
engine = create_engine("postgresql://trung:123456@localhost:5433/hadong_traffic")

# 2. Lấy dữ liệu (Lọc bớt những đường không có tên để bản đồ nhẹ hơn)
# 2. Chỉ lấy các loại đường chính (loại bỏ các ngõ ngách, đường nội bộ quá nhỏ)
query = """
    SELECT r.road_name, r.geom, a.avg_speed, a.congestion_level
    FROM road_segment r
    JOIN traffic_analytics a ON r.road_id = a.road_id
    WHERE r.road_type IN ('primary', 'secondary', 'tertiary', 'trunk', 'motorway')
      AND r.road_name IS NOT NULL
"""
gdf = gpd.read_postgis(query, engine, geom_col='geom')

# 3. Đảm bảo hệ tọa độ chuẩn cho Web
if gdf.crs is None:
    gdf.set_crs(epsg=4326, inplace=True)

# 4. Hàm định nghĩa màu sắc cho style_function
def style_fn(feature):
    level = feature['properties']['congestion_level']
    color = 'green'
    if level == 'Kẹt xe (Heavy)': color = 'red'
    elif level == 'Mật độ cao (Medium)': color = 'orange'
    
    return {
        'color': color,
        'weight': 4,
        'opacity': 0.7
    }

# 5. Khởi tạo bản đồ
m = folium.Map(location=[20.97, 105.77], zoom_start=14, tiles='cartodbpositron')

# 6. Thêm nguyên cục GeoDataFrame vào (Không dùng vòng lặp for nữa)
folium.GeoJson(
    gdf,
    style_function=style_fn,
    tooltip=folium.GeoJsonTooltip(
        fields=['road_name', 'avg_speed', 'congestion_level'],
        aliases=['Đường:', 'Tốc độ:', 'Trạng thái:'],
        localize=True
    )
).add_to(m)

# 7. Lưu file
m.save("ban_do_giao_thong_ha_dong.html")
print("🚀 XONG! Bạn hãy mở file ban_do_giao_thong_ha_dong.html bằng Chrome hoặc Edge nhé!")