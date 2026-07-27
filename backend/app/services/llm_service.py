# app/services/llm_service.py

import os
import re
import google.generativeai as genai

# ============================================
# 1. KONFIGURASI GEMINI API
# ============================================

# Ambil API key dari environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("⚠️ GEMINI_API_KEY tidak ditemukan di environment variable.")
    print("📝 Silakan set GEMINI_API_KEY di file .env atau environment.")
    # Fallback: bisa pakai Ollama jika Gemini tidak tersedia
    # raise ValueError("GEMINI_API_KEY environment variable not set")

# Konfigurasi Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Pilih model (gratis dan cepat)
# Pilihan model: "gemini-2.5-flash" (terbaru), "gemini-1.5-flash", "gemini-2.5-pro"
MODEL_NAME = "gemini-2.5-flash"  # Bisa ganti ke "gemini-1.5-flash" atau "gemini-2.5-pro"

if GEMINI_API_KEY:
    model = genai.GenerativeModel(MODEL_NAME)
    print(f"✅ Gemini API siap menggunakan model: {MODEL_NAME}")
else:
    model = None
    print("⚠️ Gemini API tidak aktif. Gunakan fallback atau set API key.")


# ============================================
# 2. FUNGSI UTAMA GENERATE ANSWER
# ============================================

def generate_answer(question: str, context: str, history: list) -> str:
    """
    Generate jawaban menggunakan Google Gemini API.
    """
    
    # Jika Gemini tidak aktif, coba fallback ke Ollama (jika ada)
    if model is None:
        print("⚠️ Gemini tidak aktif, coba fallback ke Ollama...")
        try:
            # Coba panggil Ollama sebagai fallback
            import ollama
            response = ollama.chat(
                model="gemma2:2b",
                messages=[{"role": "user", "content": build_prompt_optimized(question, context, history)}],
                options={"temperature": 0.2, "num_predict": 800}
            )
            raw_answer = response["message"]["content"]
            cleaned_answer = clean_gemma_answer(raw_answer)
            return force_step_numbering(cleaned_answer)
        except:
            return "Maaf, terjadi kesalahan: API Gemini tidak aktif dan fallback Ollama gagal."
    
    # Build prompt
    prompt = build_prompt_optimized(question, context, history)
    
    try:
        # Panggil Gemini API
        response = model.generate_content(prompt)
        raw_answer = response.text
        
        # Clean dan format (pakai fungsi yang sudah ada)
        cleaned_answer = clean_gemma_answer(raw_answer)
        formatted_answer = force_step_numbering(cleaned_answer)
        
        return formatted_answer
        
    except Exception as e:
        print(f"❌ Error generating answer with Gemini: {str(e)}")
        
        # Coba fallback jika Gemini gagal
        try:
            import ollama
            print("🔄 Coba fallback ke Ollama...")
            response = ollama.chat(
                model="gemma2:2b",
                messages=[{"role": "user", "content": build_prompt_optimized(question, context, history)}],
                options={"temperature": 0.2, "num_predict": 800}
            )
            raw_answer = response["message"]["content"]
            cleaned_answer = clean_gemma_answer(raw_answer)
            return force_step_numbering(cleaned_answer)
        except:
            return f"Maaf, terjadi kesalahan saat memproses jawaban: {str(e)}"


# ============================================
# 3. SYSTEM PROMPT (SAMA SEPERTI SEBELUMNYA)
# ============================================

def get_system_prompt() -> str:
    """
    System prompt yang dioptimalkan.
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


# ============================================
# 4. BUILD PROMPT (SAMA SEPERTI SEBELUMNYA)
# ============================================

def build_prompt_optimized(question: str, context: str, history: list) -> str:
    """
    Build prompt yang dioptimalkan.
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


# ============================================
# 5. FUNGSI FORMATTING (SAMA SEPERTI SEBELUMNYA)
# ============================================

def force_step_numbering(text: str) -> str:
    """
    MEMAKSA FORMAT NOMOR LANGKAH DARI BACKEND
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
            result.append(title)
            continue
        
        lower = trimmed.lower()
        if 'langkah-langkah' in lower or 'langkah langkah' in lower:
            continue
        if 'catatan' in lower or 'note' in lower:
            is_note_section = True
            continue
        
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
        
        clean = trimmed
        if clean.startswith('•'):
            clean = clean[1:].strip()
        if clean.startswith('-'):
            clean = clean[1:].strip()
        if clean.startswith('*'):
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
    
    if has_title:
        final_lines.append(title)
    else:
        final_lines.append('**Prosedur**')
    
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
            if clean_note.startswith('•'):
                clean_note = clean_note[1:].strip()
            if clean_note.startswith('-'):
                clean_note = clean_note[1:].strip()
            if clean_note.startswith('*'):
                clean_note = clean_note[1:].strip()
            if clean_note:
                final_lines.append(f'• {clean_note}')
    
    result_text = '\n'.join(final_lines)
    
    result_text = re.sub(r'\*\*Langkah-langkah:\*\*\s*\*\*Langkah-langkah:\*\*', '**Langkah-langkah:**', result_text)
    result_text = re.sub(r'\*\*Catatan:\*\*\s*\*\*Catatan:\*\*', '**Catatan:**', result_text)
    result_text = re.sub(r'\d+\.\s*Catatan:', '', result_text, flags=re.IGNORECASE)
    
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


# ============================================
# 6. FUNGSI CLEANING (SAMA SEPERTI SEBELUMNYA)
# ============================================

def clean_gemma_answer(answer: str) -> str:
    """
    Membersihkan jawaban.
    """
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