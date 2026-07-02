from fastapi import FastAPI
from app.api.upload import router as upload_router
from app.api.search import router as search_router

app = FastAPI(
    title="Enterprise RAG API",
    version="1.0.0"
)

app.include_router(upload_router, prefix="/api")
app.include_router(search_router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "Enterprise RAG API is running!"
    }