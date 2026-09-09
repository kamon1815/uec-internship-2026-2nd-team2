import time
import cv2
import numpy as np
import openvino as ov
import pose_estimation
import math
from pathlib import Path
from pypuclib import CameraFactory

BASE_DIR = Path(__file__).resolve().parent
# コードファイルの読み取り
def get_codetype(img):
    globals
    code_A = BASE_DIR / "codetype/1.png"
    code_D = BASE_DIR / "codetype/2.jpg"
    code_E = BASE_DIR / "codetype/3.jpg"

    code_A_1 = cv2.imread(code_A)
    code_D_1 = cv2.imread(code_D)
    code_E_1 = cv2.imread(code_E)
    if code_A_1 is None:
        print("エラー: 画像ファイルが見つからないか、読み込めませんでした。")
    
    # グレースケール
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    code_A_gray = cv2.cvtColor(code_A_1, cv2.COLOR_BGR2GRAY)
    code_D_gray = cv2.cvtColor(code_D_1, cv2.COLOR_BGR2GRAY)
    code_E_gray = cv2.cvtColor(code_E_1, cv2.COLOR_BGR2GRAY)

    # テンプレートマッチングの実行
    result_A = cv2.matchTemplate(img_gray, code_A_gray, cv2.TM_CCOEFF_NORMED)
    result_D = cv2.matchTemplate(img_gray, code_D_gray, cv2.TM_CCOEFF_NORMED)
    result_E = cv2.matchTemplate(img_gray, code_E_gray, cv2.TM_CCOEFF_NORMED)

    # テンプレートの最大類似度と位置
    # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    _, max_val_A, _, max_loc_A = cv2.minMaxLoc(result_A)
    _, max_val_D, _, max_loc_D = cv2.minMaxLoc(result_D)
    _, max_val_E, _, max_loc_E = cv2.minMaxLoc(result_E)

    # 一番スコアが高いものを表示
    results = {
        'コードA': (max_val_A, max_loc_A, code_A_gray.shape),
        'コードD': (max_val_D, max_loc_D, code_D_gray.shape),
        'コードE': (max_val_E, max_loc_E, code_E_gray.shape)
        }

    if max_val_A > 0.7:
        print('コードA')
    elif max_val_D > 0.7:
        print('コードD')
    elif max_val_E > 0.7:
        print('コードE')
    return code_A_1, code_D_1, code_E_1


lx1 = None
ly1 = None
lx2 = None
ly2 = None
lx3 = None
ly3 = None

# 座標取得
def decide_potion():
    finger = pose_estimation.get_finger_position('Left', 1)
    global lx1, ly1, lx2, ly2, lx3, ly3
    list_rength = len(finger)
    print(list_rength)
    lx1 = finger[3].x
    ly1 = finger[3].y

    finger = pose_estimation.get_finger_position('Left', 2)
    
    lx2 = finger[3].x
    ly2 = finger[3].y

    finger = pose_estimation.get_finger_position('Left', 3)
    
    lx3 = finger[3].x
    ly3 = finger[3].y
    print(lx1, ly1, lx2, ly2, lx3, ly3)
    return(lx1, ly1, lx2, ly2, lx3, ly3)
    

# コード判定
def get_lefthand_potions(lx1, ly1, lx2, ly2, lx3, ly3):
    # 指間の距離
    dist_12 = math.hypot(lx2 - lx1, ly2 - ly1)
    dist_23 = math.hypot(lx3 - lx2, ly3 - ly2)
    dist_31 = math.hypot(lx1 - lx3, ly1 - ly3)

    # 外積
    cross_product = (lx2 - lx1) * (ly3 - ly1) - (ly2 - ly1) * (lx3 - lx1)

    # 三角形の面積
    area = abs(cross_product) / 2

    if -1 < area < 1:
        print("コードA")
    else:
        print("コードD")
        print("コードE")
  


while True:
    # code_A_1, code_D_1, code_E_1 = get_codetype(img)
    lx1, ly1, lx2, ly2, lx3, ly3 = decide_potion()
    get_lefthand_potions(lx1, ly1, lx2, ly2, lx3, ly3)
