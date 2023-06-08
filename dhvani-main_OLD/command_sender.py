#pip simple_websocket_server
from simple_websocket_server import WebSocketServer, WebSocket
import serial
import time

port = "/dev/ttyACM0"
arduino = serial.Serial()
arduino.baudrate = 9600
arduino.port = port
arduino.open()

bell = {
        "count": 0,
        "silent": True,
        "bell_ringing": False,
        "motor_speed": 160
    }

class SimpleEcho(WebSocket):
    def handle(self):
        # echo message back to client
        if self.data == "nothing":
            bell["count"] = 0
            print(" "*50,end="\r")
            print("Backgound Noise",end="\r")
            bell["silent"] = True
            bell["bell_ringing"] = False
        else:
            print(" "*50,end="\r")
            print("Bell Sound",end="\r")
            bell["count"] += 1
            bell["silent"]=False

        if bell['count'] > 1 and bell["silent"]==False and bell["bell_ringing"] == False:
            print(" "*50,end="\r")
            print("Motor Rotating...",end="\r")
            self.rotate_motor()

            bell['count'] = 0
            bell["bell_ringing"]=True


    def motor_stop(self):
        print("Motor Stop")



    def rotate_motor(self):
        arduino.write(bytes(str(bell['motor_speed']), 'utf-8'))

       


    def connected(self):
        print(self.address, 'connected',end="\r")

    def handle_close(self):
        print(self.address, 'closed',end="\r")



server = WebSocketServer('', 8000, SimpleEcho)
server.serve_forever()

