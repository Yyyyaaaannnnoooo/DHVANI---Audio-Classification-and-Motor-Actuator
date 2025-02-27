import sounddevice as sd
import numpy as np

def test_mic():
    print("Recording for 3 seconds...")
    fs = 44100  # Sample rate
    duration = 3  # Seconds

    try:
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype=np.float32)
        sd.wait()  # Wait for recording to finish
        print("Recording complete!")
    except Exception as e:
        print("Error:", e)

test_mic()
