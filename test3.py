import adb  # hoặc từ adb import ADBController nếu bạn tách file

device = adb.ADBController(debug=True)

for i in range(1000):
    if input("Nhấn Enter để chụp (hoặc nhập gì đó để dừng): ") == "":
        filename = fr"D:\Downloads\train\train_{i}.png"  # f-string raw để giữ nguyên \\
        device.capture_screenshot(filename)
        print(f"✅ Đã lưu: {filename}")
    else:
        print("⛔ Dừng vòng lặp")
        break
