# app/services/llm_service.py

import os
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# ============================================
# 1. KONFIGURASI GEMINI API
# ============================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("⚠️ GEMINI_API_KEY tidak ditemukan di environment variable.")
    print("📝 Silakan set GEMINI_API_KEY di file .env atau environment.")

MODEL_NAME = "gemini-2.5-flash"

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
    print(f"✅ Gemini API siap menggunakan model: {MODEL_NAME}")
else:
    client = None
    print("⚠️ Gemini API tidak aktif. Set GEMINI_API_KEY di file .env.")


# ============================================
# 2. FUNGSI UTAMA GENERATE ANSWER
# ============================================

def generate_answer(question: str, context: str, history: list) -> str:
    """
    Generate jawaban menggunakan Google Gemini API (google-genai package).
    """

    if client is None:
        print("⚠️ Gemini tidak aktif, coba fallback ke Ollama...")
        try:
            import ollama
            response = ollama.chat(
                model="gemma2:2b",
                messages=[{"role": "user", "content": build_prompt_optimized(question, context, history)}],
                options={"temperature": 0.2, "num_predict": 800}
            )
            raw_answer = response["message"]["content"]
            cleaned_answer = clean_answer(raw_answer)
            return force_step_numbering(cleaned_answer)
        except Exception as e:
            return f"Maaf, terjadi kesalahan: API Gemini tidak aktif dan fallback Ollama gagal. ({str(e)})"

    prompt = build_prompt_optimized(question, context, history)

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=2048,
            )
        )

        raw_answer = response.text
        cleaned_answer = clean_answer(raw_answer)
        formatted_answer = force_step_numbering(cleaned_answer)
        return formatted_answer

    except Exception as e:
        print(f"❌ Error generating answer with Gemini: {str(e)}")
        try:
            import ollama
            print("🔄 Coba fallback ke Ollama...")
            response = ollama.chat(
                model="gemma2:2b",
                messages=[{"role": "user", "content": build_prompt_optimized(question, context, history)}],
                options={"temperature": 0.2, "num_predict": 800}
            )
            raw_answer = response["message"]["content"]
            cleaned_answer = clean_answer(raw_answer)
            return force_step_numbering(cleaned_answer)
        except:
            return f"Maaf, terjadi kesalahan saat memproses jawaban: {str(e)}"


# ============================================
# 3. BUILD PROMPT
# ============================================

def build_prompt_optimized(question: str, context: str, history: list) -> str:
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

    prompt = f"""Anda adalah asisten AI universitas yang membantu mahasiswa memahami SOP kampus.
Jawab HANYA berdasarkan konteks yang diberikan. Sertakan detail lengkap: syarat, prosedur, batas waktu, dan biaya jika ada.

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

--- JAWABAN ---
"""
    return prompt


# ============================================
# 4. FUNGSI FORMATTING
# ============================================

def force_step_numbering(text: str) -> str:
    if not text:
        return text

    lines = text.split('\n')
    step_items = []
    note_items = []
    is_note_section = False
    has_title = False
    title = ""

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

        if trimmed.startswith('**') and trimmed.endswith('**'):
            has_title = True
            title = trimmed
            continue

        lower = trimmed.lower()
        if 'langkah-langkah' in lower or 'langkah langkah' in lower:
            continue
        if 'catatan' in lower or 'note' in lower:
            is_note_section = True
            continue

        if is_note_section:
            clean = trimmed
            for ch in ['•', '-', '*']:
                if clean.startswith(ch):
                    clean = clean[1:].strip()
            if clean:
                note_items.append(clean)
            continue

        clean = trimmed
        for ch in ['•', '-', '*']:
            if clean.startswith(ch):
                clean = clean[1:].strip()

        if re.match(r'^\d+\.', clean):
            clean = re.sub(r'^\d+\.\s*', '', clean)

        is_step = False
        for kw in step_keywords:
            if kw in clean.lower():
                is_step = True
                break

        if len(clean) > 30 and not clean.lower().startswith('catatan'):
            is_step = True

        if any(word in clean.lower() for word in ['melalui', 'dengan', 'untuk', 'pada', 'ke']):
            if len(clean) > 25:
                is_step = True

        if is_step:
            step_items.append(clean)
        else:
            if clean and not clean.lower().startswith('catatan'):
                note_items.append(clean)

    final_lines = []
    final_lines.append(title if has_title else '**Prosedur**')
    final_lines.append('')

    if step_items:
        final_lines.append('**Langkah-langkah:**')
        for i, item in enumerate(step_items, 1):
            if item.lower().startswith('catatan:'):
                continue
            final_lines.append(f'{i}. {item}')
        final_lines.append('')

    if note_items:
        final_lines.append('**Catatan:**')
        for item in note_items:
            clean_note = item
            for ch in ['•', '-', '*']:
                if clean_note.startswith(ch):
                    clean_note = clean_note[1:].strip()
            if clean_note:
                final_lines.append(f'• {clean_note}')

    result_text = '\n'.join(final_lines)
    result_text = re.sub(r'\*\*Langkah-langkah:\*\*\s*\*\*Langkah-langkah:\*\*', '**Langkah-langkah:**', result_text)
    result_text = re.sub(r'\*\*Catatan:\*\*\s*\*\*Catatan:\*\*', '**Catatan:**', result_text)
    result_text = re.sub(r'\d+\.\s*Catatan:', '', result_text, flags=re.IGNORECASE)

    return result_text.strip()


# ============================================
# 5. FUNGSI CLEANING
# ============================================

def clean_answer(answer: str) -> str:
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
    answer = re.sub(r'\n{3,}', '\n\n', answer)
    return answer.strip()
