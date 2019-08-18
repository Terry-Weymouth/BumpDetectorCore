import serial
# Note for version one - using USB connection
# device = '/dev/ttyUSB0'
baud = 9600
device = '/dev/ttys0'
ser = serial.Serial(device,9600)
while True:
    line=ser.readline()
    line = line.strip()
    if line:
        print(line)
