from fastapi import APIRouter
from pydantic import BaseModel

from app.services.retrieval_service import get_context
from app.services.llm_service import generate_answer

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(request: ChatRequest):

    context, sources = get_context(request.question)

    if not context:
        return {
            "status": "success",
            "answer": "Dokumen belum tersedia atau tidak ada informasi yang relevan.",
            "sources": []
        }

    answer = generate_answer(
        request.question,
        context
    )

    return {
        "question": request.question,
        "answer": answer,
        "sources": sources
    }