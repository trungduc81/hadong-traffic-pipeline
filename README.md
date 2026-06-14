# 🚦 Xây dựng Hạ tầng Dữ liệu Không gian Giám sát Giao thông Quận Hà Đông

## 📋 Thông tin Dự án

| Thông tin | Chi tiết |
|-----------|---------|
| **Tên dự án** | Xây dựng Hạ tầng Dữ liệu Không gian Giám sát Giao thông Quận Hà Đông |
| **Sinh viên thực hiện** | Trần Đức Trung |
| **Mã sinh viên** | B23DCCN864 |
| **Công nghệ chính** | Python 3.10, Streamlit, PostGIS, PostgreSQL, GeoPandas |

---

## 🏗️ Kiến trúc Dự án

```
Hạ tầng Dữ liệu Giao thông
│
├── 📥 ETL Pipeline (Data Ingestion)
│   ├── 1️⃣ osm_data.py → Trích xuất dữ liệu từ OpenStreetMap
│   ├── 2️⃣ clean_data.py → Làm sạch dữ liệu thô
│   ├── 3️⃣ normalize.py → Chuẩn hóa cấu trúc & hệ tọa độ
│   └── 4️⃣ data_loading.py → Nạp vào PostgreSQL + PostGIS
│
├── 📊 Streaming Data (Real-time)
│   └── gps_simulator.py → Giả lập GPS tracking liên tục
│
└── 🎨 Dashboard (Visualization)
    └── app.py → Giao diện Streamlit hiển thị Heatmap & Speed Map
```

---

## 📦 Tech Stack

- **Backend**: Python 3.10
- **Web Framework**: Streamlit
- **Database**: PostgreSQL 15 + PostGIS 3.3
- **Data Processing**: Pandas, GeoPandas, Shapely, OSMnx, NetworkX
- **Containerization**: Docker & Docker Compose

---

## 🚀 Hướng dẫn Cài đặt (One-click Run)

### Yêu cầu tiên quyết
- Docker & Docker Compose đã cài đặt
- Port 8501 (Streamlit) và 5433 (PostgreSQL) không bị chiếm dụng

### Bước 1: Clone hoặc tải dự án
```bash
cd d:\Ky2_Nam3\TTCS
```

### Bước 2: Khởi chạy toàn bộ hệ thống
```bash
docker compose up --build -d
```

**Giải thích lệnh:**
- `up` → Khởi chạy các service
- `--build` → Rebuild image từ Dockerfile
- `-d` → Chạy ở chế độ background (daemon)

### Bước 3: Truy cập Dashboard
Mở trình duyệt và vào:
```
http://localhost:8501
```

### Bước 4: Theo dõi tiến độ
```bash
# Xem logs của tất cả container
docker compose logs -f

# Xem logs của service web
docker compose logs -f web

# Xem logs của service db
docker compose logs -f db
```

---

## 🛑 Dừng dự án

```bash
docker compose down
```

Để xóa cả volume (dữ liệu):
```bash
docker compose down -v
```

---

## 📁 Cấu trúc Thư mục

```
TTCS/
├── src/
│   ├── osm_data.py           # Bước 1: Trích xuất OSM
│   ├── clean_data.py         # Bước 2: Làm sạch
│   ├── normalize.py          # Bước 3: Chuẩn hóa
│   ├── data_loading.py       # Bước 4: Nạp DB
│   ├── gps_simulator.py      # Streaming GPS
│   └── app.py                # Dashboard Streamlit
│
├── data/                      # Lưu trữ file geojson/csv
├── postgres_data/             # Database files (Docker)
├── cache/                     # Cache files
│
├── Dockerfile                 # Đóng gói Python env
├── docker-compose.yml         # Orchestrate services
├── entrypoint.sh              # Script chạy ETL
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore rules
└── README.md                  # Tài liệu này
```

---

## 🔧 Biến Môi trường

File `docker-compose.yml` tự động thiết lập:

| Biến | Giá trị |
|------|--------|
| `POSTGRES_DB` | hadong_traffic |
| `POSTGRES_USER` | trung |
| `POSTGRES_PASSWORD` | 123456 |
| `POSTGRES_HOST` | db (từ Docker network) |
| `POSTGRES_PORT` | 5432 |
| `DB_URI` | postgresql://trung:123456@db:5432/hadong_traffic |

---

## 🔄 Luồng ETL Pipeline

### Bước 1: Trích xuất từ OpenStreetMap (`osm_data.py`)
- Sử dụng **OSMnx** để tải dữ liệu đường xá từ OpenStreetMap
- Giới hạn khu vực: Quận Hà Đông, Hà Nội
- Output: GeoJSON chứa tất cả edges & nodes

### Bước 2: Làm sạch Dữ liệu (`clean_data.py`)
- Xóa các cạnh trùng lặp, không hợp lệ
- Chuẩn hóa cột dữ liệu (tên đường, tốc độ max, v.v.)
- Output: GeoJSON sạch

### Bước 3: Chuẩn hóa (`normalize.py`)
- Kiểm tra & chuyển đổi hệ tọa độ (EPSG:4326)
- Làm phẳng cấu trúc nested JSON
- Output: GeoJSON chuẩn hóa

### Bước 4: Nạp vào Database (`data_loading.py`)
- Tạo schema PostgreSQL với PostGIS extension
- Nạp dữ liệu vào bảng `road_segment`
- Tạo bảng `vehicle` (phương tiện giả lập)
- Tạo bảng `gps_tracking` (để chứa dữ liệu GPS streaming)

---

## 📊 Streaming GPS (gps_simulator.py)

- Chạy **liên tục** ngầm trong container
- Giả lập vị trí GPS của các phương tiện trên đường
- Ghi nhận vào bảng `gps_tracking` với timestamp
- Dashboard sử dụng dữ liệu này để vẽ Heatmap

---

## 🎨 Dashboard (app.py)

**Tính năng:**
- 🔥 **Heatmap**: Hiển thị điểm tập trung mật độ giao thông
- 🛣️ **Speed Map**: Hiển thị tốc độ trung bình trên từng đoạn đường
- 📊 Thống kê: Tổng số phương tiện, tốc độ trung bình, v.v.

**Truy cập:**
```
http://localhost:8501
```

---

## 🐛 Troubleshooting

### 1. Port 8501 hoặc 5433 đã bị chiếm dụng
```bash
# Thay đổi port trong docker-compose.yml
# Ví dụ: "8502:8501" thay vì "8501:8501"
docker compose up --build -d
```

### 2. PostgreSQL không khởi động
```bash
docker compose logs db
```

### 3. Streamlit không kết nối được Database
- Kiểm tra `entrypoint.sh` có chạy ETL chưa
- Kiểm tra Database có bảng `gps_tracking` chưa

### 4. Xóa tất cả và reset
```bash
docker compose down -v
docker system prune -a
docker compose up --build -d
```

---

## 📝 Ghi chú Phát triển

Để chỉnh sửa code trong quá trình phát triển:
1. Sửa file trong `src/`
2. Container sẽ tự động reload (do volume mount)
3. Hoặc rebuild: `docker compose up --build -d`

---

## 📚 Tài liệu Tham khảo

- [Streamlit Documentation](https://docs.streamlit.io/)
- [GeoPandas Documentation](https://geopandas.org/)
- [PostGIS Documentation](https://postgis.net/)
- [OSMnx Documentation](https://osmnx.readthedocs.io/)

---

## 📄 License

Dự án thực tập - Trường Đại học Công nghệ, Đại học Quốc gia Hà Nội

---

**Ngày cập nhật:** 2024  
**Liên hệ:** Trần Đức Trung - B23DCCN864
