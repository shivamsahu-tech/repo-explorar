

import uuid, os, git, shutil



def clone_repository(github_url: str) -> str:
    session_id = str(uuid.uuid4())
    local_path = os.path.join("data", "repos", session_id)
    git.Repo.clone_from(github_url, local_path)
    print("repo cloned succesfully.")
    return session_id, local_path




def cleanup_repo(repo_path: str):
    """Remove cloned repository"""
    print("clean up successfully")
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)