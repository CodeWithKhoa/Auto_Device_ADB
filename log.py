import os
import subprocess
import time
import cv2
import numpy as np
import pytesseract

# Đường dẫn đến Tesseract (nếu cần, thay đổi tùy hệ điều hành)
# Ví dụ: pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Bảng chuyển đổi tiếng Việt có dấu sang kiểu Telex 
telex_map = {
    "à": "af", "á": "as", "ả": "ar", "ã": "ax", "ạ": "aj",
    "è": "ef", "é": "es", "ẻ": "er", "ẽ": "ex", "ẹ": "ej",
    "ì": "if", "í": "is", "ỉ": "ir", "ĩ": "ix", "ị": "ij",
    "ò": "of", "ó": "os", "ỏ": "or", "õ": "ox", "ọ": "oj",
    "ù": "uf", "ú": "us", "ủ": "ur", "ũ": "ux", "ụ": "uj",
    "ỳ": "yf", "ý": "ys", "ỷ": "yr", "ỹ": "yx", "ỵ": "yj",
    "â": "aa", "ầ": "aaf", "ấ": "aas", "ẩ": "aar", "ẫ": "aax", "ậ": "aaj",
    "ê": "ee", "ề": "eef", "ế": "ees", "ể": "eer", "ễ": "eex", "ệ": "eej",
    "ô": "oo", "ồ": "oof", "ố": "oos", "ổ": "oor", "ỗ": "oox", "ộ": "ooj",
    "ơ": "ow", "ờ": "owf", "ớ": "ows", "ở": "owr", "ỡ": "owx", "ợ": "owj",
    "ư": "uw", "ừ": "uwf", "ứ": "uws", "ử": "uwr", "ữ": "uwx", "ự": "uwj",
    "ă": "aw", "ằ": "awf", "ắ": "aws", "ẳ": "awr", "ẵ": "awx", "ặ": "awj",
    "đ": "dd",
    "À": "AF", "Á": "AS", "Ả": "AR", "Ã": "AX", "Ạ": "AJ",
    "È": "EF", "É": "ES", "Ẻ": "ER", "Ẽ": "EX", "Ẹ": "EJ",
    "Ì": "IF", "Í": "IS", "Ỉ": "IR", "Ĩ": "IX", "Ị": "IJ",
    "Ò": "OF", "Ó": "OS", "Ỏ": "OR", "Õ": "OX", "Ọ": "OJ",
    "Ù": "UF", "Ú": "US", "Ủ": "UR", "Ũ": "UX", "Ụ": "UJ",
    "Ỳ": "YF", "Ý": "YS", "Ỷ": "YR", "Ỹ": "YX", "Ỵ": "YJ",
    "Â": "AA", "Ầ": "AAF", "Ấ": "AAS", "Ẩ": "AAR", "Ẫ": "AAX", "Ậ": "AAJ",
    "Ê": "EE", "Ề": "EEF", "Ế": "EES", "Ể": "EER", "Ễ": "EEX", "Ệ": "EEJ",
    "Ô": "OO", "Ồ": "OOF", "Ố": "OOS", "Ổ": "OOR", "Ỗ": "OOX", "Ộ": "OOJ",
    "Ơ": "OW", "Ờ": "OWF", "Ớ": "OWS", "Ở": "OWR", "Ỡ": "OWX", "Ợ": "OWJ",
    "Ă": "AW", "Ằ": "AWF", "Ắ": "AWS", "Ẳ": "AWR", "Ẵ": "AWX", "Ặ": "AWJ",
    "Ư": "UW", "Ừ": "UWF", "Ứ": "UWS", "Ử": "UWR", "Ữ": "UWX", "Ự": "UWJ",
    "Đ": "DD"
}

def convert_to_telex(text):
    """Chuyển văn bản tiếng Việt có dấu sang kiểu Telex"""
    result = ""
    for char in text:
        if char in telex_map:
            result += telex_map[char]
        else:
            result += char
    return result

