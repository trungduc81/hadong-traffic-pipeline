- Cấu trúc CSDL được chia làm **3 lớp dữ liệu chính**: 

   --  Lớp hạ tầng : Bảng **road_segment** (lưu thông tin đường xá tại Hà Đông)

   --  Lớp đối tượng : Bảng **vehicle** (lưu thông tin xe cộ)

   --  Lớp động : Bảng **gps_tracking**( lưu lịch sử di chuyển) và bảng **traffic_analytics** lưu kết quả phân tích giao thông 

- Bảng **road_segment**:
```
CREATE TABLE road_segment (
    road_id SERIAL PRIMARY KEY, --  Khóa chính 
    osm_id BIGINT ,       -- ID của OSM (không phải duy nhất )
    road_name TEXT,             -- tên đường
    road_type TEXT,             -- kiểu đường 
    oneway BOOLEAN,             -- đường có một chiều hay không 
    length_m FLOAT,             -- độ dài đường
    max_speed INT,              -- tốc độ tối đa trên đoạn đường 
    geom GEOMETRY(LineString, 4326)  -- tọa độ kiểu LineString 
);
```

- Bảng **vehicle**:
```
CREATE TABLE vehicle (
    vehicle_id SERIAL PRIMARY KEY,  
    vehicle_code VARCHAR(50),
    vehicle_type VARCHAR(100)
);
```

- Bảng **gps_tracking**:
```
CREATE TABLE gps_tracking (
    tracking_id BIGSERIAL PRIMARY KEY,    
    vehicle_id INTEGER REFERENCES vehicle(vehicle_id), --khóa ngoại trỏ tới bảng xe
    gps_time TIMESTAMP,   -- mốc thời gian ghi nhận tọa độ 
    speed_kmh DOUBLE PRECISION,  -- vận tốc của xe tại thời điểm đó 
    geom GEOMETRY(Point, 4326)    -- tọa độ kiểu Point 
);
```

- Bảng **traffic_analytics**:
```
CREATE TABLE traffic_analytics (
    road_id INTEGER REFERENCES road_segment(road_id),
    check_time TIMESTAMP,
    avg_speed DOUBLE PRECISION,
    congestion_level VARCHAR(50), 
    PRIMARY KEY (road_id, check_time)
);
``` 