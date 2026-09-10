import cv2
import mediapipe as mp
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pypuclib
from pypuclib import CameraFactory, Camera, XferData, Decoder
from pypuclib import Resolution, PUCException, GPUSetup
from pathlib import Path
from collections import deque
import math
#import pygame.mixer as mix
from playsound import sound_admin


import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path
from PIL import Image, ImageTk # need to import extra module "pip install pillow"



#音楽管理も含めたウィンドウ作成クラス
class Application(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master)
        master.title("air guitar")
        master.geometry("1000x800")
        master.bind("<KeyPress>", self.press_key)
        self.pack(expand=1, fill=tk.BOTH, anchor=tk.NW)

        #webcam
        #self.cap = cv2.VideoCapture(0)

        #INFINICAM
        self.cam = CameraFactory().create()
        self.fcreator = None
        self.decoder = self.cam.decoder()
        
        #音管理
        self.s_admin = sound_admin()

        #変数管理
        self.instStr = tk.StringVar()
        self.volInt = tk.IntVar()
        self.font = tkfont.Font(self,family="Arial",size=10,weight="bold")
        self.recent_sound = ""
        self.s_volume = 1.0
        #self.t=0 #確認用

        self.createWidget()

        self.delay = 15
        self.updateID = 0
        self.update()

    def createWidget(self):
        #---------------------------------------------------
        # option Frame
        #---------------------------------------------------
        frameWidth=300
        self.optionFrame = ttk.LabelFrame(self, 
                                          text="options", 
                                          width=frameWidth,
                                          relief=tk.RAISED)
        self.optionFrame.propagate(False)
        self.optionFrame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        #---------------------------------------------------
        # instrument select
        #---------------------------------------------------
        #楽器選択フレームの作成
        self.instrumentPanel = ttk.Frame(self.optionFrame,
                                        width=frameWidth,
                                        height=30,
                                        relief=tk.FLAT)
        self.instrumentPanel.propagate(False)
        self.instrumentPanel.pack(side=tk.TOP, fill=tk.Y, padx=5, pady=5)
        #フレーム内に配置するラベルの作成、配置
        self.instrumentLabel = ttk.Label(self.instrumentPanel,text="Instrument", width=20)
        self.instrumentLabel.pack(side=tk.LEFT, padx=5)
        #選択ボックスの作成、配置
        self.instrumentList = ttk.Combobox(self.instrumentPanel, 
                                          values=["piano", "guitar"], 
                                          textvariable=self.instStr)
        self.instrumentList.pack(side=tk.LEFT, padx=5)
        #同期イベントの設定
        self.instrumentList.bind("<<ComboboxSelected>>", self.updateinstrument)

        #---------------------------------------------------
        # volume
        #---------------------------------------------------
        self.volumePanel = ttk.Frame(self.optionFrame,
                                        width=frameWidth,
                                        height=30,
                                        relief=tk.FLAT)
        self.volumePanel.pack(side=tk.TOP, fill=tk.Y, padx=5, pady=5)
        #フレーム内に配置するラベルの作成、配置
        self.volumeLabel = ttk.Label(self.volumePanel,text="volume", width=20)
        self.volumeLabel.pack(side=tk.LEFT, padx=5)
        #選択ボックスの作成、配置
        self.volumeList = ttk.Scale(self.volumePanel, 
                                          from_=0, 
                                          to=10,
                                          variable=self.volInt,
                                          command=self.updatevolume)
        self.volumeList.pack(side=tk.LEFT, padx=5)

        #---------------------------------------------------
        # recent sound
        #---------------------------------------------------
        #楽器選択フレームの作成
        self.soundPanel = ttk.Frame(self.optionFrame,
                                        width=frameWidth,
                                        height=30,
                                        relief=tk.FLAT)
        self.soundPanel.propagate(False)
        self.soundPanel.pack(side=tk.TOP, fill=tk.Y, padx=5, pady=5)
        #フレーム内に配置するラベルの作成、配置
        self.soundLabel = ttk.Label(self.soundPanel,text="Ringing Sound", width=20)
        self.soundLabel.pack(side=tk.LEFT, padx=5)
        #選択ボックスの作成、配置
        self.soundList = ttk.Label(self.soundPanel, 
                                          text="No Sound", 
                                          width=20)
        self.soundList.pack(side=tk.LEFT, padx=5)

        #---------------------------------------------------
        # canvas
        #---------------------------------------------------
        self.canvas = tk.Canvas(self, width=1296, height=1080)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        #---------------------------------------------------
        # initialize UI
        #---------------------------------------------------
        self.instrumentList.set("guitar")
        self.volumeList.set(10)

    #更新関数(定期的に呼び出し)
    def update(self):
        #webcam
        #ret, data = self.cap.read()
        
        #INFINICAM
        data = self.cam.grab()
        
        self.updatecanvas(data)
        self.updateID = self.after(self.delay, self.update)
        

    #映像の更新
    def updatecanvas(self, data):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        #h, w, _ = data.shape #webcam
        #INFINICAM
        w = data.resolution().width
        h = data.resolution().height

        scale = 1
        if cw > 1 and ch > 1:
            scale = cw/w if cw/w < ch/h else ch/h
        

        #webcam
        #array = cv2.cvtColor(data, cv2.COLOR_RGB2BGR)
        #INFINICAM
        array = self.decoder.decode(data)
        array = cv2.cvtColor(array, cv2.COLOR_GRAY2BGR)

        #骨格推定
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=array) #mediapipeの画像として使える塊にする。    
        frame_timestamp = int((time.time() - start_time) * 1000) #タイムスタンプ作成
        
        landmarker.detect_async(mp_image, frame_timestamp) #手を検出
        draw_landmarks(array, current_hands) #骨格に色付け
        
        # 検出結果を記録
        if current_hands is not None:
            hand_postion = get_hand_position('Right', current_hands)
            if hand_postion:
                hand_position_history.append([hand_postion.x, hand_postion.y])
            else:
                hand_position_history.append([])
        else:
               hand_position_history.append([])

        # 相対座標の取得
        global was_on_guitar
        relative_rx, relative_ry, is_on_guitar = get_hand_relative_position()
        if (was_on_guitar == 0) and (is_on_guitar == 1) and (get_hands_count(current_hands) == 2):
            lx1, ly1, lx2, ly2, lx3, ly3 = get_lefthand_potions()
            chord = decide_code(lx1, ly1, lx2, ly2, lx3, ly3)
            self.start_sound(chord)
        #else:
            #print("再生条件を満たしていません")
        was_on_guitar = is_on_guitar 
        #初期位置の描画
        array = draw_start_position(array)
        array = cv2.flip(array, 1)

        #PILオブジェクトに変換してサイズを調整
        i = Image.fromarray(array).resize((int(w*scale), int(h*scale)))
        self.img = ImageTk.PhotoImage(image=i)#PILオブジェクトをtkinterで表示できる形に変換
        self.canvas.delete("all")#前の画像を削除
        pos = [(cw-i.width)/2,(ch-i.height)/2]#位置の設定
        self.canvas.create_image(pos[0], pos[1], anchor="nw", image=self.img)
        self.canvas.create_text(pos[0]+5, pos[1]+5, anchor="nw", 
                                text="test",
                                font=self.font, fill="limeGreen")

    #音量調整
    def updatevolume(self,e):
        volume = self.volInt.get()
        self.s_volume = round(volume / 10.0, 1)
        #print(self.s_volume)

    #最新の音の表示更新
    def updatesound(self):
        self.soundList["text"] = self.recent_sound

    def updateinstrument(self,e):
        inst = self.instStr.get()
        self.s_admin.changesound(inst)

    #キー入力に反応
    def press_key(self, e):
        key = ord(e.keysym)
        
        if key & 0xFF == ord('w'):
            self.start_sound("ド")
        elif key & 0xFF == ord('e'):
            self.start_sound("レ")
        elif key & 0xFF == ord('r'):
            self.start_sound("ミ")
        elif key & 0xFF == ord('t'):
            self.start_sound("ファ")
        elif key & 0xFF == ord('y'):
            self.start_sound("ソ")
        elif key & 0xFF == ord('u'):
            self.start_sound("ラ")
        elif key & 0xFF == ord('i'):
            self.start_sound("シ")

    #演奏用
    #------------------------------------------------------
    def start_sound(self, select, volume=1.0):
        svolume = volume * self.s_volume
        self.s_admin.start_sound(select, svolume)
        self.recent_sound = select
        self.updatesound()

    def stop_sound(self, select):
        self.s_admin.stop_sound(select)
    #------------------------------------------------------

