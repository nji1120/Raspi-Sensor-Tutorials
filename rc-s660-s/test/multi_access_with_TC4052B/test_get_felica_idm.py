"""
2025/8/9
TCB4052BでUARTのスイッチングを行うテストプログラム
→ テスト完了.swicth_slave関数でスイッチするだけでUARTのスイッチングができた.
"""

from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent.parent
import sys
sys.path.append(str(ROOT_DIR))
import time

import RPi.GPIO as GPIO

from src.rcs660s import RCS660S
from src.ccid_command.reset_device import ResetDevice
from src.ccid_command.manage_session import ManageSession, ManageSessionDataObjectTag
from src.ccid_command.switch_protocol import SwitchProtocol, SwitchProtocolDataObjectTag
from src.ccid_command.transparent_exchange import TransparentExchange, TransparentExchangeDataObjectTag
from src.utils import print_hex

def print_response(response: dict):
    for key, value in response.items():
        print(f"\033[34m{key}\033[0m:")
        print("status: ", value["status"], ", message: ", value["message"])
        print_hex("response: ", value["response"])
        print("---")

def test_get_idm():
    """
    カードと通信を行う代表的なシーケンスは以下
    0) reset device
    1) Start Transparent Session
    2) SwitchProtocol (TypeA/B/F)
    3) Transmission and Reception Flag などでフラグ設定 (カードコマンドに依存)
    4) transmission bit framing
    5) 通信速度設定
    6) RF On
    7) Transceive(Transmit/Receive)でカードコマンドを送受信
    8) RF Off
    9) End Transparent Session
    """

    # -- rc-s660の初期化
    port = "/dev/ttyAMA0"
    baudrate = 115200
    timeout_fps = 100
    rcs660s = RCS660S(port=port, baudrate=baudrate, timeout_fps=timeout_fps)

    # # -- リセット
    print("リセット:")
    rcs660s.create_command_frame(
        ccid_command=ResetDevice(), is_debug=True
    )
    rcs660s.send_command_frame()
    rcs660s.uart.read(128)
    
    # -- カードと通信を行う
    # 1) Start Transparent Session
    print("1) Start Transparent Session:")
    rcs660s.create_command_frame(
        ccid_command=ManageSession(
            data_object_tag=ManageSessionDataObjectTag.START_TRANSPARENT_SESSION
        ), is_debug=True
    )
    rcs660s.send_command_frame()
    response = rcs660s.read_response()
    print_response(response)
    print("\n")

    # 2) SwitchProtocol (TypeA/B/F)
    print("2) SwitchProtocol (TypeA/B/F):")
    rcs660s.create_command_frame(
        ccid_command=SwitchProtocol(
            # ここはpollingまで開けても問題ない. ただし, 無駄なのでfelica通信設定のみだけで良い.
            data_object_tag=SwitchProtocolDataObjectTag.SWITCH_TO_FELICA
        ), is_debug=True
    )
    rcs660s.send_command_frame()
    time.sleep(0.1)
    response = rcs660s.read_response()
    print_response(response)
    print("\n")


    # 3)送受信処理フラグ
    print("3)送受信処理フラグ:")
    rcs660s.create_command_frame(
        ccid_command=TransparentExchange(
            # 0bit目, 1bit目はFalse必須
            data_object_tag=TransparentExchangeDataObjectTag.TRANSMISSION_RECEPTION_FLAG(False,False,True,True)
        ), is_debug=True
    )
    rcs660s.send_command_frame()
    response = rcs660s.read_response()
    print_response(response)
    print("\n")

    # 4) transmission bit framing
    print("4) transmission bit framing:")
    command=[0x00]
    rcs660s.create_command_frame(
        ccid_command=TransparentExchange(
            data_object_tag=TransparentExchangeDataObjectTag.Transmission_BIT_FRAMING(command)
        ), is_debug=True
    )
    rcs660s.send_command_frame()
    response = rcs660s.read_response()
    print_response(response)
    print("\n")

    # 5) 通信速度設定
    print("5) 通信速度設定:")
    command=[0x05, 0x01, 0x89]
    rcs660s.create_command_frame(
        ccid_command=ManageSession(
            data_object_tag=ManageSessionDataObjectTag.SET_PARAMETERS(command)
        ), is_debug=True
    )
    rcs660s.send_command_frame()
    response = rcs660s.read_response()
    print_response(response)
    print("\n")

    # 6) RF ON
    print("6) RF ON:")
    rcs660s.create_command_frame(
        ccid_command=ManageSession(
            data_object_tag=ManageSessionDataObjectTag.RF_ON
        ), is_debug=True
    )
    rcs660s.send_command_frame()
    response = rcs660s.read_response()
    print_response(response)
    print("\n")

    # 7) polling
    print("7) polling:")
    timer_command=[0x60,0xea,0x00,0x00] # 待機時間[ms], リトルエンディアン
    timer_ccid=TransparentExchangeDataObjectTag.TIMER(timer_command)
    polling_command=[0x06,0x00,0xff,0xff,0x00,0x00] # idm取得コマンド, 謎の0x06が必須(長さではない...)
    polling_ccid=TransparentExchangeDataObjectTag.TRANSCEIVE(polling_command)
    rcs660s.create_command_frame(
        ccid_command=TransparentExchange(
            data_object_tag=timer_ccid + polling_ccid
        ), is_debug=True
    )
    rcs660s.send_command_frame()
    time.sleep(0.1)
    response = rcs660s.read_response()
    print_response(response)
    print("\n")

    # 8) RF OFF
    print("8) RF OFF:")
    rcs660s.create_command_frame(
        ccid_command=ManageSession(
            data_object_tag=ManageSessionDataObjectTag.RF_OFF
        ), is_debug=True
    )
    rcs660s.send_command_frame()
    response = rcs660s.read_response()
    print_response(response)
    print("\n")

    # 9) End Transparent Session
    print("9) End Transparent Session:")
    rcs660s.create_command_frame(
        ccid_command=ManageSession(
            data_object_tag=ManageSessionDataObjectTag.END_TRANSPARENT_SESSION
        ), is_debug=True
    )
    rcs660s.send_command_frame()
    response = rcs660s.read_response()
    print_response(response)
    print("\n")

    rcs660s.uart.close()

def switch_slave(gpio_a:GPIO.PWM, gpio_b:GPIO.PWM, bool_a:bool, bool_b:bool):
    """
    gpio_a, gpio_bをスイッチングする
    """
    GPIO.output(gpio_a, int(bool_a))
    GPIO.output(gpio_b, int(bool_b))


if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM) # GPIOのピン番号を指定するモード
    GPIO.setwarnings(False)

    # ここでTC4052Bのチャンネル選択をする 
    # [A=L, B=L] → 0, [A=H, B=L] → 1
    gpio_a = 21
    gpio_b = 20
    GPIO.setup(gpio_a, GPIO.OUT)
    GPIO.setup(gpio_b, GPIO.OUT)

    switch_slave(gpio_a, gpio_b, False, False)
    # チャンネルごとに別のfelicaを乗せたらちゃんと取得できた
    # c0：01 2E 50 E5 21 83 82 4A
    # c1：01 2E 50 E5 21 83 81 79

    test_get_idm()