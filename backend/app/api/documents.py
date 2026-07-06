# app/api/documents.py

from fastapi import APIRouter, HTTPException
from app.services.document_service import (
    get_documents, 
    delete_document, 
    delete_all_documents,
    is_file_exists,
    get_document_file_path
)

router = APIRouter()


@router.get("/documents")
def list_documents():
    """Daftar semua dokumen yang sudah diupload"""
    try:
        docs = get_documents()
        
        # Tambahkan info apakah file fisik masih ada
        for doc in docs:
            filename = doc.get("filename")
            doc["file_exists"] = is_file_exists(filename)
            doc["file_path"] = get_document_file_path(filename) if doc["file_exists"] else None
        
        print(f"📄 Jumlah dokumen: {len(docs)}")
        return {
            "status": "success",
            "documents": docs
        }
    except Exception as e:
        print(f"❌ Error get documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get documents: {str(e)}"
        )


@router.delete("/documents/{filename}")
def remove_document(filename: str):
    """Hapus dokumen berdasarkan nama file (termasuk file fisik)"""
    print(f"🗑️ Mencoba menghapus: {filename}")
    
    try:
        # Cek apakah file ada di database
        deleted = delete_document(filename)
        
        if deleted == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Document '{filename}' not found in database."
            )
        
        # Cek apakah file fisik masih ada setelah penghapusan
        file_still_exists = is_file_exists(filename)
        
        return {
            "status": "success",
            "message": f"Document '{filename}' deleted successfully.",
            "deleted_chunks": deleted,
            "file_deleted": not file_still_exists,
            "file_path": get_document_file_path(filename) if file_still_exists else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error delete document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.delete("/documents")
def remove_all_documents():
    """Hapus SEMUA dokumen (termasuk semua file fisik) - HATI-HATI!"""
    try:
        deleted = delete_all_documents()
        
        return {
            "status": "success",
            "message": f"All documents deleted successfully.",
            "deleted_chunks": deleted,
            "warning": "This action cannot be undone!"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete all documents: {str(e)}"
        )