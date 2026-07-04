from collections import defaultdict

# Menyimpan riwayat chat sementara (di RAM)
chat_memory = defaultdict(list)


def add_message(session_id, role, content):

    chat_memory[session_id].append({

        "role": role,

        "content": content

    })


def get_history(session_id):

    return chat_memory.get(session_id, [])


def clear_history(session_id):

    chat_memory.pop(session_id, None)