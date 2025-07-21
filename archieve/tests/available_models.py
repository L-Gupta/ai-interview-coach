import google.generativeai as genai

# Configure your API key
genai.configure(api_key="REDACTED_GEMINI_API_KEY")

# Fetch and list all available models
models = genai.list_models()

for model in models:
    print(model.name)
