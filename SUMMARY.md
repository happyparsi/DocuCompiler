# PROJECT OVERVIEW (DocuCompiler)

## What Problem the Project Solves
DocuCompiler solves the problem of information overload. It automatically extracts, analyzes, and summarizes long documents (PDFs, DOCXs, TXTs) or pasted text into concise, meaningful summaries. It also integrates a QA (Question Answering) system, allowing users to ask specific questions about the processed document.

## Core Functionality
- **Multi-format Extraction**: Extracts raw text from diverse document formats (PDF, DOCX, TXT).
- **Intelligent Processing**: Performs lexical analysis (cleaning sentences) and structural parsing (removing noise).
- **Semantic Optimization**: Uses Graph-based algorithms (PageRank via NetworkX) and sentence embeddings (`SentenceTransformers`) to identify the most critical sentences.
- **Summary Generation**: Generates outputs in various modes (paragraphs, bullets) controlled by an optimization strategy (aggressive to conservative).
- **QA Capabilities**: Built-in retrieval-augmented generation (RAG) using FAISS and T5 to answer user queries based on document context.
- **Session Management**: Full-fledged authentication and chat-session history tracking to store past summaries.

## End-to-End Workflow
1. **User Action**: User signs up/logs in, then uploads a document or pastes text via the web interface. 
2. **Backend Processing**: 
   - `SourceReader` extracts text.
   - `LexicalAnalyzer` and `StructuralParser` clean it.
   - `SemanticGraph` builds a graph of sentences and computes PageRank.
   - `OptimizationEngine` filters out redundancy and keeps top-ranked sentences based on user-chosen strategy.
   - `TargetGenerator` pieces it together into a summary.
3. **Database Saving**: `SemanticIR` persists intermediate representations and embeddings. Chat history and summaries are saved in the SQLite user database.
4. **Display**: The final text (summary + QA if requested) is shown in the ChatGPT-like frontend.

## Tech Stack
- **Frontend**: HTML5, Vanilla JavaScript, Vanilla CSS (Dynamic Glassmorphic UI).
- **Backend**: Python 3, FastAPI (for API/Routing), Uvicorn ( ASGI Server).
- **Database**: SQLite (`app.db` for auth/sessions, `docucompiler.db` for Semantic IR).
- **ML / AI**: 
  - `SentenceTransformers` (`all-MiniLM-L6-v2`) for embeddings.
  - `Hugging Face Transformers` (T5-small) for QA generation.
  - `spaCy` & `NLTK` for tokenization and lexical parsing.
  - `FAISS` for fast vector retrieval.
  - `NetworkX` for graph algorithms (PageRank).
- **Deployment Tools**: Local environment / Python (`pip` dependencies).

## Project Architecture
The project follows a decoupled, phase-based compiler architecture. 
- **Frontend** talks strictly to the **FastAPI Backend** via REST endpoints (`/api/summarize`, `/api/login`, etc.).
- **Backend Components** (the `src/` modules) act as compiler phases:
  - Frontend request -> `app.py` -> `src.extractor` -> `src.lexical` -> `src.structural` -> `src.semantic` -> `src.ir` -> `src.optimizer` -> `src.generator`.
  - The QA process uses `src.query` post-generation to augment the response.
- **State** is maintained via SQLite, managed through simple cursor queries in `app.py` and `ir.py`.

## Folder & File Structure

### Root Directory
- `app.py`: FastAPI server, routing, database init (auth/sessions), and full pipeline coordinator for web. Connects frontend with AI backend.
- `main.py`: CLI equivalent of `app.py`. A terminal-based entry point for running the DocuCompiler pipeline.
- `app.db` / `docucompiler.db`: SQLite databases for users/sessions and intermediate document semantics respectively.

### `static/` Directory (Frontend)
- `index.html`: The main user interface. Renders the auth overlay and the main chat view.
- `style.css`: All styling, animations, and layout logic.
- `script.js`: Handles API calls, DOM manipulation, authentication state, and chat interactions. Connections to `app.py`.

### `src/` Directory (AI Core)
- `extractor.py`: First phase. Reads PDFs (`fitz`), DOCX (`docx`), and TXT files.
- `lexical.py`: Tokenizes and cleans sentences using `spaCy` or `NLTK`.
- `structural.py`: Removes duplicates and noisy sentences (like tables/symbols).
- `semantic.py`: Creates embeddings and computes sentence importance via Graph PageRank.
- `ir.py`: Semantic Intermediate Representation. Persists embeddings and sentences into SQLite.
- `optimizer.py`: Eliminates redundant/dead sentences based on a user-chosen strategy.
- `generator.py`: Stitches optimized sentences back into a final summary string.
- `query.py`: Implements QA. Builds FAISS index from embeddings and uses T5 to answer questions.
