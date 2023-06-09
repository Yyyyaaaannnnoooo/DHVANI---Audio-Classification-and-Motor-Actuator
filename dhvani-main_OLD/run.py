from flask import Flask,render_template, redirect, url_for, request, jsonify
import flask
from loguru import logger
from tinydb import TinyDB, Query
from flask_socketio import SocketIO
import socket
import random
import time
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, Length
import serial
import time
import os 
import threading


try:
    arduino = serial.Serial('/dev/ttyACM0')
    print('connected to arduino')
except:
    arduino = serial.Serial('/dev/ttyACM1')

time.sleep(2)


app = Flask(__name__, static_folder="static")

db = TinyDB('db.json')
query = Query()

# Web Socket
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


# Variables
delay_between_notes = 2

bell_1 = {
        "count": 0,
        "silent": True,
        "bell_ringing": False
        }

bell_2 = {
        "count": 0,
        "silent": True,
        "bell_ringing": False
        }

bell_3 = {
        "count": 0,
        "silent": True,
        "bell_ringing": False
        }

bell_4 = {
        "count": 0,
        "silent": True,
        "bell_ringing": False
        }


state_dict = {'ringing': False}

def random_notes_generator_single(speed_limit_max = 10,
                                  speed_limit_min = 99,
                                  no_of_notes = 1
                                  ):
    
    l = [(random.randrange(int(speed_limit_min), int(speed_limit_max))) for i in range(int(no_of_notes))]
    return l


def random_notes_generator(no_of_motors = 4,
                           speed_limit_max = 10,
                           speed_limit_min = 99,
                           no_of_notes = 3
                           ):
    # no_of_motors = 4
    # speed_limit_max = 100
    # speed_limit_min = 20
    # no_of_notes = 3

    l = [(random.randrange(0, no_of_motors), random.randrange(int(speed_limit_min), int(speed_limit_max))) for i in range(int(no_of_notes))]

    list_of_notes = []
 
    for note_tuple in l:
        note_dict = {0:'000',
                    1:'000',
                    2:'000',
                    3:'000'}

        motor_no, motor_speed = note_tuple
        note_dict[motor_no] = f'{motor_speed:03}'

        final_signal = {'device1': f'{note_dict[0]}{note_dict[1]}',  'device2': f'{note_dict[2]}{note_dict[3]}'}
        list_of_notes.append(final_signal)
    
    return list_of_notes


def dict_maker(var_dict):
    data_dict = db.search(query.project == "dhvwani")
    data_dict = data_dict[0]

    for key in data_dict.keys():
        var_dict[key] = data_dict[key]

    # logger.debug(var_dict)

    return var_dict




@socketio.on('connect')
def test_connect(auth):
    logger.debug("User has connected!")

'''
here the python code handles the 
message passed from javascript
'''

@socketio.on('message')
def handle_message(data):
    # HERE THE CODE SHOULD READ WHEN THE ROBOTIC ARM IS DONE WITH ITS ACTIONS
    # print("received data")
    # try:
    # except:
    #     print("no message")
    # serial_read = arduino.readline()
    # decoded = str(serial_read[0:len(serial_read)-2].decode("utf-8"))
    # print(decoded)
    var_dict = {}
    var_dict = dict_maker(var_dict)


    #New Code

    # data type() is "dict" that's why::

    # data variable replace with sound_type

    # logger.debug(data)

    sound_type = data["sound_type"]
    accuracy = data["accuracy"]



    trigger_dict = {
        var_dict["sound_type_1"] : {
            "speed_limit_max" : var_dict["speed_limit_max_1"],
            "speed_limit_min" : var_dict["speed_limit_min_1"],
            "no_of_notes" : var_dict["no_of_notes_1"],
            "delay_between_notes" : var_dict["delay_between_notes_1"],
            "accuracy_range" : float(var_dict["accuracy_range_1"])/100
        },
         var_dict["sound_type_2"] : {
            "speed_limit_max" : var_dict["speed_limit_max_2"],
            "speed_limit_min" :  var_dict["speed_limit_min_2"],
            "no_of_notes" : var_dict["no_of_notes_2"],
            "delay_between_notes" : var_dict["delay_between_notes_2"],
            "accuracy_range" : float(var_dict["accuracy_range_2"])/100
        },
         var_dict["sound_type_3"] : {
            "speed_limit_max" : var_dict["speed_limit_max_3"],
            "speed_limit_min" : var_dict["speed_limit_min_3"],
            "no_of_notes" : var_dict["no_of_notes_3"],
            "delay_between_notes" : var_dict["delay_between_notes_3"],
            "accuracy_range" : float(var_dict["accuracy_range_3"])/100
        },
         var_dict["sound_type_4"] : {
            "speed_limit_max" : var_dict["speed_limit_max_4"],
            "speed_limit_min" : var_dict["speed_limit_min_4"],
            "no_of_notes" : var_dict["no_of_notes_4"],
            "delay_between_notes" : var_dict["delay_between_notes_4"],
            "accuracy_range" : float(var_dict["accuracy_range_4"])/100
        }
    }

    # Command Sender to Motor
    
    params = trigger_dict.get(sound_type)

    if state_dict["ringing"] == False and sound_type != "Background Noise" and accuracy >= params["accuracy_range"]: # add accuracy threshold + threshold in database
        # logger.debug(params["accuracy_range"])
        
        # print("Device Activate",end="\r")
        # UDP Socket
        # logger.debug(var_dict)

        # client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # client_addr_d1 = (var_dict["device1_ip"], int(var_dict["device1_port"]))
        # client_addr_d2 = (var_dict["device2_ip"], int(var_dict["device2_port"]))
        # bell1_data = f"{var_dict['device1_m1_speed']}{000}".encode("utf-8")
        
        # notes_to_play = random_notes_generator(4,
        #                                         params["speed_limit_max"],

        #                                         params["speed_limit_min"],

        #                                         params["no_of_notes"])

        notes_to_play = random_notes_generator_single(params["speed_limit_max"],
                                                      params["speed_limit_min"],
                                                      params["no_of_notes"])
        state_dict['ringing'] = True
        # this is important to prevent overflowing the read/write buffer
        # arduino.flushInput()
        for note in notes_to_play:
            # logger.debug(note)
            logger.debug("motor activate")
            cmd = "startf"+str(note)+"b"+str(note)
            logger.debug(cmd)
            arduino.write(str(cmd).encode())

            # final_note_d1 = note["device1"].encode("utf-8")
            # final_note_d2 = note["device2"].encode("utf-8")
            # client_socket.sendto(final_note_d1,client_addr_d1)
            # client_socket.sendto(final_note_d2,client_addr_d2)
            time.sleep(delay_between_notes)
 
        state_dict['ringing'] = False
    else:
        pass



