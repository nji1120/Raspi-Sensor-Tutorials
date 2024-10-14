"""
100Hzのサンプリング周波数でセンサ値を取ってくる
取れた生データは↓ここにぶち込んで、パワースペクトルを解析してみる
https://cattech-lab.com/science-tools/fft/
"""


# -*- coding:utf-8 -*-
import time
import spidev
import numpy as np
from pathlib import Path

Vref = 3.334  # 電圧をテスターで実測する

spi = spidev.SpiDev()

spi.open(0, 0)  # bus0,cs0
spi.max_speed_hz = 75000  # kHz 必ず指定する
spi.mode=0

def readAdc(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 200])
    data = ((adc[1] & 3) << 8) + adc[2]
    # print(f"responce : {adc}")
    return data

def convertVolts(data, vref):
    volts = (data * vref) / float(1023)
    return volts

if __name__ == '__main__':
    start_time=time.time()
    volt_trj=[]
    try:
        while True:
            if time.time()-start_time<5: #センサの安定化のために5秒間停止
                time.sleep(0.5)
                continue

            channel=0
            data = readAdc(channel=channel)
            volts = convertVolts(data, Vref)
            volt_trj.append(volts)
            print(volts)
            time.sleep(0.01)   

    except KeyboardInterrupt:
        spi.close()

    finally:
        with open(Path(__file__).parent/"sensor_values.txt","w") as f:
            for val in volt_trj:
                f.write(f"{val}\n")

