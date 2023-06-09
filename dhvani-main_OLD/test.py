import serial
import time

try:
    arduino = serial.Serial('/dev/cu.usbmodem21101')
except:
    arduino = serial.Serial('/dev/cu.usbmodem21101')
time.sleep(2)
note = "startf50b50"
arduino.write(str(note).encode())