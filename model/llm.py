from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key=os.getenv("LLM_API_KEY")
client = genai.Client(api_key=api_key)

def chat(prompt): 
  response = client.models.generate_content(
  model="gemini-2.5-flash",
  contents=prompt,
  )
  return response.text

  

