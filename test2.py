import serial
import speech_recognition as sr
import time
import queue

# Cấu hình cổng Serial
SERIAL_PORT = "COM4"
BAUD_RATE = 115200

# Khởi tạo kết nối Serial
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Đã kết nối tới {SERIAL_PORT} với baud rate {BAUD_RATE}")
except serial.SerialException as e:
    print(f"Lỗi kết nối Serial: {e}")
    exit()

# Khởi tạo nhận diện giọng nói
recognizer = sr.Recognizer()
mic = sr.Microphone()
command_queue = queue.Queue()  # Hàng đợi để lưu lệnh nhận diện được

# Hàm gửi dữ liệu qua Serial
def send_command(command):
    command = command + "\n"
    ser.write(command.encode('utf-8'))
    print(f"Đã gửi: {command.strip()}")
    time.sleep(1)  # Đợi ESP32 phản hồi
    while ser.in_waiting > 0:
        try:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            if response:
                print(f"Phản hồi từ ESP32: {response}")
        except UnicodeDecodeError as e:
            print(f"Lỗi giải mã dữ liệu từ ESP32: {e}")

# Hàm callback khi nhận diện giọng nói
def speech_callback(recognizer, audio):
    try:
        text = recognizer.recognize_google(audio, language="vi-VN")
        print(f"Bạn đã nói: {text}")
        command_queue.put(text.lower())  # Thêm lệnh vào hàng đợi
    except sr.UnknownValueError:
        print("Không nhận diện được giọng nói")
    except sr.RequestError as e:
        print(f"Lỗi kết nối tới dịch vụ nhận diện: {e}")

# Vòng lặp chính
try:
    # Điều chỉnh tiếng ồn môi trường ban đầu
    with mic as source:
        print("Đang điều chỉnh tiếng ồn môi trường...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

    # Bắt đầu lắng nghe liên tục trong nền
    print("Mic đã mở, đang lắng nghe liên tục (nói 'thoát' để dừng)...")
    stop_listening = recognizer.listen_in_background(mic, speech_callback)

    while True:
        try:
            # Lấy lệnh từ hàng đợi (không chặn nếu không có lệnh)
            command = command_queue.get_nowait()
            if command:
                if "thoát" in command:
                    send_command(command)
                    stop_listening(wait_for_stop=False)  # Tắt mic khi thoát
                    break
                send_command(command)
            time.sleep(0.1)  # Giảm tải CPU
        except queue.Empty:
            time.sleep(0.1)  # Chờ nếu không có lệnh mới

except KeyboardInterrupt:
    print("\nĐã dừng bởi người dùng")
    stop_listening(wait_for_stop=False)  # Tắt mic khi nhấn Ctrl+C

finally:
    time.sleep(1)  # Đợi phản hồi cuối từ ESP32
    ser.close()
    print("Đã đóng kết nối Serial")