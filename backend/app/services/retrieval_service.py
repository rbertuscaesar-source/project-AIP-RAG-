import chromadb
from sentence_transformers import SentenceTransformer

from app.services.bm25_service import search_bm25

# Embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# ChromaDB
client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(
    name="documents"
)


def semantic_search(query, top_k=5):

    embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )

    response = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for doc, meta, distance in zip(
        documents,
        metadatas,
        distances
    ):

        response.append({

            "text": doc,

            "metadata": meta,

            "score": distance,

            "method": "semantic"

        })

    return response


def hybrid_search(query, top_k=5):

    semantic = semantic_search(query, top_k)
    keyword = search_bm25(query, top_k)

    fused = {}

    # Semantic Search
    for rank, item in enumerate(semantic):
        key = item["text"]

        if key not in fused:
            fused[key] = item.copy()
            fused[key]["final_score"] = 0

        fused[key]["final_score"] += 1 / (60 + rank)

    # BM25 Search
    for rank, item in enumerate(keyword):
        key = item["text"]

        if key not in fused:
            fused[key] = item.copy()
            fused[key]["final_score"] = 0

        fused[key]["final_score"] += 1 / (60 + rank)

    results = list(fused.values())

    results.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    return results[:top_k]


def get_context(query):

    results = hybrid_search(query)

    if not results:
        return "", []
    if results[0]["method"] == "semantic" and results[0]["score"] > 1.2:
        return "", []

    context = ""
    for item in results:
        context += item["text"] + "\n\n"    

    return context, results