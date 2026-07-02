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

    for i, chunk in enumerate(chunks):

        embedding = model.encode(chunk["text"]).tolist()

        documents.append(chunk["text"])
        embeddings.append(embedding)
        metadatas.append(chunk["metadata"])

        ids.append(
            f'{chunk["metadata"]["source"]}_{chunk["metadata"]["page"]}_{i}'
        )

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(ids)