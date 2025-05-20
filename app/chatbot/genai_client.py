import os
from google import genai
from dotenv import load_dotenv

# Load environment variables from .env.local file
load_dotenv(".env.local")

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Google Generative AI client
client = genai.Client(api_key=GEMINI_API_KEY) 