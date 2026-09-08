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
data = """
NormalizedLandmark(x=0.5428542494773865, y=0.4200127422809601, z=0.04844113066792488, visibility=None, presence=None, name=None),
NormalizedLandmark(x=0.5870059728622437, y=0.41215941309928894, z=0.0647120550274849, visibility=None, presence=None, name=None),
NormalizedLandmark(x=0.6176277995109558, y=0.40548330545425415, z=0.06839596480131149, visibility=None, presence=None, name=None),
NormalizedLandmark(x=0.6388885974884033, y=0.39930304884910583, z=0.06845066696405411, visibility=None, presence=None, name=None)
"""
finger = get_finger_position('Right', 1)
base_rx = finger[3].x
base_ry = finger[3].y

# 座標取得
def get_finger(data):

    finger = get_finger_position('Right', 1)
    if base_rx == None:
        base_rx = finger[3].x
        base_ry = finger[3].y

    current_rx = finger[3].x
    current_ry = finger[3].y

    relative_rx = current_rx - base_rx
    relative_ry = current_ry - base_ry
    print(f"{relative_rx}, {relative_ry}")

while True:
    get_finger(data)
    if (-10 <= relative_rx <= 10) & (-10 <= relative_ry <= 0):
        get_chord_by_position_l(100, 150) # 変数化