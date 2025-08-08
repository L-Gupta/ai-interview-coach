import json, os, requests
from pathlib import Path
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")
DEEPGRAM_API_KEY=os.getenv('DEEPGRAM_API_KEY')
REPORTS_DIR = Path("end/reports")

"""Transcriber given audio file into a text file and returns the transcription."""
async def transcribe_audio_file(file_path:str):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None

    headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}", "Content-Type": "audio/wav"}
    url = "https://api.deepgram.com/v1/listen"

    try:
        with open(file_path, 'rb') as audio_file:
            response = requests.post(url, headers=headers, data=audio_file, timeout=15)

        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return ""
        
        data = response.json()
        transcript = data.get('results', {}) \
                         .get('channels', [{}])[0] \
                         .get('alternatives', [{}])[0] \
                         .get('transcript', "")
        return transcript.strip()
    except Exception as e:
        print(f"❌ Unexpected response structure : {e}")
        return ""


"""
Updates conv_history.json with the transcript for a specific question.

JSON structure:
{
    "q1": "This is the answer transcript",
    "q2": "Another answer transcript"
}
"""
async def update_conv_history_json(resume_id:str, question:str, transcript:str, q_id:str):
    resume_dir = REPORTS_DIR / resume_id
    resume_dir.mkdir(parents=True, exist_ok=True)

    conv_file = resume_dir / "conv_history.json"

    # ✅ Load existing data if available
    if conv_file.exists():
        with open(conv_file, "r", encoding="utf-8") as f:
            try:
                conv_data = json.load(f)
            except json.JSONDecodeError:
                conv_data = {}
    else:
        conv_data = {}

    # ✅ Update or add transcript for this question
    conv_data[f"{q_id} + {question}"] = transcript

    # ✅ Save back to file
    with open(conv_file, "w", encoding="utf-8") as f:
        json.dump(conv_data, f, indent=4)

    print(f"✅ Updated conv_history.json for {resume_id} -> {question}")
