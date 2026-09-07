import time
import cv2
import numpy as np
import openvino as ov
from pathlib import Path
from pypuclib import CameraFactory


MODE = "npu_fp16"   
# 画像の読み込み
# カメラ
cap = cv2.VideoCapture(0) # webカメラ

if not cap.isOpened():
    print("エラー: Webカメラを開けませんでした。")
    exit()

# カメラの最大解像度を要求
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 10000)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 10000)

# 解像度 W, H および FPS を取得
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

if fps == 0 or fps is None or fps > 120:
    fps = 30.0

print(f"適用されたWebカメラ解像度: {W}x{H}, FPS: {fps}")

# モデル
core = ov.Core()
print(f"使えるデバイス: {core.available_devices}")

# cam = CameraFactory().create() # INFINICAM
# cam.setFramerateShutter(30, 30)
# decoder = cam.decoder()
# W, H = cam.resolution().width, cam.resolution().height
# USE_GPU_DECODE = decoder.getAvailableGPUProcess()     # CUDA専用。無ければCPUデコード
img = cv2.imread('cap')
code_A = cv2.imread('codetype/コードA.jpg')
code_D = cv2.imread('codetype/コードD.jpg')
code_E = cv2.imread('codetype/コードE.jpg')

# グレースケール
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
code_A_gray = cv2.cvtColor(code_A, cv2.COLOR_BGR2GRAY)
code_D_gray = cv2.cvtColor(code_D, cv2.COLOR_BGR2GRAY)
code_E_gray = cv2.cvtColor(code_E, cv2.COLOR_BGR2GRAY)

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


ys, xs = np.where(result_A >= 0.9)
ys, xs = np.where(result_D >= 0.9)
ys, xs = np.where(result_E >= 0.9)

colorize = True
fps, t_prev = 0.0, time.perf_counter()

while True:
    ret, gray = cap.read()
    if not ret:
            print("カメラからのフレーム取得に失敗しました。")
            break
    if gray.ndim == 3:                          # 1chに揃える
            gray = gray[:, :, 0]
    h, w = gray.shape[:2]

    frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    # 表示
    now = time.perf_counter()
    fps = 0.9 * fps + 0.1 / (now - t_prev)      # 移動平均でちらつきを抑える
    t_prev = now

    cv2.putText(frame, f"{MODE}  {fps:5.1f} fps", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imshow("INFINICAM", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:                                # Esc:終了
        break

cv2.destroyAllWindows()
cap.release()