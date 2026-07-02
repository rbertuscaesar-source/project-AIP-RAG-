import chromadb
from sentence_transformers import SentenceTransformer

# Load model embedding
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect ke ChromaDB
client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(
    name="documents"
)


def search_documents(query: str, top_k: int = 5):

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    response = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, meta, distance in zip(documents, metadatas, distances):

        response.append({
            "text": doc,
            "metadata": meta,
            "score": round(distance, 4)
        })

    return response