from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# from read_repo_to_index import read_all_files
# from services.pinecone_module import get_pinecone_connector
# from services.embedding import get_embeddings
# from services.create_context_for_llm import create_context
# from services.llm import chat
# from template.prompt import get_prompt
from utils.process import process_repository
from utils.retrieval import search_code 
from template.prompt import get_prompt
from model.llm import chat
from template.query_optimization import get_optimized_query


app = FastAPI(title="Codebase RAG Service")

class RepoRequest(BaseModel):
    github_url: str

class deleteIndexRequest(BaseModel):
    index_name: str

class chatRequest(BaseModel):
    index_name: str
    query_text: str


@app.get("/test")
async def test():
    return {"status": "success", "message": "backend is up"}

@app.post("/process-repo")
async def process_repo(req: RepoRequest):
    try:
        print("Processing repository... ", req.github_url)
        index_name = process_repository(req.github_url)
        return {"status": "success", "index_name": index_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# @app.post("/delete-index")
# async def delete_index(req: deleteIndexRequest):
#     try:
#         index_name=req.index_name
#         pc=get_pinecone_connector()
#         pc.delete_index(index_name)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e)) 
    

@app.post("/chat-with-codebase")
async def chat_with_codebase(req: chatRequest):
    print("Chat with codebase called")
    try:
        optimized_query=get_optimized_query(req.query_text)
        context=search_code(optimized_query, req.index_name)
        prompt=get_prompt(context, req.query_text)
        print(prompt)
        llm_response=chat(prompt)
        return {"status": "success", "llm_response": llm_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




