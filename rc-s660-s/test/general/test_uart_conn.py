import serial

port="/dev/ttyAMA0"
baudrate=115200

uartport=serial.Serial(
    port=port,
    baudrate=baudrate,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

if uartport.isOpen():
    print("Serial port is open")
else:
    print("Serial port is not open")