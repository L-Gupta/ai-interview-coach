import requests
import os

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

def transcribe_audio(filepath: str) -> str:
    with open(filepath, "rb") as audio_file:
        response = requests.post(
            "https://api.deepgram.com/v1/listen",
            headers={
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": "audio/m4a"  # or audio/wav, depending on file
            },
            data=audio_file
        )

    result = response.json()
    return result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")

