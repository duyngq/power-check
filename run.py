import os
import sys
import subprocess

def main():
    # Thư mục chứa file frontend/app.py
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "app.py")
    
    if not os.path.exists(frontend_path):
        print(f"Error: Could not find {frontend_path}")
        sys.exit(1)

    print("--- Dang khoi dong Lich Cup Dien Dashboard ---")
    
    # Lệnh chạy streamlit
    cmd = [
        "streamlit", "run", frontend_path,
        "--server.headless", "true",
        "--server.port", "8501"
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n--- Da dung ung dung. ---")
    except Exception as e:
        print(f"--- Co loi xay ra: {e} ---")

if __name__ == "__main__":
    main()
