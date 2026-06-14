CREATE EXTENSION IF NOT EXISTS postgis;

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

CREATE INDEX IF NOT EXISTS idx_road_geom ON road_segment USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_gps_geom ON gps_tracking USING GIST (geom);

CREATE OR REPLACE VIEW traffic_analytics AS
SELECT 
    r.road_id,
    COALESCE(ROUND(CAST(AVG(g.speed_kmh) AS NUMERIC), 2), CAST(r.max_speed AS NUMERIC)) AS avg_speed,
    CASE 
        WHEN AVG(g.speed_kmh) <= 20 THEN 'Ùn tắc'
        WHEN AVG(g.speed_kmh) <= 40 THEN 'Bình thường'
        ELSE 'Thông thoáng'
    END AS congestion_level
FROM road_segment r
LEFT JOIN gps_tracking g ON ST_DWithin(r.geom, g.geom, 0.0001)
GROUP BY r.road_id, r.max_speed;