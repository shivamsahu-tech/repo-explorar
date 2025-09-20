import os
from pinecone import Pinecone
from neo4j import GraphDatabase


_pc_instance = None
__neo4j_driver = None


def get_pinecone_connector():
    global _pc_instance
    if _pc_instance is None:
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")
        _pc_instance = Pinecone(api_key=api_key)
    return _pc_instance


def get_neo4j_driver():
    global __neo4j_driver
    if __neo4j_driver is None:
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")  
        neo4j_password = os.getenv("NEO4J_PASSWORD")
        
        if not neo4j_uri:
            raise ValueError("NEO4J_URI not found in environment variables")
        if not neo4j_password:
            raise ValueError("NEO4J_PASSWORD not found in environment variables")
            
        __neo4j_driver = GraphDatabase.driver(
            neo4j_uri, 
            auth=(neo4j_username, neo4j_password)
        )
    return __neo4j_driver