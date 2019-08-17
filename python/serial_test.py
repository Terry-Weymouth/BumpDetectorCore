import serial
from datetime import datetime
ser = serial.Serial('/dev/ttyUSB0',9600)
bytes_second = 0
lines = 0
start = datetime.now()
while True:
    line=ser.readline()
    line = line.strip()
    if line:
        print(line)
