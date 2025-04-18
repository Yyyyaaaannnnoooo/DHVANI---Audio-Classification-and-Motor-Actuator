import numpy as np
import sounddevice as sd
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import audio
import time as tt
import concurrent.futures
import json
import random
import math
import serial
import datetime
# Parameters
fs = 44100.0  # Sample rate
sample_rate = 16000
channels = 16  # Mono audio
block_size = 256   # Number of samples per callback
device_index = 1  # Replace with your desired input device index
output_device = 1
NUM_CHANNELS = 4
MAX_TREND_LENGTH = 100
assignments = []
instruments = ["bells", "ghungroo", "wind", "gong"]
commands = {
    "bells": {
        "fw": {"positive": 10, "negative": 5},
        "bw": {"positive": 10, "negative": 5},
        "r": 4
    },
    "ghungroo": {
        "fw": {"positive": 10, "negative": 5},
        "bw": {"positive": 10, "negative": 5},
        "r": 3
    },
    "wind": {
        "fw": {"positive": 10, "negative": 5},
        "bw": {"positive": 10, "negative": 5},
        "r": 1
    },
    "gong": {
        "fw": {"positive": 10, "negative": 5},
        "bw": {"positive": 10, "negative": 5},
        "r": 5
    },
}
trends_initialized = True
trends = {}
scores = {}
for inst in instruments:
    trends[inst] = []
    scores[inst] = []
# print(trends)
classifiers = []
arduinos = []
arduinos_usb_paths = [
    {"path": '/dev/cu.usbmodem241101', "inst": "bells"},
    {"path": '/dev/cu.usbmodem241101', "inst": "bells"},
    {"path": '/dev/cu.usbmodem241101', "inst": "bells"},
    {"path": '/dev/cu.usbmodem241101', "inst": "bells"},
    {"path": '/dev/cu.usbmodem241301', "inst": "ghungroo"},
    {"path": '/dev/cu.usbmodem241201', "inst": "wind"},
    # {"path": '/dev/cu.usbmodem114202', "inst": "gong"},
]


arduino = 0

AudioClassifier = mp.tasks.audio.AudioClassifier
AudioClassifierOptions = mp.tasks.audio.AudioClassifierOptions
AudioClassifierResult = mp.tasks.audio.AudioClassifierResult
AudioRunningMode = mp.tasks.audio.RunningMode
BaseOptions = mp.tasks.BaseOptions

# Prepare the data
AudioData = mp.tasks.components.containers.AudioData
# Thread pool for processing multiple channels in parallel
executor = concurrent.futures.ThreadPoolExecutor(max_workers=NUM_CHANNELS)
# Device infos
device_info = sd.query_devices(device_index, 'input')
device_name = device_info['name']
print(sd.query_devices())
tt.sleep(2)
global_timestamp_ms = None


def send_command(inst, slope, arduino):
    # print(note)
    # note should be a value between 0 - 99
    # cmd = "startF"+str(note)+"B"+str(note)+"x"+str(repeats)
    fw = commands[inst]["fw"][slope]
    bw = commands[inst]["bw"][slope]
    repeat = commands[inst]["r"]
    cmd = "startF"+str(fw)+"B"+str(bw)+"x"+str(repeat)
    # print(cmd)
    # arduino.write(str(cmd).encode())


with open("./yamnet-assignments.json") as file:
    assignments = json.load(file)
print(assignments)


def analyze_trends():
    trend_index = 0
    result = []
    activate = True
    for key in trends:
        trend = trends[key]
        score = scores[key]
        positives = [val for val in trend if val > 0.0]
        positive_scores = [item for item in score if item["score"] > 0.0]
        print("?/?/?/?/?/?/?/?/?/?/?/?/?/")
        if len(trend) > 0:
            perc = len(positives) / len(trend)
            print(f"instrument {key} has {perc}% positives")
        # print(trend)
        # zeros = [val for val in trend if val == 0]
        # print(zeros)
        print(positive_scores)
        print("?/?/?/?/?/?/?/?/?/?/?/?/?/")
        # print(positives)
        if len(positives) < 1:
            activate = False
        if len(trend) < 2:
            print("not enough data to determine trend")
            return False
        else:
            y = trend
            x = np.arange(len(y))
            slope, intercept = np.polyfit(x, y, 1)
            result.append({"slope": slope, "intercept": intercept,
                          "inst": key, "activate": activate})
        trend_index += 1
    return result


