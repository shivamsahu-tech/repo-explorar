from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("LLM_API_KEY") 

client = genai.Client(api_key=key)

def chat(prompt): 
  try:
      response = client.models.generate_content(
          model="gemini-2.5-flash",
          contents=prompt,
      )
      return response.text
  except Exception as e:
      print(f"An error occurred during chat: {e}")
      return "Error: Unable to get response from the model."
  




print(chat("Write a python function to add two numbers"))



