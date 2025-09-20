# import os, git, uuid, shutil


# IGNORE_DIRS = {
#     '.git', '.github', '__pycache__', '.venv', 'venv', 'env',
#     'node_modules', 'bower_components', 'dist', 'build', 'out',
#     'coverage', '.next', '.nuxt', '.vite', '.idea', '.vscode'
# }

# def clone_repo(github_url: str, repo_id: str) -> str:
#     local_path = os.path.join("data", "repos", repo_id)
#     git.Repo.clone_from(github_url, local_path)
#     return local_path

# def read_all_files(repo_url: str) -> str:
#     session_id = str(uuid.uuid4())
#     repo_path = clone_repo(repo_url, session_id)
#     pc = get_pinecone_connector()
#     index_name = f"repo-{session_id}"

#     try:
#         # Create Pinecone index for this repo
#         pc.create_index(index_name)
#         chunks = []

#         # Walk repo and split files into nodes
#         for root, dirs, files in os.walk(repo_path):
#             dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
#             for file in files:
#                 file_path = os.path.join(root, file)
#                 print("Reading file:", file_path)
#                 try:
#                     nodes = split_code_file(file_path)
#                     # Attach file_path to each node's metadata for later use
#                     for n in nodes:
#                         n.metadata["file_path"] = file_path
#                     chunks.extend(nodes)
#                 except Exception as e:
#                     print(f"Skipping file {file_path} due to split error: {e}")

#         if not chunks:
#             print("No chunks created, skipping embedding/upsert.")
#             return index_name

#         # Generate embeddings
#         texts = [node.text for node in chunks]
#         embeddings = get_embeddings(texts)

#         # Build Pinecone vectors
#         vectors = []
#         for i, (node, embedding) in enumerate(zip(chunks, embeddings), start=1):
#             if not isinstance(embedding, (list, tuple)):
#                 print(f"⚠️ Skipping chunk {i}: embedding is not a list/tuple")
#                 continue

#             embedding = [float(x) for x in embedding]
#             if len(embedding) != 384:
#                 print(f"⚠️ Skipping chunk {i}: wrong embedding length {len(embedding)}")
#                 continue

#             # Ensure metadata fields are valid types (not None)
#             start_line = node.metadata.get("start_line")
#             end_line = node.metadata.get("end_line")
#             file_path = node.metadata.get("file_path")

#             vectors.append({
#                 "id": f"{os.path.relpath(file_path, repo_path)}-chunk-{i}",
#                 "values": embedding,
#                 "metadata": {
#                     "file_path": str(file_path or ""),
#                     "start_line": int(start_line) if start_line is not None else -1,
#                     "end_line": int(end_line) if end_line is not None else -1,
#                     "code": node.text[:300],
#                     "session_id": session_id,
#                 },
#             })

#         # Only upsert if there are valid vectors
#         if vectors:
#             print(f"📤 Upserting {len(vectors)} vectors to index '{index_name}'...")
#             pc.upsert_vectors(index_name, vectors)
#             print(f"✅ Inserted {len(vectors)} vectors into Pinecone index '{index_name}'")
#         else:
#             print("⚠️ No valid vectors to upsert.")

#         return index_name

#     except Exception as e:
#         print(f"Error processing repo: {e}")
#         raise e

#     finally:
#         # Clean up cloned repo
#         if os.path.exists(repo_path):
#             shutil.rmtree(repo_path)
#             print(f"Cleaned up cloned repo at {repo_path}")
