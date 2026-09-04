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
INPUT_C = BASE_DIR / "sound/ピアノ_ド.mp3"
INPUT_D = BASE_DIR / "sound/ピアノ_レ.mp3"
INPUT_E = BASE_DIR / "sound/ピアノ_ミ.mp3"
INPUT_F = BASE_DIR / "sound/ピアノ_ファ.mp3"
INPUT_G = BASE_DIR / "sound/ピアノ_ソ.mp3"
INPUT_A = BASE_DIR / "sound/ピアノ_ラ.mp3"
INPUT_B = BASE_DIR / "sound/ピアノ_シ.mp3"

os.chdir(os.path.dirname(os.path.abspath(__file__)))

sounds = {"drum" : INPUT1, "chime" : INPUT2}
# Set filepath to save image
savePath = BASE_DIR / "hello_world.bmp"

class sound_admin:
    def __init__(self):
        mix.init()
        self.sounds = {"drum" : mix.Sound(INPUT1),
                       "chime" : mix.Sound(INPUT2),
                       "ド" : mix.Sound(INPUT_C),
                       "レ" : mix.Sound(INPUT_D),
                       "ミ" : mix.Sound(INPUT_E),
                       "ファ" : mix.Sound(INPUT_F),
                       "ソ" : mix.Sound(INPUT_G),
                       "ラ" : mix.Sound(INPUT_A),
                       "シ" : mix.Sound(INPUT_B)
                       }
        
    def start_sound(self, select, volume = 1):
        self.sounds[select].set_volume = volume
        self.channel = self.sounds[select].play()

    def stop_sound(self, select):
        self.sound = self.sounds[select].stop()


# Function : Save single image as BMP 
def saveBMP(img):
    cv2.imwrite(savePath, img)
    print("saved a BMP image")



#infinicam用
if __name__ == '__main__':
    sa = sound_admin()

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

    # GPUの接続有無をチェック
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

    #channel = select_sound("chime")

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
        elif key & 0xFF == ord('d'): # d : drum sound
            sa.start_sound("drum")
        elif key & 0xFF == ord('c'): # c : chime sound
            sa.start_sound("chime")
        elif key & 0xFF == ord('w'):
            sa.start_sound("ド")
        elif key & 0xFF == ord('e'):
            sa.start_sound("レ")
        elif key & 0xFF == ord('r'):
            sa.start_sound("ミ")
        elif key & 0xFF == ord('t'):
            sa.start_sound("ファ")
        elif key & 0xFF == ord('y'):
            sa.start_sound("ソ")
        elif key & 0xFF == ord('u'):
            sa.start_sound("ラ")
        elif key & 0xFF == ord('i'):
            sa.start_sound("シ")

            
    # Close live image window
    cv2.destroyAllWindows()

    if GPUStatus == True:
        decoder.teardownGPUDecode()

    
    