import pygame.mixer as mix
import time
import os
from pathlib import Path
import cv2 # pip install opencv-python"
import pypuclib
from pypuclib import CameraFactory, Camera, XferData, Decoder
from pypuclib import Resolution, PUCException, GPUSetup

#統合に必要な部分
#-------------------------------------
BASE_DIR = Path(__file__).resolve().parent
INPUT1 = BASE_DIR / "sound/ドラムロール.mp3"
INPUT2 = BASE_DIR / "sound/放送開始チャイム.mp3"
INPUT_C = BASE_DIR / "sound/C.wav"
INPUT_D = BASE_DIR / "sound/D.wav"
INPUT_E = BASE_DIR / "sound/E.wav"
INPUT_F = BASE_DIR / "sound/F.wav"
INPUT_G = BASE_DIR / "sound/G.wav"
INPUT_A = BASE_DIR / "sound/A.wav"
INPUT_B = BASE_DIR / "sound/B.wav"
INPUT_C_P = BASE_DIR / "sound/ピアノ_ド.mp3"
INPUT_D_P = BASE_DIR / "sound/ピアノ_レ.mp3"
INPUT_E_P = BASE_DIR / "sound/ピアノ_ミ.mp3"
INPUT_F_P = BASE_DIR / "sound/ピアノ_ファ.mp3"
INPUT_G_P = BASE_DIR / "sound/ピアノ_ソ.mp3"
INPUT_A_P = BASE_DIR / "sound/ピアノ_ラ.mp3"
INPUT_B_P = BASE_DIR / "sound/ピアノ_シ.mp3"


os.chdir(os.path.dirname(os.path.abspath(__file__)))

sounds = {"drum" : INPUT1, "chime" : INPUT2}
# Set filepath to save image
savePath = BASE_DIR / "hello_world.bmp"

#音声管理用クラス
class sound_admin:
    def __init__(self, max = 6):
        mix.init()
        self.sounds = {"drum" : mix.Sound(INPUT1),
                       "chime" : mix.Sound(INPUT2),
                       "C" : mix.Sound(INPUT_C),
                       "D" : mix.Sound(INPUT_D),
                       "E" : mix.Sound(INPUT_E),
                       "F" : mix.Sound(INPUT_F),
                       "G" : mix.Sound(INPUT_G),
                       "A" : mix.Sound(INPUT_A),
                       "B" : mix.Sound(INPUT_B)
                       }
        self.active_channel = []
        self.max_channel = max

    def update(self):
        if len(self.active_channel) >= self.max_channel:
            d_channel = self.active_channel.pop(0)
            d_channel.stop()
        
    def start_sound(self, select, volume = 1):
        #多重再生の管理
        self.update()
        
        self.sounds[select].set_volume(volume)
        channel = self.sounds[select].play()
        self.active_channel.append(channel)

    def stop_sound(self, select):
        self.sound = self.sounds[select].stop()

    def stop_allsound(self):
        for value in self.sounds.values():
            value.stop()

    def changesound(self, inst="guitar"):
        self.stop_allsound()
        if inst == "piano":
            self.sounds = {
                       "C" : mix.Sound(INPUT_C_P),
                       "D" : mix.Sound(INPUT_D_P),
                       "E" : mix.Sound(INPUT_E_P),
                       "F" : mix.Sound(INPUT_F_P),
                       "G" : mix.Sound(INPUT_G_P),
                       "A" : mix.Sound(INPUT_A_P),
                       "B" : mix.Sound(INPUT_B_P)
                       }
        elif inst == "guitar":
            self.sounds = {
                            "C" : mix.Sound(INPUT_C),
                            "D" : mix.Sound(INPUT_D),
                            "E" : mix.Sound(INPUT_E),
                            "F" : mix.Sound(INPUT_F),
                            "G" : mix.Sound(INPUT_G),
                            "A" : mix.Sound(INPUT_A),
                            "B" : mix.Sound(INPUT_B)
                            }
        else:
            print("input error")
#-------------------------------------


# Function : Save single image as BMP 
def saveBMP(img):
    cv2.imwrite(savePath, img)
    print("saved a BMP image")



#infinicam用
if __name__ == '__main__':
    sa = sound_admin()
    sound_volume = 1.0

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
            sa.start_sound("ド", sound_volume)
        elif key & 0xFF == ord('e'):
            sa.start_sound("レ", sound_volume)
        elif key & 0xFF == ord('r'):
            sa.start_sound("ミ", sound_volume)
        elif key & 0xFF == ord('t'):
            sa.start_sound("ファ", sound_volume)
        elif key & 0xFF == ord('y'):
            sa.start_sound("ソ", sound_volume)
        elif key & 0xFF == ord('u'):
            sa.start_sound("ラ", sound_volume)
        elif key & 0xFF == ord('i'):
            sa.start_sound("シ", sound_volume)
        elif key & 0xFF == ord('p'):
            sa.changesound("piano")
        elif key & 0xFF == ord('v'):
            if sound_volume >= 0.1:
                sound_volume -= 0.1
                print(f"volume: {sound_volume:.1f}")
            else:
                print("これ以上小さくできません")
        elif key & 0xFF == ord('b'):
            if sound_volume <=0.9:
                sound_volume += 0.1
                print(f"volume: {sound_volume:.1f}")
            else:
                print("これ以上大きくできません")
        elif key & 0xFF == ord('k'):
            sa.stop_allsound()
            
    # Close live image window
    cv2.destroyAllWindows()

    if GPUStatus == True:
        decoder.teardownGPUDecode()

    
    