class SetApplication(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master)
        master.title("Setup")
        master.geometry("1000x800")
        #master.bind("<KeyPress>", self.press_key)
        self.pack(expand=1, fill=tk.BOTH, anchor=tk.NW)

        #webcam
        #self.cap = cv2.VideoCapture(0)

        #INFINICAM
        self.cam = CameraFactory().create()
        self.fcreator = None
        self.decoder = self.cam.decoder()
        

        self.font = tkfont.Font(self,family="Arial",size=10,weight="bold")
        self.message = tk.StringVar()
        self.message.set("初期位置の設定をします。両手でギターを持つように構えてください。")
        self.starttime = 0
        self.endflag = False
        self.handflag = False

        #self.t=0動作確認

        self.createWidget()
        
        self.delay = 15
        self.updateID = 0
        self.update()

    def createWidget(self):
        #---------------------------------------------------
        # option Frame
        #---------------------------------------------------
        frameWidth=300
        frameHeight=100
        self.optionFrame = ttk.LabelFrame(self, 
                                          text="explanation", 
                                          width=frameWidth,
                                          height=frameHeight,
                                          relief=tk.RAISED)
        self.optionFrame.propagate(False)
        self.optionFrame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        #---------------------------------------------------
        # explain text
        #---------------------------------------------------
        #説明文の作成
        self.explainPanel = ttk.Frame(self.optionFrame,
                                        width=frameWidth,
                                        height=frameHeight,
                                        relief=tk.FLAT)
        self.explainPanel.propagate(False)
        self.explainPanel.pack(anchor=tk.S, fill=tk.BOTH, padx=5, pady=5)
        #フレーム内に配置するラベルの作成、配置
        self.explainLabel = ttk.Label(self.explainPanel,textvariable=self.message, width=60, anchor=tk.CENTER,font=("Arial", 20))
        self.explainLabel.pack(side=tk.TOP,expand=True, fill=tk.BOTH, padx=20)

        #---------------------------------------------------
        # canvas
        #---------------------------------------------------
        self.canvas = tk.Canvas(self, width=1296, height=1080)
        self.canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=5, pady=5)

    def update(self):
        #webcam
        #ret, data = self.cap.read()
        
        #INFINICAM
        data = self.cam.grab()
        
        self.updatecanvas(data)
        if self.endflag == False:
            self.updateID = self.after(self.delay, self.update)
        else:
            self.master.destroy()
            #self.quit()

    def updatecanvas(self, data):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        #h, w, _ = data.shape # webcam
        #INFINICAM
        w = data.resolution().width
        h = data.resolution().height

        scale = 1
        if cw > 1 and ch > 1:
            scale = cw/w if cw/w < ch/h else ch/h   

        #webcam
        #data = cv2.cvtColor(data, cv2.COLOR_RGB2BGR)

        #INFINICAM
        array = self.decoder.decode(data)
        array = cv2.cvtColor(array, cv2.COLOR_GRAY2BGR)

        #骨格推定
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=array) #mediapipeの画像として使える塊にする。    
        frame_timestamp = int((time.time() - start_time) * 1000) #タイムスタンプ作成
                
        landmarker.detect_async(mp_image, frame_timestamp) #手を検出
        draw_landmarks(array, current_hands) #骨格に色付け
        array = cv2.flip(array, 1)

        if get_hands_count(current_hands) == 2:
            if self.handflag == False:
                self.starttime = time.time()
                self.updatetext("そのまま維持してください。3秒後に初期位置が決まります。")
                self.handflag = True
            elif (time.time() - self.starttime) >= 3:
                global height, width
                height, width, _ = array.shape
                get_hand_relative_position()
                self.endflag = True
                self.terminate()
            else:
                t = int(time.time() - self.starttime)
                self.updatetext(f"そのまま維持してください。{3-t}秒後に初期位置が決まります。")
        else:
            if self.handflag == True:
                self.updatetext("読み取りに失敗しました。もう一度お願いします。")
                self.handflag = False
        
        #PILオブジェクトに変換してサイズを調整
        i = Image.fromarray(array).resize((int(w*scale), int(h*scale)))
        self.img = ImageTk.PhotoImage(image=i)#PILオブジェクトをtkinterで表示できる形に変換
        self.canvas.delete("all")#前の画像を削除
        pos = [(cw-i.width)/2,(ch-i.height)/2]#位置の設定
        self.canvas.create_image(pos[0], pos[1], anchor="nw", image=self.img)
        self.canvas.create_text(pos[0]+5, pos[1]+5, anchor="nw", 
                                text="test",
                                font=self.font, fill="limeGreen")

    def updatetext(self, text):
        self.message.set(text)

    def resettext(self):
        self.message.set("初期位置の設定をします。両手でギターを持つように構えてください")

    def terminate(self):
        self.after_cancel(self.updateID)
        #self.cap.release() # webcam
        self.cam.close() # INFINICAM

