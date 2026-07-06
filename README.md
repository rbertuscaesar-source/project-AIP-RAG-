# 📚 Enterprise RAG Assistant

Enterprise RAG Assistant is an AI-powered **Retrieval-Augmented Generation (RAG)** application designed to help users search and ask questions about **SOP (Standard Operating Procedure)** documents in university or corporate environments.

## ✨ Features

- 📄 **Document Upload** - Supports PDF, DOCX, TXT formats
- 🔍 **Hybrid Search** - Combines Semantic Search (Embedding) and Keyword Search (BM25)
- 💬 **AI Chat** - Interactive Q&A based on document context
- 📋 **Structured Responses** - Numbered steps (1, 2, 3) and bullet point notes
- 📂 **Document Sidebar** - View all uploaded documents
- 🗑️ **Delete Documents** - Remove from database and physical folder
- 📤 **Export Chat History** - Export to TXT and PDF formats
- 🎨 **Modern UI** - Responsive with gradients and animations

## 🛠️ Tech Stack

## Backend
- **FastAPI** - Python API Framework
- **Ollama** - Local LLM (Gemma2:2b)
- **ChromaDB** - Vector Database
- **Sentence-Transformers** - Embedding (all-MiniLM-L6-v2)
- **BM25** - Keyword Search (rank-bm25)

### Frontend
- **React** + **Vite** - UI Framework
- **React Markdown** - Markdown rendering
- **Axios** - HTTP Client
- **CSS3** - Modern styling



## 🚀 Installation & Running

**1. Clone Repository**

git clone https://github.com/username/project-AIP-RAG-.git
cd project-AIP-RAG-


**2. Backend**
**Create virtual environment**
-> python -m venv venv

**Install dependencies**
-> pip install -r requirements.txt

**Run server**
-> uvicorn main:app --reload


**3. Frontend**
**Install dependencies**
-> npm install

**Run development server**
-> npm run dev

**4. Ollama (LLM)**
Make sure Ollama is installed and the Gemma2:2b model is pulled:

**Install Ollama (https://ollama.ai)**
-> ollama pull gemma2:2b

**5. Open Application**
http://localhost:5173

📸 Screenshots
<img width="955" height="443" alt="Screenshot 2026-07-06 093934" src="https://github.com/user-attachments/assets/407f1e1f-31d8-4bf9-af5f-edd9a8a82b67" />

