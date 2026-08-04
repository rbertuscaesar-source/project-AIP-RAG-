# app/services/embedding_service.py

import os
import uuid
import chromadb
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = "gemini-embedding-001"

# Inisialisasi Gemini client
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Inisialisasi ChromaDB
chroma_client = chromadb.PersistentClient(path="chroma_db")

collection = chroma_client.get_or_create_collection(
    name="documents"
)


def get_embedding(text: str) -> list:
    """
    Generate embedding menggunakan Gemini Embedding API.
    """
    response = gemini_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )
    return response.embeddings[0].values


def save_embeddings(chunks):
    documents = []
    embeddings = []
    metadatas = []
    ids = []

    for chunk in chunks:
        try:
            embedding = get_embedding(chunk["text"])
            documents.append(chunk["text"])
            embeddings.append(embedding)
            metadatas.append(chunk["metadata"])
            ids.append(str(uuid.uuid4()))
        except Exception as e:
            print(f"❌ Error embedding chunk: {str(e)}")
            continue

    if documents:
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        print(f"✅ Saved {len(ids)} embeddings to ChromaDB")

    return len(ids)