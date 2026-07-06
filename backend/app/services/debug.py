# app/services/debug.py
from app.services.embedding_service import collection

def check_database():
    """Cek isi database ChromaDB"""
    count = collection.count()
    print(f"📊 Total dokumen di ChromaDB: {count}")
    
    if count == 0:
        print("⚠️ DATABASE KOSONG! Upload file dulu.")
        return
    
    # Ambil sample
    sample = collection.get(limit=3)
    for i, doc in enumerate(sample['documents']):
        print(f"\n📄 Sample {i+1}:")
        print(f"  Teks: {doc[:150]}...")
        print(f"  Metadata: {sample['metadatas'][i]}")