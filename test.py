import google.generativeai as genai

# Put your actual API key here (replace with your real key)
genai.configure(api_key="REDACTED_GEMINI_API_KEY")

print("Testing AI Interview Coach setup...")

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Generate one interview question for a Python developer.")
    
    print("✅ SUCCESS! Your setup is working!")
    print("Here's your first AI-generated interview question:")
    print(response.text)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Check your API key!")