import serial

# Parts of the code, copy modified from:
#   | http://www.danmandle.com/blog/getting-gpsd-to-work-with-python/
#   | Written by Dan Mandle http://dan.mandle.me September 2012
#   | License: GPL 2.0
 
from gps import *
from time import *
import time
import threading
 
gpsd = None #seting the global variable
 
class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true
 
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer
 
if __name__ == '__main__':
  gpsp = GpsPoller() # create the thread
  try:
    gpsp.start() # start it up
    ser = serial.Serial('/dev/ttyUSB0',9600)
    with open('somefile.txt', 'a') as the_file:
        while True:
            line = ser.readline()
            line = "".join( ch for ch in line)
            if not line:
                continue
            line = line.strip()
            if not line:
                continue
            parts = line.split(":")
            seqNumber = parts[0].strip()
            value = parts[1].split(",")
            if not len(value) == 6:
                print("bad line: ", seqNumber)
                continue
            more_line = "{},{},{},{},{}".format(
                gpsd.utc,
                gpsd.fix.latitude,
                gpsd.fix.longitude,
                gpsd.fix.altitude,
                gpsd.fix.speed)
            line = "{}:{},{}".format(seqNumber, parts[1], more_line)
            the_file.write(line)
            the_file.write("\n")
            the_file.flush()
 
  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print "\nKilling Thread..."
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doing
  print "Done.\nExiting."
