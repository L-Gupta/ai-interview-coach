"""
Audio Analysis Agent - Analyzes tone and speech patterns
Uses Librosa for audio feature extraction
"""
import librosa
import numpy as np
from typing import List, Dict, Any
from collections import Counter

class AudioAnalysisAgent:
    def __init__(self):
        pass
    
    def analyze_audio(self, audio_path: str, chunk_length: int = 5) -> Dict[str, Any]:
        """
        Analyze audio file for tone and emotional content
        Args:
            audio_path: Path to audio file
            chunk_length: Length of each chunk in seconds
        Returns:
            Dictionary with tone analysis results
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=16000, mono=True)
            
            # Split into chunks
            samples_per_chunk = int(chunk_length * sr)
            chunks = []
            
            for start in range(0, len(y), samples_per_chunk):
                end = start + samples_per_chunk
                chunk = y[start:end]
                
                if len(chunk) > sr:  # At least 1 second
                    if len(chunk) < samples_per_chunk:
                        chunk = np.pad(chunk, (0, samples_per_chunk - len(chunk)))
                    chunks.append(chunk)
            
            # Analyze each chunk
            tone_predictions = []
            for chunk in chunks:
                tone = self._predict_tone(chunk, sr)
                tone_predictions.append(tone)
            
            if not tone_predictions:
                return self._default_result()
            
            # Calculate statistics
            tone_counts = Counter(tone_predictions)
            total = len(tone_predictions)
            
            return {
                "dominant_tone": tone_counts.most_common(1)[0][0],
                "tone_distribution": {
                    tone: count / total 
                    for tone, count in tone_counts.items()
                },
                "tone_sequence": tone_predictions,
                "confidence": 0.7
            }
            
        except Exception as e:
            print(f"Error analyzing audio: {e}")
            return self._default_result()
    
    def _predict_tone(self, chunk: np.ndarray, sr: int) -> str:
        """
        Predict tone from audio chunk using acoustic features
        """
        try:
            # Extract features
            mfcc = librosa.feature.mfcc(y=chunk, sr=sr, n_mfcc=13)
            energy = np.mean(np.abs(mfcc))
            variance = np.var(mfcc)
            
            # Extract pitch
            f0, voiced_flag, voiced_probs = librosa.pyin(
                chunk, 
                fmin=50, 
                fmax=500, 
                sr=sr
            )
            pitch = np.nanmean(f0) if np.any(~np.isnan(f0)) else 0
            
            # Extract spectral features
            centroid = np.mean(librosa.feature.spectral_centroid(y=chunk, sr=sr))
            bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=chunk, sr=sr))
            
            # Classification logic (simplified)
            if energy > 55 and pitch > 200 and centroid > 2500:
                return "excited"
            elif energy > 40 and pitch > 150:
                return "confident"
            elif variance < 15 and centroid < 1800 and bandwidth < 2000:
                return "calm"
            elif energy < 25 and pitch < 100:
                return "nervous"
            else:
                return "neutral"
                
        except Exception as e:
            print(f"Error predicting tone: {e}")
            return "neutral"
    
    def _default_result(self) -> Dict[str, Any]:
        """Return default result when analysis fails"""
        return {
            "dominant_tone": "neutral",
            "tone_distribution": {"neutral": 1.0},
            "tone_sequence": ["neutral"],
            "confidence": 0.5
        }