class MyForm(FlaskForm):
    speed_min = IntegerField('speed_min', validators=[DataRequired()])
    speed_max = IntegerField('speed_max', validators=[DataRequired()])
    delay = IntegerField('delay', validators=[DataRequired()])
    length = IntegerField('length', validators=[DataRequired()])

@app.route('/note_test', methods=['GET','POST'])
def note_test():
    form = MyForm()
    if request.method == 'POST' and form.validate():
        print(form.speed_min.data)
        print(form.speed_max.data)
        print(form.delay.data)
        print(form.length.data)

        notes_to_play = random_notes_generator(no_of_motors = 4,
                                                speed_limit_max = form.speed_max.data,
                                                speed_limit_min = form.speed_min.data,
                                                no_of_notes = form.length.data)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        var_dict = {}
        var_dict = dict_maker(var_dict)

        client_addr_d1 = (var_dict["device1_ip"], int(var_dict["device1_port"]))
        client_addr_d2 = (var_dict["device2_ip"], int(var_dict["device2_port"]))
        state_dict['ringing'] = True

        for note in notes_to_play:
            # logger.debug(note)
            final_note_d1 = note["device1"].encode("utf-8")
            final_note_d2 = note["device2"].encode("utf-8")
            client_socket.sendto(final_note_d1,client_addr_d1)
            client_socket.sendto(final_note_d2,client_addr_d2)
            time.sleep(form.delay.data)
        return render_template('note_test.html', form=form)
    return render_template('note_test.html', form=form)

#**********************************************************************************************************
@app.route('/testing/<device_name>',methods=['GET','POST'])
def Testing(device_name):
    # logger.debug(device_name)
    var_dict = {}
    var_dict = dict_maker(var_dict)

    if device_name == "device1":
        host = var_dict["device1_ip"]
        port = 8888
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_addr = (host, port)

        bell1_data = f"{var_dict['device1_m1_speed']}{var_dict['device1_m2_speed']}".encode("utf-8")
        logger.debug(bell1_data)
        client_socket.sendto(bell1_data,client_addr)
        # notes_to_play = random_notes_generator()
        # for note in notes_to_play:
        #     logger.debug(note)
        #     final_note = note["device1"].encode("utf-8")
        #     client_socket.sendto(final_note,client_addr)
        #     time.sleep(1)
        
    if device_name == "device2":
        host = var_dict["device2_ip"]
        port = 8887
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_addr = (host, port)
        bell2_data = f"{var_dict['device2_m1_speed']}{var_dict['device2_m2_speed']}".encode("utf-8")
        logger.debug(bell2_data)
        client_socket.sendto(bell2_data,client_addr)



    return render_template('settings.html',var_dict=var_dict)


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@app.route('/',methods=['GET','POST'])
def Main():
    return render_template('Main_page.html')
    # return render_template('../static/js/mediapipe/index.html')

            


@app.route('/settings',methods=['POST','GET'])
def Settings():
    var_dict = {}

    if request.method == "POST":
        var_list=[
                    "device1_ip",
                    "device2_ip",
                    "device1_port",
                    "device2_port",

                    # Bell
                    "sound_type_1",
                    "speed_limit_max_1",
                    "speed_limit_min_1",
                    "no_of_notes_1",
                    "delay_between_notes_1",
                    "accuracy_range_1",

                    # Clap
                    "sound_type_2",
                    "speed_limit_max_2",
                    "speed_limit_min_2",
                    "no_of_notes_2",
                    "delay_between_notes_2",
                    "accuracy_range_2",

                    # Voice
                    "sound_type_3",
                    "speed_limit_max_3",
                    "speed_limit_min_3",
                    "no_of_notes_3",
                    "delay_between_notes_3", 
                    "accuracy_range_3",

                    # Footstep
                    "sound_type_4",
                    "speed_limit_max_4",
                    "speed_limit_min_4",
                    "no_of_notes_4",
                    "delay_between_notes_4",
                    "accuracy_range_4"
                    
              

                    ]

        for form_var in var_list:
            var_dict[form_var] = request.form.get(form_var)

        # logger.debug(var_dict)



        # Save in database

        db.update(var_dict, query.project == "dhvwani")


        # logger.debug("data save successfully")

        return render_template('dhvwani_settings.html',var_dict=var_dict)


    # showing data to settings.html at loading time
         
    var_dict = dict_maker(var_dict)
    # logger.debug(var_dict)


    return render_template('dhvwani_settings.html',var_dict=var_dict)
            
def myfunction():
    os.system("chromium-browser http://127.0.0.1:5000/")
    
t1 = threading.Thread(target=myfunction)
t1.start()    


if __name__ == '__main__':
    # app.run(debug=True)
    socketio.run(app)
