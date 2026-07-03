import uuid
import chromadb
from sentence_transformers import SentenceTransformer

# Load model sekali saat aplikasi berjalan
model = SentenceTransformer("all-MiniLM-L6-v2")

# Inisialisasi ChromaDB
client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(
    name="documents"
)


def save_embeddings(chunks):

    documents = []
    embeddings = []
    metadatas = []
    ids = []

    for chunk in chunks:
        
        embedding = model.encode(chunk["text"]).tolist()

        documents.append(chunk["text"])
        embeddings.append(embedding)
        metadatas.append(chunk["metadata"])

        # ID unik
        ids.append(str(uuid.uuid4()))

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(ids)