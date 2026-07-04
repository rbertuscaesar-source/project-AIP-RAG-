from fastapi import APIRouter
from pydantic import BaseModel

from app.services.retrieval_service import get_context
from app.services.llm_service import generate_answer
from app.services.memory_service import (add_message,get_history)
router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(request: ChatRequest):

    session_id = "default"

    # Ambil context dari retrieval
    context, sources = get_context(request.question)

    # Jika tidak ada context
    if not context:
        return {
            "status": "success",
            "question": request.question,
            "answer": "Dokumen belum tersedia atau tidak ada informasi yang relevan.",
            "sources": []
        }

    # Ambil riwayat chat
    history = get_history(session_id)

    # Generate jawaban menggunakan history
    answer = generate_answer(
        request.question,
        context,
        history
    )

    # Simpan pertanyaan user
    add_message(
        session_id,
        "User",
        request.question
    )

    # Simpan jawaban AI
    add_message(
        session_id,
        "Assistant",
        answer
    )

    return {
        "status": "success",
        "question": request.question,
        "answer": answer,
        "sources": [
            {
                "file": item["metadata"]["source"],
                "page": item["metadata"]["page"],
                "confidence": round(item["final_score"], 2)
            }
            for item in sources
        ]
    }