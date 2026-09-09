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

    if -0.002 < area < 0.002:
        print("コードA")
        return("ラ")
    else:
        print("コードD")
        print("コードE")
        return("ド")


while True:
    lx1, ly1, lx2, ly2, lx3, ly3 = get_lefthand_potions()
    decide_code(lx1, ly1, lx2, ly2, lx3, ly3)
    # get_lefthand_potions()