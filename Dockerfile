FROM python:3.10-slim

# Cài đặt các thư viện hệ thống cần thiết cho GeoPandas và PostGIS
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy requirements.txt và cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ project
COPY . .

# Cấp quyền thực thi cho entrypoint script
RUN chmod +x entrypoint.sh

# Expose cổng Streamlit
EXPOSE 8501

# Chạy entrypoint script
ENTRYPOINT ["./entrypoint.sh"]
