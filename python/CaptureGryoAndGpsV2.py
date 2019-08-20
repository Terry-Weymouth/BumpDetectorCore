"""
    Parts of the code, copy modified from:
        http://www.danmandle.com/blog/getting-gpsd-to-work-with-python/
        Written by Dan Mandle http://dan.mandle.me September 2012
        License: GPL 2.0
    and from:
        Read Gyro and Accelerometer by Interfacing Raspberry Pi with MPU6050 using Python
        http://www.electronicwings.com
        see: https://www.electronicwings.com/raspberry-pi/mpu6050-accelerometergyroscope-interfacing-with-raspberry-pi
"""

from gps import *
import smbus  # import SMBus module of I2C
from time import sleep  # import
import threading
from datetime import datetime

gpsd = None  # setting the global variable

# some MPU6050 Registers and their Address
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47


class GyroAndAcc:
    def __init__(self):
        self.bus = smbus.SMBus(1)  # or bus = smbus.SMBus(0) for older version boards
        self.device_address = 0x68  # MPU6050 device address

        # write to sample rate register
        self.bus.write_byte_data(self.device_address, SMPLRT_DIV, 7)
        # Write to power management register
        self.bus.write_byte_data(self.device_address, PWR_MGMT_1, 1)
        # Write to Configuration register
        self.bus.write_byte_data(self.device_address, CONFIG, 0)
        # Write to Gyro configuration register
        self.bus.write_byte_data(self.device_address, GYRO_CONFIG, 24)
        # Write to interrupt enable register
        self.bus.write_byte_data(self.device_address, INT_ENABLE, 1)

        # Initialise output values
        self.acc_x = 0
        self.acc_y = 0
        self.acc_z = 0
        self.gyro_x = 0
        self.gyro_y = 0
        self.gyro_z = 0

    def read_raw_data(self, addr):
        # Accelero and Gyro value are 16-bit
        high = self.bus.read_byte_data(self.device_address, addr)
        low = self.bus.read_byte_data(self.device_address, addr + 1)

        # concatenate higher and lower value
        value = ((high << 8) | low)

        # to get signed value from mpu6050
        if value > 32768:
            value = value - 65536
        return value

    def update_values(self):
        # Read Accelerometer raw value
        self.acc_x = self.read_raw_data(ACCEL_XOUT_H)
        self.acc_y = self.read_raw_data(ACCEL_YOUT_H)
        self.acc_z = self.read_raw_data(ACCEL_ZOUT_H)

        # Read Gyroscope raw value
        self.gyro_x = self.read_raw_data(GYRO_XOUT_H)
        self.gyro_y = self.read_raw_data(GYRO_YOUT_H)
        self.gyro_z = self.read_raw_data(GYRO_ZOUT_H)

        # Full scale range +/- 250 degree/C as per sensitivity scale factor
        self.acc_x = self.acc_x / 16384.0
        self.acc_y = self.acc_y / 16384.0
        self.acc_z = self.acc_z / 16384.0

        self.gyro_x = self.gyro_x / 131.0
        self.gyro_y = self.gyro_y / 131.0
        self.gyro_z = self.gyro_z / 131.0

    def get_formatted_output(self):
        self.update_values()
        return "{},{},{},{},{},{}".format(
            self.gyro_x, self.gyro_y, self.gyro_z, self.acc_x, self.acc_y, self.acc_z
        )


class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd  # bring it in scope
        gpsd = gps(mode=WATCH_ENABLE)  # starting the stream of info
        self.current_value = None
        self.running = True  # setting the thread running to true

    def run(self):
        global gpsd
        while gpsp.running:
            gpsd.next()  # this will continue to loop and grab EACH set of gpsd info to clear the buffer


if __name__ == '__main__':
    gpsp = GpsPoller()  # create the thread
    gyro_acc = GyroAndAcc()
    seqNumber = 0
    filename = datetime.now().strftime("RunData_%Y%m%d_%H%M%S.txt")
    try:
        gpsp.start()  # start it up
        with open(filename, 'a') as the_file:
            while True:
                seqNumber = seqNumber + 1
                line = gyro_acc.get_formatted_output()
                more_line = "{},{},{},{},{}".format(
                    gpsd.utc,
                    gpsd.fix.latitude,
                    gpsd.fix.longitude,
                    gpsd.fix.altitude,
                    gpsd.fix.speed)
                line = "V2-{}:{},{}".format(seqNumber, line, more_line)
                the_file.write(line)
                the_file.write("\n")
                the_file.flush()
                sleep(0.1)

    except (KeyboardInterrupt, SystemExit):  # when you press ctrl+c
        print("\nKilling Thread...")
        gpsp.running = False
        gpsp.join()  # wait for the thread to finish what it's doing
    print("Done.\nExiting.")
