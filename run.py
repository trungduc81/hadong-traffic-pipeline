import subprocess
import sys
import time
import os
from sqlalchemy import create_engine, text

DB_URI = os.getenv("DB_URI", "postgresql://trung:123456@hadong_db:5432/hadong_traffic")
engine = create_engine(DB_URI)

def init_database():
    create_sql = """
    CREATE TABLE IF NOT EXISTS vehicle (
        vehicle_code TEXT,
        vehicle_type TEXT
    );

    CREATE TABLE IF NOT EXISTS road_segment (
        road_id TEXT,
        road_name TEXT,
        road_type TEXT,
        max_speed NUMERIC,
        geom GEOMETRY(LineString, 4326)
    );

    CREATE TABLE IF NOT EXISTS gps_tracking (
        vehicle_id TEXT,
        gps_time TIMESTAMP,
        speed_kmh NUMERIC,
        geom GEOMETRY(Point, 4326)
    );

    CREATE OR REPLACE VIEW traffic_analytics AS
    SELECT 
        r.road_id,
        COALESCE(ROUND(AVG(g.speed_kmh)::NUMERIC, 2), r.max_speed::NUMERIC) AS avg_speed,
        CASE 
            WHEN AVG(g.speed_kmh) <= 20 THEN 'Ùn tắc'
            WHEN AVG(g.speed_kmh) <= 40 THEN 'Bình thường'
            ELSE 'Thông thoáng'
        END AS congestion_level
    FROM road_segment r
    LEFT JOIN gps_tracking g ON ST_DWithin(r.geom, g.geom, 0.0001)
    GROUP BY r.road_id, r.max_speed;
    """
    try:
        with engine.begin() as conn:
            conn.execute(text(create_sql))
        print("Khởi tạo database và dashboard thành công")
    except Exception as e:
        print(f"Lỗi khởi tạo Database: {e}")
        sys.exit(1)

pipeline_steps = [
    "src/osm_data.py",
    "src/clean_data.py",
    "src/normalize.py",
    "src/data_loading.py"
]

def run_pipeline():
    init_database()
    for step in pipeline_steps:
        try:
            subprocess.run([sys.executable, step], check=True)
            print(f"Xong: {step}")
        except subprocess.CalledProcessError as e:
            print(f"Lỗi tại {step}: {e}")
            sys.exit(1)
            
    # Khởi chạy Simulator và Dashboard
    subprocess.Popen([sys.executable, "src/gps_simulator.py"])
    
    print("Khởi chạy Streamlit Dashboard...",flush=True)
    subprocess.run(["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"])

if __name__ == "__main__":
    time.sleep(3)
    run_pipeline()
