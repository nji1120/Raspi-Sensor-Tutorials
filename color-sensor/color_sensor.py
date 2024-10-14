from smbus2 import SMBus

class ColorSensor():

    BUS_NUM=1 #バス番号. 基本は1
    I2C_BUS=SMBus(BUS_NUM) #クラスで共通のバスを使う

    def __init__(self,is_switch=False,switch_addr=None,switch_channel=None,sensor_addr=0x2a) -> None:
        """
        :param is_switch: マルチプレクサを使うかどうか
        :param switch_addr: マルチプレクサのアドレス
        :param switch_channel: マルチプレクサのチャンネル. 0b00000001とか
        :param sensor_addr: カラーセンサのアドレス [S11059 0x2a]
        """
        
        self.is_switch=is_switch
        self.switch_addr=switch_addr
        self.switch_channel=switch_channel
        self.sensor_addr=sensor_addr

        self.__selsect_channel()

        # >> センサのスリープ解除と設定変更 >>
        ColorSensor.I2C_BUS.write_byte_data(
            self.sensor_addr,
            register=0x00,
            value=0x80
        )
        ColorSensor.I2C_BUS.write_byte_data(
            self.sensor_addr,
            register=0x00,
            value=0x0b
        )
        # << センサのスリープ解除と設定変更 <<

    def __selsect_channel(self):
        if self.is_switch:
            ColorSensor.I2C_BUS.write_byte_data(
                i2c_addr=self.switch_addr,
                register=0x00, #ここはこれでいいか分からん
                value=self.switch_channel
            )
            print(f"select channel {self.switch_channel} complete")

    def read(self):
        self.__selsect_channel()
        data=ColorSensor.I2C_BUS.read_i2c_block_data(
            self.sensor_addr,
            register=0x03,
            length=8
        )

        rgbi_a=[117.0,85.0,44.8,30.0] #センサのカウントとルクスの係数
        rgbi_key=["R","G","B","IR"]
        rgbi={}
        for i in range(4):
            rgbi[rgbi_key[i]]=int(((data[2*i]<<8)+data[2*i+1])/rgbi_a[i]) #センサ値をルクスに変換

        return rgbi

if __name__=="__main__":
    import time

    # color_sensor=ColorSensor()

    # I2Cアドレス70のマルチプレクサ channel1にカラーセンサを接続
    color_sensor=ColorSensor(
        is_switch=True,
        switch_addr=0x71,
        switch_channel=0b00000001,
        sensor_addr=0x2a
    )

    idx=0
    while True:
        try:
            print(idx,color_sensor.read())
        except Exception as e:
            print(e)
            break
        time.sleep(0.5)
        idx+=1
