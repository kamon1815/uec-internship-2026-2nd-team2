import time
import cv2
import numpy as np
import openvino as ov
import main
from pathlib import Path
from pypuclib import CameraFactory

# MODE = "npu_fp16"   

# DEVICE, PRECISION = {"cpu_fp32": ("CPU", "f32"),
#                      "gpu_fp16": ("GPU", "f16"),
#                      "npu_fp16": ("NPU", "f16")}[MODE]
# # 画像の読み込み
# # カメラ
# cap = cv2.VideoCapture(0) # webカメラ

# if not cap.isOpened():
#     print("エラー: Webカメラを開けませんでした。")
#     exit()

# # カメラの最大解像度を要求
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 10000)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 10000)

# # 解像度 W, H および FPS を取得
# W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# fps = cap.get(cv2.CAP_PROP_FPS)

# if fps == 0 or fps is None or fps > 120:
#     fps = 30.0

# print(f"適用されたWebカメラ解像度: {W}x{H}, FPS: {fps}")

# # モデル
# core = ov.Core()

# cam = CameraFactory().create() # INFINICAM
# cam.setFramerateShutter(30, 30)
# decoder = cam.decoder()
# W, H = cam.resolution().width, cam.resolution().height
# USE_GPU_DECODE = decoder.getAvailableGPUProcess()     # CUDA専用。無ければCPUデコード
# #ret, img = cap.read()
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



    # 描画する。
    dst = img.copy()
    for x, y in zip():
        cv2.rectangle(
            dst,
            (x, y),
            (x + code_A.shape[1], y + code_A.shape[0]),
            color=(0, 255, 0),
            thickness=2,
        )
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

# 座標からコード判定
def decide_code():
    # 座標取得
    finger = main.get_finger_position('Left', 1)
    global lx1, ly1, lx2, ly2, lx3, ly3
    lx1 = finger[3].x
    ly1 = finger[3].y

    finger = main.get_finger_position('Left', 2)
    
    lx2 = finger[3].x
    ly2 = finger[3].y

    finger = main.get_finger_position('Left', 3)
    
    lx3 = finger[3].x
    ly3 = finger[3].y
    print(lx1, ly1, lx2, ly2, lx3, ly3)
    return(lx1, ly1, lx2, ly2, lx3, ly3)


while True:
    lx1, ly1, lx2, ly2, lx3, ly3 = decide_code()
