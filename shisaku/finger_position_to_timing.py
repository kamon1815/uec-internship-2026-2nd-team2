import pose_estimation
def get_chord_by_position_l(xl1, yl1):
    # テスト (座標)
    base_lx = 100 # 変数化
    base_ly = 200
    current_lx = 207
    current_ly = 290
    relative_lx = current_lx - base_lx
    relative_ly = current_ly - base_ly
    # 指の座標でコードを決める
    if (0 <= relative_lx < 200) & (0 <= relative_ly < 200): # 範囲の決定
        chord_type = "A"
    elif (200 <= relative_lx < 400) & (200 <= relative_ly < 400):
        chord_type = "D"
    elif (400 <= relative_lx < 600) & (400 <= relative_ly < 600):
        chord_type = "E"
    else:
        print('コードがわかりません')
        print(f"左手の相対座標:({relative_lx}, {relative_ly})")
        return 

    print(f"コード{chord_type}")

# 得られる座標

base_rx = None
base_ry = None

# 座標取得
def get_finger():

    finger = pose_estimation.get_finger_position('Right', 1)
    global base_rx, base_ry
    if base_rx is None:
        base_rx = finger[3].x
        base_ry = finger[3].y

    current_rx = finger[3].x
    current_ry = finger[3].y

    relative_rx = current_rx - base_rx
    relative_ry = current_ry - base_ry
    print(f"{relative_rx}, {relative_ry}")
    return relative_rx, relative_ry

while True:
    relative_rx, relative_ry = get_finger()
    if (-0.05 <= relative_rx <= 0.05) & (-0.05 <= relative_ry <= 0.05):
        get_chord_by_position_l(100, 150) # 変数化