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

# Parameters
fs = 44100.0  # Sample rate
sample_rate = 16000
channels = 16  # Mono audio
block_size = 256  # Number of samples per callback
device_index = 0  # Replace with your desired input device index
output_device = 1
NUM_CHANNELS = 6
MAX_TREND_LENGTH = 50
assignments = []
instruments = ["ghungroo", "ghungroo", "bells","bells", "wind", "wind"]
trends_initialized = False
trends = [[],[],[],[],[],[]]
classifiers = []
arduinos = []
arduinos_usb_paths = [
  '/dev/cu.usbmodem11301',
  '/dev/cu.usbmodem11101',
  '/dev/cu.usbmodem11201',
  '/dev/cu.usbmodem114301',
  '/dev/cu.usbmodem114101',
]

arduino = 0

AudioClassifier = mp.tasks.audio.AudioClassifier
AudioClassifierOptions = mp.tasks.audio.AudioClassifierOptions
AudioClassifierResult = mp.tasks.audio.AudioClassifierResult
AudioRunningMode = mp.tasks.audio.RunningMode
BaseOptions = mp.tasks.BaseOptions

### Prepare the data
AudioData = mp.tasks.components.containers.AudioData
# Thread pool for processing multiple channels in parallel
executor = concurrent.futures.ThreadPoolExecutor(max_workers=NUM_CHANNELS)
# Device infos
device_info = sd.query_devices(device_index, 'input')
device_name = device_info['name']

global_timestamp_ms = None


def send_command(note, arduino):
  print(note)
  # note should be a value between 0 - 99
  cmd = "startF"+str(note)+"B"+str(note)
  print(cmd)
  arduino.write(str(cmd).encode())


with open("./yamnet-assignments.json") as file:
  assignments = json.load(file)




def analyze_trends():
  trend_index = 0
  result = []
  for trend in trends:
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    if len(trend) < 2:
      print("not enough data to determine trend")
    else:
      y = trend
      x = np.arange(len(y))
      slope, intercept = np.polyfit(x, y, 1)
      print(instruments[trend_index])
      print("Slope:", slope) 
      print("Intercept:", intercept)
      print("list length: ", len(trend))
      result.append({"slope": slope, "intercept": intercept})
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    trend_index += 1
  return result

def actuate_motors(time):
    print('activate motors at: ', time)
    analysis = analyze_trends()
    # print(analysis)
    loop_length = len(arduinos_usb_paths)
    # print(loop_length)
    for i in range(loop_length):
      slope = analysis[i]["slope"]
      print(slope)
      print(f"activate arduino number: {i} at {arduinos_usb_paths[i]}")
      if slope > 0:
        print("positive slope")
        send_command(80, arduinos[i])
      else:
        print("negative slope")
        send_command(20, arduinos[i])
      
    # form the analysis the commands should be sent to the various arduinos



def trim_array(arr):
    if len(arr) > MAX_TREND_LENGTH:
        arr.pop(0)  # Remove the first element
    return arr

def update_trends(val, index):
  trends[index].append(val)
  trends[index] = trim_array(trends[index])

def get_values(assignment, categories, index):
  total = 0
  for category in categories:
    for name in assignment:
      if category.category_name == name and category.score > 0:
        # print(name)
        # print(category.score)
        total += category.score
  update_trends(total, index)

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
      analyze_results(classification, channel_index)
    # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
      

def create_classifier(channel_index):
    """Creates a classifier that includes channel information."""
    def result_callback(result, timestamp_ms):
        classify_audio(result, timestamp_ms, channel_index)  # Pass the channel index
    options = AudioClassifierOptions(
      base_options=BaseOptions(model_asset_path='./yamnet.tflite'),
      running_mode=AudioRunningMode.AUDIO_STREAM,
      # max_results=5,
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
  print("initializing trends: "+str((count/12)*100)+"%")
  for trend in trends:
    if len(trend) >= 2:
      initialized_index+=1
  if initialized_index >= 6:
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
  mp_audio_data = AudioData.create_from_array(audio_data_np, sample_rate=16000)
  # Run classification asynchronously
  classifiers[channel_index].classify_async(mp_audio_data, timestamp_ms)


# Callback function to process audio in real-time
def audio_callback(indata, frames, time, status):
  global global_timestamp_ms
  if status:
      print(status, flush=True)  # Handle errors
  # Get the correct timestamp
  if global_timestamp_ms is None:
      global_timestamp_ms = int(tt.time() * 1000)  # Use system time for the first timestamp
  else:
      global_timestamp_ms += (frames / 16000) * 1000  # Increment by frame duration
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
def start_stream ():
  with sd.InputStream(samplerate=sample_rate, channels=channels, callback=audio_callback, blocksize=block_size, device=device_index):
      print(f"🎤 Listening to: {device_name}")
      # print("Streaming from device:", device_index)
      print("Press Ctrl+C to stop.")
      next_call_time = tt.monotonic()  # Get the current time
      interval = random.uniform(1, 5)  # Initial random interval
      try:
        while True:
          if trends_initialized:
            current_time = tt.monotonic()
            # Check if it's time to run the function
            if current_time >= next_call_time:
                actuate_motors(next_call_time)
                interval = math.floor(random.uniform(8, 10))  # Update interval dynamically
                print(f"next execution in {interval} seconds")
                next_call_time = current_time + interval  # Set next execution time
          # tt.sleep(0.9)
          pass  # Keep the stream open
      except KeyboardInterrupt:
        print('stpped!')

def connect_arduinos():
  global arduinos
  # global arduino
  try:
  # arduino = serial.Serial('/dev/ttyACM0')
  # arduino = serial.Serial('/dev/tty.usbmodem111301')
    for usb_path in arduinos_usb_paths:
      print(usb_path)
      arduino = serial.Serial(usb_path)
      print('connected to arduino: ' + usb_path)
      tt.sleep(2)
      arduinos.append(arduino)
      # send_command(50, arduino)
    arduino_connected = True
  except:
      # arduino = serial.Serial('/dev/ttyACM1')
      print('connection failed')



init_classifiers()
connect_arduinos()
start_stream()



    