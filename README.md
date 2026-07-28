# 📚 Enterprise RAG Assistant

Enterprise RAG Assistant is an AI-powered **Retrieval-Augmented Generation (RAG)** application designed to help users search and ask questions about **SOP (Standard Operating Procedure)** documents in university or corporate environments.

> 🎓 Built as a final project for AI Project Management course — Universitas Nusantara Teknologi

---

## ✨ Features

- 📄 **Document Upload** — Supports PDF, DOCX, TXT formats
- 🔍 **Hybrid Search** — Combines Semantic Search (Embedding) and Keyword Search (BM25)
- 💬 **AI Chat** — Interactive Q&A based on document context using Google Gemini
- 📋 **Structured Responses** — Numbered steps and bullet point notes with source citation
- 📂 **Document Sidebar** — View all uploaded documents and chunk count
- 🗑️ **Delete Documents** — Remove from database and physical folder
- 📤 **Export Chat History** — Export to TXT and PDF formats
- 🎨 **Modern UI** — Responsive with gradients and animations

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** — Python API Framework
- **Google Gemini API** (`gemini-2.5-flash`) — LLM for answer generation
- **ChromaDB** — Vector Database for semantic search
- **Sentence-Transformers** (`all-MiniLM-L6-v2`) — Embedding model
- **BM25** (`rank-bm25`) — Keyword search
- **PyMuPDF + python-docx** — Document parsing

### Frontend
- **React + Vite** — UI Framework
- **Axios** — HTTP Client
- **CSS3** — Modern styling with gradients and animations

---

## 🚀 Installation & Running

### 1. Clone Repository

```bash
git clone https://github.com/rbertuscaesar-source/project-AIP-RAG-.git
cd project-AIP-RAG-
```

### 2. Setup Environment

Copy the example env file and fill in your API key:

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

# Install dependencies
pip install -r requirements.txt

# Run backend server
cd backend
uvicorn app.main:app --reload
```

### 4. Frontend (Development only)

```bash
cd frontend
npm install
npm run dev
```

### 5. Open Application

- **Full app (backend serves frontend):** http://localhost:8000
- **Frontend dev server only:** http://localhost:5173

> For production/demo, only run the backend — it already serves the built frontend at port 8000.

---

## 🌐 Public Access (Demo)

To share with others without deploying, use ngrok:

```bash
# Install ngrok from https://ngrok.com/download
ngrok http 8000
```

Share the generated URL (e.g. `https://xxxx.ngrok-free.app`) with anyone — no installation needed on their end.

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
│   └── .env              # API keys (not committed)
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   └── services/     # API service layer
│   └── dist/             # Built frontend (served by backend)
├── .env.example           # Environment variable template
├── requirements.txt       # Python dependencies
└── README.md
```

---

## 📸 Screenshots

<img width="955" height="443" alt="Enterprise RAG Assistant UI" src="https://github.com/user-attachments/assets/407f1e1f-31d8-4bf9-af5f-edd9a8a82b67" />

---

## 👥 Team

