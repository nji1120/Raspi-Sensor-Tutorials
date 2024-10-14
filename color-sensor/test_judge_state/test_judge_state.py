# カードの表裏を検出
import sys
from pathlib import Path
sys.path.append(
    str(Path(__file__).parent.parent)
)

import time
import cv2

from color_sensor import ColorSensor

FREQ=16 #Hz
IMAGE_WIDTH = 400  # 画像の幅

STATE_THRESHOLD={
    "is_card":25, #IRの閾値
    "state":{
        "front":{ #表側表示
            "r":{"low":1,"high":9},
            "g":{"low":1,"high":10},
            "b":{"low":1,"high":10},
            "ir":{"low":1,"high":4},
        },
    }
}

def judge_state(sensor_value:dict, state_shreshold:dict):
    state="no card"

    r,g,b,ir=list(sensor_value.values())
    if state_shreshold["is_card"]<=ir or (r+g+b)>=100: #上にあったらrgbの合計が100より小さくなる(と思う)
        state="no card"
    else:
        for key,val in state_shreshold["state"].items():
            r_low,r_high=list(val["r"].values())
            g_low,g_high=list(val["g"].values())
            b_low,b_high=list(val["b"].values())

            if (r_low<=r<=r_high) and (g_low<=g<=g_high) and (b_low<=b<=b_high):
                if "front" in key:
                    state="front side"
            else:
                state="back side"
    return state


def resize_image(img):
    height, width = img.shape[:2]
    scale = IMAGE_WIDTH / width
    return cv2.resize(img, (int(width * scale), int(height * scale)))


def main():
    cs = ColorSensor(is_switch=False, sensor_addr=0x2a)

    prev_state = None
    while True:
        try:
            data = cs.read()
            print(data)
        except Exception as e:
            print(e)
            break

        time.sleep(1.0 / FREQ)

        state = judge_state(data, STATE_THRESHOLD)
        if state != prev_state:  # 状態が更新されたら新しい画像を表示する
            print("State:", state)

            # 画像のパスを選択
            if state == "no card":
                img_path = Path(__file__).parent/"images/no_image.jpg"
            elif state == "front side":
                img_path = Path(__file__).parent/"images/front_side.jpg"
            elif state == "back side":
                img_path = Path(__file__).parent/"images/back_side.jpg"
            else:
                img_path = None

            # 古い画像が表示されていれば閉じる
            if prev_state is not None:
                cv2.destroyAllWindows()

            # 画像の読み込み
            if img_path:
                img = cv2.imread(str(img_path))
                img = resize_image(img)  # 画像をリサイズ
                cv2.imshow("Image", img)  # 新しい画像を表示
                cv2.moveWindow('Window', 0, 0) # ウィンドウの表示位置を設定

            prev_state = state

        if cv2.waitKey(1) == ord("0"):  # キーが0の場合は終了
            break

    cv2.destroyAllWindows()
    

if __name__ == "__main__":
    main()

