from fastapi import APIRouter
from pydantic import BaseModel

from app.services.retrieval_service import get_context

router = APIRouter()


class SearchRequest(BaseModel):
    question: str


@router.post("/search")
def search(request: SearchRequest):

    context, sources = get_context(request.question)

    return {
        "question": request.question,
        "context": context,
        "sources": sources
    }