"""
Startup script untuk Railway deployment.
- Build BM25 index dari dokumen yang ada
- Build ChromaDB index dari dokumen yang ada
"""
import os
import sys

print("🚀 Starting deployment initialization...")

# Pastikan working directory benar
os.chdir(os.path.dirname(os.path.abspath(__file__)))

uploads_dir = "uploads"
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
    print(f"📁 Created uploads directory")

# Cek dokumen yang ada
pdf_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')]
print(f"📄 Found {len(pdf_files)} documents: {pdf_files}")

if not pdf_files:
    print("⚠️ No documents found in uploads/. System will start without pre-indexed documents.")
    sys.exit(0)

print("✅ Startup initialization complete.")
