import serial
import time
import random

print('testing')
# CONNECT ARDUINOS

def send_command(note, arduino):
  # note should be a value between 0 - 255
  cmd = "startF"+str(note)+"B"+str(note)
  print(cmd)
  arduino.write(str(cmd).encode())

try:
    # arduino = serial.Serial('/dev/ttyACM0')
    # arduino = serial.Serial('/dev/tty.usbmodem111301')
    arduino = serial.Serial('/dev/cu.usbmodem1301')
    print('connected to arduino')
    # arduino_connected = True
    time.sleep(2)
    send_command(50, arduino)
    last_command_time = time.time()
except:
    # arduino = serial.Serial('/dev/ttyACM1')
    print('connection failed')


# Read messages from Arduino
try:
    while True:
        if arduino.in_waiting > 0:  # Check if data is available
            line = arduino.readline().decode('utf-8').strip()  # Read and decode
            print("Arduino says:", line)
        
        # Check if 5 seconds have passed
        if time.time() - last_command_time >= 10:
            rand = random.randint(70, 99)
            send_command(rand, arduino)  # Example command to send every 5 seconds
            print("Sent command 200")
            last_command_time = time.time()  # Reset timer

except KeyboardInterrupt:
    print("Closing connection")
    arduino.close()