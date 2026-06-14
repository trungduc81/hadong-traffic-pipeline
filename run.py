import subprocess
import sys
import time

pipeline_steps = [
    "src/osm_data.py",
    "src/clean_data.py",
    "src/normalize.py",
    "src/data_loading.py"
]

def run_pipeline():
    for step in pipeline_steps:
        try:
            subprocess.run([sys.executable, step], check=True)
            print(f"Xong: {step}")
        except subprocess.CalledProcessError as e:
            print(f"Lỗi tại {step}: {e}")
            sys.exit(1)
            
    subprocess.Popen([sys.executable, "src/gps_simulator.py"])
    
    # Khởi chạy Streamlit
    print("Khởi chạy Streamlit Dashboard...")
    subprocess.run(["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"])

if __name__ == "__main__":
    run_pipeline()