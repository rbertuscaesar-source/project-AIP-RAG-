# app/services/bm25_service.py
import pickle
import os
from rank_bm25 import BM25Okapi

BM25_PATH = "bm25_index.pkl"

def build_bm25(chunks):
    """Build BM25 index dari chunks"""
    try:
        # Tokenisasi sederhana
        tokenized_corpus = [chunk["text"].split() for chunk in chunks]
        bm25 = BM25Okapi(tokenized_corpus)
        
        # Simpan ke file
        with open(BM25_PATH, "wb") as f:
            pickle.dump((bm25, chunks), f)
        
        print(f"✅ BM25 index saved: {len(chunks)} chunks")
        return True
    except Exception as e:
        print(f"⚠️ Error building BM25: {str(e)}")
        return False

def search_bm25(query, top_k=5):
    """Search menggunakan BM25"""
    try:
        if not os.path.exists(BM25_PATH):
            return []
        
        with open(BM25_PATH, "rb") as f:
            bm25, chunks = pickle.load(f)
        
        tokenized_query = query.split()
        scores = bm25.get_scores(tokenized_query)
        
        # Ambil top_k
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                "text": chunks[idx]["text"],
                "metadata": chunks[idx]["metadata"],
                "score": scores[idx],
                "method": "bm25"
            })
        
        return results
    except Exception as e:
        print(f"⚠️ Error searching BM25: {str(e)}")
        return []

def delete_bm25_document(filename):
    """Hapus dokumen dari BM25 index"""
    try:
        if not os.path.exists(BM25_PATH):
            return
        
        with open(BM25_PATH, "rb") as f:
            bm25, chunks = pickle.load(f)
        
        # Filter chunks yang bukan dari filename
        new_chunks = [chunk for chunk in chunks if chunk["metadata"].get("source") != filename]
        
        if len(new_chunks) == 0:
            # Hapus file jika tidak ada chunks tersisa
            os.remove(BM25_PATH)
            print(f"🗑️ BM25 index deleted (no chunks left)")
        else:
            # Rebuild BM25
            tokenized_corpus = [chunk["text"].split() for chunk in new_chunks]
            new_bm25 = BM25Okapi(tokenized_corpus)
            
            with open(BM25_PATH, "wb") as f:
                pickle.dump((new_bm25, new_chunks), f)
            
            print(f"✅ BM25 updated: {len(new_chunks)} chunks remaining")
            
    except Exception as e:
        print(f"⚠️ Error deleting BM25 doc: {str(e)}")

def reset_bm25():
    """Reset BM25 index"""
    try:
        if os.path.exists(BM25_PATH):
            os.remove(BM25_PATH)
            print("🗑️ BM25 reset")
    except Exception as e:
        print(f"⚠️ Error resetting BM25: {str(e)}")