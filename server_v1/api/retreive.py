from fastapi import APIRouter
from pydantic import BaseModel

from services.retreive.pipeline import run_retreival_pipeline


router = APIRouter()

class RetreivalRequest(BaseModel):
    session_id: str
    query: str


@router.post("/")
async def retreive_answer(request: RetreivalRequest):
    llm_response = run_retreival_pipeline(
        request.session_id,
        request.query
    )
    return {"status" : "success", "llm_response" : llm_response}