import pyaudio
import wave
import keyboard
from datetime import datetime
import os

def record_audio(filename="temp_recording.wav", duration=None):
    CHUNK = 2048
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recording_{timestamp}.wav"
    recordings_dir = os.path.join(os.path.dirname(__file__), "recordings")
    os.makedirs(recordings_dir, exist_ok=True)
    full_path = os.path.join(recordings_dir, filename)

    try:
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    except Exception as e:
        print(f"❌ Audio device error: {e}")
        return None

    frames = []
    print("🎤 Press ENTER to start recording...")
    keyboard.wait("enter")
    print("● Recording... Press ENTER to stop.")

    recording = True
    def stop(e): nonlocal recording; recording = False
    keyboard.on_press_key("enter", stop)

    while recording:
        try:
            frames.append(stream.read(CHUNK, exception_on_overflow=False))
        except:
            continue

    stream.stop_stream()
    stream.close()
    audio.terminate()
    keyboard.unhook_all()

    with wave.open(full_path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    return full_path

