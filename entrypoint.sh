#!/bin/bash

set -e

# Màu sắc cho output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Hàm log
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_wait() {
    echo -e "${YELLOW}[WAIT]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Đợi PostgreSQL khởi động
log_wait "Đợi PostgreSQL mở cổng 5432..."
POSTGRES_HOST=${POSTGRES_HOST:-localhost}
POSTGRES_PORT=${POSTGRES_PORT:-5432}

max_attempts=30
attempt=0
while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT" 2>/dev/null; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        log_error "PostgreSQL không phản hồi sau 30 lần thử"
        exit 1
    fi
    log_wait "Lần thử $attempt/$max_attempts... PostgreSQL đang khởi động"
    sleep 2
done
log_info "PostgreSQL đã sẵn sàng ✓"

# Chạy luồng ETL tĩnh theo thứ tự
log_info "Bắt đầu chạy luồng ETL Pipeline..."

if [ -f "src/osm_data.py" ]; then
    log_info "Bước 1/4: Trích xuất dữ liệu từ OpenStreetMap..."
    python src/osm_data.py || log_error "Lỗi tại bước trích xuất OSM"
else
    log_error "File src/osm_data.py không tìm thấy"
fi

if [ -f "src/clean_data.py" ]; then
    log_info "Bước 2/4: Làm sạch dữ liệu thô..."
    python src/clean_data.py || log_error "Lỗi tại bước làm sạch dữ liệu"
else
    log_error "File src/clean_data.py không tìm thấy"
fi

if [ -f "src/normalize.py" ]; then
    log_info "Bước 3/4: Chuẩn hóa cấu trúc và hệ tọa độ..."
    python src/normalize.py || log_error "Lỗi tại bước chuẩn hóa"
else
    log_error "File src/normalize.py không tìm thấy"
fi

if [ -f "src/data_loading.py" ]; then
    log_info "Bước 4/4: Nạp dữ liệu vào Database..."
    python src/data_loading.py || log_error "Lỗi tại bước nạp dữ liệu"
else
    log_error "File src/data_loading.py không tìm thấy"
fi

log_info "ETL Pipeline hoàn tất ✓"

# Chạy GPS simulator ngầm
if [ -f "src/gps_simulator.py" ]; then
    log_info "Chạy GPS Simulator ngầm..."
    python src/gps_simulator.py > /dev/null 2>&1 &
    GPS_PID=$!
    log_info "GPS Simulator chạy với PID: $GPS_PID"
else
    log_error "File src/gps_simulator.py không tìm thấy"
fi

# Cuối cùng, khởi chạy Streamlit Dashboard
log_info "Khởi chạy Streamlit Dashboard..."
streamlit run src/app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --logger.level=info \
    --client.showErrorDetails=true
