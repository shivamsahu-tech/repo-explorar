from core.logging import get_logger
from services.ingest.repo_handler import clone_repo, cleanup_repo
from services.ingest.file_traversal import extract_all_nodes
from services.ingest.storage import store_nodes_in_neo4j
import uuid

logger = get_logger(__name__)

def run_ingest_pipeline(repo_url: str):

    session_id, repo_path = clone_repo(repo_url)
    all_nodes = extract_all_nodes(repo_path)
    cleanup_repo(repo_path)
    
    if not all_nodes:
        logger.info("No nodes found")
        return session_id

    store_nodes_in_neo4j(all_nodes, session_id)
    logger.info("Stored nodes in neo4j")
    return session_id




