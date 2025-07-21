import google.generativeai as genai
from config.settings import settings

def test_gemini_connection():
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Say hello to test the connection!")
        print("✅ Gemini API connection successful!")
        print(f"Response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Gemini API connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing AI Interview Coach Setup...")
    test_gemini_connection()