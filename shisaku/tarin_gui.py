import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path
from PIL import Image, ImageTk # need to import extra module "pip install pillow"

import numpy as np
import os, csv, json, threading
from enum import IntEnum
import cv2
import pygame.mixer as mix
import time

BASE_DIR = Path(__file__).resolve().parent
INPUT1 = BASE_DIR / "sound/ドラムロール.mp3"
INPUT2 = BASE_DIR / "sound/放送開始チャイム.mp3"
G_INPUT_C = BASE_DIR / "sound/C.wav"
G_INPUT_D = BASE_DIR / "sound/D.wav"
G_INPUT_E = BASE_DIR / "sound/E.wav"
G_INPUT_F = BASE_DIR / "sound/F.wav"
G_INPUT_G = BASE_DIR / "sound/G.wav"
G_INPUT_A = BASE_DIR / "sound/A.wav"
G_INPUT_B = BASE_DIR / "sound/B.wav"

class sound_admin:
    def __init__(self, max = 6):
        mix.init()
        self.sounds = {"drum" : mix.Sound(INPUT1),
                       "chime" : mix.Sound(INPUT2),
                       "ド" : mix.Sound(G_INPUT_C),
                       "レ" : mix.Sound(G_INPUT_D),
                       "ミ" : mix.Sound(G_INPUT_E),
                       "ファ" : mix.Sound(G_INPUT_F),
                       "ソ" : mix.Sound(G_INPUT_G),
                       "ラ" : mix.Sound(G_INPUT_A),
                       "シ" : mix.Sound(G_INPUT_B)
                       }
        self.active_channel = []
        self.max_channel = max

    def update(self):
        if len(self.active_channel) >= self.max_channel:
            d_channel = self.active_channel.pop(0)
            d_channel.stop()
        
        
    def start_sound(self, select, volume = 1.0):
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

#音楽管理も含めたウィンドウ作成クラス
class Application(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master)
        master.title("gui_sample")
        master.geometry("800x600")
        #キーバインド
        master.bind("<KeyPress>", self.press_key)
        self.pack(expand=1, fill=tk.BOTH, anchor=tk.NW)

        #webcam
        self.cap = cv2.VideoCapture(0)

        #INFINICAM
        '''
        self.cam = CameraFactory().create()
        self.fcreator = None
        self.decoder = self.cam.decoder()
        '''
        #音管理
        self.s_admin = sound_admin()

        #変数管理
        self.instStr = tk.StringVar()
        self.volInt = tk.IntVar()
        self.font = tkfont.Font(self,family="Arial",size=10,weight="bold")
        self.recent_sound = ""
        self.s_volume = 1.0

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
        #self.framerateList.bind("<<ComboboxSelected>>", self.updateinstrumental)

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
        ret, data = self.cap.read()
        #INFINICAM
        #data = self.cam.grab()
        
        self.updatecanvas(data)
        self.updateID = self.after(self.delay, self.update)
        

    #映像の更新
    def updatecanvas(self, data):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        h, w, _ = data.shape
        '''
        w = data.resolution().width
        h = data.resolution().height
        '''
        scale = 1
        if cw > 1 and ch > 1:
            scale = cw/w if cw/w < ch/h else ch/h
        

        #webcam用
        array = cv2.cvtColor(data, cv2.COLOR_BGR2RGB)
        #INFINICAM用
        #array = self.decoder.decode(data)
        #arrya = cv2.cvtColor(array, cv2.COLOR_GRAY2RGB)

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

#実行部分
if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master = root)
    app.mainloop()
    #root.terminate()