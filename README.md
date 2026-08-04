# 📚 Enterprise RAG Assistant

Enterprise RAG Assistant is an AI-powered **Retrieval-Augmented Generation (RAG)** application designed to help users search and ask questions about **SOP (Standard Operating Procedure)** documents in university or corporate environments.

> 🎓 Built as a final project for AI Project Management course — Universitas Nusantara Teknologi

---

## ✨ Features

- 📄 **Document Upload** — Supports PDF, DOCX, TXT formats (multi-file upload)
- 🔍 **Hybrid Search** — Combines Semantic Search (Gemini Embedding) and Keyword Search (BM25)
- 💬 **AI Chat** — Interactive Q&A based on document context using Google Gemini 2.5 Flash
- 📋 **Structured Responses** — Numbered steps and bullet point notes with source citation
- 📂 **Document Sidebar** — View all uploaded documents and chunk count
- 🗑️ **Delete Documents** — Remove from database and physical folder
- 📤 **Export Chat History** — Export to TXT and PDF formats
- 📱 **Responsive UI** — Works on both desktop and mobile browsers
- 🌐 **Single Port** — Frontend served directly from backend (port 8000)

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** — Python API Framework
- **Google Gemini 2.5 Flash** — LLM for answer generation
- **Google Gemini Embedding** (`gemini-embedding-001`) — Vector embedding model
- **ChromaDB** — Vector Database for semantic search
- **BM25** (`rank-bm25`) — Keyword search
- **PyMuPDF + python-docx** — Document parsing (PDF, DOCX, TXT)

### Frontend
- **React + Vite** — UI Framework
- **Axios** — HTTP Client
- **CSS3** — Responsive styling with gradients and animations

---

## 🚀 Installation & Running

### 1. Clone Repository

```bash
git clone https://github.com/rbertuscaesar-source/project-AIP-RAG-.git
cd project-AIP-RAG-
```

### 2. Setup Environment

Copy the example env file:

```bash
cp .env.example backend/.env
```

Edit `backend/.env`:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your free API key at: **https://aistudio.google.com/apikey**

### 3. Backend

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies (from backend folder)
cd backend
pip install -r requirements.txt

# Run backend server
uvicorn app.main:app --reload
```

### 4. Frontend (Development only)

```bash
cd frontend
npm install
npm run dev
```

> For production/demo, skip this step — the backend already serves the built frontend at port 8000.

### 5. Build Frontend (for production)

```bash
cd frontend
npm install
npm run build
```

### 6. Open Application

- **Full app (recommended):** http://localhost:8000
- **Frontend dev only:** http://localhost:5173

---

## 🌐 Public Access (Demo)

To share with others without deploying, use ngrok:

```bash
# Install ngrok from https://ngrok.com/download
# Add your authtoken first:
ngrok config add-authtoken YOUR_TOKEN

# Expose the app (use static domain if available):
ngrok http --url=your-static-domain.ngrok-free.dev 8000
```

Share the generated URL with anyone — no installation needed on their end. Works on both desktop and mobile browsers.

---

## 📁 Project Structure

```
project-AIP-RAG-/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI route handlers
│   │   ├── services/     # RAG pipeline, LLM, embedding, retrieval
│   │   └── main.py       # App entry point + static file serving
│   ├── uploads/          # Uploaded SOP documents
│   ├── chroma_db/        # Vector database (auto-generated)
│   ├── requirements.txt  # Python dependencies
│   └── .env              # API keys (not committed)
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   └── services/     # API service layer
│   └── dist/             # Built frontend (served by backend)
├── .env.example          # Environment variable template
└── README.md
```

---

## 📸 Screenshots

### Desktop
<img width="955" height="443" alt="Enterprise RAG Assistant Desktop UI" src="https://github.com/user-attachments/assets/407f1e1f-31d8-4bf9-af5f-edd9a8a82b67" />

---

## 👥 Team

Built by students of Universitas Nusantara Teknologi as part of the AI Project Management course (2024/2025).