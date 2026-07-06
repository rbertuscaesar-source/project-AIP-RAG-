# app/api/export.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.memory_service import get_history
import datetime
import io

router = APIRouter()

class ExportRequest(BaseModel):
    format: str = "txt"

@router.post("/export")
async def export_chat(request: ExportRequest):
    session_id = "default"
    
    # 🔥 CEK SEMUA SESSION YANG ADA
    from app.services.memory_service import chat_histories
    print(f"📊 All sessions: {list(chat_histories.keys())}")
    
    history = get_history(session_id)
    
    print(f"📤 Export chat - Session: {session_id}, History length: {len(history)}")
    
    if not history:
        raise HTTPException(
            status_code=404, 
            detail=f"Tidak ada riwayat chat untuk session '{session_id}'. Silakan chat dulu dengan asisten."
        )
    
    chat_text = format_chat_history(history)
    
    if request.format == "txt":
        return export_txt(chat_text)
    elif request.format == "pdf":
        return export_pdf_simple(chat_text)
    else:
        raise HTTPException(status_code=400, detail="Format tidak didukung.")

def format_chat_history(history: list) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("          EXPORT CHAT HISTORY")
    lines.append("=" * 60)
    lines.append(f"Tanggal: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 60)
    lines.append("")
    
    for msg in history:
        role = msg.get("role", "Unknown")
        content = msg.get("content", "")
        timestamp = msg.get("timestamp", "")
        
        if role == "user":
            lines.append(f"[{timestamp}] 👤 ANDA:")
        else:
            lines.append(f"[{timestamp}] 🤖 ASISTEN:")
        
        for line in content.split('\n'):
            if line.strip():
                lines.append(f"  {line}")
        lines.append("")
        lines.append("-" * 40)
        lines.append("")
    
    lines.append("=" * 60)
    lines.append("          AKHIR CHAT HISTORY")
    lines.append("=" * 60)
    return '\n'.join(lines)

def export_txt(chat_text: str):
    filename = f"chat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    return StreamingResponse(
        io.BytesIO(chat_text.encode('utf-8')),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

def export_pdf_simple(chat_text: str):
    filename = f"chat_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    return StreamingResponse(
        io.BytesIO(chat_text.encode('utf-8')),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )