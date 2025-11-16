import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

__neo4j_driver = None


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
            