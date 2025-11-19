from google import genai
import os
from dotenv import load_dotenv
from fastapi import HTTPException
from core.logging import get_logger

logger = get_logger(__name__)

load_dotenv()
key = os.getenv("LLM_API_KEY") 

client = genai.Client(api_key=key)

def chat(prompt): 
    logger.info(f"Querying to llm for prompt : {prompt}")
    logger.info("Gemini is on the way!!!!!!!!!!")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        logger.error(f"Failed in LLM Response! | Error : {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed in LLM Response! | Error : {e}"
        )
  




# print(chat("Write a python function to add two numbers"))



