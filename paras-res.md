# DocuCompiler

## Overview
DocuCompiler is an end-to-end document processing and summarization tool designed to solve the problem of information overload. It automatically extracts, analyzes, and summarizes long documents (PDFs, DOCX, TXTs) or pasted text into concise, meaningful summaries. The application also integrates a QA (Question Answering) system, allowing users to ask specific contextual questions about the processed document.

## Core Features
- **Multi-format Extraction**: Seamlessly extracts raw text from diverse document formats including PDF, DOCX, and TXT.
- **Intelligent Processing**: Performs comprehensive lexical analysis (cleaning sentences) and structural parsing (removing noise like tables and symbols).
- **Semantic Optimization**: Leverages Graph-based algorithms (PageRank via NetworkX) and advanced sentence embeddings (`SentenceTransformers`) to identify and prioritize the most critical sentences.
- **Summary Generation**: Generates contextual summaries in multiple modes (paragraphs, bullet points) controlled by user-defined optimization strategies (ranging from aggressive to conservative).
- **QA Capabilities**: Built-in retrieval-augmented generation (RAG) using FAISS and T5 to answer user queries grounded strictly in the document's context.
- **Session Management**: Full-fledged user authentication (Signup/Login) and chat session history tracking to persist past summaries and interactions.

## Tech Stack
The project leverages a robust and modern stack, segmented logically into decoupled compiler-like phases.

### Frontend
- **HTML5, Vanilla JavaScript, Vanilla CSS**: A dynamic, responsive, and glassmorphic UI resembling modern chat interfaces.

### Backend
- **Python 3**: The core language for pipelines and server logic.
- **FastAPI / Uvicorn**: High-performance REST framework and ASGI server for creating API endpoints.
- **SQLite**: Local relational databases (`app.db` for auth/sessions, `docucompiler.db` for Semantic IR).

### Machine Learning & AI
- **SentenceTransformers (`all-MiniLM-L6-v2`)**: Used for generating high-quality context embeddings.
- **Hugging Face Transformers (T5-small)**: Powers the generative question-answering system.
- **spaCy & NLTK**: Handles tokenization, stemming, and heavy lexical parsing.
- **FAISS**: Facilitates lightning-fast vector retrieval for the QA RAG pipeline.
- **NetworkX**: Utilized for executing graph algorithms (PageRank) to determine sentence importance.

## How It Works (End-to-End Workflow)

DocuCompiler is structured similarly to a decoupled compiler, executing text processing in distinct phases:

1. **User Interaction**:
   - The user securely logs in/signs up through the sleek web UI.
   - The user uploads a document (PDF, DOCX, TXT) or directly pastes text, and specifies options like target strategy, target format, and an optional question.
2. **Backend Processing Pipeline** (`src/` modules):
   - **Extraction** (`src.extractor`): Reads raw text from the chosen file.
   - **Lexical & Structural Analysis** (`src.lexical`, `src.structural`): Tokenizes text, cleans out stop words, drops noisy structures, and normalizes sentences.
   - **Semantic Analysis** (`src.semantic`): Converts sentences into embeddings and plots them on a semantic graph to calculate PageRank centrality.
   - **Intermediate Storage** (`src.ir`): Persists vectors and metadata in the SQLite DB for potential secondary retrieval.
   - **Optimization** (`src.optimizer`): Filters out redundancies, filtering down strictly to the top-ranked sentences based on the selected output length strategy.
   - **Generation & QA** (`src.generator`, `src.query`): Compiles the top sentences into a human-readable summary. If a query is provided, FAISS indexes the embeddings to retrieve context, which is then fed into T5 to generate an answer.
3. **Delivery**:
   - Results, including the summary and query answers, are fed back to the Frontend.
   - Both the generated summary and chat history are saved securely in the `app.db` SQLite database to be viewed over multiple sessions.

## Project Structure
- `app.py`: Main FastAPI server, handles routing, API endpoints, db init, and coordination.
- `main.py`: CLI version of the DocuCompiler application.
- `static/`: Contains the Frontend assets (`index.html`, `style.css`, `script.js`).
- `src/`: Contains the independent Python modules forming the AI processing core.
