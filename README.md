# FaceAutoVN – Tự Động Tạo Tài Khoản Facebook

**FaceAutoVN** là giải pháp Python toàn diện, sử dụng ADB và AI inference để tự động tạo tài khoản Facebook trên thiết bị Android. Dự án chỉ cần hai file chính `main.py` và `adb.py`, cùng mô-đun xử lý ảnh tích hợp YOLOv10 hỗ trợ.

---

## 1. Tổng quan

* **Mục tiêu**: Giảm thiểu thao tác thủ công, tự động khởi tạo, xác thực và lưu trữ tài khoản Facebook.
* **Luồng chính**:

  1. Khởi ADB + scrcpy để stream màn hình Android.
  2. Xử lý hình ảnh realtime bằng AI model (YOLOv10) để nhận diện UI.
  3. Thực thi hành động (tap, input\_text) qua `ADBController`.
  4. Tạo email tạm, đọc mã xác nhận và hoàn thiện đăng ký.

---

## 2. Kiến trúc hệ thống

```
┌────────────────┐    ┌──────────────┐    ┌─────────────┐
│  main.py       │ -> │ ADBController│ -> │  Android    │
│  (Flow + Image │    │ (adb.py)     │    │  Device     │
│  Processing)   │    │              │    │             │
└────────────────┘    └──────────────┘    └─────────────┘
        │
        ▼
┌─────────────────────────┐
│ Email Service           │
│ (tempmail.id.vn API)    │
└─────────────────────────┘
```

* **main.py**: điều phối toàn bộ quy trình, bao gồm:

  * Stream màn hình và xử lý hình ảnh realtime với YOLOv10.
  * Thực thi thao tác thông qua `ADBController`.
  * Tạo và đọc email tạm để lấy mã xác nhận.
* **adb.py**: lớp `ADBController` khởi scrcpy, chụp màn hình, thao tác UI.
* **Email Service**: giao tiếp API `tempmail.id.vn` để tạo và đọc email xác thực.

---

## 3. Tính năng nổi bật

1. **AI-driven UI Detection**

   * Mô hình **YOLOv10** fine-tuned với gần 1,000 ảnh Facebook.
   * Thời gian inference \~200ms/frame (5+ FPS).
2. **Hoạt động tự động**

   * Từ khởi động scrcpy đến hoàn thành đăng ký, không cần tương tác tay.
3. **Email tạm tích hợp**

   * Tạo email, poll nhận mã xác nhận, xử lý luồng đăng ký.
4. **Mô-đun hóa linh hoạt**

   * `inference.py` và `ADBController` có thể tái sử dụng cho các dự án khác.
5. **Dễ cấu hình**

   * Tuỳ chỉnh thông tin cá nhân và tham số inference ngay trên `main.py`.

---

## 4. Cài đặt & Chạy

### 4.1. Yêu cầu môi trường

* Python ≥3.8
* ADB (`adb`) và `scrcpy` (≥v1.16) trong `PATH`
* Mạng internet để gọi API và HuggingFace
* (Tuỳ chọn) Giả lập Android nếu không có thiết bị thật

### 4.2. Cài đặt

```bash
git clone https://github.com/CodeWithKhoa/Auto_tap_on_phone.git
cd Auto_tap_on_phone
pip install -r requirements.txt
```

### 4.3. Cấu hình

Mở `main.py`, hiệu chỉnh các biến sau dòng đầu:

```python
# Thông tin người dùng
tokenEmail = "<TEMPMAIL_TOKEN>"
name, ho, gtinh = "Khoa", "Tranfa", "Nữ"
ngay_sinh, thang_sinh, nam_sinh = "31", "12", "2006"
sdt_or_email = "email"  # hoặc "sdt"
matkhau = "TranKhoa2006"
# AI model inference
model = get_model(
    model_id="trandangkhoa/22",
    api_key="<HUGGINGFACE_API_KEY>"
)
```

### 4.4. Khởi chạy

```bash
python main.py
```

* Dự án sẽ tự khởi scrcpy, hiển thị cửa sổ OpenCV.
* Toàn bộ quá trình: detect UI → tap/input → xử lý email → confirm.

---

## 5. Hướng dẫn `ADBController` (adb.py)

```python
from adb import ADBController
# Khởi thiết bị, debug=True để log chi tiết
device = ADBController(id_device=None, debug=True)
# Chụp màn hình
path = device.capture_screenshot("capture.png")
# Tap
device.tap(x=150, y=300)
# Long press
device.long_press(x=150, y=300, duration_ms=2000)
# Nhập văn bản
device.input_text("Xin chào Facebook", delete=True)
# Xóa ký tự
device.delete_left(count=5)
# Swipe
device.swipe(x1=100, y1=500, x2=100, y2=100, duration=800)
# Điều hướng
device.press_back()
device.press_home()
```

---

## 6. Xử lý hình ảnh trong `main.py`

Phần xử lý hình ảnh và AI Inference được tích hợp ngay trong `main.py`:

* **Ảnh đầu vào**: `phone.capture_screenshot()` lấy file `temp.png`.
* **Chuyển sang PIL**:

  ```python
  pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
  ```
* **Inference YOLOv10**:

  ```python
  result = model.infer(pil_img)[0].predictions
  ```
* **Xử lý kết quả**: lặp qua `predictions`, vẽ bounding box, lưu thông tin `class_name`, `confidence`, `box`.
* **Cơ chế tối ưu**:

  * Reuse Redis-like `shared_frame`, `shared_predictions` để đồng bộ giữa thread hiển thị và xử lý.
  * Sử dụng `detect_event` để trigger capture và infer mỗi khi cần.

---

## 7. Phương Pháp Kiểm Thử & Media Ví Dụ

Để minh họa năng lực xử lý hình ảnh và hoạt động tự động, FaceAutoVN hỗ trợ chèn trực tiếp **ảnh** và **video** demo:

### 7.1 Ảnh minh họa

* **Kết quả detection** trên màn hình Facebook:

  *Hình 1: Bounding box hiển thị các button/form được nhận diện.*

* **Luồng nhập liệu tự động**:

  *Hình 2: Ví dụ nhập tên và email tự động.*

### 7.2 Video demo

* Xem video quay lại toàn bộ quá trình chạy script:

  *Nhấp để xem video demo (MP4, \~20s).*

---

## 8. Giấy phép & Liên hệ

© 2025 FaceAutoVN by Tran Dang Khoa. All rights reserved.

* **License**: Distributed under the MIT License. Xem file [LICENSE](LICENSE) để biết chi tiết.
* **Email**: [tdkhoa.24104300082@sv.uneti.edu.vn](mailto:tdkhoa.24104300082@sv.uneti.edu.vn)