def clear_input():
    """Xóa nội dung trong ô nhập liệu tại tọa độ (x, y)"""
    try:
        # Di chuyển con trỏ về cuối dòng
        subprocess.run(["adb", "shell", "input", "keyevent", "123"], check=True)  # KEYCODE_MOVE_END
        
        # Xóa toàn bộ nội dung (giả sử tối đa 50 ký tự)
        for _ in range(50):
            subprocess.run(["adb", "shell", "input", "keyevent", "67"], check=True)  # KEYCODE_DEL
        print(f"✅ Đã xóa nội dung.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi xóa input: {e}")

def input_text(text):
    clear_input()
    """Nhập văn bản vào thiết bị qua ADB"""
    telex_text = convert_to_telex(text)
    print(f"🔹 Nhập văn bản: {text} (Telex: {telex_text})")
    
    adb_text = telex_text.replace(" ", "%s")
    try:
        subprocess.run(["adb", "shell", "input", "text", adb_text], check=True)
        print("✅ Gửi thành công")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi gửi: {e}")

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

def paste_text():
    """Dán nội dung từ clipboard (chỉ hoạt động trên một số thiết bị)."""
    subprocess.run(["adb", "shell", "input", "keyevent", "279"], check=True)  # 279 = Ctrl + V
    time.sleep(1)

def find_text(text_to_find="Đăng xuất"):
    """Tìm văn bản trên màn hình bằng OCR và in debug."""
    screen_path = capture_screen()
    screen = cv2.imread(screen_path)

    if screen is None:
        print("❌ Lỗi khi đọc ảnh màn hình.")
        return None

    gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Cấu hình nhận diện
    custom_config = r'--oem 3 --psm 6'
    data = pytesseract.image_to_data(gray, lang='vie', config=custom_config, output_type=pytesseract.Output.DICT)

    print("📋 Văn bản nhận diện được:")
    for i in range(len(data["text"])):
        text = data["text"][i].strip()
        x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]

        if text:
            print(f"🔹 '{text}' tại ({x}, {y}) - Kích thước: {w}x{h}")

        if text_to_find.lower() in text.lower():
            print(f"✅ Tìm thấy '{text_to_find}' tại ({x}, {y})")
            return x + w // 2, y + h // 2

    print(f"❌ Không tìm thấy '{text_to_find}' trên màn hình.")
    return None
def input_text_vietnamese(text):
    """Nhập văn bản tiếng Việt bằng cách copy-paste từ clipboard."""
    print(f"⌨️ Nhập: {text}")
    
    # Đặt nội dung vào clipboard
    subprocess.run(["adb", "shell", "am", "broadcast", "-a", "clipper.set", "--es", "text", text], check=True)

    time.sleep(1)  # Chờ một chút để clipboard cập nhật
    
    # Dán nội dung bằng Ctrl+V (KEYCODE_PASTE)
    subprocess.run(["adb", "shell", "input", "keyevent", "279"], check=True)

