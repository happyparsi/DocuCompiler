# DocuCompiler

DocuCompiler is an AI-powered document intelligence platform that allows users to seamlessly upload documents (PDF, DOCX, TXT), generate structured summaries, and interact with the text through an intelligent follow-up Q&A system. 

It leverages a powerful FastAPI backend and a visually stunning React frontend.

---

## 🚀 Key Features

- **Premium UI**: A sleek, dark-glassmorphism React interface with Light/Dark/System theme toggling.
- **Intelligent Summarization**: Context-aware AI summarization, scoring sentences via an NLP PageRank algorithm.
- **Chat Memory**: Keep the conversation flowing without re-uploading files. The backend remembers the parsed document context across the session.
- **Enhanced Retrieval-Augmented Generation (RAG)**: Employs FAISS vector retrieval and a fine-tuned T5 generator with beam search for comprehensive, Markdown-formatted answers.

---

## 🧠 How It Works

### The Pipeline
1. **Extraction (`extractor.py`)**: Parses raw text from user-uploaded PDFs, Word documents, or plain text.
2. **Lexical & Structural Parsing (`lexical.py`, `structural.py`)**: Breaks the text into sentences, cleans noisy symbols, and filters out invalid structures.
3. **Semantic Graphing (`semantic.py`)**: Encodes the sentences into dense vectors (embeddings) using `SentenceTransformer` and runs a NetworkX PageRank algorithm over their cosine similarities to score the sentences' importance.
4. **Optimization & Generation (`optimizer.py`, `generator.py`)**: Selects the top-ranked sentences and generates a polished, Markdown-formatted summary (paragraphs or bullets).
5. **Interactive Q&A (`query.py`)**: User queries are matched against the FAISS index. The most relevant text segments ($k=7$) are retrieved and fed into a T5 conditional generation model using beam search to synthesize a detailed answer up to 512 tokens.

### Data Flow
- **Frontend (React)**: Handles all user interactions natively in `static/index.html`. Uses `marked.js` to render Markdown.
- **Backend (FastAPI)**: Receives the data and handles user auth & sessions via SQLite.
- **Chat Memory**: Sentences and embeddings are preserved via Python's `pickle` and `json` into the database, allowing for rapid follow-up queries.

---

## 💻 How to Run it on VS Code

To get the platform running locally on your machine via Visual Studio Code:

### 1. Open the Project
- Open VS Code.
- Go to **File > Open Folder...** and select the `DocuCompiler` folder.

### 2. Activate the Virtual Environment
Open a new Integrated Terminal in VS Code (`Ctrl + ~` or `Cmd + j`) and run:
```powershell
.\.venv\Scripts\activate
```
*(If you haven't created the environment yet, run `python -m venv .venv` followed by `pip install -r requirements.txt`)*

### 3. Start the Server
Run the FastAPI backend using `uvicorn`:
```powershell
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Access the Platform
- Open your browser and navigate to: **http://127.0.0.1:8000**
- You can create a new account or log in with the test credentials:
  - **Username**: `paras_rawal117`
  - **Password**: `Rawal@117`
