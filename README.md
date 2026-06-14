# 🚦 Traffic-Flow-Analyzer (Hà Đông Traffic Monitoring)

Hệ thống Data Pipeline tự động hóa dùng để thu thập, giả lập và phân tích dữ liệu giao thông thực tế tại khu vực quận Hà Đông, Hà Nội.

## 1. Tổng quan dự án và tác dụng
Dự án được thiết kế để giải quyết bài toán quản lý dữ liệu không gian hạ tầng giao thông. Hệ thống cho phép:
* **Tự động hóa luồng dữ liệu (ETL)**: Thu thập mạng lưới đường từ OpenStreetMap, làm sạch và chuẩn hóa dữ liệu bản đồ.
* **Mô phỏng thực tế**: Giả lập luồng di chuyển của các phương tiện với dữ liệu GPS giả lập 
* **Phân tích thông minh**: Áp dụng thuật toán tính toán mật độ giao thông và trạng thái ùn tắc trên các phân đoạn đường.
* **Trực quan hóa**: Cung cấp Dashboard theo dõi trực tiếp các điểm nóng (Hotspots) và vận tốc phương tiện trên bản đồ.

## 2. Công nghệ sử dụng
Dự án sử dụng các công nghệ:
* **Ngôn ngữ**: Python 3.10 và các thư viện hỗ trợ 
* **Data Engineering**: ETL Pipeline , Pandas, GeoPandas, SQLAlchemy
* **Deploy**: Docker & Docker Compose 
* **Spatial Data**: PostGIS & PostgresSQL 

## 3. Cấu trúc dự án
Hệ thống vận hành theo một quy trình khép kín, được điều phối bởi run.py. Luồng đi của dữ liệu như sau:

Extract (Trích xuất): src/osm_data.py -> Tải dữ liệu thô từ OpenStreetMap về máy.

Transform (Biến đổi - Bước 1): src/clean_data.py -> Loại bỏ các thông tin dư thừa, xử lý dữ liệu rác từ file thô.

Transform (Biến đổi - Bước 2): src/normalize.py -> Định dạng lại cấu trúc cột, kiểu dữ liệu, hệ tọa độ (EPSG:4326) để khớp với Schema trong Database.

Load (Nạp): src/data_loading.py -> Đẩy dữ liệu đã làm sạch vào PostgreSQL/PostGIS.

Simulation & Analytics:

src/gps_simulator.py: Tạo luồng dữ liệu giả lập (GPS) và nạp vào DB.

src/app.py: Đọc dữ liệu từ DB (kết hợp qua View traffic_analytics) và hiển thị lên Dashboard.
```
hadong-traffic-pipeline/
├── src/                   
│   ├── osm_data.py         # (E) Extract: Tải dữ liệu OSM
│   ├── clean_data.py       # (T) Transform: Làm sạch dữ liệu
│   ├── normalize.py        # (T) Transform: Chuẩn hóa cấu trúc
│   ├── data_loading.py     # (L) Load: Nạp dữ liệu vào DB
│   ├── gps_simulator.py    # Giả lập luồng di chuyển của xe
│   └── app.py              # Streamlit Dashboard hiển thị kết quả
│
├── data/                   # Chứa dữ liệu thô (.geojson, .csv)
├── init.sql                # Script khởi tạo database
├── run.py                  # Điều phối toàn bộ Pipeline
├── Dockerfile               
├── docker-compose.yml      
└── README.md               
```
## 4. Cách cài đặt và chạy

Dự án sử dụng Docker để đồng bộ hóa môi trường phát triển. Hãy đảm bảo bạn đã cài đặt [Docker](https://www.docker.com/products/docker-desktop/) và Docker Compose trước khi bắt đầu.

### Bước 1: Clone dự án 
```
git clone https://github.com/trungduc81/hadong-traffic-pipeline.git
```
### Bước 2: Khởi chạy hệ thống
```
docker compose up -d --build
```
### Bước 3: Kiểm tra trạng thái tiến trình 
``` 
docker logs -f hadong_web
```
### Bước 4 : Truy cập dashboard
```
Mở trình duyệt web và truy cập http://localhost:8501
```
