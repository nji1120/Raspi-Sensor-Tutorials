from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent.parent
import sys
sys.path.append(str(ROOT_DIR))

from src.rcs660s import RCS660S
from src.ccid_command.get_data import GetData
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

def test_conn_type_a():
    """
    カードと通信を行う代表的なシーケンスは以下のとおりです。
    1) Start Transparent Session
    2) SwitchProtocol (TypeA/B/F)
    3) Transmission and Reception Flag などでフラグ設定 (カードコマンドに依存)
    4) RF On
    5) Transceive(Transmit/Receive)でカードコマンドを送受信
    6) RF Off
    7) End Transparent Session
    """

    # -- rc-s660の初期化
    port = "/dev/ttyAMA0"
    baudrate = 115200
    timeout_fps = 10
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
    print("2) SwitchProtocol (TypeA):")
    rcs660s.create_command_frame(
        ccid_command=SwitchProtocol(
            data_object_tag=SwitchProtocolDataObjectTag.SWITCH_TO_TYPEA_LAYER3
        ), is_debug=True
    )
    rcs660s.send_command_frame()
    response = rcs660s.read_response()
    print_response(response)
    print("\n")

    # # Get Parameters → タグの捕捉はやはりできている
    # print("Get Parameters:")
    # command=[0x01,0x00, 0x02,0x00, 0x03,0x00, 0x04,0x00, 0x05,0x00, 0x08,0x00]
    # rcs660s.create_command_frame(
    #     ccid_command=ManageSession(
    #         data_object_tag=ManageSessionDataObjectTag.GET_PARAMETERS(command)
    #     ), is_debug=True
    # )
    # rcs660s.send_command_frame()
    # response = rcs660s.read_response()
    # print_response(response)
    # print("\n")

    # # #  switch後にreceiveしてみる
    # # # → 意味なし
    # # print("switch後にreceiveしてみる:")
    # # rcs660s.create_command_frame(
    # #     ccid_command=TransparentExchange(
    # #         data_object_tag=TransparentExchangeDataObjectTag.RECEIVE
    # #     ), is_debug=True
    # # )
    # # rcs660s.send_command_frame()
    # # response = rcs660s.read_response()
    # # print_response(response)
    # # print("\n")


    # # 3) Transmission and Reception Flag などでフラグ設定 (カードコマンドに依存)
    # print("3) Transmission and Reception Flag などでフラグ設定 (カードコマンドに依存):")
    # rcs660s.create_command_frame(
    #     ccid_command=TransparentExchange(
    #         data_object_tag=TransparentExchangeDataObjectTag.TRANSMISSION_RECEPTION_FLAG(True,True,False,False)
    #     ), is_debug=True
    # )
    # rcs660s.send_command_frame()
    # response = rcs660s.read_response()
    # print_response(response)
    # print("\n")

    # # ------------------------------ trainsmitとreceiveを別々でやってみる → 意味無し ------------------------------
    # # transmit
    # print("transmit:")
    # command=[0xFF,0xCB,0x00,0x00,0x00]
    # rcs660s.create_command_frame(
    #     ccid_command=TransparentExchange(
    #         data_object_tag=TransparentExchangeDataObjectTag.TRANSMIT(command)
    #     ), is_debug=True
    # )
    # rcs660s.send_command_frame()
    # response = rcs660s.read_response()
    # print_response(response)
    # print("\n")

    # # receive
    # print("receive:")
    # rcs660s.create_command_frame(
    #     ccid_command=TransparentExchange(
    #         data_object_tag=TransparentExchangeDataObjectTag.RECEIVE
    #     ), is_debug=True
    # )
    # rcs660s.send_command_frame()
    # response = rcs660s.read_response()
    # print_response(response)
    # print("\n")
    # # ----------------------------------------------------------------------------------------------------------


    # # 5) Transceive(Transmit/Receive)でカードコマンドを送受信
    # print("5) Transceive(Transmit/Receive)でカードコマンドを送受信:")
    # command=[0xFF,0xCB,0x00,0x00,0x00]
    # # command = [0x26]
    # # command = [0x93,0x20]
    # # command=[0xD4, 0x4A, 0x01, 0x00] # 何かが返ってくる. が、uidではない...
    # # command=[0xD4, 0x40] + [0xFF,0xCA,0x00,0x00,0x00]
    # # command = [0x00, 0xA4, 0x00, 0x00]
    # # command = [0x00, 0xB0, 0x00, 0x00, 0x00]
    # rcs660s.create_command_frame(
    #     ccid_command=TransparentExchange(
    #         data_object_tag=TransparentExchangeDataObjectTag.TRANSCEIVE(command)
    #     ), is_debug=True
    # )
    # rcs660s.send_command_frame()
    # response = rcs660s.read_response()
    # print_response(response)
    # print("\n")

    # Get Data
    print("Get Data:")
    rcs660s.create_command_frame(
        ccid_command=GetData(), is_debug=True
    )
    rcs660s.send_command_frame()
    response = rcs660s.read_response()
    print_response(response)
    print("\n")


    # 6) RF Off
    print("6) RF Off:")
    rcs660s.create_command_frame(
        ccid_command=ManageSession(
            data_object_tag=ManageSessionDataObjectTag.RF_OFF
        ), is_debug=True
    )
    rcs660s.send_command_frame()
    response = rcs660s.read_response()
    print_response(response)
    print("\n")

    # 7) End Transparent Session
    print("7) End Transparent Session:")
    rcs660s.create_command_frame(
        ccid_command=ManageSession(
            data_object_tag=ManageSessionDataObjectTag.END_TRANSPARENT_SESSION
        ), is_debug=True
    )
    rcs660s.send_command_frame()
    response = rcs660s.read_response()
    print_response(response)
    print("\n")


if __name__ == "__main__":
    test_conn_type_a()