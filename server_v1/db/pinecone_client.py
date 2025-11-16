import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

__pc_instace = None


def get_pinecone_connector():
    global __pc_instace
    if __pc_instace is None:
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
        __pc_instace = Pinecone(api_key=api_key)
    return __pc_instace