def actuate_motors(time):
    print('activate motors at: ', time)
    analysis = analyze_trends()
    if not analysis:
        print("stop analysis from motor actuation")
        return
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    # print(analysis)
    for value in analysis:
        inst = value["inst"]
        activate = value["activate"]
        print("activate arduino for intrument: "+inst+" " + str(activate))
        if activate == False:
            print("skip to next instrument")
            continue
        slope = value["slope"]
        print(f"slope for instrument {inst} = {slope}")
        # print(value["inst"])
        # print(value["slope"])
        # print(value["activate"])
        this_arduinos = [item["arduino"]
                         for item in arduinos if item["inst"] == inst]
        paths = [item["path"] for item in arduinos if item["inst"] == inst]
        # print(paths)
        # for arduino_path in paths:
        #     print(f"actuating motor for {inst} at arduino {arduino_path}")

        for this_arduino in this_arduinos:
            if slope > 0:
                # print("positive slope")
                # send_command(80, this_arduino)
                send_command(inst, "positive", this_arduino)
            else:
                # print("negative slope")
                # send_command(20, this_arduino)
                send_command(inst, "negative", this_arduino)

    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    # loop_length = len(arduinos_usb_paths)
    # print(loop_length)
    # for i in range(loop_length):
    #     slope = analysis[i]["slope"]
    #     print(slope)
    #     print(f"activate arduino number: {i} at {arduinos_usb_paths[i]}")
    #     if slope > 0:
    #         print("positive slope")
    #         send_command(80, arduinos[i])
    #     else:
    #         print("negative slope")
    #         send_command(20, arduinos[i])

    # form the analysis the commands should be sent to the various arduinos


def trim_array(arr):
    if len(arr) > MAX_TREND_LENGTH:
        to_remove = MAX_TREND_LENGTH - len(arr)
        arr = arr[-(MAX_TREND_LENGTH):]
    return arr


def update_trends(val, index):
    key = instruments[index]
    # trends[key].append(val)
    # trends[key].concat(val)
    trends[key] = trends[key] + val
    trends[key] = trim_array(trends[key])
    # print(trends)


def update_scores(val, index):
    key = instruments[index]
    # trends[key].append(val)
    # trends[key].concat(val)
    scores[key] = scores[key] + val
    scores[key] = trim_array(scores[key])
    # print(trends)


def get_values(assignment, categories, index):
    total = 0
    # obj = {""}
    result = []
    score = []
    for category in categories:
        for name in assignment:
            if category.category_name == name and category.score >= 0:
                # print(name)
                # print(category.category_name)
                # print(category.score)
                total += category.score
                # obj[name] = category.score
                obj = {"name": name, "score": category.score}
                score.append(obj)
                result.append(category.score)
    # print("###################")
    # print("reults")
    # print(score)
    # print("###################")
    # update_trends(total, index)
    update_trends(result, index)
    update_scores(score, index)


def analyze_results(arr, index):
    # print(index)
    # print(instruments[index])
    instrument = instruments[index]
    assignment = assignments[instrument]
    categories = arr.categories
    get_values(assignment, categories, index)


def classify_audio(
    result: AudioClassifierResult,
    timestamp_ms: int,
    channel_index: int
):
    # print('AudioClassifierResult result: {}'.format(result))
    # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    # print(f'Timestamp: {timestamp_ms} ms')
    # print(f'Audio Channel: {channel_index + 1}')

    for classification in result.classifications:
        # print(classification)
        analyze_results(classification, channel_index)
    # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


def create_classifier(channel_index):
    """Creates a classifier that includes channel information."""
    def result_callback(result, timestamp_ms):
        # Pass the channel index
        classify_audio(result, timestamp_ms, channel_index)
    options = AudioClassifierOptions(
        base_options=BaseOptions(model_asset_path='./yamnet.tflite'),
        running_mode=AudioRunningMode.AUDIO_STREAM,
        max_results=-1,
        result_callback=result_callback)
    return AudioClassifier.create_from_options(options)


