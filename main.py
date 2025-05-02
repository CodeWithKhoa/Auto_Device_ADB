import cv2
import adb
import time

import cv2

def find(adb, button, press=False, rate=False, leftright=False, topbottom=False):
    dem = 0
    while True:
        dem += 1
        path = "imgkiemtra.png"
        path_button = f"img_dark/{button}.png"
        adb.capture_screenshot(path)
        img = cv2.imread(path)
        img_2 = cv2.imread(path_button)
        method = cv2.TM_CCOEFF_NORMED
        mask = cv2.matchTemplate(img, img_2, method)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(mask)
        
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            topleft = minLoc
        else:
            topleft = maxLoc
        
        print(f"Độ chính xác: {(maxVal*100):.2f}%")
        if rate:
            return maxVal
        
        mid = (int(topleft[0] + img_2.shape[1]/2), int(topleft[1] + img_2.shape[0]/2))
        if topbottom < 0:
            mid = (mid[0], 0)
        elif topbottom > 0:
            mid = (mid[0], ((img.shape[0])))
        if leftright < 0:
            mid = (0, mid[1])
        elif leftright > 0:
            mid = (img.shape[1]-10, mid[1])
        
        print(mid)
        
        # Vẽ chấm đỏ tại vị trí mid
        if maxVal >= 0.8:
            cv2.circle(img, mid, 10, (0, 255, 0), -1)  # Vẽ vòng tròn đỏ (bán kính 10)
            cv2.imwrite("imgkiemtra_with_dot.png", img)  # Lưu ảnh với chấm đỏ
            
            if press == False:
                adb.tap(mid[0], mid[1])
            else:
                adb.long_press(mid[0], mid[1], press)
            return True
        
        if dem > 2:
            return False

# adb = adb.ADBController("emulator-5554",True)
# adb.capture_screenshot()
# print(find(adb,"register1"))
# if maxVal >= 0.9:
#     adb.tap(mid[0],mid[1])
# while True:
#     cv2.imshow("image", img)
#     if cv2.waitKey(1) == ord('q'):
#         break
if __name__ == "__main__":
    gtinh = "male"
    adb = adb.ADBController(debug=False)
    width_heght = adb.get_device_info()["resolution"]
    if "x" in width_heght: 
        width = int(width_heght.split("x")[0])
        heght = int(width_heght.split("x")[1])
    else:
        width = 0
        heght = 0
    adb.capture_screenshot("imgkiemtra.png")
    adb.restart_app("com.facebook.katana")
    time.sleep(5)
    if find(adb, "register1",rate=True) > find(adb, "home",rate=True):
        print("Đang vào trang đăng kí")
        while(find(adb, "register1")==False):
            dem = 0
            adb.restart_app("com.facebook.katana")
            time.sleep(2)
            if dem > 3:
                exit("Lỗi trang đăng nhập!!")
    else: 
        print("Đang vào trang đăng nhập")
        while(find(adb, "home", leftright=1)==False):
            dem = 0
            adb.restart_app("com.facebook.katana")
            time.sleep(2)
            if dem > 3:
                exit("Lỗi trang home!!")
        time.sleep(1)
        adb.swipe(width/2,heght-30,width/2,60,600)
        print("Đang vào trang logout")
        find(adb, "logout1")
        find(adb, "logout2")
        find(adb, "register1")
    find(adb, "register2.1")
    if find(adb, "register_lastname") == False:
        exit("Lỗi phần Lastname")
    else:
        adb.input_text("Tran")
    if find(adb, "register_firstname") == False:
        exit("Lỗi phần Firstname")
    else:
        adb.input_text("Khoa")
    if find(adb, "next") == False:
        exit("Lỗi phần Next")
    if find(adb, "birthday_year", 2000) == False:
        exit("Lỗi phần birthday_year")
    else:
        adb.input_text("2005")
    if find(adb, "birthday_month") == False:
        exit("Lỗi phần birthday_month")
    else:
        adb.delete_left(2)
        adb.input_text("thg 12")
    if find(adb, "birthday_day") == False:
        exit("Lỗi phần birthday_day")
    else:
        adb.input_text("31",True)
    if find(adb, "birthday_set") == False:
        exit("Lỗi phần birthday_set")
    if find(adb, "next") == False:
        exit("Lỗi phần Next")
    if find(adb, gtinh) == False:
        exit("Lỗi phần Giới tính")
    if find(adb, "next") == False:
        exit("Lỗi phần Next")
    if find(adb, "convert_email") == False:
        exit("Lỗi phần Convert Email")
    if find(adb, "email") == False:
        exit("Lỗi phần Email")
    else:
        adb.input_text("TranDangKhoa@gmail.com",True)
    if find(adb, "next") == False:
        exit("Lỗi phần Next")
    time.sleep(3)
    if find(adb, "password") == False:
        exit("Lỗi phần Password")
    else:
        adb.input_text("TranDangKhoa",True)
    if find(adb, "next") == False:
        exit("Lỗi phần Next")
    if find(adb, "save") == False:
        exit("Lỗi phần Next")
    
    
