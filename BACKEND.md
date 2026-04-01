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
- `POST /api/signup` -> Registers a new user inside `app.db`.
- `POST /api/login` -> Authenticates a user and generates a token.
- `GET /api/me` -> Fetches logged-in user details.
- `GET /api/sessions` -> Gets a list of past chats for a user.
- `GET /api/sessions/{session_id}` -> Fetches the full message history for a specific chat.
- `DELETE /api/sessions/{session_id}` -> Deletes a chat history.
- `POST /api/summarize` -> **The Core Engine Endpoint.** Receives files/text, runs the NLP pipeline, and returns the AI summary & answers.

### Business Logic
- **Authentication**: JWT-like token generation (URL-safe string), stored in `tokens` table. Passwords are hashed using SHA-256.
- **Pipeline Execution**: Uploaded files are saved temporarily. Text is extracted, cleaned, passed to a semantic graph, optimized, and converted to a summary.
- **QA Integration**: If a question is asked along with a document, FAISS index is built on the fly, and T5 generates an answer.

### Code Explanation (Line-By-Line)

```python
# FastAPI Framework aur zaroori Python modules import kar rahe hain
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Header
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import sqlite3, hashlib, secrets, os, tempfile
from datetime import datetime

# DocuCompiler ke apne custom NLP modules (Pipeline Phases) import kiye
from src.extractor import SourceReader
from src.lexical import LexicalAnalyzer
from src.structural import StructuralParser
from src.semantic import SemanticGraph
from src.ir import SemanticIR
from src.optimizer import OptimizationEngine
from src.generator import TargetGenerator

# Database file ka naam jisme users/chats rahenge
DB_PATH = "app.db"

# == DB INITIALIZATION ==
def init_db():
    # Database create ya open karna
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # User accounts table banaya: id, name, email, password hashes honge
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        email TEXT UNIQUE,
        password_hash TEXT
    )''')
    
    # Login tokens store karne ke liye table
    c.execute('''CREATE TABLE IF NOT EXISTS tokens (
        token TEXT PRIMARY KEY,
        user_id INTEGER,
        created_at DATETIME
    )''')
    
    # Har chat (session) ka ek Title aur Owner hota hai
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        created_at DATETIME
    )''')
    
    # Ek specific chat ke andar kya messages ("role: user/assistant") aaye/gaye, wo idhar save hongi
    c.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        role TEXT,
        content TEXT,
        created_at DATETIME
    )''')
    
    conn.commit()
    conn.close()

# App shuru hote hi Database table structures bana do agar nahi hain
init_db()

# == FASTAPI SETUP ==
app = FastAPI(title="DocuCompiler API")

# Cross-Origin (CORS) setup taaki frontend API ko kisi aur port se bhi hit kar sake
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static folder link kiya (html/css/js serve karne ke lie)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_root():
    # Jab user website kholega (localhost:8000), toh index.html file bhejenge
    return FileResponse("static/index.html")

# == AUTHENTICATION MIDDLEWARE ==
def get_current_user(authorization: str = Header(None)):
    # Frontend jo token bhejta hai 'Bearer <token>' form mein, usko verify karna
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
        
    token = authorization.split(" ")[1]
    
    # Check karna ki token DB me exist karta hai ya nahi?
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT user_id FROM tokens WHERE token = ?', (token,))
    row = c.fetchone()
    conn.close()
    
    # Token valid nahi hai toh 401 Unauthorized Error do!
    if not row:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    # User ID return kardo
    return row[0]

# == API ROUTES ==
@app.post("/api/login")
def login(name: str = Form(...), password: str = Form(...)):
    # Password ka Hash (SHA-256) banaya compare karne ke liye
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # DB me dhundha ki koi user hai jiska naam/email aur password match kare?
    c.execute('SELECT id, name FROM users WHERE (name = ? OR email = ?) AND password_hash = ?', (name, name, hashed))
    user = c.fetchone()
    
    if not user:
        conn.close()
        raise HTTPException(status_code=401, detail="Galat username ya password")
    
    # Agar mil gaya toh ek lambi secure string (token) banai
    user_id = user[0]
    token = secrets.token_urlsafe(32)
    
    # Uss token ko Database mein save kar diya aur frontend ko wapas bhej diya
    c.execute('INSERT INTO tokens (token, user_id, created_at) VALUES (?, ?, ?)', (token, user_id, datetime.utcnow()))
    conn.commit()
    conn.close()
    
    return {"token": token, "name": user[1]}

# == MAIN NLP PIPELINE: THE SUMMARIZE ROUTE ==
@app.post("/api/summarize")
async def summarize(
    file: UploadFile = File(None), # Ya toh file aayegi...
    text: str = Form(None),        # Ya toh plain text aayega
    query: str = Form(None),       # Optional user ka sawal (Query)
    strategy: str = Form("moderate"),
    mode: str = Form("paragraph"),
    session_id: str = Form(None),
    user_id: int = Depends(get_current_user) # Authentication zoruri
):
    # Error Handling agar na file di aur na hi text format mein query
    if not file and not text:
        raise HTTPException(status_code=400, detail="Must provide either a file or text.")
    
    raw_text = ""
    file_name = "Text Input"
    temp_path = None
    
    try:
        # Agar USER ne ek PDF ya DOCX file attach ki hai:
        if file:
            file_name = file.filename
            suffix = os.path.splitext(file.filename)[1]
            
            # Use file ko temporary taur par server ki memory mein save kiya (tempfile)
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await file.read()
                tmp.write(content)
                temp_path = tmp.name
            
            # NLP Phase 1: File_path SourceReader ko dekar text nikalna
            source_data = SourceReader.read(temp_path)
            raw_text = source_data.get("raw_text", "")
        else:
            raw_text = text

        # NLP Phase 2: SpaCy/NLTK ka use karke sentences ko alag karna
        lexical = LexicalAnalyzer(use_spacy=True)
        sentences = lexical.analyze(raw_text)
        
        # NLP Phase 3: Faltu line/tables/syms nikal ke filter karna
        structural = StructuralParser()
        validated_sentences = structural.parse(sentences)
        
        # NLP Phase 4: PageRank Graph banake har sentence ka importance "Scoring" karna
        semantic = SemanticGraph()
        scores, embeddings = semantic.build_graph(validated_sentences)
        
        # NLP Phase 5: Ghatiya (fuzool) score wale sentences drop karna strategy (moderate) ke basis pe
        optimizer = OptimizationEngine(strategy=strategy)
        optimized_sentences = optimizer.optimize(validated_sentences, scores, embeddings)
        
        # NLP Phase 6: Bachay hue top sentences ko jod kar summary banana (Bullet or Paragraph mein)
        generator = TargetGenerator()
        summary = generator.generate(optimized_sentences, mode=mode)

        final_answer = summary
        
        # NLP QA (Phase 7): Agar user ki koi query hai toh AI model se answer lo
        if query and query.strip() and QueryCompiler:
            qc = QueryCompiler()
            qc.build_index(validated_sentences, embeddings) # Retrival index banaya (FAISS)
            answer = qc.answer(query) # T5 se answer nikal liya
            final_answer += f"\n\n**Q: {query}**\n**A:** {answer}"

        # DB Me HISTORY save karni hai:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Session check and insert logic ... (Code omitted yahan)
        # Session create hone k baad, user aur AI 'messages' history me insert ho jate hain
        
        conn.commit()
        conn.close()

        # Final JSON Responce wapis Frontend jayega!
        return JSONResponse(content={
            "summary": summary,
            "session_id": sid, # taaki next message ishi chat me aaye
             "metrics": { "raw_sentences": len(sentences) }
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup: Processing k baad temp file computer space bachane k liye delete kar do
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
```

