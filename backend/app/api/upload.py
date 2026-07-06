import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.document_loader import load_pdf, load_docx, load_txt
from app.services.text_splitter import split_text
from app.services.embedding_service import save_embeddings
from app.services.bm25_service import build_bm25
from app.services.document_service import get_documents, delete_document

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload dan proses file PDF, DOCX, atau TXT.
    Jika file dengan nama yang sama sudah ada, akan dihapus dan diganti.
    """
    
    # ============================================
    # 1. VALIDASI EKSTENSI FILE
    # ============================================
    allowed_extensions = [".pdf", ".docx", ".txt"]
    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Only {', '.join(allowed_extensions)} are allowed."
        )

    # ============================================
    # 2. CEK APAKAH FILE SUDAH PERNAH DIUPLOAD
    # ============================================
    try:
        existing_docs = get_documents()
        for doc in existing_docs:
            if doc.get("filename") == file.filename:
                print(f"⚠️ File '{file.filename}' sudah ada, menghapus yang lama...")
                
                # Hapus dari database dan file fisik
                deleted = delete_document(file.filename)
                print(f"✅ File lama dihapus: {deleted} chunk terhapus")
                break
    except Exception as e:
        print(f"⚠️ Gagal cek dokumen existing: {str(e)}")
        # Lanjutkan saja

    # ============================================
    # 3. SIMPAN FILE KE DISK
    # ============================================
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"✅ File saved: {file_path}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {str(e)}"
        )

    # ============================================
    # 4. BACA ISI DOKUMEN
    # ============================================
    try:
        if extension == ".pdf":
            pages = load_pdf(file_path)
        elif extension == ".docx":
            pages = load_docx(file_path)
        else:  # .txt
            pages = load_txt(file_path)
    except Exception as e:
        # Hapus file yang sudah disimpan jika gagal baca
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read document: {str(e)}"
        )

    # ============================================
    # 5. CEK APAKAH DOKUMEN TERBACA
    # ============================================
    if not pages:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail=f"Gagal membaca file '{file.filename}'. "
                   f"Pastikan file bukan hasil scan/gambar dan memiliki teks yang bisa diekstrak."
        )

    print(f"✅ Jumlah halaman terbaca: {len(pages)}")
    print(f"✅ Sample teks halaman 1: {pages[0]['text'][:200]}...")

    # ============================================
    # 6. CHUNKING (PECAH DOKUMEN)
    # ============================================
    all_chunks = []
    total_text_length = 0

    for page in pages:
        page_text = page["text"].strip()
        
        # Skip halaman kosong
        if not page_text:
            print(f"⚠️ Halaman {page['page']} kosong, dilewati.")
            continue
        
        total_text_length += len(page_text)
        
        # Split teks per halaman
        chunks = split_text(page_text)
        
        for index, chunk in enumerate(chunks):
            # Skip chunk kosong
            if not chunk or not chunk.strip():
                continue
                
            all_chunks.append({
                "text": chunk.strip(),
                "metadata": {
                    "source": file.filename,
                    "page": page["page"],
                    "chunk": index,
                    "total_pages": len(pages)
                }
            })

    # ============================================
    # 7. CEK APAKAH CHUNK TERBENTUK
    # ============================================
    if not all_chunks:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail=f"Tidak ada teks yang bisa diekstrak dari '{file.filename}'. "
                   f"Total halaman: {len(pages)}, Total karakter: {total_text_length}. "
                   f"Pastikan file memiliki teks yang terbaca."
        )

    print(f"✅ Jumlah chunk terbentuk: {len(all_chunks)}")
    print(f"✅ Total karakter: {total_text_length}")
    print(f"✅ Rata-rata per chunk: {total_text_length / len(all_chunks):.0f} karakter")
    print(f"✅ Contoh chunk pertama: {all_chunks[0]['text'][:150]}...")

    # ============================================
    # 8. SIMPAN EMBEDDING KE CHROMADB
    # ============================================
    try:
        total_saved = save_embeddings(all_chunks)
        print(f"✅ Embedding tersimpan: {total_saved} chunk")
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Gagal menyimpan embedding: {str(e)}"
        )

    # ============================================
    # 9. CEK APAKAH BERHASIL DISIMPAN
    # ============================================
    if total_saved == 0:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail="Gagal menyimpan embeddings ke database (0 chunk tersimpan)."
        )

    # ============================================
    # 10. BUILD BM25 INDEX
    # ============================================
    try:
        build_bm25(all_chunks)
        print(f"✅ BM25 index berhasil dibangun")
    except Exception as e:
        print(f"⚠️ Warning: Gagal build BM25: {str(e)}")
        # Tidak dianggap fatal, lanjutkan

    # ============================================
    # 11. PREVIEW UNTUK RESPONSE
    # ============================================
    preview = []
    for chunk in all_chunks[:3]:
        preview.append({
            "text": chunk["text"][:200] + ("..." if len(chunk["text"]) > 200 else ""),
            "metadata": chunk["metadata"]
        })

    # ============================================
    # 12. RETURN RESPONSE SUKSES
    # ============================================
    return {
        "status": "success",
        "filename": file.filename,
        "total_pages": len(pages),
        "total_chunks": len(all_chunks),
        "total_characters": total_text_length,
        "saved_embeddings": total_saved,
        "preview": preview,
        "message": f"File '{file.filename}' berhasil diupload dan diproses dengan {len(all_chunks)} chunk."
    }