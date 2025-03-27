import cv2
import numpy as np

def find_button_in_image(template_path, image_path, threshold=0.8):
    # Đọc ảnh mẫu (nút) và ảnh lớn
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    
    # Kiểm tra xem ảnh có được đọc thành công không
    if template is None or image is None:
        print("❌ Lỗi: Không thể đọc file ảnh")
        return False, 0, None
    
    # Chuyển sang ảnh xám để xử lý
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Lấy kích thước của template
    h, w = template_gray.shape
    
    # Áp dụng template matching
    result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    
    # Tìm vị trí có độ khớp cao nhất
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # Kiểm tra xem có vượt ngưỡng không
    if max_val >= threshold:
        # Tính tỷ lệ phần trăm
        match_percentage = max_val * 100
        
        # Tọa độ góc trên trái và dưới phải của vùng khớp
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        
        # Vẽ hình chữ nhật lên ảnh gốc
        image_with_rectangle = image.copy()
        cv2.rectangle(image_with_rectangle, top_left, bottom_right, (0, 255, 0), 2)
        
        # Thu nhỏ ảnh trước khi hiển thị (ví dụ: giảm còn 50% kích thước)
        scale_percent = 50  # Tỷ lệ phần trăm kích thước (có thể chỉnh thành 30, 20, v.v.)
        width = int(image_with_rectangle.shape[1] * scale_percent / 100)
        height = int(image_with_rectangle.shape[0] * scale_percent / 100)
        resized_image = cv2.resize(image_with_rectangle, (width, height), interpolation=cv2.INTER_AREA)
        
        # Hiển thị ảnh đã thu nhỏ
        cv2.imshow('Result', resized_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return True, match_percentage, top_left
    else:
        return False, max_val * 100, None

# Sử dụng hàm
def main():
    # Đường dẫn đến ảnh
    template_path = 'img/month.png'  # Ảnh của nút cần tìm
    image_path = 'screen.png'  # Ảnh lớn chứa nút
    
    # Ngưỡng (threshold) từ 0 đến 1, điều chỉnh tùy mức độ khớp mong muốn
    threshold = 0.8
    
    # Gọi hàm kiểm tra
    found, percentage, position = find_button_in_image(template_path, image_path, threshold)
    
    if found:
        print(f"Đã tìm thấy nút với độ khớp: {percentage:.2f}%")
        print(f"Vị trí: {position}")
    else:
        print(f"Không tìm thấy nút. Độ khớp cao nhất: {percentage:.2f}%")

if __name__ == "__main__":
    main()