import cv2
import mediapipe as mp
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

model_path = 'shisaku/hand_landmarker.task'

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

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
    result_callback=print_result)

landmarker = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0) #カメラの指定

# def HandOverwrite(position, frame): #手の上に点を表示
    
start_time = time.time()

# 検出された手の数を取得
def get_hands_count(result): 
    if result and result.hand_landmarks:
        return len(result.hand_landmarks)
    return 0

# 検出された座標を取得
def get_hands_position(result, hand_num, point_num):
    if result and result.hand_landmarks:
        return result.hand_landmarks[hand_num][point_num]
    return "unknown"

def draw_landmarks(image, detection_result):
    """検出されたランドマークと骨格を描画
    
    Args:
        image: 描画対象の画像（RGB形式）
        detection_result: MediaPipeの検出結果
    
    Returns:
        ランドマークと骨格が描画された画像
    """
    if detection_result and detection_result.hand_landmarks:
        
        image_height, image_width, _ = image.shape
        
        # 検出された各手に対して処理
        for hand_landmarks in detection_result.hand_landmarks:
            # 各ランドマーク（関節）を円で描画
            for landmark in hand_landmarks:
                # 正規化座標（0.0〜1.0）をピクセル座標に変換
                px = int(landmark.x * image_width)
                py = int(landmark.y * image_height)
                # 緑色の円で描画（半径5ピクセル）
                cv2.circle(image, (px, py), 5, (0, 255, 0), -1)
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
                # 赤色の線で描画（太さ2ピクセル）
                cv2.line(image, pt1, pt2, (255, 0, 0), 2)
        
        return image
    return image


while cap.isOpened():
    # ウェブカメラの画像取得
    ret, frame = cap.read() #カメラから画像取得(BGR)
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #OpenCVの形式(GBR)からMediaPipeの形式(RGB)に変換

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame) #mediapipeの画像として使える塊にする。

    frame_timestamp = int((time.time() - start_time) * 1000) #タイムスタンプ作成

    landmarker.detect_async(mp_image, frame_timestamp) #手を検出
    hands_count = get_hands_count(current_hands)

    print(f"手の数: {hands_count}")
    print(f"右手人差し指の位置: {get_hands_position(current_hands, 0 ,8 )}")
    draw_landmarks(frame, current_hands)
    # 画像表示
    cv2.imshow('test', frame)

    cv2.waitKey(1) #待機時間、ミリ秒指定、0の場合はボタンが押されるまで待機

cap.release()
cv2.destroyAllWindows()


