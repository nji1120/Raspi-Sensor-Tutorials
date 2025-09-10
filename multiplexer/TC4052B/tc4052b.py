from RPi import GPIO
GPIO.setmode(GPIO.BCM)
import pandas as pd


class AddressPin:
    """
    GPIOのwrapperクラス
    """
    def __init__(self, pin:int):
        self.pin=int(pin)
        GPIO.setup(self.pin, GPIO.OUT)
    
    def set_high(self):
        GPIO.output(self.pin, GPIO.HIGH)
    
    def set_low(self):
        GPIO.output(self.pin, GPIO.LOW)
    
    def __del__(self):
        GPIO.cleanup(self.pin)


class TC4052B:
    """
    TC4052Bを制御するクラス
    mappingテーブルを受け取って, 指定のchannelを開けるだけ
    """

    def __init__(self, mapping):
        """
        :param mapping: 
            columns: channel_name, gpio_pins (開けるチャンネル名とアドレス指定に使うgpioのピン番号)
            rows: ch0, LOW, HIGH, LOW, LOW,... (開けるチャンネル名と各GPIOのHIGH/LOW)

            ex)
            channel_name, 29, 31, 33, 35,
            'ch0', LOW, HIGH, LOW, LOW,
            'ch1', LOW, LOW, HIGH, LOW,
            ...
        """

        # gpioピン
        # これのset_high, set_lowをlistに格納して実行するだけ
        self.address_pins=[
            AddressPin(pin) for pin in mapping.columns[1:]
        ] 


