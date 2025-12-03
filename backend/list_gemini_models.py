import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ No Gemini API key found in .env")
    exit()

print("=" * 50)
print("Listing available Gemini models...")
print("=" * 50)

try:
    # Configure
    genai.configure(api_key=api_key)
    
    # List all models
    models = list(genai.list_models())
    
    print(f"Found {len(models)} models:")
    print("-" * 50)
    
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Description: {model.description}")
            print(f"   Input Token Limit: {model.input_token_limit}")
            print(f"   Output Token Limit: {model.output_token_limit}")
            print(f"   Supported Methods: {model.supported_generation_methods}")
            print("-" * 50)
    
    # Try specific models
    print("\n" + "=" * 50)
    print("Testing specific models...")
    print("=" * 50)
    
    test_models = [
        "gemini-1.5-pro-latest",
        "gemini-1.5-pro",
        "gemini-1.0-pro",
        "gemini-1.0-pro-001",
        "gemini-1.0-pro-latest",
        "models/gemini-pro",
    ]
    
    for model_name in test_models:
        print(f"\nTesting: {model_name}")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say 'Hello' in one word")
            print(f"  ✅ Works! Response: '{response.text}'")
            print(f"  Use this model in your code: '{model_name}'")
            break
        except Exception as e:
            print(f"  ❌ Failed: {str(e)[:100]}")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")