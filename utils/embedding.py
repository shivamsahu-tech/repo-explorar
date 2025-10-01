# This file was edited to switch from a local embedding service to using Google Gemini for embeddings.
# The previous implementation using a local service is commented out below for reference.


# import requests, os
# from dotenv import load_dotenv

# load_dotenv() 

# api_key = os.getenv("EMBEDDING_API_KEY")
# def get_embeddings(chunks):
#     response = requests.post(
#         "http://localhost:8001/embed",
#         json={"chunks": chunks},
#         headers={"Content-Type": "application/json"}
#     )
#     response.raise_for_status()
#     return response.json()["embeddings"]






import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()



genai.configure(api_key=os.getenv("LLM_API_KEY"))

if not os.getenv("LLM_API_KEY"):
    raise ValueError("Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")

model_id = "gemini-embedding-001"

def get_embeddings(chunks: list[str]) -> list[list[float]]:

    try:
        response = genai.embed_content(
            model=model_id,
            content=chunks,
            task_type="RETRIEVAL_DOCUMENT" 
        )

        return response['embedding']

    except Exception as e:
        print(f"An error occurred during embedding: {e}")
        return []
    

