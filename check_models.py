import google.generativeai as genai
import os

# Option A: Load from your secrets file (Best Practice)
# If you are running this locally and have the .streamlit/secrets.toml file:
try:
    import toml
    secrets = toml.load(".streamlit/secrets.toml")
    api_key = secrets["GOOGLE_API_KEY"]
except:
    # Option B: Paste key directly just for this test
    api_key = "PASTE_YOUR_API_KEY_HERE"

genai.configure(api_key=api_key)

print("🔍 Scanning available Gemini models for your API key...\n")

for m in genai.list_models():
    # We only care about models that can generate text/content
    if 'generateContent' in m.supported_generation_methods:
        print(f"- Name: {m.name}")
        print(f"  Display: {m.display_name}")
        print(f"  Version: {m.version}")
        print("---")