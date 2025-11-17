from typing import List, Dict
from core.logging import get_logger
from services.llm.embedding import get_embeddings
from db.neo4j_client import get_neo4j_driver
from db.pinecone_client import get_pinecone_connector
from pinecone import ServerlessSpec
from fastapi import HTTPException
import json # Added to handle serialization of the neighbors list

logger = get_logger(__name__)

neo4j_driver = get_neo4j_driver() # get_neo4j_driver() 
pc = None # get_pinecone_connector()


def store_nodes_in_neo4j(nodes: List[Dict], session_id: str):

    if not nodes:
        logger.warning("No nodes to store in Neo4j.")
        return

    flattened = []
    relationship_edges = []  # store edges separately

    for node in nodes:
        node_id = node.get("id")
        meta = node.get("metadata", {})
        rels = node.get("relationships", {})

        # Collect flattened node
        flattened.append({
            "id": node.get("id"),
            "name": node.get("name") or node.get("ast_type"),
            "code_str": node.get("code_str", ""),
            "ast_type": node.get("ast_type"),
            "file": node.get("file"),
            "language": node.get("language"),
            "start_line": node.get("start_line"),
            "end_line": node.get("end_line"),
            "start_byte": node.get("start_byte"),
            "end_byte": node.get("end_byte"),
            "size": node.get("size"),

            # metadata flattened
            "depth": meta.get("depth"),
            "calls": meta.get("calls", []),
            "inherits": meta.get("inherits", []),
            "type_references": meta.get("type_references", []),
            "is_definition": meta.get("is_definition"),
            "definition_type": meta.get("definition_type"),
        })

        # Collect relationship edges in (source, target, type) format
        for rel_type, targets in rels.items():
            # Special handling for imports_from
            if rel_type == "imports_from":
                for imp in targets:
                    # Skip external imports
                    if imp.get("is_external"):
                        continue

                    # resolved_node_ids contains actual nodes in graph
                    resolved_ids = imp.get("resolved_node_ids", [])
                    for tid in resolved_ids:
                        relationship_edges.append({
                            "source": node_id,
                            "target": tid,
                            "type": "IMPORTS_FROM"
                        })
                continue

            # Normal relationships (list of IDs)
            if isinstance(targets, list):
                for tid in targets:
                    relationship_edges.append({
                        "source": node_id,
                        "target": tid,
                        "type": rel_type.upper()
                    })

    try:
        with neo4j_driver.session() as session:

            # -------------------------------------
            # 1. Create nodes
            # -------------------------------------
            session.run(
                """
                UNWIND $nodes AS node
                CREATE (n:CodeNode)
                SET n += node,
                    n.session_id = $session_id
                """,
                nodes=flattened,
                session_id=session_id
            )

            # Add AST labels
            session.run(
                """
                MATCH (n:CodeNode {session_id: $session_id})
                CALL apoc.create.addLabels(n, [n.ast_type]) YIELD node
                RETURN node
                """,
                session_id=session_id
            )

            # -------------------------------------
            # 2. Create dynamic relationships
            # -------------------------------------
            session.run(
                """
                UNWIND $edges AS edge
                MATCH (a:CodeNode {id: edge.source, session_id: $session_id})
                MATCH (b:CodeNode {id: edge.target, session_id: $session_id})
                CALL apoc.create.relationship(a, edge.type, {}, b) YIELD rel
                RETURN rel
                """,
                edges=relationship_edges,
                session_id=session_id
            )

            logger.info("Stored nodes + all relationship types successfully.")

    except Exception as e:
        logger.error(f"Neo4j storage error: {e}")
        raise



def store_nodes_in_pinecone(nodes: List[Dict], index_name: str):
    """Store node embeddings in Pinecone with error handling."""
    if not nodes:
        logger.warning("No nodes to store in Pinecone. Skipping.")
        return
    
    # 1. Prepare Text for Embedding (Add context: name + chunk content)
    # We must try to infer a name for non-function/class nodes (like expression_statement)
    texts = []
    vectors_to_upsert = []
    
    for node in nodes:
        node_name = node.get('name') or node.get('ast_type', 'Code Chunk')
        # Use node type and file path as context for embedding (better retrieval)
        context = f"File: {os.path.basename(node.get('file', ''))}, Type: {node.get('ast_type', 'chunk')}. "
        texts.append(context + node.get('text', '')[:2000])

    try:
        # 2. Create embeddings and get the dimension
        # NOTE: get_embeddings is mocked here. Assuming it returns [[...], [...]]
        embeddings = get_embeddings(texts) 
        dimension = len(embeddings[0]) if embeddings and embeddings[0] else 384
        
        # 3. Format data for Pinecone upsert
        for i, node in enumerate(nodes):
            vector_id = node.get('id', f"node_{i}")
            vector_values = embeddings[i]
            
            # Metadata for filtering/retrieval (essential for RAG)
            metadata = {
                "file": node.get('file', 'unknown'),
                "ast_type": node.get('ast_type', 'unknown'),
                "language": node.get('language', 'unknown'),
                "start_line": node.get('start_line', 0),
                "text": node.get('text', '')[:500] # store summary text
            }
            vectors_to_upsert.append((vector_id, vector_values, metadata))

        # 4. Index Creation and Upsert
        if index_name not in pc.list_indexes():
            logger.info(f"Creating Pinecone index '{index_name}'...")
            pc.create_index(
                name=index_name,
                dimension=dimension, 
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )   
            logger.info("Created Pinecone index.")
        else:
            logger.info(f"Index '{index_name}' already exists. Skipping creation.")

        index = pc.Index(index_name)
        index.upsert(vectors=vectors_to_upsert, timeout=15)
        logger.info(f"Upsert Successful! Total vectors: {len(vectors_to_upsert)}")

    except Exception as e:
        logger.error(f"Pinecone API error during vector upsert or index creation. Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Vector Database operation failed. Error: {str(e)}"
        )