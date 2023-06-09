import serial
import time
try:
    arduino = serial.Serial('/dev/ttyACM0')
except:
    arduino = serial.Serial('/dev/ttyACM1')
time.sleep(2)
cmd = "startf50b50"
arduino.write(str(cmd).encode())


