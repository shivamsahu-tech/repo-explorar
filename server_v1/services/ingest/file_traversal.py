import os
from typing import Dict, List
from core.logging import get_logger
from services.ingest.nodes_extractor import extract_nodes_from_file

logger = get_logger(__name__)

IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'dist', 'build', '.next', 'coverage'}
LANGUAGES = {'py': 'python', 'js': 'javascript', 'ts': 'typescript', 'jsx': 'javascript', 'tsx': 'typescript'}


# takes repo_path & traverse each files and return a list of nodes for whole repository
def extract_all_nodes(repo_path: str) -> List[Dict]:

    all_nodes = []
    file_relationships = {}

    logger.info(f"Starting extraction from {repo_path}")

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            ext = file.split(".")[-1].lower()
            if ext in LANGUAGES:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)
                language = LANGUAGES.get(ext)

                nodes = extract_nodes_from_file(file_path, language)
                logger.info(f"Nodes Extracted from {relative_path}...")

                # Track file relationships, like imports
                file_node = next((n for n in nodes if n['type'] == 'FILE'), None)
                if file_node:
                    file_relationships[relative_path] = file_node.get('imports', [])
                
                all_nodes.extend(nodes)
            
            elif file.lower().endswith(('.md', '.txt')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    chunks = chunk_text(content, 1000, 100)
                    for i, chunk in enumerate(chunks):
                        all_nodes.append({
                            'id': f"{file_path}:FILE_CHUNK_{i}",
                            'type': 'FILE_CHUNK',
                            'name': f"{os.path.basename(file_path)}_chunk_{i}",
                            'text': chunk,
                            'file': file_path,
                            'language': "md/txt",
                            'start_line': None,
                            'end_line': None,
                        })

                except Exception as e:
                    logger.error(f"Failed to read {file_path} : {e}")
            
    # Now add all imports as relation ship of this file
    for node in all_nodes:
        if node['type'] == 'FILE':
            node['file_relationships'] = file_relationships
    
    logger.info(f"Extracted {len(all_nodes)} nodes from {file_path} with all relatiohships : {len(file_relationships)}")

    return all_nodes



def chunk_text(text, chunk_size=1000, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks



