from fastapi import APIRouter, UploadFile, File
import os
import shutil

router = APIRouter()

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    allowed = [".pdf", ".docx", ".txt"]

    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in allowed:
        return {
            "status": "error",
            "message": "Unsupported file type"
        }

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "status": "success",
        "filename": file.filename
    }