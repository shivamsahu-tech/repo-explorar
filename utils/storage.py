from typing import List, Dict
import logging
from utils.embedding import get_embeddings
from utils.db_conntections import get_neo4j_driver, get_pinecone_connector
from pinecone import ServerlessSpec

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

neo4j_driver = get_neo4j_driver()
pc = get_pinecone_connector()


def store_nodes_in_neo4j(nodes: List[Dict], session_id: str):
    """Store code nodes and relationships in Neo4j with error handling."""
    if not nodes:
        logging.warning("No nodes to store in Neo4j. Skipping.")
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
            logging.info("Successfully stored all nodes and relationships in Neo4j.")

    except Exception as e:
        logging.error(f"Failed to store nodes in Neo4j for session {session_id}. Error: {e}")









        

def store_nodes_in_pinecone(nodes: List[Dict], index_name: str):
    """Store node embeddings in Pinecone with error handling."""
    if not nodes:
        logging.warning("No nodes to store in Pinecone. Skipping.")
        return
    
    try:
        # Create embeddings and get the dimension
        texts = [f"{n['name']} {n['text'][:200]}" for n in nodes]
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
        
        # ... (rest of your code)

        # Create index if it doesn't exist
        if index_name not in pc.list_indexes():
            logging.info(f"Creating Pinecone index '{index_name}'...")
            try:
                pc.create_index(
                    name=index_name,
                    dimension=dimension, 
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1")
                )   
            except Exception as e:
                logging.error(f"Failed to create Pinecone index '{index_name}'. Error: {e}")
                return
            logging.info("Created Pinecone index.")
        else:
            logging.info(f"Index '{index_name}' already exists. Skipping creation.")

        # Upsert vectors
        try:
            index = pc.Index(index_name)
            
            # Upsert the correctly formatted batch
            index.upsert(vectors=vectors_to_upsert, timeout=15)
                 
            print("✅ Upsert completed")
            
        except Exception as e:
            print(f"❌ Upsert failed: {str(e)}")
            return False
        # ... (rest of your code)

    except Exception as e:
        logging.error(f"Pinecone API error during vector upsert or index creation. Error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during Pinecone operations. Error: {e}")













































# from typing import List, Dict
# from utils.embedding import get_embeddings
# from utils.db_conntections import get_neo4j_driver, get_pinecone_connector
# from pinecone import ServerlessSpec



# neo4j_driver = get_neo4j_driver()
# pc = get_pinecone_connector()


# def store_nodes_in_neo4j(nodes: List[Dict], session_id: str):
#     with neo4j_driver.session() as session:
#         # Batch create all nodes
#         session.run("""
#             UNWIND $nodes as node
#             CREATE (n:CodeNode {
#                 id: node.id, type: node.type, name: node.name, 
#                 file: node.file, start_line: node.start_line, 
#                 session_id: $session_id
#             })
#         """, nodes=nodes, session_id=session_id)
        
#         # Batch create relationships with better matching
#         session.run("""
#             MATCH (caller:CodeNode {session_id: $session_id, type: 'FUNCTION'})
#             MATCH (call:CodeNode {session_id: $session_id, type: 'CALL'})
#             MATCH (target:CodeNode {session_id: $session_id, type: 'FUNCTION'})
#             WHERE call.file = caller.file 
#             AND caller.start_line <= call.start_line <= caller.end_line
#             AND call.name = target.name
#             CREATE (caller)-[:CALLS]->(target)
#         """, session_id=session_id)
        

# def store_nodes_in_pinecone(nodes: List[Dict], index_name: str):
#     """Store node embeddings in Pinecone"""
#     if not nodes:
#         return
    
#     # Create embeddings
#     texts = [f"{n['name']} {n['text'][:200]}" for n in nodes]
#     embeddings = get_embeddings(texts)
    
#     # Create vectors
#     vectors = []
#     for node, embedding in zip(nodes, embeddings):
#         vectors.append({
#             'id': node['id'],
#             'values': embedding,
#             'metadata': {
#                 'name': node['name'],
#                 'type': node['type'],
#                 'file': node['file'],
#                 'language': node['language']
#             }
#         })
    
#     pc.create_index(
#                 name=index_name,
#                 dimension=384,
#                 metric="cosine",
#                 spec=ServerlessSpec(cloud="aws", region="us-east-1")
#             )
#     pc.upsert_vectors(index_name, vectors)