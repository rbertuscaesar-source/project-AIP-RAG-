# app/api/chat.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.retrieval_service import get_context
from app.services.llm_service import generate_answer
from app.services.memory_service import add_message, get_history

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.post("/chat")
def chat(request: ChatRequest):
    session_id = "default"
    
    print(f"💬 Chat request: {request.question}")
    
    context, sources = get_context(request.question)
    
    if not context:
        return {
            "status": "success",
            "question": request.question,
            "answer": "Maaf, saya tidak menemukan informasi tersebut pada dokumen.",
            "sources": []
        }
    
    history = get_history(session_id)
    print(f"📚 History length before: {len(history)}")
    
    answer = generate_answer(request.question, context, history)
    
    # 🔥 SIMPAN HISTORY
    add_message(session_id, "User", request.question)
    add_message(session_id, "Assistant", answer)
    
    # 🔥 CEK APAKAH TERSIMPAN
    history_after = get_history(session_id)
    print(f"📚 History length after: {len(history_after)}")
    
    return {
        "status": "success",
        "question": request.question,
        "answer": answer,
        "sources": [
            {
                "file": item["metadata"]["source"],
                "page": item["metadata"]["page"],
                "confidence": round(item.get("final_score", 0), 2)
            }
            for item in sources
        ]
    }