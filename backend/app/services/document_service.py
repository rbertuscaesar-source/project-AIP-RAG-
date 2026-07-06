# app/services/document_service.py

import os
import chromadb
from app.services.embedding_service import collection
from app.services.bm25_service import delete_bm25_document

# Folder tempat file disimpan
UPLOAD_FOLDER = "uploads"


def get_documents():
    """
    Mendapatkan daftar semua dokumen yang tersimpan di ChromaDB
    """
    try:
        # Ambil semua metadata dari ChromaDB
        results = collection.get()
        
        # Ekstrak unique filenames dari metadata
        documents = {}
        for meta in results['metadatas']:
            source = meta.get('source', 'unknown')
            if source not in documents:
                documents[source] = {
                    "filename": source,
                    "chunks": 0,
                    "pages": set()
                }
            documents[source]["chunks"] += 1
            if 'page' in meta:
                documents[source]["pages"].add(meta['page'])
        
        # Konversi set ke list
        result_list = []
        for doc in documents.values():
            doc["pages"] = sorted(list(doc["pages"]))
            result_list.append(doc)
        
        print(f"📄 Dokumen ditemukan: {len(result_list)}")
        return result_list
        
    except Exception as e:
        print(f"❌ Error get_documents: {str(e)}")
        return []


def delete_document(filename: str):
    """
    Menghapus semua chunk dari dokumen berdasarkan nama file
    DAN menghapus file fisik dari folder uploads/
    
    Returns: jumlah chunk yang dihapus
    """
    try:
        # ============================================
        # 1. HAPUS DARI CHROMADB
        # ============================================
        results = collection.get()
        
        ids_to_delete = []
        for i, meta in enumerate(results['metadatas']):
            if meta.get('source') == filename:
                ids_to_delete.append(results['ids'][i])
        
        if not ids_to_delete:
            print(f"⚠️ Dokumen '{filename}' tidak ditemukan di database")
            return 0
        
        # Hapus dari ChromaDB
        collection.delete(ids=ids_to_delete)
        print(f"🗑️ Menghapus {len(ids_to_delete)} chunk dari ChromaDB")
        
        # ============================================
        # 2. HAPUS DARI BM25 (jika ada)
        # ============================================
        try:
            delete_bm25_document(filename)
            print(f"🗑️ Menghapus dari BM25 index")
        except Exception as e:
            print(f"⚠️ Gagal hapus dari BM25: {str(e)}")
        
        # ============================================
        # 3. HAPUS FILE FISIK DARI FOLDER UPLOADS
        # ============================================
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"🗑️ File fisik dihapus: {file_path}")
            except Exception as e:
                print(f"⚠️ Gagal menghapus file fisik: {str(e)}")
                # Tidak dianggap fatal, tetap return success
        else:
            print(f"⚠️ File fisik tidak ditemukan: {file_path}")
        
        return len(ids_to_delete)
        
    except Exception as e:
        print(f"❌ Error delete_document: {str(e)}")
        raise


def delete_all_documents():
    """
    Menghapus SEMUA dokumen (hati-hati!)
    Termasuk menghapus semua file fisik di folder uploads/
    """
    try:
        # ============================================
        # 1. AMBIL SEMUA ID DARI CHROMADB
        # ============================================
        results = collection.get()
        ids = results['ids']
        
        if not ids:
            print("⚠️ Database kosong, tidak ada yang dihapus")
            return 0
        
        # ============================================
        # 2. AMBIL DAFTAR FILENAME UNTUK DIHAPUS FILENYA
        # ============================================
        filenames = set()
        for meta in results['metadatas']:
            source = meta.get('source')
            if source:
                filenames.add(source)
        
        # ============================================
        # 3. HAPUS DARI CHROMADB
        # ============================================
        collection.delete(ids=ids)
        print(f"🗑️ Menghapus semua {len(ids)} chunk dari ChromaDB")
        
        # ============================================
        # 4. RESET BM25
        # ============================================
        try:
            from app.services.bm25_service import reset_bm25
            reset_bm25()
            print(f"🗑️ BM25 direset")
        except Exception as e:
            print(f"⚠️ Gagal reset BM25: {str(e)}")
        
        # ============================================
        # 5. HAPUS SEMUA FILE FISIK DI FOLDER UPLOADS
        # ============================================
        deleted_files = 0
        for filename in filenames:
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    deleted_files += 1
                    print(f"🗑️ File fisik dihapus: {file_path}")
                except Exception as e:
                    print(f"⚠️ Gagal hapus file {filename}: {str(e)}")
        
        print(f"🗑️ Total {deleted_files} file fisik dihapus")
        
        return len(ids)
        
    except Exception as e:
        print(f"❌ Error delete_all_documents: {str(e)}")
        raise


def get_document_file_path(filename: str):
    """
    Mendapatkan path lengkap file fisik
    """
    return os.path.join(UPLOAD_FOLDER, filename)


def is_file_exists(filename: str):
    """
    Cek apakah file fisik masih ada
    """
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    return os.path.exists(file_path)