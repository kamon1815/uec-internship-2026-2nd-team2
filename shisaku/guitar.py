speed = 50 # 変数化
s1 = 100
s2 = 30
from pydub import AudioSegment
volume = None # 音量
chord_type = None # コード
import pyautogui
get_chord_by_position_l1 = ('xl1, yl1') # 左手人差し指の座標
get_chord_by_position_l2 = ('xl2, yl2') # 左手中指の座標
get_chord_by_position_l3 = ('xl3, yl3') # 左手薬指の座標
# 画面の幅と高さを取得する
width, height = pyautogui.size()

# 左手の相対座標からコードを決める
def get_chord_by_position_l(xl1, yl1):
    # 画面サイズが横 800 x 縦 600 の場合を想定
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

# 右手のスピードから音の大きさを決める
if speed > s1:
   volume = 'big'
elif speed < s2:
   volume = 'small'
else:
   volume = 'middle'

# 右手の基準値を決める
# 右手の相対座標から音が鳴るタイミングを決める
base_rx = 100 # 変数化
base_ry = 200
current_rx = 107
current_ry = 190
relative_rx = current_rx - base_rx
relative_ry = current_ry - base_ry

if (-10 <= relative_rx <= 10) & (-10 <= relative_ry <= 0):
    get_chord_by_position_l(100, 150) # 変数化
    print(f"大きさ{volume}")
    