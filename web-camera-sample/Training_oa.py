import cv2 # need to import extra module "pip install opencv-python"
import pypuclib
from pypuclib import CameraFactory, Camera, XferData, Decoder
from pypuclib import Resolution, PUCException, GPUSetup
from pathlib import Path

#print(Path(__file__))
#print(Path(__file__).resolve())
#print(Path(__file__).resolve().parent)

cap = cv2.VideoCapture(0)
while True:
    # ウェブカメラの画像取得
    ret, img = cap.read()

    #グレースケール化
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    #エッジ検出(Canny)
    img_edge = cv2.Canny(img_gray, 150.0, 190.0)

    # 画像表示
    cv2.imshow('test', img_edge)
    k = cv2.waitKey(1) #待機時間、ミリ秒指定、0の場合はボタンが押されるまで待機
    if k == ord('e'):
        break

cap.release()
cv2.destroyAllWindows()