model_path = 'hand_landmarker.task'

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

'''
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
'''


# グローバル変数
current_hands = None
hand_position_history = deque(maxlen=20)
base_rx = None
base_ry = None
was_on_guitar = 0
RANGE_X = 0.1
RANGE_Y = 0.1
height = 0
width = 0


def print_result(result, output_image: mp.Image, timestamp_ms: int):
    global current_hands
    current_hands = result
    # print('hand landmarker result: {}'.format(result))

base_options = python.BaseOptions(model_asset_path=str(model_path))

options = HandLandmarkerOptions(
    base_options=base_options,
    running_mode=VisionRunningMode.LIVE_STREAM,
    num_hands=2,
    min_hand_detection_confidence=0.2,
    min_hand_presence_confidence=0.2,
    result_callback=print_result)

landmarker = vision.HandLandmarker.create_from_options(options)
start_time = time.time()

# 検出された手の数を取得
def get_hands_count(result = current_hands): 
    if result and result.hand_landmarks:
        return len(result.hand_landmarks)
    return 0


# 指定した指の位置を取得
def get_finger_position(
    handedness, finger_num, result=current_hands
):  # handednessには文字列（"Right" or "Left"） finger_numにはほしい指の番号(親指が0、小指が4)
  if result and result.handedness and result.hand_landmarks:
    landmarks = []
    finger_positions = []
    for i, handedness_list in enumerate(result.handedness):
      category = handedness_list[0]
      hand_label = category.category_name  # 'Left' または 'Right'
      if hand_label == handedness:
        landmarks = result.hand_landmarks[i]
        break
    if not landmarks:
      return []

    first_position = finger_num * 4 + 1

    for i in range(first_position, first_position + 4):
      finger_positions.append(landmarks[i])

    return finger_positions

  return []


