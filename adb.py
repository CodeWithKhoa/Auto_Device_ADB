import os
import time, subprocess
from datetime import datetime

class ADBController:
    def __init__(self, id_device=None, debug=False):
        self.debug = debug
        if self._run_command("adb version") != 0:
            raise Exception("ADB không được cài đặt hoặc không hoạt động!")
        self.devices = self._get_connected_devices()
        if not self.devices:
            raise Exception("Không tìm thấy thiết bị Android nào được kết nối!")
        if id_device:
            if id_device in self.devices:
                self.device_id = id_device
                self._print(f"Sử dụng thiết bị được chỉ định: {self.device_id}")
            else:
                raise Exception(f"Thiết bị {id_device} không được kết nối!")
        else:
            self.device_id = self._select_device()

        self._start_scrcpy_with_uhid()

    def _start_scrcpy_with_uhid(self):
        """Chạy scrcpy với --keyboard=uhid và --no-video để tránh bật bàn phím ảo"""
        try:
            self._print("Khởi động scrcpy với --keyboard=uhid và không hiển thị hình...")
            subprocess.Popen(["scrcpy", "--keyboard=uhid", "--no-video", "--no-window", "--serial", self.device_id])
            time.sleep(2)
        except Exception as e:
            self._print(f"Lỗi khi khởi chạy scrcpy: {e}")

    def _print(self, message):
        if self.debug:
            print(message)

    def _run_command(self, command):
        return os.system(command)

    def _run_adb_command(self, command):
        return os.system(f"adb -s {self.device_id} {command}")

    def _get_adb_output(self, command):
        return os.popen(f"adb -s {self.device_id} shell {command}").read().strip()

    def _get_connected_devices(self):
        devices_output = os.popen("adb devices").read().strip().split("\n")[1:]
        return [line.split("\t")[0] for line in devices_output if "device" in line]

    def _select_device(self):
        if len(self.devices) == 1:
            print(f"Sử dụng thiết bị duy nhất: {self.devices[0]}")
            return self.devices[0]
        print("Nhiều thiết bị được kết nối:")
        for i, device in enumerate(self.devices, 1):
            print(f"{i}. {device}")
        while True:
            try:
                choice = int(input("Chọn thiết bị (nhập số): "))
                if 1 <= choice <= len(self.devices):
                    selected_device = self.devices[choice - 1]
                    self._print(f"Đã chọn thiết bị: {selected_device}")
                    return selected_device
                else:
                    self._print("Lựa chọn không hợp lệ, vui lòng chọn lại!")
            except ValueError:
                self._print("Vui lòng nhập một số!")

    def install_apk(self, apk_path, override_existing=False):
        """Cài đặt file APK lên thiết bị"""
        try:
            if not os.path.exists(apk_path):
                raise Exception(f"File APK không tồn tại tại: {apk_path}")
            
            self._print(f"Đang cài đặt APK: {apk_path}")
            command = f"adb -s {self.device_id} install"
            if override_existing:
                command += " -r"
            command += f" {apk_path}"
            result = os.system(command)
            if result == 0:
                self._print(f"Đã cài đặt thành công APK: {apk_path}")
                return True
            else:
                raise Exception(f"Cài đặt thất bại (exit code: {result})")
        except Exception as e:
            self._print(f"Lỗi khi cài đặt APK: {str(e)}")
            return False

    def uninstall_app(self, package_name):
        """Gỡ cài đặt ứng dụng"""
        try:
            self._print(f"Đang gỡ cài đặt ứng dụng: {package_name}")
            result = self._run_adb_command(f"uninstall {package_name}")
            if result == 0:
                self._print(f"Đã gỡ cài đặt thành công: {package_name}")
                return True
            else:
                raise Exception(f"Gỡ cài đặt thất bại (exit code: {result})")
        except Exception as e:
            self._print(f"Lỗi khi gỡ cài đặt: {str(e)}")
            return False

    def get_device_info(self):
        try:
            info = {
                "serial": self.device_id,
                "model": self._get_adb_output("getprop ro.product.model"),
                "android_version": self._get_adb_output("getprop ro.build.version.release"),
                "resolution": self._get_adb_output("wm size").replace("Physical size: ", "") if "Physical size" in self._get_adb_output("wm size") else "Không xác định"
            }
            self._print("\nThông tin thiết bị:")
            for key, value in info.items():
                self._print(f"{key}: {value}")
            return info
        except Exception as e:
            self._print(f"Lỗi khi lấy thông tin thiết bị: {str(e)}")
            return None

    def capture_screenshot(self, save_path=None):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot.png"
        if save_path is None:
            save_path = filename
        device_path = "/sdcard/screenshot.png"
        try:
            self._print("Đang chụp màn hình...")
            self._run_adb_command(f"shell screencap {device_path}")
            time.sleep(1)
            self._print("Đang chuyển file về máy tính...")
            self._run_adb_command(f"pull {device_path} {save_path}")
            self._print("Đang dọn dẹp...")
            self._run_adb_command(f"shell rm {device_path}")
            self._print(f"Đã lưu ảnh tại: {save_path}")
            return save_path
        except Exception as e:
            self._print(f"Lỗi khi chụp màn hình: {str(e)}")
            return None

    def tap(self, x, y):
        try:
            self._print(f"Click vào tọa độ ({x}, {y})...")
            self._run_adb_command(f"shell input tap {x} {y}")
        except Exception as e:
            self._print(f"Lỗi khi click: {str(e)}")

    def long_press(self, x, y, duration=1000):
        try:
            self._print(f"Ấn giữ tại ({x}, {y}) trong {duration}ms...")
            self._run_adb_command(f"shell input tap {x} {y}")
            time.sleep(duration / 1000.0)
            self._print("Đã thả long press")
            time.sleep(0.5)
        except Exception as e:
            self._print(f"Lỗi khi ấn giữ: {str(e)}")

    def swipe(self, x1, y1, x2, y2, duration=500):
        try:
            self._print(f"Lướt từ ({x1}, {y1}) đến ({x2}, {y2}) trong {duration}ms...")
            result = self._run_adb_command(f"shell input swipe {x1} {y1} {x2} {y2} {duration}")
            if result != 0:
                self._print(f"Cảnh báo: Lệnh swipe có thể không thành công (exit code: {result})")
            else:
                self._print("Swipe thành công")
            time.sleep(0.5)
        except Exception as e:
            self._print(f"Lỗi khi lướt: {str(e)}")

    def input_text(self, text, delete=False):
        """Nhập văn bản, nếu delete=True thì xóa văn bản hiện tại trước"""
        try:
            if delete:
                self._print("Xóa văn bản hiện tại...")
                for _ in range(5):
                    self._run_adb_command("shell input keyevent 67")
                    # time.sleep(0.05)
                self._print("Đã xóa văn bản hiện tại")

            self._print(f"Nhập văn bản: {text}")
            escaped_text = text.replace(" ", "%s").replace("'", "\\'")
            self._run_adb_command(f"shell input text '{escaped_text}'")
            # time.sleep(0.5)
        except Exception as e:
            self._print(f"Lỗi khi nhập văn bản: {str(e)}")

    def delete_left(self, count=1):
        """Xóa số ký tự về phía trái bằng phím Backspace"""
        try:
            self._print(f"Xóa {count} ký tự về phía trái...")
            for _ in range(count):
                self._run_adb_command("shell input keyevent 67")
                time.sleep(0.05)
            self._print(f"Đã xóa {count} ký tự")
        except Exception as e:
            self._print(f"Lỗi khi xóa ký tự: {str(e)}")

    def launch_app(self, package_name=None):
        """Khởi động ứng dụng với kiểm tra lỗi"""
        try:
            if package_name:
                self._print(f"Khởi động ứng dụng: {package_name}")
                result = self._run_adb_command(f"shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
                time.sleep(2)
                if result != 0:
                    self._print(f"Lỗi: Ứng dụng {package_name} không khởi động được (exit code: {result})")
                    return False
                # Sử dụng findstr thay cho grep trên Windows
                current_app = self._get_adb_output('dumpsys window | findstr mCurrentFocus')
                if package_name not in current_app:
                    self._print(f"Cảnh báo: Ứng dụng {package_name} có thể đã bị crash hoặc không mở đúng!")
                    return False
                self._print(f"Ứng dụng {package_name} đã khởi động thành công")
                return True
            else:
                packages = self._get_adb_output("pm list packages --user 0").splitlines()
                packages = [pkg.replace("package:", "") for pkg in packages]
                print("\nDanh sách ứng dụng đã cài đặt:")
                for i, pkg in enumerate(packages, 1):
                    print(f"{i}. {pkg}")
                while True:
                    try:
                        choice = int(input("Chọn ứng dụng để khởi động (nhập số, 0 để thoát): "))
                        if choice == 0:
                            self._print("Đã thoát khỏi chọn ứng dụng.")
                            return False
                        if 1 <= choice <= len(packages):
                            selected_package = packages[choice - 1]
                            return self.launch_app(selected_package)
                        else:
                            self._print("Lựa chọn không hợp lệ, vui lòng chọn lại!")
                    except ValueError:
                        self._print("Vui lòng nhập một số!")
        except Exception as e:
            self._print(f"Lỗi khi khởi động ứng dụng: {str(e)}")
            return False

    def restart_app(self, package_name):
        """Khởi động lại ứng dụng với kiểm tra lỗi"""
        try:
            self._print(f"Đang khởi động lại ứng dụng: {package_name}")
            self._run_adb_command(f"shell am force-stop {package_name}")
            time.sleep(1)
            result = self._run_adb_command(f"shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
            time.sleep(2)
            if result != 0:
                self._print(f"Lỗi: Không thể khởi động lại ứng dụng {package_name} (exit code: {result})")
                return False
            # Sử dụng findstr thay cho grep trên Windows
            current_app = self._get_adb_output('dumpsys window | findstr mCurrentFocus')
            if package_name not in current_app:
                self._print(f"Cảnh báo: Ứng dụng {package_name} có thể đã bị crash sau khi khởi động lại!")
                return False
            self._print(f"Đã khởi động lại ứng dụng: {package_name}")
            return True
        except Exception as e:
            self._print(f"Lỗi khi khởi động lại ứng dụng: {str(e)}")
            return False

    def close_app(self, package_name):
        """Thoát ứng dụng"""
        try:
            self._print(f"Đang thoát ứng dụng: {package_name}")
            self._run_adb_command(f"shell am force-stop {package_name}")
            time.sleep(1)
            self._print(f"Đã thoát ứng dụng: {package_name}")
            return True
        except Exception as e:
            self._print(f"Lỗi khi thoát ứng dụng: {str(e)}")
            return False

    def press_back(self):
        try:
            self._print("Nhấn nút quay lại...")
            self._run_adb_command("shell input keyevent 4")
            time.sleep(0.5)
        except Exception as e:
            self._print(f"Lỗi khi nhấn nút quay lại: {str(e)}")

    def press_home(self):
        try:
            self._print("Nhấn nút Home...")
            self._run_adb_command("shell input keyevent 3")
            time.sleep(0.5)
        except Exception as e:
            self._print(f"Lỗi khi nhấn nút Home: {str(e)}")

    def press_recent(self):
        try:
            self._print("Nhấn nút Recent Apps...")
            self._run_adb_command("shell input keyevent 187")
            time.sleep(0.5)
        except Exception as e:
            self._print(f"Lỗi khi nhấn nút Recent Apps: {str(e)}")

# Ví dụ sử dụng
if __name__ == "__main__":
    # try:
        adb = ADBController(None, debug=True)  # Chạy với debug để kiểm tra
        adb.get_device_info()
        adb.input_text("Hello World")
    #     # Cài đặt Facebook APK
    #     apk_path = "com.facebook.katana.apk"
    #     adb.install_apk(apk_path, override_existing=True)

    #     # Khởi động Facebook
    #     if adb.launch_app("com.facebook.katana"):
    #         time.sleep(3)
    #         adb.tap(500, 500)  # Giả lập click vào một tọa độ
    #         adb.input_text("Hello Facebook")  # Nhập mà không xóa
    #         time.sleep(2)
    #         adb.delete_left(5)  # Xóa 5 ký tự về phía trái
    #         time.sleep(1)
    #         adb.input_text("New Text", delete=True)  # Xóa toàn bộ trước khi nhập
    #         time.sleep(2)
    #     else:
    #         print("Không thể mở ứng dụng, thử khởi động lại...")
    #         adb.restart_app("com.facebook.katana")

    #     # Thoát ứng dụng
    #     adb.close_app("com.facebook.katana")
    #     time.sleep(2)

    #     # Khởi động lại ứng dụng
    #     adb.restart_app("com.facebook.katana")
    #     time.sleep(3)

    #     # Các thao tác khác
    #     adb.press_back()
    #     adb.press_home()
    #     adb.press_recent()
    # except Exception as e:
    #     print(f"Lỗi khởi tạo: {str(e)}")