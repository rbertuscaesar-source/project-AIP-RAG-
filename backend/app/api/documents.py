from fastapi import APIRouter, HTTPException

from app.services.document_service import (
    get_documents,
    delete_document
)

router = APIRouter()


@router.get("/documents")
def list_documents():

    return {
        "status": "success",
        "documents": get_documents()
    }


@router.delete("/documents/{filename}")
def remove_document(filename: str):

    deleted = delete_document(filename)

    if deleted == 0:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return {
        "status": "success",
        "deleted_chunks": deleted
    }