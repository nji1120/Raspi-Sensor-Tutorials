"""
とりあえずfirmware versionをuartで取得してみる
このコードの感じで
    APDU → CCID → コマンドフレーム
の順でuartで送信するコマンドを作成する.

src/rcs660sにはこの流れがカプセル化されている.
"""

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

import serial
from math import ceil
from utils import print_hex


"""
コマンドフレームの構成手順
1. パケットデータ(CCIDコマンド)の作成
2. CCIDコマンド以外のデータを計算
3. 1.と2.を組み合わせてコマンドフレームを作成
"""


"""----------------------------------------------------------------------------------------------------------------------
1. パケットデータ(CCIDコマンド)の作成
今回はfirmware versionを取得するCCIDコマンド(=PC_to_RDB_ESCAPE)を使用
CCIDコマンドの構成手順は以下
    1.1. abDataに格納するAPDUコマンドデータの作成
    1.2. 残りのフィールドを設定
    1.3. 1.1.と1.2.を組み合わせてCCIDコマンドを作成
"""

# 1.1. abDataに格納するAPDUコマンドデータの作成
# Get Firmware VersionのAPDUコマンドを使用
ab_data=[0xFF, 0x56, 0x00, 0x00] # Leコマンドはなしとしたversion
# ab_data=[0xFF, 0x56, 0x00, 0x00, 0x00] # Leコマンドを00としたversion

# 1.2. 残りのフィールドを設定
b_message_type=[0x6B] #これがPC_to_RDB_ESCAPEを表す
dw_length=list(len(ab_data).to_bytes(4, 'little')) # データ長は4バイト, リトルエンディアンで表現
b_slot=[0x00]
b_seq=[0x00] # シーケンス番号は0とした. 通信ごとにカウントアップしてもよい.
ab_rfu=[0x00, 0x00, 0x00]

# 1.3. 1.1.と1.2.を組み合わせてCCIDコマンドを作成
ccid_command=b_message_type+dw_length+b_slot+b_seq+ab_rfu+ab_data


"""----------------------------------------------------------------------------------------------------------------------
2. CCIDコマンド以外のデータを計算
"""
preamble=[0x00]
start_code=[0x00, 0xFF]
packet_length=list(len(ccid_command).to_bytes(2, 'big')) # ccidコマンド長を2バイト&ビッグエンディアンで表現
packet_data_checksum=list(( 
    (16**2) * ceil(sum(ccid_command)/(16**2)) - sum(ccid_command)
).to_bytes(1, 'big')) # パケットデータのチェックサムを計算
packet_length_checksum=list(( 
    (16**2) * ceil(sum(packet_length)/(16**2)) - sum(packet_length)
    ).to_bytes(1, 'big')) # パケット長のチェックサムを計算
postamble=[0x00]

"""----------------------------------------------------------------------------------------------------------------------
3. 1.と2.を組み合わせてコマンドフレームを作成
"""
command_frame=preamble+start_code+packet_length+packet_length_checksum+ccid_command+packet_data_checksum+postamble

def debug_ccid_command():
    print("[CCID COMMAND]")
    print_hex("ab_data", ab_data)
    print_hex("b_message_type", b_message_type)
    print_hex("dw_length", dw_length)
    print_hex("b_slot", b_slot)
    print_hex("b_seq", b_seq)
    print_hex("ab_rfu", ab_rfu)
    print_hex("ccid_command", ccid_command)
    print("--------------------------------")
def debug_command_frame():
    print("[COMMAND FRAME]")
    print_hex("preamble", preamble)
    print_hex("start_code", start_code)
    print_hex("packet_length", packet_length)
    print_hex("packet_length_checksum", packet_length_checksum)
    print_hex("ccid_command", ccid_command)
    print_hex("packet_data_checksum", packet_data_checksum)
    print_hex("postamble", postamble)
    print_hex("command_frame", command_frame)
    print("*ccid_command + packet_data_checksum", hex(sum(ccid_command+packet_data_checksum)))
    print("*packet_length + packet_length_checksum", hex(sum(packet_length+packet_length_checksum)))
    print("--------------------------------")

debug_ccid_command()
debug_command_frame()


# uart通信 -------------------------------------------------------------------------------
port="/dev/ttyAMA0"
baudrate=115200
timeout_fps=16 # ここを小さくすると応答がゆっくりになる

uartport=serial.Serial(
    port=port,
    baudrate=baudrate,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1.0/timeout_fps
)

uartport.write(bytes(command_frame)) # コマンドフレームを送信

# レスポンスを受信
response=uartport.read(128)
print_hex("response", response)