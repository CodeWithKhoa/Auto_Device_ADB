import subprocess
import time
from pynput import mouse

# Biến toàn cục để kiểm soát việc nghe sự kiện
running = True

def enable_show_taps():
    """Bật hiển thị vị trí nhấn trên màn hình thiết bị"""
    try:
        subprocess.run(["adb", "shell", "settings", "put", "system", "show_touches", "1"], check=True)
        print("✅ Đã bật hiển thị vị trí nhấn trên thiết bị")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi bật hiển thị vị trí nhấn: {e}")

def start_scrcpy():
    """Khởi động scrcpy để hiển thị màn hình thiết bị"""
    try:
        # Chạy scrcpy với kích thước tối đa 1024
        subprocess.Popen(["scrcpy", "-m", "1024"])
        print("✅ Đã khởi động scrcpy")
        time.sleep(2)  # Đợi scrcpy khởi động
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi khởi động scrcpy: {e}")

def on_click(x, y, button, pressed):
    """Xử lý sự kiện nhấn chuột"""
    global running
    if pressed:
        print(f"🔹 Vị trí chạm: ({x}, {y})")
        # Thoát nếu nhấn chuột phải
        if button == mouse.Button.right:
            print("🛑 Dừng script (nhấn chuột phải)")
            running = False
            return False  # Dừng listener

def listen_mouse():
    """Lắng nghe sự kiện chuột và hiển thị tọa độ"""
    with mouse.Listener(on_click=on_click) as listener:
        while running:
            time.sleep(0.1)  # Giảm tải CPU
        listener.stop()

if __name__ == "__main__":
    # Bật hiển thị vị trí nhấn trên thiết bị
    enable_show_taps()
    
    # Khởi động scrcpy
    start_scrcpy()
    
    # Lắng nghe sự kiện chuột
    print("ℹ️ Nhấn chuột trái trong cửa sổ scrcpy để hiển thị tọa độ. Nhấn chuột phải để thoát.")
    listen_mouse()