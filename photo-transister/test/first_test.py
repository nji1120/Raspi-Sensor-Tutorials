# -*- coding:utf-8 -*-
import time
import spidev
import numpy as np

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
    try:
        while True:
            channel=0
            data = readAdc(channel=channel)
            volts = convertVolts(data, Vref)
            print(f"CH{channel} volts: {volts:.2f}")

            time.sleep(0.3)

    except KeyboardInterrupt:
        spi.close()