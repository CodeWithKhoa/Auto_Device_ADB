import os
import subprocess
import time
import cv2
import numpy as np
import pytesseract

# Đường dẫn đến Tesseract (nếu cần, thay đổi tùy hệ điều hành)
# Ví dụ: pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def capture_screen(filename="screen.png"):
    """Chụp ảnh màn hình từ thiết bị Android."""
    subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"], check=True)
    subprocess.run(["adb", "pull", "/sdcard/screen.png", filename], check=True)
    return filename

def get_screen_size():
    """Lấy kích thước màn hình thiết bị."""
    result = subprocess.run(["adb", "shell", "wm", "size"], capture_output=True, text=True)
    output = result.stdout.strip()
    if "Physical size:" in output:
        size = output.split(": ")[-1]
        width, height = map(int, size.split("x"))
        return width, height
    return 1080, 1920  # Giá trị mặc định

def tap(x, y):
    """Chạm vào màn hình tại vị trí (x, y)."""
    print(f"🔹 Chạm vào ({x}, {y})")
    subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)], check=True)

def swipe_down(width, height, times=1):
    """Vuốt màn hình xuống `times` lần để tải nội dung mới."""
    for _ in range(times):
        print("🔄 Vuốt màn hình xuống")
        subprocess.run(["adb", "shell", "input", "swipe", str(width // 2), str(height - 300),
                        str(width // 2), "300", "500"], check=True)
        time.sleep(1.5)

def find_button(image_name, threshold=0.7):
    """Tìm vị trí nút (Home) trên màn hình bằng so khớp ảnh."""
    screen_path = capture_screen()
    screen = cv2.imread(screen_path, cv2.IMREAD_GRAYSCALE)

    if screen is None:
        print("❌ Lỗi khi đọc ảnh màn hình.")
        return None

    template_path = f"img/{image_name}.png"
    if not os.path.exists(template_path):
        print(f"⚠️ Không tìm thấy mẫu ảnh: {template_path}")
        return None

    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"⚠️ Lỗi khi đọc ảnh mẫu: {template_path}")
        return None

    best_match = None
    best_value = 0

    for scale in [1.0, 0.9, 0.8, 1.1]:  
        resized_template = cv2.resize(template, (0, 0), fx=scale, fy=scale)
        result = cv2.matchTemplate(screen, resized_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val > best_value:
            best_value = max_val
            best_match = (max_loc, resized_template.shape[::-1])  # (x, y) và (w, h)

    if best_match and best_value >= threshold:
        x, y = best_match[0]
        w, h = best_match[1]

        if image_name == "home":
            screen_width, _ = get_screen_size()
            x = screen_width - w - 10  # Dịch về góc phải

        return x + w // 2, y + h // 2  # Trả về tọa độ trung tâm nút

    return None

def find_text(text_to_find="Đăng xuất"):
    """Tìm văn bản trên màn hình bằng OCR."""
    screen_path = capture_screen()
    screen = cv2.imread(screen_path)

    if screen is None:
        print("❌ Lỗi khi đọc ảnh màn hình.")
        return None

    # Chuyển ảnh sang grayscale và tăng độ tương phản nếu cần
    gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Nhận diện văn bản bằng pytesseract
    data = pytesseract.image_to_data(gray, lang='vie', output_type=pytesseract.Output.DICT)  # 'vie' cho tiếng Việt

    # Tìm vị trí của văn bản cần tìm
    n_boxes = len(data['text'])
    for i in range(n_boxes):
        if text_to_find.lower() in data['text'][i].lower():
            x = data['left'][i]
            y = data['top'][i]
            w = data['width'][i]
            h = data['height'][i]
            return x + w // 2, y + h // 2  # Trả về tọa độ trung tâm của văn bản

    return None

def auto_process():
    """Tự động tìm nút Home, lướt xuống 3-4 lần, rồi tìm văn bản 'Đăng xuất'."""
    width, height = get_screen_size()

    # 1️⃣ Tìm và nhấn vào nút Home
    home_position = find_button("home")
    if home_position:
        tap(*home_position)
        print("🏠 Đã nhấn vào nút Home (góc phải).")
        time.sleep(1)

        # 2️⃣ Lướt xuống 3-4 lần
        swipe_down(width, height, times=3)
        time.sleep(1)

        # 3️⃣ Tìm và nhấn vào văn bản "Đăng xuất"
        for _ in range(5):  # Lặp tối đa 5 lần nếu chưa tìm thấy
            logout_position = find_text("Đăng xuất")
            if logout_position:
                tap(*logout_position)
                print("🚪 Đã nhấn vào văn bản 'Đăng xuất'.")
                return
            else:
                print("🔍 Không tìm thấy 'Đăng xuất', vuốt xuống tiếp...")
                swipe_down(width, height, times=1)
                time.sleep(1)

if __name__ == "__main__":
    auto_process()