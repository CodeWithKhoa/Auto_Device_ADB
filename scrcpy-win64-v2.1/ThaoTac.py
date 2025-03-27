import os
import subprocess

def check_adb():
    """Kiểm tra xem ADB đã được cài đặt chưa"""
    try:
        subprocess.run(["adb", "version"], check=True, capture_output=True)
        print("✅ ADB đã được cài đặt và hoạt động!")
    except FileNotFoundError:
        print("❌ Không tìm thấy ADB. Hãy cài đặt nó từ https://developer.android.com/studio/releases/platform-tools")
        exit()

def connect_device():
    """Hiển thị danh sách thiết bị và kết nối"""
    result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    devices = result.stdout.strip().split("\n")[1:]
    
    if not devices or devices == ['']:
        print("❌ Không có thiết bị nào được kết nối! Hãy bật gỡ lỗi USB và cắm cáp USB.")
        exit()
    
    print("🔗 Thiết bị đã kết nối:")
    for device in devices:
        print(device)

def get_screen_size():
    """Lấy kích thước màn hình thiết bị"""
    result = subprocess.run(["adb", "shell", "wm", "size"], capture_output=True, text=True)
    output = result.stdout.strip()
    if "Physical size:" in output:
        size = output.split(": ")[-1]
        width, height = map(int, size.split("x"))
        return width, height
    return 1080, 1920  # Giá trị mặc định

def start_scrcpy():
    """Mở scrcpy để hiển thị màn hình điện thoại"""
    try:
        subprocess.run(["scrcpy"], check=True)
    except FileNotFoundError:
        print("❌ Không tìm thấy scrcpy. Hãy cài đặt từ https://github.com/Genymobile/scrcpy")
        exit()

def start_sndcpy():
    """Khởi chạy sndcpy để truyền âm thanh từ điện thoại về máy tính"""
    try:
        subprocess.run(["sndcpy"], check=True)
    except FileNotFoundError:
        print("❌ Không tìm thấy sndcpy. Hãy tải về từ https://github.com/rom1v/sndcpy")
        exit()

def tap(x, y):
    """Chạm vào màn hình tại vị trí (x, y)"""
    print(f"🔹 Chạm vào ({x}, {y})")
    subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)], check=True)

def swipe(x1, y1, x2, y2, duration=500):
    """Vuốt từ (x1, y1) đến (x2, y2) trong thời gian duration (ms)"""
    print(f"🔹 Vuốt từ ({x1}, {y1}) đến ({x2}, {y2}) trong {duration}ms")
    subprocess.run(["adb", "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)], check=True)

def input_text(text):
    """Nhập văn bản vào thiết bị"""
    print(f"🔹 Nhập văn bản: {text}")
    subprocess.run(["adb", "shell", "input", "text", text.replace(" ", "%s")], check=True)

def main():
    check_adb()
    connect_device()
    width, height = get_screen_size()
    
    print(f"📱 Kích thước màn hình: {width}x{height}")
    start_scrcpy()
    start_sndcpy()
if __name__ == "__main__":
    main()
