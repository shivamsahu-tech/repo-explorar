from core.logging import get_logger
from services.ingest.repo_handler import clone_repo, cleanup_repo
from services.ingest.file_traversal import extract_all_nodes
from services.ingest.storage import store_nodes_in_neo4j
import uuid
from fastapi import HTTPException

logger = get_logger(__name__)

def run_ingest_pipeline(repo_url: str):
    # session_id, repo_path = clone_repo(repo_url)
    repo_path = "data/repos/f18d2f57-cf74-46a8-9ff0-850c3e2936ab"
    print(repo_path)
    all_nodes = extract_all_nodes(repo_path)
    session_id = str(uuid.uuid4())
    print(session_id)
    try:
        if not all_nodes:
            print("No nodes found")
            return session_id

        store_nodes_in_neo4j(all_nodes, session_id)
        logger.info("Stored nodes in neo4j")
        return {
            "session_id" : session_id,
            "all_nodes" : all_nodes,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Issue in embedding or storage"
        )
        # cleanup_repo(repo_path)



