import librosa, json
import soundfile as sf
import numpy as np
from pathlib import Path

REPORTS_DIR = Path("end/reports")

"""
Splits the given WAV file into fixed-length chunks.

Args:
    file_path (str): Path to the audio file.
    chunk_length (int): Chunk size in seconds.

Returns:
    list: A list of NumPy arrays, each containing audio samples for one chunk.
"""
async def chunk_audio(file_path: str, chunk_length: int = 5):
    try:
        # ✅ 1. Load audio file
        y, sr = librosa.load(file_path, sr=None, mono=True)

        # ✅ 2. Calculate number of samples per chunk
        samples_per_chunk = int(chunk_length * sr)

        chunks = []
        for start in range(0, len(y), samples_per_chunk):
            end = start + samples_per_chunk
            chunk = y[start:end]

            if len(chunk) > 0:
                # Pad last chunk with zeros if it's shorter than required
                if len(chunk) < samples_per_chunk:
                    chunk = np.pad(chunk, (0, samples_per_chunk - len(chunk)))
                chunks.append(chunk)

        return chunks

    except Exception as e:
        print(f"❌ Error in chunk_audio: {e}")
        return []

"""
Predict tone for each audio chunk.

Args:
    chunks (list): List of NumPy arrays representing audio chunks.
    sr (int): Sample rate for feature extraction (default 16kHz).

Returns:
    list: A list of predicted tone strings, one per chunk.
"""
async def predict_tone(chunks, sr: int = 16000):
    #Initiates the list of tone
    all_tone = []

    for idx, chunk in enumerate(chunks):
        try:
            # ✅ 1. Extract MFCCs
            mfcc = librosa.feature.mfcc(y=chunk, sr=sr, n_mfcc=13)
            energy = np.mean(np.abs(mfcc))
            variance = np.var(mfcc)

            # ✅ 2. Extract pitch (F0)
            f0, _, _ = librosa.pyin(chunk, fmin=50, fmax=500, sr=sr)
            pitch = np.nanmean(f0) if np.any(~np.isnan(f0)) else 0

            # ✅ 3. Extract spectral centroid and bandwidth
            centroid = np.mean(librosa.feature.spectral_centroid(y=chunk, sr=sr))
            bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=chunk, sr=sr))

            # ✅ 4. Combine thresholds (tuned)
            if energy > 55 and pitch > 200 and centroid > 2500:
                predicted_tone = "Excited"
            elif energy > 40 and pitch > 150:
                predicted_tone = "Happy"
            elif variance < 15 and centroid < 1800 and bandwidth < 2000:
                predicted_tone = "Calm"
            elif energy < 25 and pitch < 100:
                predicted_tone = "Sad"
            else:
                predicted_tone = "Neutral"

            all_tone.append(predicted_tone)

        except Exception as e:
            print(f"❌ Error predicting tone for chunk {idx}: {e}")
            all_tone.append("Neutral")

    return all_tone

"""
Updates tone.json for a given resume_id with tones for a specific question.

JSON structure:
{
    "q1": ["Happy", "Nervous", "Calm"],
    "q2": ["Neutral", "Excited"]
}
"""
async def update_tone_json(resume_id: str, question_id: str, tone: list):
    resume_dir = REPORTS_DIR / resume_id
    resume_dir.mkdir(parents=True, exist_ok=True)

    tone_file = resume_dir / "tone.json"

    # ✅ Load existing data if file exists
    if tone_file.exists():
        with open(tone_file, "r", encoding="utf-8") as f:
            try:
                tone_data = json.load(f)
            except json.JSONDecodeError:
                tone_data = {}
    else:
        tone_data = {}

    # ✅ Update or add the new tone for the question_id
    tone_data[question_id] = tone

    # ✅ Save updated JSON back to file
    with open(tone_file, "w", encoding="utf-8") as f:
        json.dump(tone_data, f, indent=4)

    print(f"✅ Updated tone.json for {resume_id} -> {question_id}")

