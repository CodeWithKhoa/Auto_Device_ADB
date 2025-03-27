import os
import subprocess
import base64
import urllib.parse
import time
import cv2
import numpy as np

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
        subprocess.Popen(["scrcpy"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)  # Delay để đảm bảo scrcpy khởi động trước
    except FileNotFoundError:
        print("❌ Không tìm thấy scrcpy. Hãy cài đặt từ https://github.com/Genymobile/scrcpy")

def start_sndcpy():
    """Khởi chạy sndcpy để truyền âm thanh từ điện thoại về máy tính (nếu tồn tại)"""
    if not os.path.exists("sndcpy"):
        print("⚠️ Không tìm thấy sndcpy. Hãy tải về từ https://github.com/rom1v/sndcpy nếu cần âm thanh.")
        return
    try:
        subprocess.Popen(["sndcpy"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)  # Delay để đảm bảo sndcpy khởi động trước
    except FileNotFoundError:
        print("⚠️ Không thể khởi chạy sndcpy.")

def tap(x, y):
    """Chạm vào màn hình tại vị trí (x, y)"""
    print(f"🔹 Chạm vào ({x}, {y})")
    subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)], check=True)

def swipe_down(width, height):
    """Vuốt màn hình xuống để tải nội dung mới"""
    print("🔄 Vuốt màn hình xuống")
    subprocess.run(["adb", "shell", "input", "swipe", str(width // 2), str(height - 300),
                    str(width // 2), "300", "500"], check=True)

def capture_screen(filename="screen.png"):
    """Chụp ảnh màn hình từ thiết bị Android"""
    subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"], check=True)
    subprocess.run(["adb", "pull", "/sdcard/screen.png", filename], check=True)
    return filename

def find_like_button(threshold=0.7):
    """Tìm nút Like (dạng sáng hoặc tối) trên màn hình"""
    screen_path = capture_screen()
    screen = cv2.imread(screen_path, cv2.IMREAD_GRAYSCALE)

    if screen is None:
        print("❌ Lỗi khi đọc ảnh màn hình.")
        return None

    templates = {
        "like": "img/like.png",
    }

    best_match = None
    best_value = 0

    for name, template_path in templates.items():
        if not os.path.exists(template_path):
            print(f"⚠️ Không tìm thấy tệp mẫu: {template_path}")
            continue

        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"⚠️ Lỗi khi đọc ảnh mẫu: {template_path}")
            continue

        for scale in [1.0, 0.9, 0.8, 1.1]:  
            resized_template = cv2.resize(template, (0, 0), fx=scale, fy=scale)

            result = cv2.matchTemplate(screen, resized_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            print(f"🔍 Mức độ khớp ({name}, scale {scale}): {max_val}")

            if max_val > best_value:
                best_value = max_val
                best_match = (max_loc, resized_template.shape[::-1])  # (x, y) và (w, h)

    if best_match and best_value >= threshold:
        x, y = best_match[0]
        w, h = best_match[1]
        x_center, y_center = x + w // 2, y + h // 2
        print(f"👍 Nút Like được tìm thấy tại ({x_center}, {y_center}) với độ khớp {best_value:.2f}")
        return x_center, y_center  

    print("❌ Không tìm thấy nút Like.")
    return None

def auto_like_loop(max_swipes=20):
    """Tự động tìm và nhấn vào nút Like, nếu không tìm thấy thì cuộn xuống"""
    width, height = get_screen_size()
    for _ in range(max_swipes):
        position = find_like_button()
        if position:
            x, y = position
            tap(x, y)  # Chạm vào tâm của nút Like
            time.sleep(1)  # Delay trước khi tìm tiếp
        else:
            swipe_down(width, height)  # Vuốt xuống nếu không thấy nút Like
            time.sleep(1)  # Đợi tải nội dung mới

def main():
    check_adb()
    connect_device()
    width, height = get_screen_size()
    print(f"📱 Kích thước màn hình: {width}x{height}")
    start_scrcpy()
    start_sndcpy()
    
    print("📲 Bắt đầu tự động hóa")
    time.sleep(1)  # Delay để đảm bảo mọi thứ đã khởi động
    auto_like_loop()  # Tự động tìm và nhấn nút Like, nếu không thì cuộn xuống

if __name__ == "__main__":
    main()
