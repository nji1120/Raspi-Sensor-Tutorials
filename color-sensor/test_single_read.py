# 参考 https://itecjapan.xsrv.jp/2020/05/23/raspberrypi-カラーセンサーs11059-02dt/

import time
from smbus2 import SMBus

FREQ=4 #Hz

def main():
    bus_num=1 #バス番号 i2c-{bus_num} バスは基本的に1本. 自分でGPIOピン使って増やすこともできる
    smbus2=SMBus(bus_num)

    slave_addr=0x2a #カラーセンサのアドレス

    #センサのスリープ解除
    smbus2.write_byte_data(
        slave_addr,
        register=0x00,
        value=0x80,
    )

    #センサの設定変更
    smbus2.write_byte_data(
        slave_addr,
        register=0x00,
        value=0x0b,
    )


    while True:

        try:
            #0番レジスタから, 11byte分のデータ読み込み
            data=smbus2.read_i2c_block_data(
                slave_addr,
                register=0x00, 
                length=11
            )
            # print(data,len(data))

            # 上位バイトと下位バイトを組み合わせて16ビットの値にする
            red = (data[0] << 8) | data[1]
            green = (data[2] << 8) | data[3]
            blue = (data[4] << 8) | data[5]
            infrared = (data[6] << 8) | data[7]
            print([red,green,blue,infrared])

        except Exception as e:
            print(e)
            break

        time.sleep(1.0/FREQ)

    

if __name__=="__main__":
    main()
