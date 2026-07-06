# app/services/llm_service.py

import ollama
import re


def generate_answer(question: str, context: str, history: list) -> str:
    """
    Generate jawaban menggunakan Ollama dengan model Gemma2:2b
    """
    
    prompt = build_prompt_optimized(question, context, history)
    
    try:
        response = ollama.chat(
            model="gemma2:2b",
            messages=[
                {
                    "role": "system",
                    "content": get_system_prompt()
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.2,
                "top_p": 0.8,
                "num_predict": 800,
                "repeat_penalty": 1.1,
            }
        )
        
        raw_answer = response["message"]["content"]
        cleaned_answer = clean_gemma_answer(raw_answer)
        
        # 🔥 FORMAT ULANG DARI BACKEND
        formatted_answer = force_step_numbering(cleaned_answer)
        
        return formatted_answer
        
    except Exception as e:
        print(f"❌ Error generating answer: {str(e)}")
        return f"Maaf, terjadi kesalahan saat memproses jawaban: {str(e)}"


def get_system_prompt() -> str:
    """
    System prompt yang dioptimalkan untuk Gemma2:2b
    """
    return """
Anda adalah asisten AI yang membantu menjawab pertanyaan tentang SOP universitas.

**WAJIB:**
1. Jawab HANYA berdasarkan konteks.
2. Gunakan format EXACT seperti di bawah ini:

CONTOH FORMAT WAJIB:
**Judul Prosedur**

Langkah-langkah:
1. Teks langkah pertama
2. Teks langkah kedua
3. Teks langkah ketiga

Catatan:
• Catatan penting 1
• Catatan penting 2

JANGAN gunakan format lain!
"""


def build_prompt_optimized(question: str, context: str, history: list) -> str:
    """
    Build prompt yang dioptimalkan untuk Gemma2:2b
    """
    
    history_text = ""
    if history and len(history) > 0:
        history_text = "\n--- Riwayat Percakapan ---\n"
        for msg in history[-4:]:
            role = "User" if msg.get("role") == "user" else "Assistant"
            content = msg.get("content", "")
            history_text += f"{role}: {content}\n"
        history_text += "---\n\n"
    
    if len(context) > 2500:
        context = context[:2500] + "..."
    
    prompt = f"""
{history_text}

--- KONTEKS ---
{context}

--- PERTANYAAN ---
{question}

--- FORMAT WAJIB ---
**Judul Prosedur**

Langkah-langkah:
1. ...
2. ...
3. ...

Catatan:
• ...

--- JAWABAN (PAKAI FORMAT DI ATAS, JANGAN PAKAI FORMAT LAIN) ---
"""
    
    return prompt


def force_step_numbering(text: str) -> str:
    """
    🔥 MEMAKSA FORMAT NOMOR LANGKAH DARI BACKEND
    """
    if not text:
        return text
    
    lines = text.split('\n')
    result = []
    step_items = []
    note_items = []
    is_note_section = False
    has_title = False
    title = ""
    
    # 🔥 Keyword untuk mendeteksi langkah
    step_keywords = [
        'mengajukan', 'melakukan', 'verifikasi', 'pengajuan', 'proses', 
        'login', 'upload', 'isi', 'pilih', 'masuk', 'daftar', 'memesan',
        'menghubungi', 'menentukan', 'menggunakan', 'membuat', 'mengisi',
        'menyiapkan', 'menyerahkan', 'menunggu', 'konfirmasi', 'pemesanan',
        'penggunaan', 'pembayaran', 'pendaftaran', 'memperoleh', 'mendapatkan'
    ]
    
    for line in lines:
        trimmed = line.strip()
        
        if not trimmed:
            continue
        
        # 🔥 Deteksi judul (yang pakai **)
        if trimmed.startswith('**') and trimmed.endswith('**'):
            has_title = True
            title = trimmed
            result.append(title)
            continue
        
        # 🔥 Deteksi "Langkah-langkah:" atau "Catatan:"
        lower = trimmed.lower()
        if 'langkah-langkah' in lower or 'langkah langkah' in lower:
            continue
        if 'catatan' in lower or 'note' in lower:
            is_note_section = True
            continue
        
        # 🔥 Jika di section catatan
        if is_note_section:
            clean = trimmed
            if clean.startswith('•'):
                clean = clean[1:].strip()
            if clean.startswith('-'):
                clean = clean[1:].strip()
            if clean.startswith('*'):
                clean = clean[1:].strip()
            if clean:
                note_items.append(clean)
            continue
        
        # 🔥 Jika ini bullet point, ubah jadi langkah
        clean = trimmed
        if clean.startswith('•'):
            clean = clean[1:].strip()
        if clean.startswith('-'):
            clean = clean[1:].strip()
        if clean.startswith('*'):
            clean = clean[1:].strip()
        
        # 🔥 Hapus nomor yang sudah ada
        if re.match(r'^\d+\.', clean):
            clean = re.sub(r'^\d+\.\s*', '', clean)
        
        # 🔥 Deteksi apakah ini langkah
        is_step = False
        
        # Cek dengan keyword
        for kw in step_keywords:
            if kw in clean.lower():
                is_step = True
                break
        
        # Jika panjang > 30 karakter dan bukan catatan, anggap langkah
        if len(clean) > 30 and not clean.lower().startswith('catatan'):
            is_step = True
        
        # 🔥 Jika ini kalimat yang mengandung "melalui", "dengan", "untuk"
        if any(word in clean.lower() for word in ['melalui', 'dengan', 'untuk', 'pada', 'ke']):
            if len(clean) > 25:
                is_step = True
        
        if is_step:
            step_items.append(clean)
        else:
            if clean and not clean.lower().startswith('catatan'):
                note_items.append(clean)
    
    # 🔥 Bangun hasil akhir
    final_lines = []
    
    # Tambahkan judul
    if has_title:
        final_lines.append(title)
    else:
        final_lines.append('**Prosedur**')
    
    final_lines.append('')
    
    # 🔥 TAMBAHKAN LANGKAH-LANGKAH (WAJIB)
    if step_items:
        final_lines.append('**Langkah-langkah:**')
        for i, item in enumerate(step_items, 1):
            # Pastikan item tidak dimulai dengan "Catatan:"
            if item.lower().startswith('catatan:'):
                continue
            final_lines.append(f'{i}. {item}')
        final_lines.append('')
    
    # Tambahkan catatan
    if note_items:
        final_lines.append('**Catatan:**')
        for item in note_items:
            # Hapus bullet yang sudah ada
            clean_note = item
            if clean_note.startswith('•'):
                clean_note = clean_note[1:].strip()
            if clean_note.startswith('-'):
                clean_note = clean_note[1:].strip()
            if clean_note.startswith('*'):
                clean_note = clean_note[1:].strip()
            if clean_note:
                final_lines.append(f'• {clean_note}')
    
    # 🔥 Gabungkan
    result_text = '\n'.join(final_lines)
    
    # 🔥 Hapus duplikasi
    result_text = re.sub(r'\*\*Langkah-langkah:\*\*\s*\*\*Langkah-langkah:\*\*', '**Langkah-langkah:**', result_text)
    result_text = re.sub(r'\*\*Catatan:\*\*\s*\*\*Catatan:\*\*', '**Catatan:**', result_text)
    
    # 🔥 Hapus "Catatan:" yang ada di tengah langkah
    result_text = re.sub(r'\d+\.\s*Catatan:', '', result_text, flags=re.IGNORECASE)
    
    # 🔥 Jika tidak ada "Langkah-langkah:" tapi ada step_items, tambahkan
    if step_items and '**Langkah-langkah:**' not in result_text:
        lines2 = result_text.split('\n')
        new_lines = []
        inserted = False
        for line in lines2:
            if line.strip().startswith('**Catatan:**') and not inserted:
                new_lines.append('**Langkah-langkah:**')
                for i, item in enumerate(step_items, 1):
                    new_lines.append(f'{i}. {item}')
                new_lines.append('')
                inserted = True
            new_lines.append(line)
        if not inserted:
            result_text = f"**Langkah-langkah:**\n"
            for i, item in enumerate(step_items, 1):
                result_text += f"{i}. {item}\n"
            result_text += "\n" + result_text
    
    return result_text.strip()


def clean_gemma_answer(answer: str) -> str:
    """
    Membersihkan jawaban dari Gemma
    """
    # Hapus kata pengantar
    patterns = [
        r'^Berdasarkan konteks,?',
        r'^Dari konteks,?',
        r'^Menurut konteks,?',
        r'^Jawaban:?',
        r'^Answer:?',
        r'^Berikut adalah?',
        r'^Berikut ini?',
    ]
    for p in patterns:
        answer = re.sub(p, '', answer, flags=re.IGNORECASE)
    
    # Hapus spasi berlebih
    answer = re.sub(r'\n{3,}', '\n\n', answer)
    
    return answer.strip()