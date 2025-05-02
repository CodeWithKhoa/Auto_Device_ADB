import cv2
import adb

adb = adb.ADBController(None,True)
# adb.uninstall_app("com.facebook.katana")
# adb.install_apk("com.facebook.katana.apk",True)
adb.get_device_info()
adb.capture_screenshot()
try:
    img   = cv2.imread("screenshot.png")
    img_2 = cv2.imread("img_test/img1.png")
except:
    exit("Không tìm thấy hình ảnh")

method = eval('cv2.TM_CCOEFF_NORMED')
mask = cv2.matchTemplate(img, img_2,method)
minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(mask)
if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
    topleft = minLoc
else:
    topleft = maxLoc
print(f"Độ chính xác: {(maxVal*100):.2f}%")
mid = (topleft[0]+img_2.shape[1]/2,topleft[1]+img_2.shape[0]/2)
# if maxVal >= 0.9:
#     adb.tap(mid[0],mid[1])
cv2.rectangle(img,topleft, (topleft[0]+img_2.shape[1],topleft[1]+img_2.shape[0]),(0,255,0),3)
cv2.imwrite("output.png",img)
# while True:
#     cv2.imshow("image", img)
#     if cv2.waitKey(1) == ord('q'):
#         break