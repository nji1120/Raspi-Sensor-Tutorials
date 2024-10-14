"""
複数のpasoriをmultithredでsocket通信するコード
"""

from __future__ import print_function
from ctypes import *
from copy import deepcopy

from socket import socket,AF_INET,SOCK_DGRAM
from multiprocessing import Process
import time

# CLIENT="127.0.0.1"
CLIENT="192.168.1.3"
BASE_PORT=5000
sock1=socket(AF_INET,SOCK_DGRAM)
sock2=socket(AF_INET,SOCK_DGRAM)
sock1.bind(("",BASE_PORT))
sock2.bind(("",BASE_PORT+1))
msg,addr=sock1.recvfrom(65335)
print(msg,addr)
msg,addr=sock2.recvfrom(65335)
print(msg,addr)

class Pasori():
    def __init__(self,id:int):
        self.id=id
        self.pasori=libpafe.pasori_open_n(id)
        libpafe.pasori_init(self.pasori)
    
    def __del__(self):
        libpafe.pasori_close(self.pasori)

    def read(self,freq=5.0):
        """
        felicaを読み込見込み続ける
        :param freq: 読み込む周波数 Hz
        """
        timeout=1/freq*10**3 #ms?
        libpafe.pasori_set_timeout(self.pasori,int(timeout))
        print(timeout)

        print(f"===Pasori Reading [{self.id}]===")
        while True:
            t=time.time_ns()
            idm = c_uint64()
            try:
                #felica読み込み
                self.felica=libpafe.felica_polling(self.pasori, FELICA_POLLING_ANY,0 ,0)
                libpafe.felica_get_idm(self.felica, byref(idm))
                libpafe.free(self.felica)

                msg=f"pasori_id:{self.id},felica_id:{sort_idm(idm.value)}"
                print(msg)

            except KeyboardInterrupt:
                print(f"===Pasori Finished [{self.id}]===")
                break

            sleep(previous_time=t,sleeping_time=1/freq*10**9)
            # print(f"pasori ID:{self.id}",sort_idm(idm.value),(time.time_ns()-t)*10**-9)

    def read_and_send(self,freq,sock,client,port):
        """
        felicaを読み込見込んで送り続ける
        :param freq: 読み込む周波数 Hz
        """
        timeout=1/freq*10**3 #ms
        libpafe.pasori_set_timeout(self.pasori,int(timeout)) #カードが置かれなかった時の更新頻度

        print(f"===Pasori Reading [{self.id}]===")
        while True:
            t=time.time_ns()
            idm = c_uint64()
            try:
                #felica読み込み
                self.felica=libpafe.felica_polling(self.pasori, FELICA_POLLING_ANY,0 ,0)
                libpafe.felica_get_idm(self.felica, byref(idm))
                libpafe.free(self.felica)

                #socket送信
                msg=f"pasori_id:{self.id},felica_id:{sort_idm(idm.value)}"
                sock.sendto(msg.encode("utf-8"),(client,port))
                print(msg)

            except KeyboardInterrupt:
                print(f"===Pasori Finished [{self.id}]===")
                break

            sleep(previous_time=t,sleeping_time=1/freq*10**9)

def sleep(previous_time,sleeping_time):
    """
    :param previous_time: 前回の処理時刻   
    :prama sleeping_time: 待機時間
    """
    while time.time_ns()-previous_time<sleeping_time:
        pass


def read_and_send_felica_processing(pasoris:list,sockets:list,freq:5):
    """
    マルチスレッドでpasoriで読み込む関数
    :param read_freq: 読み込みの周波数 Hz
    """

    processes=[]
    for pasori,sock in zip(pasoris,sockets):
        processes.append(Process(
            target=pasori.read_and_send,args=(freq,sock,CLIENT,BASE_PORT+pasori.id)
        ))
    
    for process in processes:
        process.start()

    for process in processes:
        process.join()

FELICA_POLLING_ANY = 0xffff

def sort_idm(idm)->str:
    """
    libpafe+ctypesで取得したidmの順番が8ビットごとに逆だから並び替える関数

    ex)
        libpafe+ctypes -> 354A0F8DC0482E01

        本来           -> 012E48C08D0F4A35

    -input-
        idm:
            libpafeで受け取ったidm.value

    -return-
        idm_sorted:
            012E48C08D0F4A35 みたいな感じ
    """

    def fold_8bit(bit:str)->list:
        """
        2進数の文字列を8bitごとに区切る関数
        """
        bit_list=list(bit)

        ###最初の0xをpop
        bit_list.pop(0) 
        bit_list.pop(0)
        ###

        ###64bitにする
        while len(bit_list)<64:
            bit_list=deepcopy(["0"]+bit_list)
        ###

        bites=[]
        for i in range(int(len(bit_list)/8+1)):
            bites.append(bit_list[i*8:(i+1)*8])

        return bites

    bin_folded_8bit=fold_8bit(bin(idm)) #8bitごとに区切った2進数

    bin_folded_8bit.reverse() #ひっくり返して並び替える
    bin_sorted="".join(["".join(bit8) for bit8 in bin_folded_8bit]) #2進数文字列に変換

    idm_sorted=list(hex(int(bin_sorted,2))) #16進数のlist

    ###最初の0xをpopで消す
    idm_sorted.pop(0)
    idm_sorted.pop(0)
    ###

    ###16桁にする
    while len(idm_sorted)<16:
        idm_sorted=deepcopy(["0"]+idm_sorted)
    ###
    
    return "".join(idm_sorted).upper() #文字列化＆小文字→大文字にしてreturn

    
if __name__ == '__main__':
    """
    引数の指定が必ず必要

    ないと, segmentation error (core dump) になる
    """
    
    libpafe = cdll.LoadLibrary("/usr/local/lib/libpafe.so")

    ###関数の引数,返り値の指定
    libpafe.pasori_open_n.restype = c_void_p
    libpafe.pasori_init.argtypes=(c_void_p,) #引数の指定
    libpafe.felica_polling.argtypes = (c_void_p,c_int,c_int,c_int) #引数の指定
    libpafe.felica_polling.restype = c_void_p
    libpafe.felica_get_idm.argtypes = (c_void_p,c_void_p) #引数の指定
    libpafe.felica_get_idm.restype = c_void_p
    libpafe.free.argtypes=(c_void_p,) #引数の指定
    libpafe.pasori_close.argtypes=(c_void_p,) #引数の指定
    libpafe.pasori_set_timeout.argtypes=(c_void_p,c_int)    
    ###

    socks=[sock1,sock2]
    pasoris=[]
    n_pasori=1
    for i in range(n_pasori):
        pasoris.append(Pasori(id=i))
    # pasoris.reverse()

    read_and_send_felica_processing(pasoris,socks,freq=1)
       
    sock1.close()
    sock2.close()