import numpy as np
import sounddevice as sd
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import audio
import time as tt
import concurrent.futures

# Parameters
fs = 44100.0  # Sample rate
sample_rate = 16000
channels = 16  # Mono audio
block_size = 256  # Number of samples per callback
device_index = 0  # Replace with your desired input device index
output_device = 1
NUM_CHANNELS = 6

AudioClassifier = mp.tasks.audio.AudioClassifier
AudioClassifierOptions = mp.tasks.audio.AudioClassifierOptions
AudioClassifierResult = mp.tasks.audio.AudioClassifierResult
AudioRunningMode = mp.tasks.audio.RunningMode
BaseOptions = mp.tasks.BaseOptions

def print_result(
  result: AudioClassifierResult, 
  timestamp_ms: int, 
  channel_index: int
  ):
    # print('AudioClassifierResult result: {}'.format(result))
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f'Timestamp: {timestamp_ms} ms')
    print(f'Audio Channel: {channel_index + 1}')
    for classification in result.classifications:
      for category in classification.categories:
        print(f'{category.category_name}: {category.score:.2f}')
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
      

# options = AudioClassifierOptions(
#     base_options=BaseOptions(model_asset_path='./yamnet.tflite'),
#     running_mode=AudioRunningMode.AUDIO_STREAM,
#     max_results=5,
#     result_callback=print_result)

def create_classifier(channel_index):
    """Creates a classifier that includes channel information."""
    def result_callback(result, timestamp_ms):
        print_result(result, timestamp_ms, channel_index)  # Pass the channel index
    options = AudioClassifierOptions(
      base_options=BaseOptions(model_asset_path='./yamnet.tflite'),
      running_mode=AudioRunningMode.AUDIO_STREAM,
      max_results=5,
      result_callback=result_callback)
    return AudioClassifier.create_from_options(options)

classifiers = []

for i in range(NUM_CHANNELS):
  print(f"creating classifier number: {i}")
  classifiers.append(create_classifier(i))

# Send live audio data to perform audio classification.
# Results are sent to the `result_callback` provided in the `AudioClassifierOptions`
# Create the audio classifier
# classifier = AudioClassifier.create_from_options(options)
  
### Prepare the data

AudioData = mp.tasks.components.containers.AudioData




# Get device info
device_info = sd.query_devices(device_index, 'input')
device_name = device_info['name']

# Print device name
print(f"🎤 Listening to: {device_name} (ID: {device_index})")

# Thread pool for processing multiple channels in parallel
executor = concurrent.futures.ThreadPoolExecutor(max_workers=NUM_CHANNELS)

def process_channel(channel_index, audio_chunk, timestamp_ms):
  """Process and classify a single audio channel in a separate thread."""
  # print(f"Processing Channel {channel_index + 1} at {timestamp_ms} ms")
  # Convert to float32 (required by MediaPipe)
  # audio_data_np = np.copy(audio_chunk).astype(np.float32)
  audio_data_np = np.array(audio_chunk, dtype=np.float32).copy()
  # Create AudioData instance
  mp_audio_data = AudioData.create_from_array(audio_data_np, sample_rate=16000)
  # Run classification asynchronously
  classifiers[channel_index].classify_async(mp_audio_data, timestamp_ms)

# Read microphone data as np arrays, then call
global_timestamp_ms = None
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
  # Get single channel of audio
  # single_audio_channel = indata[:, 5]
  # audio_data_np = np.array(single_audio_channel, dtype=np.float32).copy()

  # classifier.classify_async(mp_audio_data, timestamp_ms)
  # Launch parallel classification for each channel
  for ch in range(NUM_CHANNELS):
      executor.submit(process_channel, ch, indata[:, ch], timestamp_ms)
  tt.sleep(0.05)

# Open a stream with the selected device
with sd.InputStream(
  samplerate=sample_rate, 
  channels=channels, 
  callback=audio_callback,
  blocksize=block_size, 
  device=device_index
  ):
  
    print("Streaming from device:", device_index)
    print("Press Ctrl+C to stop.")
    try:
      while True:
        # tt.sleep(0.9)
        pass  # Keep the stream open
    except KeyboardInterrupt:
      print('stpped!')

# Open a stream with the selected device Nad check what audio is playing
# with sd.Stream(
#   samplerate=sample_rate, 
#   channels=(channels, 1), 
#   callback=audio_callback,
#   blocksize=block_size, 
#   device=(device_index, output_device)
#   ):
  
#     print("Streaming from device:", device_index)
#     print("Press Ctrl+C to stop.")
#     try:
#       while True:
#         tt.sleep(0.9)
#         pass  # Keep the stream open
#     except KeyboardInterrupt:
#       print('stpped!')


    