# 手の位置を取得（人差し指先端）
def get_hand_position(
    handedness, result=current_hands
):  # handednessには文字列（"Right" or "Left"）
  if result and result.handedness and result.hand_landmarks:
    for i, handedness_list in enumerate(result.handedness):
      category = handedness_list[0]
      hand_label = category.category_name  # 'Left' または 'Right'
      if hand_label == handedness:
        return result.hand_landmarks[i][8]
  return []

# 手（人差指先端の移動量を計算）
def get_moved_distance():
    hand_position_history_list = list(hand_position_history)
    first = hand_position_history_list[:3]
    last = hand_position_history_list[-3:]

    if first and last:
        first_x = []
        for c in first:
            if c:
                first_x.append(c[0])
        first_y = []
        for c in first:
            if c:
                first_y.append(c[1])
        len_first = len(first_x)

        last_x = []
        for c in last:
            if c:
                last_x.append(c[0])
        last_y = []
        for c in last:
            if c:
                last_y.append(c[1])
        len_last = len(last_x)
        if first_x and last_x:
            first_avg_x = sum(first_x)/len_first
            first_avg_y = sum(first_y)/len_first
            last_avg_x = sum(last_x)/len_last
            last_avg_y = sum(last_y)/len_last
            diff_x = last_avg_x - first_avg_x
            diff_y = last_avg_y - first_avg_y
            distance = math.sqrt(diff_x**2 + diff_y**2)
            return [diff_x, diff_y, distance]

    return [0,0,0]

                

