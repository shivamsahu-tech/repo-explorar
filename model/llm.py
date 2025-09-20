import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("gemini_api_key")

genai.configure(api_key=key)

def chat(promt): 
  model = genai.GenerativeModel("gemini-1.5-flash")
  response = model.generate_content(promt)
  return response.text

