import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from sqlalchemy import create_engine

st.set_page_config(page_title="Hà Đông Traffic", layout="wide")
st.title(" Dashboard Giám sát giao thông Hà Đông")

DB_URI = "postgresql://trung:123456@localhost:5433/hadong_traffic"
engine = create_engine(DB_URI)

try:
    query_vehicles = "SELECT COUNT(DISTINCT vehicle_id) FROM gps_tracking;"
    total_vehicles = pd.read_sql(query_vehicles, engine).iloc[0, 0]
    
    query_avg_speed = """
        SELECT ROUND(AVG(speed_kmh)::numeric, 1) 
        FROM (
            SELECT DISTINCT ON (vehicle_id) speed_kmh 
            FROM gps_tracking 
            ORDER BY vehicle_id, gps_time DESC
        ) as latest_speeds;
    """
    avg_speed = pd.read_sql(query_avg_speed, engine).iloc[0, 0] or 0.0
    
    query_congested = """
    SELECT COUNT(*) 
    FROM traffic_analytics a
    JOIN road_segment r ON a.road_id = r.road_id
    WHERE a.congestion_level LIKE '%%Kẹt xe%%'
      AND r.road_type IN ('primary', 'secondary', 'tertiary', 'trunk', 'motorway')
      AND r.road_name IS NOT NULL;
    """
    congested_segments = pd.read_sql(query_congested, engine).iloc[0, 0]

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Tổng số phương tiện lưu thông", value=f"{total_vehicles} xe")
        
    with col2:
        st.metric(label="Vận tốc trung bình hệ thống", value=f"{avg_speed} km/h")
        
    with col3:
        st.metric(label="Số phân đoạn đang ùn tắc (Đỏ)", value=f"{congested_segments} đoạn")

except Exception as kpi_error:
    st.warning(f"Hệ thống đang tích lũy luồng dữ liệu, các thẻ KPI chỉ số sẽ hiển thị sau ít phút.")

st.markdown("---")

st.sidebar.header(" Bảng Điều Khiển")
layer_choice = st.sidebar.radio(
    "Chọn chế độ hiển thị:",
    (" Bản đồ mật độ (Heatmap)", " Bản đồ tốc độ (Line Map)")
)

m = folium.Map(location=[20.9718, 105.7725], zoom_start=14, tiles="cartodbpositron")

if layer_choice == " Bản đồ mật độ (Heatmap)":
    st.subheader("Phân tích điểm nóng (Hotspot) - Khu vực tập trung đông phương tiện")
    
    sql_heatmap = """
        SELECT ST_Y(geom) as lat, ST_X(geom) as lon
        FROM (
            SELECT DISTINCT ON (vehicle_id) geom
            FROM gps_tracking
            ORDER BY vehicle_id, gps_time DESC
        ) as latest_gps;
    """
    try:
        df_gps = pd.read_sql(sql_heatmap, engine)

        heat_data = df_gps[['lat', 'lon']].values.tolist()
        
        HeatMap(heat_data, radius=17, blur=12, max_zoom=1).add_to(m) 
        
    except Exception as e:
        st.error(f"Lỗi truy xuất dữ liệu: {e}")

elif layer_choice == " Bản đồ tốc độ (Line Map)":
    st.subheader("Trạng thái tốc độ và ùn tắc theo phân đoạn đường")
    
    try:
        query_lines = """
            SELECT r.road_name, r.geom, a.avg_speed, a.congestion_level
            FROM road_segment r
            JOIN traffic_analytics a ON r.road_id = a.road_id
            WHERE r.road_type IN ('primary', 'secondary', 'tertiary', 'trunk', 'motorway')
              AND r.road_name IS NOT NULL
        """
        gdf_roads = gpd.read_postgis(query_lines, engine, geom_col='geom')

        if gdf_roads.crs is None:
            gdf_roads.set_crs(epsg=4326, inplace=True)

        def style_fn(feature):
            level = feature['properties']['congestion_level']
            color = 'green'
            if level == 'Kẹt xe (Heavy)': 
                color = 'red'
            elif level == 'Mật độ cao (Medium)': 
                color = 'orange'
            
            return {
                'color': color,
                'weight': 4,
                'opacity': 0.7
            }

        folium.GeoJson(
            gdf_roads,
            style_function=style_fn,
            tooltip=folium.GeoJsonTooltip(
                fields=['road_name', 'avg_speed', 'congestion_level'],
                aliases=['Đường:', 'Tốc độ:', 'Trạng thái:'],
                localize=True
            )
        ).add_to(m)

    except Exception as e:
        st.error(f"Lỗi truy xuất dữ liệu không gian đường xá: {e}")

st_folium(m, width=1200, height=600)