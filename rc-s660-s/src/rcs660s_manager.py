from .rcs660s import RCS660S

from .ccid_command.reset_device import ResetDevice
from .ccid_command.manage_session import ManageSession, ManageSessionDataObjectTag
from .ccid_command.switch_protocol import SwitchProtocol, SwitchProtocolDataObjectTag
from .ccid_command.transparent_exchange import TransparentExchange, TransparentExchangeDataObjectTag



class RCS660SManager:
    """
    低レベルなRCS660Sの通信を管理するクラス
    一連のコマンドを実行し, 使用者にバイト列の通信を意識させない.
    """

    def __init__(self,rcs660s:RCS660S,is_debug:bool=False):
        self.rcs660s = rcs660s
        self.is_debug = is_debug


    def reset_device(self):
        self.rcs660s.create_command_frame(
            ccid_command=ResetDevice(), is_debug=self.is_debug
        )
        self.rcs660s.send_command_frame()
        self.rcs660s.uart.read(128)

    
    def setup_device(self):

        # 1) Start Transparent Session
        self.rcs660s.create_command_frame(
            ccid_command=ManageSession(
                data_object_tag=ManageSessionDataObjectTag.START_TRANSPARENT_SESSION
            ), is_debug=self.is_debug
        )
        self.rcs660s.send_command_frame()
        response = self.rcs660s.read_response()
        # print_response(response)
        # print("\n")

        # 2) SwitchProtocol (TypeA/B/F)
        rcs660s.create_command_frame(
            ccid_command=SwitchProtocol(
                # ここはpollingまで開けても問題ない. ただし, 無駄なのでfelica通信設定のみだけで良い.
                data_object_tag=SwitchProtocolDataObjectTag.SWITCH_TO_FELICA
            ), is_debug=self.is_debug
        )
        self.rcs660s.send_command_frame()
        time.sleep(0.1)
        response = self.rcs660s.read_response()
        # print_response(response)
        # print("\n")


        # 3)送受信処理フラグ
        # print("3)送受信処理フラグ:")
        rcs660s.create_command_frame(
            ccid_command=TransparentExchange(
                # 0bit目, 1bit目はFalse必須
                data_object_tag=TransparentExchangeDataObjectTag.TRANSMISSION_RECEPTION_FLAG(
                    False,False,True,True
                )
            ), is_debug=self.is_debug
        )
        self.rcs660s.send_command_frame()
        response = self.rcs660s.read_response()
        # print_response(response)
        # print("\n")

        # 4) transmission bit framing
        command=[0x00]
        rcs660s.create_command_frame(
            ccid_command=TransparentExchange(
                data_object_tag=TransparentExchangeDataObjectTag.Transmission_BIT_FRAMING(command)
            ), is_debug=self.is_debug
        )
        self.rcs660s.send_command_frame()
        response = self.rcs660s.read_response()
        # print_response(response)
        # print("\n")

        # 5) 通信速度設定
        command=[0x05, 0x01, 0x89]
        rcs660s.create_command_frame(
            ccid_command=ManageSession(
                data_object_tag=ManageSessionDataObjectTag.SET_PARAMETERS(command)
            ), is_debug=self.is_debug
        )
        self.rcs660s.send_command_frame()
        response = self.rcs660s.read_response()
        # print_response(response)
        # print("\n")

        # 6) RF ON
        # print("6) RF ON:")
        self.rcs660s.create_command_frame(
            ccid_command=ManageSession(
                data_object_tag=ManageSessionDataObjectTag.RF_ON
            ), is_debug=False
        )
        self.rcs660s.send_command_frame()
        response = self.rcs660s.read_response()
        # print_response(response)
        # print("\n")


    def polling(self) -> dict:

        timer_command=[0x60,0xea,0x00,0x00] # 待機時間[ms], リトルエンディアン
        timer_ccid=TransparentExchangeDataObjectTag.TIMER(timer_command)
        polling_command=[0x06,0x00,0xff,0xff,0x00,0x00] # idm取得コマンド, 謎の0x06が必須(長さではない...)
        polling_ccid=TransparentExchangeDataObjectTag.TRANSCEIVE(polling_command)
        self.rcs660s.create_command_frame(
            ccid_command=TransparentExchange(
                data_object_tag=timer_ccid + polling_ccid
            ), is_debug=self.is_debug
        )
        self.rcs660s.send_command_frame()
        time.sleep(0.1)
        response = self.rcs660s.read_response()
        
        # バイト列からidmと工場番号に変換
        response_dict=self.__bite2idm(response)


    def close(self):
        # 通信終了

        # 8) RF OFF
        self.rcs660s.create_command_frame(
            ccid_command=ManageSession(
                data_object_tag=ManageSessionDataObjectTag.RF_OFF
            ), is_debug=self.is_debug
        )
        self.rcs660s.send_command_frame()
        response = self.rcs660s.read_response()
        # print_response(response)
        # print("\n")

        # 9) End Transparent Session
        self.rcs660s.create_command_frame(
            ccid_command=ManageSession(
                data_object_tag=ManageSessionDataObjectTag.END_TRANSPARENT_SESSION
            ), is_debug=self.is_debug
        )
        self.rcs660s.send_command_frame()
        response = self.rcs660s.read_response()
        # print_response(response)
        # print("\n")

        self.rcs660s.uart.close()


    def __bite2idm(self,response)->dict:
        idm={}
        return idm
