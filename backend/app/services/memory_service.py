# app/services/memory_service.py

import datetime

# 🔥 PASTIKAN INI GLOBAL
chat_histories = {}

def add_message(session_id: str, role: str, content: str):
    """Tambahkan pesan ke history"""
    global chat_histories  # 🔥 PASTIKAN PAKAI GLOBAL
    
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    
    chat_histories[session_id].append({
        "role": role.lower(),
        "content": content,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })
    
    # Batasi history maksimal 50 pesan
    if len(chat_histories[session_id]) > 50:
        chat_histories[session_id] = chat_histories[session_id][-50:]
    
    # 🔥 DEBUG: Cetak jumlah history
    print(f"📝 History saved - Session: {session_id}, Total: {len(chat_histories[session_id])}")

def get_history(session_id: str) -> list:
    """Ambil history chat"""
    global chat_histories
    return chat_histories.get(session_id, [])

def clear_history(session_id: str):
    """Hapus history chat"""
    global chat_histories
    if session_id in chat_histories:
        chat_histories[session_id] = []
        print(f"🗑️ History cleared for session: {session_id}")