import serial

print('testing')

try:
    # arduino = serial.Serial('/dev/ttyACM0')
    # arduino = serial.Serial('/dev/tty.usbmodem111301')
    arduino = serial.Serial('/dev/cu.usbmodem11301')
    print('connected to arduino')
except:
    # arduino = serial.Serial('/dev/ttyACM1')
    print('connection failed')