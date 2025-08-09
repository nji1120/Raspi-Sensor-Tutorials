import RPi.GPIO as GPIO
import time
import sys

MAX_DISTANCE = 4500 # mm, 最長測定可能距離

def get_distance(trig_pin, echo_pin, speed_of_sound, timeout): 
    """
    :param trig_pin: 超音波発信ピン
    :param echo_pin: 超音波受信ピン
    :param speed_of_sound: 音速(mm/s)
    :param timeout: タイムアウト時間(s), 最長測定可能距離に相当する時間を設定する
    :return: 距離(mm), タイムアウト時は-1を返す
    """

    #Trigピンを10μsだけHIGHにして超音波の発信開始
    GPIO.output(trig_pin, GPIO.HIGH)
    time.sleep(0.000020)
    GPIO.output(trig_pin, GPIO.LOW)


    while not GPIO.input(echo_pin):
        time.sleep(0.00001)

    t1 = time.time() # 超音波発信時刻（EchoピンがHIGHになった時刻）格納


    is_timeout = False
    start_time = time.time()
    while GPIO.input(echo_pin):

        # 最長測定可能距離に相当する時間を超えたらタイムアウト
        if (time.time() - start_time) > timeout:
            is_timeout = True
            break
        time.sleep(0.00001)
    t2 = time.time() # 超音波受信時刻（EchoピンがLOWになった時刻）格納
    

    # 距離計算
    distance:float
    if is_timeout: distance = None
    else: distance = (t2 - t1) * speed_of_sound / 2 # 時間差から対象物までの距離計算


    return distance


def main():

    led_pin = 18

    trig_pin = 15                           # GPIO 15
    echo_pin = 14                           # GPIO 14
    speed_of_sound = 343700                  # 20℃での音速(mm/s)
    timeout = 4500 / speed_of_sound*2 # 最長測定可能時間(s)
    print(f"timeout: {timeout}s")

    GPIO.setmode(GPIO.BCM)                  # GPIOをBCMモードで使用
    GPIO.setwarnings(False)                 # BPIO警告無効化
    GPIO.setup(trig_pin, GPIO.OUT)          # Trigピン出力モード設定
    GPIO.setup(echo_pin, GPIO.IN)           # Echoピン入力モード設定
    GPIO.setup(led_pin, GPIO.OUT)           # LEDピン出力モード設定

    fps = 3 #[hz]
    distance_threshold = 1400 # mm

    while True:
        time_start = time.time()

        distance = get_distance(trig_pin, echo_pin, speed_of_sound, timeout)
        print(f"Distance: {distance}mm, time: {time.time() - time_start}s")

        if distance is not None and distance < distance_threshold:
            GPIO.output(led_pin, GPIO.HIGH)
        else:
            GPIO.output(led_pin, GPIO.LOW)

        while time.time() - time_start < 1/fps:
            time.sleep(0.00001)


if __name__ == "__main__":
    main()