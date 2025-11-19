from fastapi import APIRouter
from pydantic import BaseModel

from services.ingest.pipeline import run_ingest_pipeline

router = APIRouter()

class IngestRequest(BaseModel):
    repo_url: str


@router.post("/")
async def ingest_repo(request: IngestRequest):
    session_id = run_ingest_pipeline(request.repo_url)
    return {"status" : "success", "session_id" : session_id}