def init_classifiers():
    for i in range(NUM_CHANNELS):
        print(f"creating classifier number: {i}")
        classifiers.append(create_classifier(i))


def check_trends():
    global trends_initialized
    initialized_index = 0
    count = sum(len(trend) for trend in trends)
    print("initializing trends: "+str((count/4)*100)+"%")
    for trend in trends:
        if len(trend) >= 2:
            initialized_index += 1
    if initialized_index >= 4:
        print("trends initialized")
        trends_initialized = True


# Send live audio data to perform audio classification.
# Results are sent to the `result_callback` provided in the `AudioClassifierOptions`
def process_channel(channel_index, audio_chunk, timestamp_ms):
    """Process and classify a single audio channel in a separate thread."""
    # print(f"Processing Channel {channel_index + 1} at {timestamp_ms} ms")
    # Convert to float32 (required by MediaPipe)
    audio_data_np = np.array(audio_chunk, dtype=np.float32).copy()
    # Create AudioData instance
    mp_audio_data = AudioData.create_from_array(
        audio_data_np, sample_rate=16000)
    # Run classification asynchronously
    classifiers[channel_index].classify_async(mp_audio_data, timestamp_ms)


# Callback function to process audio in real-time
def audio_callback(indata, frames, time, status):
    global global_timestamp_ms
    if status:
        print(status, flush=True)  # Handle errors
    # Get the correct timestamp
    if global_timestamp_ms is None:
        # Use system time for the first timestamp
        global_timestamp_ms = int(tt.time() * 1000)
    else:
        # Increment by frame duration
        global_timestamp_ms += (frames / 16000) * 1000
    timestamp_ms = int(global_timestamp_ms)
    # Launch parallel classification for each channel
    for ch in range(NUM_CHANNELS):
        executor.submit(process_channel, ch, indata[:, ch], timestamp_ms)
    # analyze_trends()
    # print(trends_initialized)
    if trends_initialized == False:
        check_trends()

    tt.sleep(0.2)

# Open a stream with the selected device


def start_stream():
    with sd.InputStream(samplerate=sample_rate, channels=channels, callback=audio_callback, blocksize=block_size, device=device_index):
        print(f"🎤 Listening to: {device_name}")
        # print("Streaming from device:", device_index)
        print("Press Ctrl+C to stop.")
        next_call_time = tt.monotonic()  # Get the current time
        interval = random.uniform(1, 5)  # Initial random interval

        last_trigger_time = datetime.datetime.now()
        try:
            while True:
                if trends_initialized:
                    # current_time = tt.monotonic()
                    current_time = datetime.datetime.now()
                    elapsed = (current_time - last_trigger_time).total_seconds()
                    # Check if it's time to run the function
                    if elapsed >= 2:
                        actuate_motors(current_time)
                        last_trigger_time = current_time

        # try:
        #     while True:
        #         if trends_initialized:
        #             current_time = tt.monotonic()
        #             # Check if it's time to run the function
        #             if current_time >= next_call_time:
        #                 actuate_motors(next_call_time)
        #                 # Update interval dynamically
        #                 interval = math.floor(random.uniform(8, 10))
        #                 interval = 2
        #                 print(f"next execution in {interval} seconds")
        #                 next_call_time = current_time + interval  # Set next execution time
        #         # tt.sleep(0.9)
                pass  # Keep the stream open
        except KeyboardInterrupt:
            print('stpped!')


def connect_arduinos():
    global arduinos
    # global arduino
    try:
        # arduino = serial.Serial('/dev/ttyACM0')
        # arduino = serial.Serial('/dev/tty.usbmodem111301')
        for usb in arduinos_usb_paths:
            print(usb["path"])
            # arduino = serial.Serial(usb["path"])
            print('connected to arduino: ' + usb["path"])
            tt.sleep(2)
            obj = {"arduino": "arduino",
                   "inst": usb["inst"], "path": usb["path"]}
            arduinos.append(obj)
            # send_command(50, arduino)
        arduino_connected = True
        print(arduinos)
    except:
        # arduino = serial.Serial('/dev/ttyACM1')
        print('connection failed')


init_classifiers()
connect_arduinos()
start_stream()
