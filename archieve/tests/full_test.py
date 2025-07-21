from config.settings import settings
import google.generativeai as genai

def run_all_tests():
    print("🧪 Running setup verification tests...\n")
    
    # Test 1: Environment variables
    print("1. Testing environment variables...")
    if settings.GEMINI_API_KEY:
        print("   ✅ Gemini API key found")
    else:
        print("   ❌ Gemini API key missing")
    
    # Test 2: Gemini API
    print("2. Testing Gemini API connection...")
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Generate a simple interview question for a software developer.")
        print("   ✅ Gemini API working!")
        print(f"   Sample question: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ Gemini API failed: {e}")
    
    print("\n🎉 Setup verification complete!")

if __name__ == "__main__":
    run_all_tests()