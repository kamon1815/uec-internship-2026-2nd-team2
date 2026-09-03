import pygame.mixer as mx
import time
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT = BASE_DIR / "sound/ドラムロール.mp3"
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def sound():
    mx.init() #初期化

    mx.music.load(INPUT) #読み込み

    mx.music.play(1) #再生

    time.sleep(3)

    mx.music.stop() #終了

if __name__ == '__main__':

    sound()