# 骨格の描画
def draw_landmarks(image, result = current_hands):
    if result and result.hand_landmarks:
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        image_height, image_width, _ = image.shape
        

        # current_hands.hand_landmarks[どの手？][どの点？].度の座標系？

        # 検出された各手に対して処理
        for hand_landmarks in result.hand_landmarks:
            # 各ランドマーク（関節）を円で描画
            for landmark in hand_landmarks:
                # 正規化座標（0.0〜1.0）をピクセル座標に変換
                px = int(landmark.x * image_width)
                py = int(landmark.y * image_height)
                # 円で描画（半径5ピクセル）
                cv2.circle(image, (px, py), 5, (255, 255, 255), -1)
            # ランドマーク間の接続関係を定義
            connections = [
                # 親指
                (0, 1), (1, 2), (2, 3), (3, 4),
                # 人差し指
                (0, 5), (5, 6), (6, 7), (7, 8),
                # 中指
                (9, 10), (10, 11), (11, 12),
                # 薬指
                (13, 14), (14, 15), (15, 16),
                # 小指
                (0, 17), (17, 18), (18, 19), (19, 20),
                # 手のひら
                (5, 9), (9, 13), (13, 17)
            ]
            
            # 各接続線を描画
            for start_idx, end_idx in connections:
                # 始点の座標
                pt1 = (
                    int(hand_landmarks[start_idx].x * image_width),
                    int(hand_landmarks[start_idx].y * image_height)
                )
                # 終点の座標
                pt2 = (
                    int(hand_landmarks[end_idx].x * image_width),
                    int(hand_landmarks[end_idx].y * image_height)
                )
                cv2.line(image, pt1, pt2, (255, 255, 0), 2)
        
        return image
    return image

def draw_start_position(img):
    global width, height
    if base_rx is not None:
        return cv2.rectangle(img, (int((base_rx-RANGE_X)*width), int((base_ry-RANGE_Y)*height)), (int((base_rx+RANGE_X)*width), int((base_ry+RANGE_Y)*height)), (255, 0, 0), 2)
    else:
        return img


def get_hand_relative_position(): #基準点(base_rx,base_ry)に対する現在の指の相対位置を取得
    hand_position = get_hand_position('Right', current_hands)
    if hand_position == []:
        # print("読み取れませんでした")
        return -2, -2, 0
    global base_rx, base_ry
    if base_rx is None:
        base_rx = hand_position.x
        base_ry = hand_position.y

    current_rx = hand_position.x
    current_ry = hand_position.y

    relative_rx = current_rx - base_rx
    relative_ry = current_ry - base_ry

    is_on_guitar = (-RANGE_X <= relative_rx <= RANGE_X) & (-RANGE_Y <= relative_ry <= RANGE_Y)
    return relative_rx, relative_ry, is_on_guitar

# 座標取得
def get_lefthand_potions():
    finger1 = get_finger_position('Left', 1, current_hands)
    finger2 = get_finger_position('Left', 2, current_hands)
    finger3 = get_finger_position('Left', 3, current_hands)
    if (finger1 != []) & (finger2 != []) & (finger3 != []):
        global lx1, ly1, lx2, ly2, lx3, ly3
        lx1 = finger1[3].x
        ly1 = finger1[3].y
        lx2 = finger2[3].x
        ly2 = finger2[3].y
        lx3 = finger3[3].x
        ly3 = finger3[3].y
        return(lx1, ly1, lx2, ly2, lx3, ly3)
    else :
        return(0, 0, 0, 0, 0, 0)
    

# コード判定
def decide_code(lx1, ly1, lx2, ly2, lx3, ly3):
    # print(lx1, ly1, lx2, ly2, lx3, ly3)
    # 指間の距離
    dist_12 = math.hypot(lx2 - lx1, ly2 - ly1)
    dist_23 = math.hypot(lx3 - lx2, ly3 - ly2)
    dist_31 = math.hypot(lx1 - lx3, ly1 - ly3)
    # print(dist_12, dist_23, dist_31)

    # 外積
    cross_product = (lx2 - lx1) * (ly3 - ly1) - (ly2 - ly1) * (lx3 - lx1)

    # 三角形の面積
    area = abs(cross_product) / 2
    print(area)
    judge = 0.0004
    # if 0.15 < dist_31:
    #     print("コードA")
    #     return("ラ")
    # elif 0.05 > dist_23:
    #     print("コードD")
    #     return("ミ")
    # elif 0.05 > dist_12:
    #     print("コードE")
    #     return("ファ")
    # else:
    #     return("ド")
    if area < judge:
        print("コードA")
        return ("A")
    elif (ly2 > ly1) & (ly2 > ly3):
        print("コードD")
        return("D")
    elif (ly2 < ly1) & (ly2 < ly3):
        print("コードE")
        return("E")
    else:
        print("コードG")
        return("G")

