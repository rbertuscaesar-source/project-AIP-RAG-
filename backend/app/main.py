from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.upload import router as upload_router
from app.api.search import router as search_router
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.export import router as export_router

app = FastAPI(title="Enterprise RAG API", version="1.0.0")

app.include_router(upload_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(export_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Enterprise RAG API is running!"}