def auto_process(now = "home", fisrtname = "Tài", lastname = "Phan Anh", day = "31", month = "12", year = "2003", sex = "male", email = "yapoko1059@hikuhu.com", password = "Khoatran2006"):
    width, height = get_screen_size()
    if now=="home":
        """Tự động tìm nút Home, lướt xuống 3-4 lần, rồi tìm nút 'Đăng xuất' bằng hình ảnh."""
        for _ in range(5):  # Lặp tối đa 5 lần nếu chưa tìm thấy
            home_position = find_button("home", threshold=0.8)
            if home_position:
                tap(*home_position)
                print("🏠 Đã nhấn vào nút Home (góc phải).")
                time.sleep(1)
                break
            else:
                print("🔍 Không tìm thấy 'Home', Nhấn quay lại...")
                subprocess.run(["adb", "shell", "input", "keyevent", "4"], check=True)  # Nhấn nút Back
                time.sleep(2)

        # Đăng Xuất
        for _ in range(5):  # Lặp tối đa 5 lần nếu chưa tìm thấy
            logout_position = find_button("logout1", threshold=0.8)
            if logout_position:
                tap(*logout_position)
                print("🚪 Đã nhấn vào nút 'Đăng xuất1' (hình ảnh).")
                time.sleep(0.5)
                break
            else:
                print("🔍 Không tìm thấy 'Đăng xuất1', vuốt xuống tiếp...")
                swipe_down(width, height, times=1)
                time.sleep(1)
        for _ in range(5):  # Lặp tối đa 5 lần nếu chưa tìm thấy
            logout_position = find_button("logout2", threshold=0.8)
            if logout_position:
                tap(*logout_position)
                print("🚪 Đã nhấn vào nút 'Đăng xuất2' (hình ảnh).")
                time.sleep(0.5)
                break
            else:
                print("🔍 Không tìm thấy 'Đăng xuất2', vuốt xuống tiếp...")
                swipe_down(width, height, times=1)
                time.sleep(1)
    # Đăng Kí
    for _ in range(5):  # Lặp tối đa 5 lần nếu chưa tìm thấy
        register_position = find_button("register1", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("🚪 Đã nhấn vào nút 'register1' (hình ảnh).")
            break
        else:
            print("🔍 Không tìm thấy 'register1', vuốt xuống tiếp...")
            swipe_down(width, height, times=1)
            time.sleep(1)
    for _ in range(5):  # Lặp tối đa 5 lần nếu chưa tìm thấy
        register_position = find_button("register2", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("🚪 Đã nhấn vào nút 'register2' (hình ảnh).")
            break
        else:
            print("🔍 Không tìm thấy 'register2', vuốt xuống tiếp...")
            swipe_down(width, height, times=1)
            time.sleep(1)
            
    # Đăng ký
    for _ in range(5):
        register_position = find_button("register_lastname", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("📝 Đã nhấn vào form 'Họ'.")
            time.sleep(1)
            input_text(lastname)
            break
        else:
            print("🔍 Không tìm thấy 'Họ', vuốt xuống tiếp...")
            swipe_down(width, height, times=1)
            time.sleep(1)
    for _ in range(5):
        register_position = find_button("register_firstname", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("📝 Đã nhấn vào form 'Tên'.")
            time.sleep(1)
            input_text(fisrtname)
            break
        else:
            print("🔍 Không tìm thấy 'Tên', vuốt xuống tiếp...")
            swipe_down(width, height, times=1)
            time.sleep(1)
    for _ in range(5):
        register_position = find_button("next", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("🚪 Đã nhấn vào nút 'Tiếp'.")
            break
        else:
            print("🔍 Không tìm thấy 'Tiếp', vuốt xuống tiếp...")
            swipe_down(width, height, times=1)
            time.sleep(1)
    for _ in range(5):
        register_position = find_button("birthday_year", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("📝 Đã nhấn vào form 'Năm Sinh Nhật'.")
            input_text(year)
            time.sleep(1)
            break
        else:
            print("🔍 Không tìm thấy 'Năm Sinh Nhật'")
            # swipe_down(width, height, times=1)
            time.sleep(1)
    for _ in range(5):
        register_position = find_button("birthday_month", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("📝 Đã nhấn vào form 'Tháng Sinh Nhật'.")
            input_text(f"Th{month}")
            time.sleep(1)
            break
        else:
            print("🔍 Không tìm thấy 'Tháng Sinh Nhật'")
            # swipe_down(width, height, times=1)
            time.sleep(1)
    for _ in range(5):
        register_position = find_button("birthday_day", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("📝 Đã nhấn vào form 'Ngày Sinh Nhật'.")
            input_text(day)
            time.sleep(1)
            break
        else:
            print("🔍 Không tìm thấy 'Ngày Sinh Nhật'")
            # swipe_down(width, height, times=1)
            time.sleep(1)
    for _ in range(5):
        register_position = find_button("birthday_set", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("📝 Đã nhấn vào đặt 'Sinh Nhật'.")
            time.sleep(1)
            break
        else:
            print("🔍 Không tìm thấy đặt 'Sinh Nhật', vuốt xuống tiếp...")
            swipe_down(width, height, times=1)
            time.sleep(1)
    for _ in range(5):
        register_position = find_button("next", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("🚪 Đã nhấn vào nút 'Tiếp'.")
            break
        else:
            print("🔍 Không tìm thấy 'Tiếp', vuốt xuống tiếp...")
            swipe_down(width, height, times=1)
            time.sleep(1)
    for _ in range(5):
        if sex == "male":
            register_position = find_button("male", threshold=0.8)
        else: 
            register_position = find_button("female", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("🚪 Đã nhấn vào nút '"+sex+"'.")
            break
        else:
            print("🔍 Không tìm thấy '"+sex+"', vuốt xuống tiếp...")
            swipe_down(width, height, times=1)
            time.sleep(1)
    for _ in range(5):
        register_position = find_button("next", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("🚪 Đã nhấn vào nút 'Tiếp'.")
            break
        else:
            print("🔍 Không tìm thấy 'Tiếp', vuốt xuống tiếp...")
            swipe_down(width, height, times=1)
            time.sleep(1)
    for _ in range(5):
        register_position = find_button("convert_email", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("🚪 Đã nhấn vào nút 'Đăng ký bằng email'.")
            break
        else:
            print("🔍 Không tìm thấy 'Đăng ký bằng email', vuốt xuống tiếp...")
            swipe_down(width, height, times=1)
            time.sleep(1)
    for _ in range(5):
        register_position = find_button("email", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("📝 Đã nhấn vào form 'email'.")
            input_text(email)
            time.sleep(1)
            break
        else:
            print("🔍 Không tìm thấy 'email', vuốt xuống tiếp...")
            swipe_down(width, height, times=1)
            time.sleep(1)
    for _ in range(5):
        register_position = find_button("next", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("🚪 Đã nhấn vào nút 'Tiếp'.")
            break
        else:
            print("🔍 Không tìm thấy 'Tiếp', vuốt xuống tiếp...")
            swipe_down(width, height, times=1)
            time.sleep(1)
    for _ in range(5):
        register_position = find_button("password", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("📝 Đã nhấn vào form 'mật khẩu'.")
            input_text(password)
            time.sleep(1)
            break
        else:
            print("🔍 Không tìm thấy 'Mật khẩu', vuốt xuống tiếp...")
            swipe_down(width, height, times=1)
            time.sleep(1)
    for _ in range(5):
        register_position = find_button("next", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("🚪 Đã nhấn vào nút 'Tiếp'.")
            break
        else:
            print("🔍 Không tìm thấy 'Tiếp', vuốt xuống tiếp...")
            swipe_down(width, height, times=1)
            time.sleep(1)
    for _ in range(5):
        register_position = find_button("next", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("🚪 Đã nhấn vào nút 'Tiếp'.")
            break
        else:
            print("🔍 Không tìm thấy 'Tiếp', vuốt xuống tiếp...")
            swipe_down(width, height, times=1)
            time.sleep(1)
    for _ in range(5):
        register_position = find_button("save", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("🚪 Đã nhấn vào nút 'Lưu'.")
            break
        else:
            print("🔍 Không tìm thấy 'Lưu', vuốt xuống tiếp...")
            swipe_down(width, height, times=1)
            time.sleep(1)
    for _ in range(5):
        register_position = find_button("dongy", threshold=0.8)
        if register_position:
            tap(*register_position)
            print("🚪 Đã nhấn vào nút 'Đồng ý'.")
            break
        else:
            print("🔍 Không tìm thấy 'Đồng ý', vuốt xuống tiếp...")
            swipe_down(width, height, times=1)
            time.sleep(1)
    madung = False
    while(madung==False):
        ma = input("Nhập mã xác nhận: ")
        for _ in range(5):
            register_position = find_button("maxacnhan", threshold=0.8)
            if register_position:
                tap(*register_position)
                print("📝 Đã nhấn vào form 'Mã xác nhận'.")
                input_text(ma)
                time.sleep(1)
                break
            else:
                print("🔍 Không tìm thấy 'Mã xác nhận', vuốt xuống tiếp...")
                swipe_down(width, height, times=1)
                time.sleep(1)
        for _ in range(5):
            register_position = find_button("next", threshold=0.8)
            if register_position:
                tap(*register_position)
                print("🚪 Đã nhấn vào nút 'Tiếp'.")
                time.sleep(0.5)
                break
            else:
                print("🔍 Không tìm thấy 'Tiếp', vuốt xuống tiếp...")
                swipe_down(width, height, times=1)
                time.sleep(1)

        

    time.sleep(10)
    capture_screen()
    print(f"Đã tạo thành công email: {email}, Password: {password}")

if __name__ == "__main__":
    now = input()
    auto_process(now)