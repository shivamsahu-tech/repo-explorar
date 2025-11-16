from typing import List, Dict
from core.logging import get_logger
from llm.embeddings import get_embeddings
from db.neo4j_client import get_neo4j_driver
from db.pinecone_client import get_pinecone_connector
from pinecone import ServerlessSpec
from fastapi import HTTPException


logger = get_logger(__name__)
neo4j_driver = get_neo4j_driver()
pc = get_pinecone_connector()


def store_nodes_in_neo4j(nodes: List[Dict], session_id: str):
    if not nodes:
        logger.warning("No nodes to store in Neo4j. Skipping.")
        return
    

    try:
        with neo4j_driver.session() as session:
            # Create nodes with ALL fields including text and language
            session.run("""
                UNWIND $nodes as node
                CREATE (n:CodeNode {
                    id: node.id, 
                    type: node.type, 
                    name: node.name, 
                    text: node.text,
                    file: node.file, 
                    start_line: node.start_line,
                    end_line: node.end_line,
                    language: node.language,
                    session_id: $session_id
                })
            """, nodes=nodes, session_id=session_id)
            
            # Create relationships
            session.run("""
                MATCH (caller:CodeNode {session_id: $session_id, type: 'FUNCTION'})
                MATCH (call:CodeNode {session_id: $session_id, type: 'CALL'})
                MATCH (target:CodeNode {session_id: $session_id, type: 'FUNCTION'})
                WHERE call.file = caller.file 
                AND caller.start_line <= call.start_line <= caller.end_line
                AND call.name = target.name
                CREATE (caller)-[:CALLS]->(target)
            """, session_id=session_id)

            logger.info("Successfully stored all nodes and relationships in Neo4j.")

    except Exception as e:
        logger.error(f"Failed to store nodes in Neo4j for session {session_id}. Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store nodes in Neo4j for session {session_id}. Error: {e}"
        )
    

def store_nodes_in_pinecone(nodes: List[Dict], index_name: str):
    """Store node embeddings in Pinecone with error handling."""
    if not nodes:
        logger.warning("No nodes to store in Pinecone. Skipping.")
        return
    
    try:
        # Create embeddings and get the dimension
        texts = [f"{n['name']} {n['text'][:2000]}" for n in nodes]
        # Assume get_embeddings returns a list of vectors (e.g., [[...],[...]])
        embeddings = get_embeddings(texts)
        dimension = 384
        
        # Format the data for Pinecone upsert
        # Each item in `vectors_to_upsert` must be a (id, values) tuple
        vectors_to_upsert = []
        for i, node in enumerate(nodes):
            vector_id = node.get('id', f"node_{i}") # Ensure a unique ID for each vector
            vector_values = embeddings[i]
            vectors_to_upsert.append((vector_id, vector_values))
        

        # Create index if it doesn't exist
        if index_name not in pc.list_indexes():
            logger.info(f"Creating Pinecone index '{index_name}'...")
            try:
                pc.create_index(
                    name=index_name,
                    dimension=dimension, 
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1")
                )   
            except Exception as e:
                logger.error(f"Failed to create Pinecone index '{index_name}'. Error: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to create Pinecone index '{index_name}'. Error: {e}"
                )
            logger.info("Created Pinecone index.")
        else:
            logger.info(f"Index '{index_name}' already exists. Skipping creation.")

        # Upsert vectors
        try:
            index = pc.Index(index_name)
            
            index.upsert(vectors=vectors_to_upsert, timeout=15)
                 
            logger.info("Upsert Successfully!!")
            
        except Exception as e:
            logger.warning(f"Upsert Failed!! {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Vector Database upsert failed!! Error : {str(e)}"
            )

    except Exception as e:
        logger.error(f"Pinecone API error during vector upsert or index creation. Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Pinecone API error during vector upsert or index creation. Error: {str(e)}"
        )
    
