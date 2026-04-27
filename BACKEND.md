# BACKEND DOCUMENTATION

This document covers the core backend server files that drive the DocuCompiler application.

## List of Backend Files
1. `app.py` - The FastAPI web server, API routes, Database initialization, and Web Pipeline logic.
2. `main.py` - The Command-Line Interface (CLI) version of the pipeline.

---

## 1. `app.py`

### Purpose
It acts as the central brain for the web interface. It serves the frontend static files, exposes REST API endpoints for authentication (login/signup) and chat history (sessions), and coordinates the entire NLP/summarization pipeline whenever a document is uploaded. 

### API Routes / Controllers
- `GET /` -> Serves `index.html`.
- `POST /api/signup` -> Registers a new user inside `docucompiler.db`.
- `POST /api/login` -> Authenticates a user and generates a token.
- `GET /api/me` -> Fetches logged-in user details.
- `GET /api/sessions` -> Gets a list of past chats for a user.
- `GET /api/sessions/{session_id}` -> Fetches the full message history for a specific chat.
- `DELETE /api/sessions/{session_id}` -> Deletes a chat history and associated document context.
- `GET /api/sessions/{session_id}/document` -> Checks if a session has an active document loaded.
- `POST /api/summarize` -> **The Core Engine Endpoint.** Receives files/text, runs the NLP pipeline, and returns the AI summary & answers. Supports follow-up Q&A by loading stored context.

### Business Logic
- **Authentication**: Custom token generation (URL-safe string), stored in `tokens` table. Passwords are hashed using SHA-256.
- **Chat Memory**: Stores processed document context (sentences as JSON, embeddings as Pickled blobs) inside the `documents` table to avoid re-uploading on follow-up questions.
- **Pipeline Execution**: Uploaded files are saved temporarily. Text is extracted, cleaned, passed to a semantic graph, optimized, and converted to a summary.
- **Enhanced QA Integration**: Uses FAISS index and T5. Retrieves $k=7$ sentences, uses `num_beams=4` (beam search) and generates detailed markdown answers up to 512 tokens.
