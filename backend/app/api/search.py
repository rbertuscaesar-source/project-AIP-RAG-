from fastapi import APIRouter
from pydantic import BaseModel

from app.services.retrieval_service import search_documents

router = APIRouter()


class SearchRequest(BaseModel):
    question: str


@router.post("/search")
def search(request: SearchRequest):

    results = search_documents(request.question)

    return {
        "question": request.question,
        "results": results
    }