if __name__ == '__main__':
    #sa = sound_admin()
    '''
    print("演奏位置の設定を行います")
    while True:
        print("準備ができたらEnterキーを押してください")
        print("押した3秒後の手の位置を基準の位置とします")
        input("Are you OK?>>")

        print("3")
        time.sleep(1)
        print('2')
        time.sleep(1)
        print('1')
        time.sleep(1)

        #webcam用
        cap = cv2.VideoCapture(0)
        ret, array = cap.read()
        height, width, _ = array.shape

        #INFINICAM用
        
        #初期位置取得用の画像の取得
        first_data = cam.grab()
        
        # Decode the data can be used as image
        #if GPUStatus == True:
        #    array = decoder.decodeGPU(first_data, True, reso.width)
        #elif GPUStatus == False:
        #    array = decoder.decode(first_data)
        
        #array = cv2.cvtColor(array, cv2.COLOR_GRAY2BGR)
        
        


        # 骨格推定
        rgb_frame = cv2.cvtColor(array, cv2.COLOR_BGR2RGB) #OpenCVの形式(GBR)からMediaPipeの形式(RGB)に変換 

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame) #mediapipeの画像として使える塊にする。    
        frame_timestamp = int((time.time() - start_time) * 1000) #タイムスタンプ作成
        landmarker.detect_async(mp_image, frame_timestamp) #手を検出
        time.sleep(0.2)
        # 右手の相対位置を保存
        get_hand_relative_position()

        # # もし手が２本なかったらやり直し
        # if get_hands_count(current_hands) != 2:
        #     print("手の読み取りに失敗しました")
        #     print("もう一度演奏位置の設定を行います")
        #     continue    
        break

    draw_start_position(array)
    draw_landmarks(array, current_hands) #骨格の描画
    array = cv2.flip(array,1)
    array = cv2.putText(array, "これが初期位置です。5秒後に遷移します。", (400, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255,255,255), 2, cv2.LINE_AA) # 案内文の追加
    cv2.imshow("Setup", array)
    cv2.waitKey(5000) # 5秒待機
    cv2.destroyAllWindows()
    cap.release()
    '''
    setroot = tk.Tk()
    setapp = SetApplication(master=setroot)
    setapp.mainloop()

    time.sleep(0.5)

    root = tk.Tk()
    app = Application(master = root)
    app.mainloop()
'''
    while True:
        xferData = cam.grab()

        # Decode the data can be used as image
        if GPUStatus == True:
            frame = decoder.decodeGPU(xferData, True, reso.width)
        elif GPUStatus == False:
            frame = decoder.decode(xferData)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #OpenCVの形式(GBR)からMediaPipeの形式(RGB)に変換

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame) #mediapipeの画像として使える塊にする。    
        frame_timestamp = int((time.time() - start_time) * 1000) #タイムスタンプ作成

        landmarker.detect_async(mp_image, frame_timestamp) #手を検出
        draw_landmarks(frame, current_hands) #骨格に色付け

        # 検出結果を記録
        if current_hands is not None:
            hand_postion = get_hand_position('Right', current_hands)
            if hand_postion:
                hand_position_history.append([hand_postion.x, hand_postion.y])
            else:
                hand_position_history.append([])
        else:
            hand_position_history.append([])

        
        # 相対座標の取得
        relative_rx, relative_ry, is_on_guitar = get_hand_relative_position()
        if (was_on_guitar == 0) and (is_on_guitar == 1):
            print("再生中")
            chord = get_chord_by_position_l(100, 150) # 変数化
            sa.start_sound(chord)
        else:
            print("再生条件を満たしていません")
        was_on_guitar = is_on_guitar 
            

        # Show the image
        frame = cv2.flip(frame, 1)
        cv2.imshow("INFINICAM", frame)

        key = cv2.waitKey(1)
        if key & 0xFF == 27: # Esc : quit application
            break
    cv2.destroyAllWindows()
    '''
