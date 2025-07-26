import os
import requests
import wave
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

def transcribe_audio(file_path):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None

    headers = {"Authorization": f"Token {os.getenv('DEEPGRAM_API_KEY')}"}
    url = "https://api.deepgram.com/v1/listen"

    with open(file_path, 'rb') as audio_file:
        response = requests.post(
            url,
            headers=headers,
            params={
                "model": "base",
                "punctuate": "true",
                "diarize": "false"
            },
            data=audio_file,
            timeout=10
        )

    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code} - {response.text}")
        return None

    try:
        return response.json()['results']['channels'][0]['alternatives'][0]['transcript']
    except KeyError:
        print("❌ Unexpected response structure")
        return None
