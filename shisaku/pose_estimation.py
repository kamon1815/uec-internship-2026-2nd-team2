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

model_path = 'shisaku/hand_landmarker.task'

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode


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



# Create a hand landmarker instance with the live stream mode:
current_hands = None

def print_result(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
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

hand_position_history = deque(maxlen=20)
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
    first = hand_position_history_list[:10]
    last = hand_position_history_list[-10:]

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
            return [last_avg_x - first_avg_x, last_avg_y - first_avg_y]

    return [0,0]

                

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

    #初期位置取得用の画像の取得
    first_data = cam.grab()
    
    # Decode the data can be used as image
    if GPUStatus == True:
        array = decoder.decodeGPU(first_data, True, reso.width)
    elif GPUStatus == False:
        array = decoder.decode(first_data)
    
    array = cv2.cvtColor(array, cv2.COLOR_GRAY2BGR)


    # 骨格推定
    rgb_frame = cv2.cvtColor(array, cv2.COLOR_BGR2RGB) #OpenCVの形式(GBR)からMediaPipeの形式(RGB)に変換 

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame) #mediapipeの画像として使える塊にする。    
    frame_timestamp = int((time.time() - start_time) * 1000) #タイムスタンプ作成
    landmarker.detect_async(mp_image, frame_timestamp) #手を検出

    time.sleep(0.2)

    # もし手が２本なかったらやり直し
    if get_hands_count(current_hands) != 2:
        print(f"手の読み取りに失敗しました（検出された手の数: {get_hands_count()}）")
        print("もう一度演奏位置の設定を行います")
        continue    
    break

draw_landmarks(array, current_hands) #骨格の描画
array = cv2.flip(array,1)
array = cv2.putText(array, "これが初期位置です。5秒後に遷移します。", (400, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255,255,255), 2, cv2.LINE_AA) # 案内文の追加
cv2.imshow("Setup", array)
cv2.waitKey(5000) # 5秒待機
cv2.destroyAllWindows()

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
    # 移動量を出力
    print(get_moved_distance())

    # Show the image
    cv2.imshow("INFINICAM", frame)

    key = cv2.waitKey(1)
    if key & 0xFF == 27: # Esc : quit application
        break
cv2.destroyAllWindows()