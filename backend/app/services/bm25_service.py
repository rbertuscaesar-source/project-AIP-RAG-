from rank_bm25 import BM25Okapi

documents = []
metadata = []

bm25 = None


def build_bm25(chunks):

    global bm25
    global documents
    global metadata

    documents = []
    metadata = []

    tokenized = []

    for chunk in chunks:

        documents.append(chunk["text"])
        metadata.append(chunk["metadata"])

        tokenized.append(
            chunk["text"].lower().split()
        )

    bm25 = BM25Okapi(tokenized)


def search_bm25(query, top_k=5):

    if bm25 is None:
        return []

    tokens = query.lower().split()

    scores = bm25.get_scores(tokens)

    ranked = sorted(
        enumerate(scores),
        key=lambda x: x[1],
        reverse=True
    )

    results = []

    for idx, score in ranked[:top_k]:

            results.append({
            "text": documents[idx],
            "metadata": metadata[idx],
            "score": float(score),
            "method": "keyword",
            "final_score": 0
            })

    return results