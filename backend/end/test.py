import wave
import numpy as np
import librosa

AUDIO_FILE = "input.wav"  # replace with your file name

def load_and_split_audio(file_path, chunk_length=5):
    with wave.open(file_path, 'rb') as wf:
        sr = wf.getframerate()
        n_channels = wf.getnchannels()
        n_frames = wf.getnframes()
        raw_audio = wf.readframes(n_frames)

    audio_data = np.frombuffer(raw_audio, dtype=np.int16).astype(np.float32)
    if n_channels > 1:
        audio_data = audio_data.reshape(-1, n_channels)
        audio_data = audio_data.mean(axis=1)  # mono

    y = audio_data / np.iinfo(np.int16).max
    duration = len(y) / sr
    print(f"✅ Loaded {file_path}: {duration:.2f}s, SR={sr}")

    samples_per_chunk = int(chunk_length * sr)
    chunks = [y[i:i+samples_per_chunk] for i in range(0, len(y), samples_per_chunk) if len(y[i:i+samples_per_chunk]) > 0]
    print(f"✅ Created {len(chunks)} chunks of ~{chunk_length}s each")
    return chunks, sr

def extract_emotions(chunks, sr):
    energies = []
    variances = []
    features = []

    # Collect features for normalization
    for chunk in chunks:
        mfcc = librosa.feature.mfcc(y=chunk, sr=sr, n_mfcc=13)
        energy = np.mean(np.abs(mfcc))
        variance = np.var(mfcc)
        energies.append(energy)
        variances.append(variance)
        features.append((energy, variance))

    mean_energy = np.mean(energies)
    mean_var = np.mean(variances)

    emotions = []
    for idx, (energy, variance) in enumerate(features):
        # Dynamic thresholds based on relative deviation
        if energy > mean_energy * 1.3 and variance > mean_var * 1.3:
            emotion = "Excited"
        elif energy > mean_energy * 1.1:
            emotion = "Happy"
        elif energy < mean_energy * 0.7 and variance < mean_var * 0.7:
            emotion = "Calm"
        elif energy < mean_energy * 0.6:
            emotion = "Sad"
        else:
            emotion = "Neutral"

        print(f"🎵 Chunk {idx+1}: Energy={energy:.2f}, Var={variance:.2f} -> Emotion={emotion}")
        emotions.append(emotion)

    return emotions

if __name__ == "__main__":
    chunks, sr = load_and_split_audio(AUDIO_FILE, chunk_length=5)
    predicted_emotions = extract_emotions(chunks, sr)
    print("\n✅ Final Emotions:", predicted_emotions)
