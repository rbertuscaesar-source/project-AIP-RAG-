# app/services/retrieval_service.py

import os
import chromadb
from google import genai
from dotenv import load_dotenv
from app.services.bm25_service import search_bm25

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = "gemini-embedding-001"

# Inisialisasi Gemini client
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# ChromaDB
chroma_client = chromadb.PersistentClient(path="chroma_db")

collection = chroma_client.get_or_create_collection(
    name="documents"
)


def get_query_embedding(text: str) -> list:
    """
    Generate embedding untuk query menggunakan Gemini.
    """
    response = gemini_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )
    return response.embeddings[0].values


def semantic_search(query, top_k=5):
    embedding = get_query_embedding(query)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )

    response = []
    documents = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []
    distances = results["distances"][0] if results["distances"] else []

    for doc, meta, distance in zip(documents, metadatas, distances):
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

    for rank, item in enumerate(semantic):
        key = item["text"]
        if key not in fused:
            fused[key] = item.copy()
            fused[key]["final_score"] = 0
        fused[key]["final_score"] += item["score"] * 0.6

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
    # Query expansion
    expanded_query = query
    synonyms = {
        "pinjam": "peminjaman",
        "ruang": "ruang fasilitas kampus",
        "lab": "laboratorium",
        "cuti": "cuti akademik",
        "skripsi": "tugas akhir skripsi",
        "daftar": "pendaftaran",
        "sidang": "ujian sidang tugas akhir",
        "beasiswa": "beasiswa bantuan biaya",
    }
    for word, expansion in synonyms.items():
        if word in query.lower():
            expanded_query = f"{query} {expansion}"
            break

    results = hybrid_search(expanded_query)

    if not results:
        return "", []

    filtered_results = [r for r in results if r.get("final_score", 0) > 0.0]

    if not filtered_results:
        print(f"⚠️ Tidak ada hasil dengan score > 0.0")
        return "", []

    seen_texts = set()
    unique_results = []
    for item in filtered_results:
        text = item["text"].strip()
        if len(text) < 20:
            continue
        if text not in seen_texts:
            seen_texts.add(text)
            unique_results.append(item)

    context_parts = []
    for i, item in enumerate(unique_results[:3]):
        text = item["text"].strip()

        if text and not text[-1] in '.!?':
            last_sentence_end = max(
                text.rfind('. '),
                text.rfind('! '),
                text.rfind('? '),
                text.rfind('.\n'),
            )
            if last_sentence_end > 0:
                text = text[:last_sentence_end + 1]

        if text.lower().startswith("sop ini menetapkan") or text.lower().startswith("sop ini mengatur"):
            continue

        source = item["metadata"].get("source", "unknown")
        page = item["metadata"].get("page", "?")
        context_parts.append(f"[Dari {source}, halaman {page}]\n{text}")

    context = "\n\n".join(context_parts)
    return context, unique_results