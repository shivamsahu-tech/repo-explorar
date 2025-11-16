from core.logging import get_logger
from services.ingest.repo_handler import clone_repo, cleanup_repo
from ingest.file_traversal import extract_all_nodes
from ingest.storage import store_nodes_in_neo4j, store_nodes_in_pinecone

logger = get_logger(__name__)

def run_ingest_pipeline(repo_url: str):
    session_id, repo_path = clone_repo(repo_url)

    try:
        all_nodes = extract_all_nodes(repo_path)
        if not all_nodes:
            print("No nodes found")
            return session_id
        # analyze_nodes_structure(all_nodes)
        index_name = f"repo-{session_id}"

        store_nodes_in_neo4j(all_nodes, session_id)
        logger.info("Stored nodes in neo4j")
        store_nodes_in_pinecone(all_nodes, index_name)
        logger.info("Stored vectors in pinecone")
        return index_name
        
    finally:
        cleanup_repo(repo_path)



