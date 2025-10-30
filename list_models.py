"""
Script to list available Gemini models
"""

import google.generativeai as genai

# Your API key
API_KEY = "AIzaSyDIO_8C7YMWjXMbpPzemtjTOqeWH9UGT_A"

genai.configure(api_key=API_KEY)

print("Available Gemini Models:")
print("=" * 80)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"\nModel: {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Description: {model.description}")
        print(f"  Supported methods: {model.supported_generation_methods}")

