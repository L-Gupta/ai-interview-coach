import google.generativeai as genai
from config.settings import settings

def test_gemini_token():
    try:
        # Configure the API
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Create model instance
        model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        
        # Make a simple API call
        response = model.generate_content(
            "Just respond with 'OK' if you received this message",
            generation_config={"max_output_tokens": 10}
        )
        
        # Check if we got any response
        if response.text:
            print("✅ API Token is valid and working!")
            print(f"Model response: {response.text}")
            return True
            
    except Exception as e:
        print("❌ API test failed")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting API test...")
    test_gemini_token()