---

## 2. `main.py`

### Purpose
To run DocuCompiler from the terminal (CLI mode) without the Web Server/Frontend. Very useful for testing logic quickly.

### Business Logic
Instead of FastAPI routes, it uses Python's `argparse` module to take flags right from the command line (`--input`, `--query`, `--strategy`, `--mode`). It executes the pipeline exactly like the Web API but prints everything using `print()`.

### Code Explanation (Line-By-Line)

```python
import argparse
import os
import sys

# Apni modules import kar rahe hain (Extractor, Lexical wagera)
from src.extractor import SourceReader
from src.lexical import LexicalAnalyzer
from src.structural import StructuralParser
# ... (omitted)

def main():
    # Terminal me command type karte samay arguments allow kar rahe hain 
    # Example: python main.py --input "my_doc.pdf" --query "What is this?" 
    parser = argparse.ArgumentParser(description="DocuCompiler CLI")
    parser.add_argument("--input", required=True, help="Path to input document")
    parser.add_argument("--query", help="User question for QA")
    parser.add_argument("--strategy", default="moderate", choices=["aggressive", "moderate", "conservative"])
    parser.add_argument("--mode", default="paragraph", choices=["paragraph", "bullet"])
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1) # Rasta na mila toh galti dikhake band kardo

    print(f"Starting DocuCompiler pipeline for: {args.input}")

    # Phase 1: Source Reader se file read kar rhe
    try:
        source_data = SourceReader.read(args.input)
        raw_text = source_data.get("raw_text", "")
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # ... Pipeline wase hi same chalti hai jaisa app.py me tha ...
    
    # Phase 6: Semantic Optimization
    print(f"Phase 6: Optimizing with strategy '{args.strategy}'...")
    optimizer = OptimizationEngine(strategy=args.strategy)
    optimized_sentences = optimizer.optimize(validated_sentences, scores, embeddings)
    print(f"  - Selected {len(optimized_sentences)} sentences.")

    # Phase 7: Summary Generator
    generator = TargetGenerator()
    summary = generator.generate(optimized_sentences, mode=args.mode)
    
    # Screen par achha formatted output dikhane ke liye
    print("\n" + "="*40)
    print("SUMMARY")
    print("="*40)
    print(summary)

    # Phase 8: Query Compiler (QA Test)
    if args.query:
        if QueryCompiler:
            qc = QueryCompiler()
            qc.build_index(validated_sentences, embeddings)
            answer = qc.answer(args.query) # Answer dhoond liya Context se
            print(f"\nQuestion: {args.query}\nAnswer: {answer}")
        else:
            print("Error: Dependencies not installed.")

if __name__ == "__main__":
    main() # Run terminal entrypoint!
```
