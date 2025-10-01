# from typing import List, Dict
# from utils.db_conntections import get_neo4j_driver, get_pinecone_connector
# from utils.embedding import get_embeddings

# neo4j_driver = get_neo4j_driver()
# pc = get_pinecone_connector()
# def search_code(query: str, index_name: str, max_results: int = 5) -> str:
#     """Search code and return formatted results for RAG"""
#     print("reached for correspondin searching")
#     query_embedding = get_embeddings([query])[0]
#     index = pc.Index(index_name)
#     vector_results = index.query(
#         vector=query_embedding, 
#         top_k=max_results,
#         include_metadata=True
#     )
    
#     if not vector_results['matches']:
#         return "No matching code found."
    
#     formatted_results = []
    
#     with neo4j_driver.session() as session:
#         for i, match in enumerate(vector_results['matches'], 1):
#             node_id = match['id']
            
#             result = session.run("""
#                 MATCH (n:CodeNode {id: $node_id})
#                 RETURN n.text as code, n.file as file, n.language as language, 
#                        n.start_line as start_line, n.name as name, n.type as type
#             """, node_id=node_id)
            
#             record = result.single()
#             if record:
#                 code = record['code']
#                 if isinstance(code, bytes):
#                     code = code.decode('utf-8')
                
#                 formatted_results.append(f"""Result {i} (Score: {match['score']:.3f}):
# Function: {record['name']}
# Type: {record['type']}
# File: {record['file']} (Line {record['start_line']})
# Language: {record['language']}
# Code: {code}
# ---""")
    
#     return '\n'.join(formatted_results) if formatted_results else "No code details found."





from typing import List, Dict
from utils.db_conntections import get_neo4j_driver, get_pinecone_connector
from utils.embedding import get_embeddings
import logging
import time
from neo4j.exceptions import ServiceUnavailable

neo4j_driver = get_neo4j_driver()
pc = get_pinecone_connector()

def fetch_node_from_neo4j(session, node_id):
    """Fetch a single node from Neo4j"""
    result = session.run(
        """
        MATCH (n:CodeNode {id: $node_id})
        RETURN n.text as code, n.file as file, n.language as language, 
               n.start_line as start_line, n.name as name, n.type as type
        """,
        node_id=node_id
    )
    return result.single()

def search_code(query: str, index_name: str, max_results: int = 5) -> str:
    logging.info("Starting search for query: %s", query)

    # Step 1: Generate embeddings
    try:
        query_embedding = get_embeddings([query])[0]
    except Exception as e:
        logging.error("Failed to generate embeddings: %s", e)
        return "Error: Could not generate query embeddings."

    # Step 2: Query Pinecone
    try:
        index = pc.Index(index_name)
        vector_results = index.query(
            vector=query_embedding,
            top_k=max_results,
            include_metadata=True
        )
    except Exception as e:
        logging.error("Pinecone query failed: %s", e)
        return "Error: Failed to query Pinecone index."

    if not vector_results.get('matches'):
        return "No matching code found."

    formatted_results = []

    # Step 3: Fetch nodes from Neo4j with retry
    for i, match in enumerate(vector_results['matches'], 1):
        node_id = match['id']
        retries = 3
        for attempt in range(retries):
            try:
                with neo4j_driver.session() as session:
                    record = fetch_node_from_neo4j(session, node_id)
                if record:
                    code = record['code']
                    if isinstance(code, bytes):
                        code = code.decode('utf-8')

                    formatted_results.append(
                        f"Result {i} (Score: {match['score']:.3f}):\n"
                        f"Function: {record['name']}\n"
                        f"Type: {record['type']}\n"
                        f"File: {record['file']} (Line {record['start_line']})\n"
                        f"Language: {record['language']}\n"
                        f"Code: {code}\n---"
                    )
                break  # success, exit retry loop
            except ServiceUnavailable as e:
                logging.warning(
                    "Neo4j connection unavailable (attempt %d/%d): %s",
                    attempt + 1, retries, e
                )
                time.sleep(1)
            except Exception as e:
                logging.error("Neo4j query failed: %s", e)
                break  # don't retry unknown errors

    return '\n'.join(formatted_results) if formatted_results else "No code details found."
