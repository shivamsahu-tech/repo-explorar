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
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Codebase RAG Service")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         
    allow_credentials=True,
    allow_methods=["*"],            
    allow_headers=["*"],            
)


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

    

@app.post("/chat-with-codebase")
async def chat_with_codebase(req: chatRequest):
    print("Chat with codebase called")
    print(req.index_name, "  ", req.query_text)
    try:
        # optimized_query=get_optimized_query(req.query_text)
        context=search_code(req.query_text, req.index_name)
        # print("context ", context)
        prompt=get_prompt(context, req.query_text)
        print(prompt)
        llm_response=chat(prompt)
        return {"status": "success", "llm_response": llm_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




