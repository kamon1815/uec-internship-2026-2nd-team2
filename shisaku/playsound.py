import pygame.mixer as mix
import time
import os
from pathlib import Path
import cv2 # pip install opencv-python"
import pypuclib
from pypuclib import CameraFactory, Camera, XferData, Decoder
from pypuclib import Resolution, PUCException, GPUSetup

BASE_DIR = Path(__file__).resolve().parent
INPUT1 = BASE_DIR / "sound/ドラムロール.mp3"
INPUT2 = BASE_DIR / "sound/放送開始チャイム.mp3"

os.chdir(os.path.dirname(os.path.abspath(__file__)))

sounds = {"drum" : INPUT1, "chime" : INPUT2}
# Set filepath to save image
savePath = BASE_DIR / "hello_world.bmp"

def music():
    mix.init() #初期化

    mix.music.load(INPUT1) #読み込み

    mix.music.play(1) #再生

    time.sleep(3)

    mix.music.stop() #終了

def sound():
    mix.init()
    sound1 = mix.Sound(INPUT1)
    sound2 = mix.Sound(INPUT2)
    sound1.play()
    time.sleep(1)
    sound2.play()
    time.sleep(3)

def select_sound(select):
    ssound = mix.Sound(sounds[select])
    channel = ssound.play()
    #print(type(channel))
    return channel
    #time.sleep(3)

# Function : Save single image as BMP 
def saveBMP(img):
    cv2.imwrite(savePath, img)
    print("saved a BMP image")



#infinicam用
if __name__ == '__main__':
    mix.init()

    print(pypuclib.__doc__)
    # To connect the camera first detected
    cam = CameraFactory().create()
    '''
    print(cam.framerate())
    print(cam.shutter())
    print(cam.resolution())
    '''

    # To decode image, get decoder obj from camera
    decoder = cam.decoder()

    # GPUの接続有無をチェック？
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

    print("press Esc to quit this application ")
    print("press 's' to save a BMP image")

    channel = select_sound("chime")

    while True:
        # Grab the single image data
        xferData = cam.grab()

        # Decode the data can be used as image
        if GPUStatus == True:
            array = decoder.decodeGPU(xferData, True, reso.width)
        elif GPUStatus == False:
            array = decoder.decode(xferData)

        
        #画像サイズは(1008*1246)
        img_edge = cv2.Canny(array, 150.0, 190.0)

        # Show the image
        cv2.imshow("INFINICAM", array)

        key = cv2.waitKey(1)
        if key & 0xFF == ord('s'): # s : save image
            saveBMP(array)
        elif key & 0xFF == 27: # Esc : quit application
            break

        if channel.get_busy() != True:
            channel = select_sound("drum")
            
    # Close live image window
    cv2.destroyAllWindows()

    if GPUStatus == True:
        decoder.teardownGPUDecode()

    
    