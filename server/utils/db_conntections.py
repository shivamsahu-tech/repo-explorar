import os
from pinecone import Pinecone
from neo4j import GraphDatabase
from dotenv import load_dotenv
load_dotenv()


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


def cleanup_resources(index_name: str):
    """Deletes Pinecone index and clears Neo4j database."""

    pc = get_pinecone_connector()
    try:
        pc.delete_index(index_name)
        print(f"[Pinecone] Index '{index_name}' deleted.")
    except Exception as e:
        print(f"[Pinecone] Failed to delete index: {e}")

    driver = get_neo4j_driver()
    try:
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("[Neo4j] All nodes and relationships deleted.")
    except Exception as e:
        print(f"[Neo4j] Failed to clear graph: {e}")
