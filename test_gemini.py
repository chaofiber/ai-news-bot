#!/usr/bin/env python3
"""
Test script to list available Gemini models
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure API
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)

# List available models
print("Available Gemini models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  - {model.name}")

# Try the working model
model = genai.GenerativeModel('gemini-2.5-flash-lite')
response = model.generate_content("Say hello in one sentence")
print(f"Response: {response.text}")