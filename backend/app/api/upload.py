import os
import shutil

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.document_loader import (
    load_pdf,
    load_docx,
    load_txt
)

from app.services.text_splitter import split_text
from app.services.embedding_service import save_embeddings
from app.services.text_splitter import split_text
from app.services.bm25_service import build_bm25

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    allowed_extensions = [".pdf", ".docx", ".txt"]

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="File type not supported. Only PDF, DOCX, and TXT are allowed."
        )

    # Simpan file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Membaca isi dokumen
    if extension == ".pdf":
        pages = load_pdf(file_path)

    elif extension == ".docx":
        pages = load_docx(file_path)

    else:
        pages = load_txt(file_path)

    # Chunking
    all_chunks = []

    for page in pages:

        chunks = split_text(page["text"])

        for index, chunk in enumerate(chunks):

            all_chunks.append(
                {
                    "text": chunk,
                    "metadata": {
                        "source": file.filename,
                        "page": page["page"],
                        "chunk": index
                    }
                }
            )

    # Simpan embedding ke ChromaDB
    total_saved = save_embeddings(all_chunks)
    from app.services.bm25_service import build_bm25

    build_bm25(all_chunks)

    return {
        "status": "success",
        "filename": file.filename,
        "total_chunks": len(all_chunks),
        "saved_embeddings": total_saved,
        "preview": all_chunks[:3]
    }