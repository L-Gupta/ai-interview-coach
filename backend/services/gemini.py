import google.generativeai as genai
from config.settings import settings
import requests
import json


genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")

#Response generator
def generate_response(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Error: {e}"

#Generating a response using resume
def generate_question_with_resume(resume_text: str, role: str) -> str:
    endpoint = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={settings.GEMINI_API_KEY}"

    prompt = (
        f"Based on the following resume:\n\n{resume_text}\n\n"
        f"Generate a single, job-relevant mock interview question for the role of '{role}'. "
        f"Only return the question text."
    )

    data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(endpoint, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        raise Exception(f"Gemini API error: {response.status_code} - {response.text}")