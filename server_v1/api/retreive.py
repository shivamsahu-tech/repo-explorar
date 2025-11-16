from fastapi import APIRouter
from pydantic import BaseModel

from services.retreive.pipeline import run_retreival_pipeline


router = APIRouter()

class RetreivalRequest(BaseModel):
    index_name: str
    query: str


@router.post("/")
async def retreive_answer(request: RetreivalRequest):
    answer = run_retreival_pipeline(
        index_name=request.index_name,
        query=request.query
    )
    return {"status" : "success", "answer" : answer}