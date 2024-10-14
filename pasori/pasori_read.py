from __future__ import print_function
from ctypes import *
from copy import deepcopy

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
    ctypesでは引数の指定が必要

    ないと, segmentation error (core dump) になる
    """
    
    libpafe = cdll.LoadLibrary("/usr/local/lib/libpafe.so")

    libpafe.pasori_open.restype = c_void_p
    pasori = libpafe.pasori_open()

    libpafe.pasori_init.argtypes=(c_void_p,) #引数の指定
    libpafe.pasori_init(pasori)

    # libpafe.felica_polling.argtypes = (c_void_p,c_int,c_int,c_int) #引数の指定
    libpafe.felica_polling.restype = c_void_p #返り値の指定
    felica = libpafe.felica_polling(pasori, FELICA_POLLING_ANY,0 ,0)

    idm = c_uint64()
    libpafe.felica_get_idm.argtypes = (c_void_p,c_void_p) #引数の指定
    libpafe.felica_get_idm.restype = c_void_p
    libpafe.felica_get_idm(felica, byref(idm))

    print("%016X" % idm.value)
    # print(sort_idm(idm=idm.value))

    libpafe.free.argtypes=(c_void_p,) #引数の指定
    libpafe.free(felica)

    libpafe.pasori_close.argtypes=(c_void_p,) #引数の指定
    libpafe.pasori_close(pasori)