from socket import socket, AF_INET,SOCK_DGRAM
import time


FREQENCY=10 #Hz 1000Hzが限界

PORT=5000
CLIENT="192.168.1.3"
sock=socket(AF_INET,SOCK_DGRAM)
sock.bind(("",PORT))
count=1
while True:
    start_time=time.time_ns()
    try:
        msg:str=str(count)
        sock.sendto(msg.encode("utf-8"),(CLIENT,PORT))
        print(msg)
    except KeyboardInterrupt:
        sock.close()
        break
    count+=1
    
    time.sleep(1.0/FREQENCY)

    # print((time.time_ns()-start_time)*10**-9," s")
