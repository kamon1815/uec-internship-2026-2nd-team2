import time
import cv2
import numpy as np
import openvino as ov
import pose_estimation
import math
from pathlib import Path
from pypuclib import CameraFactory

lx1 = None
ly1 = None
lx2 = None
ly2 = None
lx3 = None
ly3 = None
RANGE_X = 0.1
RANGE_Y = 0.1
base_rx = None
base_ry = None

# 座標取得
def get_lefthand_potions():
    finger1 = pose_estimation.get_finger_position('Left', 1, pose_estimation.current_hands)
    finger2 = pose_estimation.get_finger_position('Left', 2, pose_estimation.current_hands)
    finger3 = pose_estimation.get_finger_position('Left', 3, pose_estimation.current_hands)
    if (finger1 is not []) & (finger2 is not []) & (finger3 is not []):
        global lx1, ly1, lx2, ly2, lx3, ly3
        lx1 = finger1[3].x
        ly1 = finger1[3].y
        lx2 = finger2[3].x
        ly2 = finger2[3].y
        lx3 = finger3[3].x
        ly3 = finger3[3].y
        print(lx1, ly1, lx2, ly2, lx3, ly3)
        return(lx1, ly1, lx2, ly2, lx3, ly3)
    else :
        return(0, 0, 0, 0, 0, 0)
    

# コード判定
def decide_code(lx1, ly1, lx2, ly2, lx3, ly3):
    # 指間の距離
    dist_12 = math.hypot(lx2 - lx1, ly2 - ly1)
    dist_23 = math.hypot(lx3 - lx2, ly3 - ly2)
    dist_31 = math.hypot(lx1 - lx3, ly1 - ly3)
    print('距離')
    print(dist_12, dist_23, dist_31)

    # 外積
    cross_product = (lx2 - lx1) * (ly3 - ly1) - (ly2 - ly1) * (lx3 - lx1)

    # 三角形の面積
    area = abs(cross_product) / 2
    print(area)

    if 0.002 < dist_31:
        print("コードA")
        return("ラ")
    elif 0.002 > dist_23:
        print("コードD")
        return("ミ")
    # elif (ly2 < ly1) & (ly2 < ly3):
    #     print("コードD")
    #     return("ド")
    # elif (ly2 > ly1) & (ly2 > ly3):
    #     print("コードE")
    #     return("ミ")

def get_hand_relative_position(): #基準点(base_rx,base_ry)に対する現在の指の相対位置を取得
    hand_position = pose_estimation.get_hand_position('Right', pose_estimation.current_hands)
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

while True:
    relative_rx, relative_ry, is_on_guitar = get_hand_relative_position()
    lx1, ly1, lx2, ly2, lx3, ly3 = get_lefthand_potions()
    decide_code(lx1, ly1, lx2, ly2, lx3, ly3)