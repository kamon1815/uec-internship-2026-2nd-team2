import time
import cv2 # need to import extra module "pip install opencv-python"
import pypuclib
from pypuclib import CameraFactory, Camera, XferData, Decoder
from pypuclib import Resolution, PUCException, GPUSetup
from pathlib import Path


# Function : Save single image as BMP 
def saveBMP(img):
    cv2.imwrite(savePath, img)
    print("saved a BMP image")

# Set filepath to save image
BASE_DIR = Path(__file__).resolve().parent
savePath = BASE_DIR / "hello_world.bmp"

if __name__ == '__main__':
    #---------------------------------
    #カメラの準備
    print(pypuclib.__doc__)

    # To connect the camera first detected
    cam = CameraFactory().create()

    # To decode image, get decoder obj from camera
    decoder = cam.decoder()

    # If a GPU device is available, decoding is done on the GPU.
    # To setup GPU device
    reso = cam.resolution()
    GPUStatus = decoder.getAvailableGPUProcess()

    if GPUStatus == True:
        param = GPUSetup(reso.width, reso.height)
        decoder.setupGPUDecode(param)
        print("Decode using a GPU device")
    elif GPUStatus == False:
        print("Since GPU is not available, decode using CPU")
    #------------------------------------

    print("演奏位置の設定を行います")
    print("準備ができたらEnterキーを押してください")
    print("押した3秒後の手の位置を基準の位置とします")
    input("Are you OK?>>")

    print("3")
    time.sleep(1)
    print('2')
    time.sleep(1)
    print('1')
    time.sleep(1)

    #初期位置取得用の画像の取得
    first_data = cam.grab()
    # Decode the data can be used as image
    if GPUStatus == True:
        array = decoder.decodeGPU(first_data, True, reso.width)
    elif GPUStatus == False:
        array = decoder.decode(first_data)

    #----------------
    #ここに処理が挟まる
    #----------------

    array = cv2.putText(array, "これが初期位置です。5秒後に遷移します。", (400, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255,255,255), 2, cv2.LINE_AA) # 案内文の追加
    cv2.imshow("Setup", array)
    cv2.waitKey(5000) # 5秒待機
    cv2.destroyAllWindows()

    #あとはいつもの映像表示
    # Explanation
    print("press Esc to quit this application ")
    print("press 's' to save a BMP image")

    while True:
        # Grab the single image data
        xferData = cam.grab()

        # Decode the data can be used as image
        if GPUStatus == True:
            array = decoder.decodeGPU(xferData, True, reso.width)
        elif GPUStatus == False:
            array = decoder.decode(xferData)

        # Show the image
        cv2.imshow("INFINICAM", array)

        key = cv2.waitKey(1)
        if key & 0xFF == ord('s'): # s : save image
            saveBMP(array)
        elif key & 0xFF == 27: # Esc : quit application
            break


    # Close live image window
    cv2.destroyAllWindows()

    if GPUStatus == True:
        decoder.teardownGPUDecode()
    
