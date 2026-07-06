# app/services/retrieval_service.py

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

    documents = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []
    distances = results["distances"][0] if results["distances"] else []

    for doc, meta, distance in zip(documents, metadatas, distances):
        # Konversi distance ke similarity (0-1)
        similarity = 1 / (1 + distance)
        
        response.append({
            "text": doc,
            "metadata": meta,
            "score": similarity,
            "distance": distance,
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
        fused[key]["final_score"] += item["score"] * 0.6

    # BM25 Search
    for rank, item in enumerate(keyword):
        key = item["text"]
        if key not in fused:
            fused[key] = item.copy()
            fused[key]["final_score"] = 0
        bm25_score = item.get("score", 0)
        if isinstance(bm25_score, (int, float)):
            fused[key]["final_score"] += bm25_score * 0.4

    results = list(fused.values())
    results.sort(key=lambda x: x["final_score"], reverse=True)

    return results[:top_k]


def get_context(query):
    results = hybrid_search(query)
    
    if not results:
        return "", []
    
    # Filter: Hanya ambil hasil dengan score > 0.3
    filtered_results = [r for r in results if r.get("final_score", 0) > 0.3]
    
    if not filtered_results:
        print(f"⚠️ Tidak ada hasil dengan score > 0.3")
        return "", []
    
    # Hapus duplikat teks
    seen_texts = set()
    unique_results = []
    for item in filtered_results:
        text = item["text"].strip()
        # Hapus teks yang terlalu pendek (kurang dari 20 karakter)
        if len(text) < 20:
            continue
        # Hapus duplikat
        if text not in seen_texts:
            seen_texts.add(text)
            unique_results.append(item)
    
    # Build context dengan format lebih bersih
    context_parts = []
    for i, item in enumerate(unique_results[:3]):  # Maks 3 chunk teratas
        text = item["text"].strip()
        
        # Perbaiki teks yang terpotong
        if text and not text[-1] in '.!?':
            last_sentence_end = max(
                text.rfind('. '),
                text.rfind('! '),
                text.rfind('? '),
                text.rfind('.\n'),
                text.rfind('!\n'),
                text.rfind('?\n')
            )
            if last_sentence_end > 0:
                text = text[:last_sentence_end + 1]
        
        # Hapus teks yang tidak informatif
        if text.lower().startswith("sop ini menetapkan") or text.lower().startswith("sop ini mengatur"):
            continue
        
        # Tambahkan metadata untuk konteks
        source = item["metadata"].get("source", "unknown")
        page = item["metadata"].get("page", "?")
        context_parts.append(f"[Dari {source}, halaman {page}]\n{text}")
    
    context = "\n\n".join(context_parts)
    
    return context, unique_results