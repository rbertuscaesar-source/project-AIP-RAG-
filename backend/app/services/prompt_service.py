def build_prompt(question, context, history):

    conversation = ""

    for item in history:

        conversation += f"{item['role']}: {item['content']}\n"

    prompt = f"""
Anda adalah AI Assistant.

Gunakan hanya informasi dari context.

Jika jawabannya tidak ada pada context,
jawab:

Maaf, saya tidak menemukan informasi tersebut pada dokumen.

Riwayat Percakapan:

{conversation}

Context:

{context}

Pertanyaan:

{question}

Jawaban:
"""

    return prompt