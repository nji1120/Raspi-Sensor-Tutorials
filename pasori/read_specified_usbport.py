#複数のpasoriをUSBポート位置を指定して読み込む
#参考（自分のnotion）：https://www.notion.so/RC-S320-USB-34712847fc2f4515863e449a178e5ac4#091e62c3bf574213b22111b68760f58c

from __future__ import print_function
from ctypes import *
from copy import deepcopy
import time
import argparse

FPS=2

FELICA_POLLING_ANY = 0xffff

def fix_idm(idm:int):
    """
    libpafe+ctypesで取得したidmの順番が8ビットごとに逆だから並び替える関数  

    論理演算で並び替えているので理解不能だと思う

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


    fixed_idm=0x0000000000000000
    for i in range(8):
        filter=0xff00000000000000>>(4*2*i)
        filtered_idm=idm&filter

        shift=4*(14-4*i)
        if shift>=0:
            fixed_idm|=(filtered_idm>>shift)
        else:
            fixed_idm|=(filtered_idm<<abs(shift))
        # print(hex(filtered_idm)[2:],hex(fixed_idm)[2:])

    return fixed_idm

    
if __name__ == '__main__':
    """
    引数の指定が必ず必要

    ないと, segmentation error (core dump) になる
    """
    
    libpafe = cdll.LoadLibrary("/usr/local/lib/libpafe.so")

    ###関数の引数,返り値の指定
    libpafe.pasori_open_port.argtypes = (c_char_p,) #文字列引数の指定
    libpafe.pasori_open_port.restype = c_void_p
    libpafe.pasori_init.argtypes=(c_void_p,) #引数の指定
    libpafe.felica_polling.argtypes = (c_void_p,c_int,c_int,c_int) #引数の指定
    libpafe.felica_polling.restype = c_void_p
    libpafe.felica_get_idm.argtypes = (c_void_p,c_void_p) #引数の指定
    libpafe.felica_get_idm.restype = c_void_p
    libpafe.free.argtypes=(c_void_p,) #引数の指定
    libpafe.pasori_close.argtypes=(c_void_p,) #引数の指定
    ###

    parser=argparse.ArgumentParser()
    parser.add_argument("--n_pasori",default=1,type=int)
    args=parser.parse_args()

    pasoris=[]
    n_pasori=args.n_pasori
    for i in range(n_pasori):
        pasoris.append(libpafe.pasori_open_port(f"port{i+1}".encode("utf-8")))
        libpafe.pasori_init(pasoris[i])

    trial=0
    while True:
        try:
    
            print(f"-TRIAL[{trial}]-----")
            for i in range(n_pasori):
                felica = libpafe.felica_polling(pasoris[i], FELICA_POLLING_ANY,0 ,0)

                idm = c_uint64()
                
                libpafe.felica_get_idm(felica, byref(idm))

                fixed_idm=fix_idm(idm=idm.value)
                print(f"PASORI:dev{i+1}",fixed_idm,hex(fixed_idm)[2:].upper())

                libpafe.free(felica)

            trial+=1
            time.sleep(1.0/FPS)

        except KeyboardInterrupt as e:
            print(e)
            for i in range(n_pasori):
                libpafe.pasori_close(pasoris[i])
            break

            
    