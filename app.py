import os
import sqlite3
import hashlib
import secrets
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Header
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import uvicorn

from src.extractor import SourceReader
from src.lexical import LexicalAnalyzer
from src.structural import StructuralParser
from src.semantic import SemanticGraph
from src.ir import SemanticIR
from src.optimizer import OptimizationEngine
from src.generator import TargetGenerator

try:
    from src.query import QueryCompiler
except ImportError:
    QueryCompiler = None

DB_PATH = "app.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        email TEXT UNIQUE,
        password_hash TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tokens (
        token TEXT PRIMARY KEY,
        user_id INTEGER,
        created_at DATETIME
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        created_at DATETIME
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        role TEXT,
        content TEXT,
        created_at DATETIME
    )''')
    
    # Seed user paras_rawal117
    c.execute('SELECT id FROM users WHERE name = ?', ('paras_rawal117',))
    if not c.fetchone():
        hashed = hashlib.sha256('Rawal@117'.encode()).hexdigest()
        c.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', 
                  ('paras_rawal117', 'parasrawal117@gmail.com', hashed))
    
    conn.commit()
    conn.close()

init_db()

app = FastAPI(title="DocuCompiler API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_root():
    return FileResponse("static/index.html")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ")[1]
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT user_id FROM tokens WHERE token = ?', (token,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=401, detail="Invalid token")
    return row[0]

@app.post("/api/signup")
def signup(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE name = ? OR email = ?', (name, email))
    if c.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="User with that name or email already exists")
    
    hashed = hashlib.sha256(password.encode()).hexdigest()
    c.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', (name, email, hashed))
    conn.commit()
    conn.close()
    return {"message": "User created successfully"}

@app.post("/api/login")
def login(name: str = Form(...), password: str = Form(...)):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name FROM users WHERE (name = ? OR email = ?) AND password_hash = ?', (name, name, hashed))
    user = c.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid username, email, or password")
    
    user_id = user[0]
    token = secrets.token_urlsafe(32)
    c.execute('INSERT INTO tokens (token, user_id, created_at) VALUES (?, ?, ?)', 
              (token, user_id, datetime.utcnow()))
    conn.commit()
    conn.close()
    return {"token": token, "name": user[1]}

@app.get("/api/me")
def get_me(user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name, email FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return {"name": user[0], "email": user[1]}

@app.get("/api/sessions")
def get_sessions(user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT id, title, created_at FROM sessions WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    sessions = [dict(row) for row in c.fetchall()]
    conn.close()
    return sessions

@app.get("/api/sessions/{session_id}")
def get_session_history(session_id: int, user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM sessions WHERE id = ? AND user_id = ?', (session_id, user_id))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Session not found")
        
    c.execute('SELECT role, content, created_at FROM history WHERE session_id = ? ORDER BY created_at ASC', (session_id,))
    history = [dict(row) for row in c.fetchall()]
    conn.close()
    return history

@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: int, user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id FROM sessions WHERE id = ? AND user_id = ?', (session_id, user_id))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Session not found")
        
    c.execute('DELETE FROM history WHERE session_id = ?', (session_id,))
    c.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
    conn.commit()
    conn.close()
    return {"message": "Session deleted"}

@app.post("/api/summarize")
async def summarize(
    file: UploadFile = File(None),
    text: str = Form(None),
    query: str = Form(None),
    strategy: str = Form("moderate"),
    mode: str = Form("paragraph"),
    session_id: str = Form(None),
    user_id: int = Depends(get_current_user)
):
    if not file and not text:
        raise HTTPException(status_code=400, detail="Must provide either a file or text.")
    
    raw_text = ""
    file_name = "Text Input"
    temp_path = None
    try:
        if file:
            file_name = file.filename
            suffix = os.path.splitext(file.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await file.read()
                tmp.write(content)
                temp_path = tmp.name
            
            source_data = SourceReader.read(temp_path)
            raw_text = source_data.get("raw_text", "")
        else:
            raw_text = text

        if not raw_text.strip():
             raise HTTPException(status_code=400, detail="Extracted text is empty.")

        lexical = LexicalAnalyzer(use_spacy=True)
        sentences = lexical.analyze(raw_text)
        structural = StructuralParser()
        validated_sentences = structural.parse(sentences)
        
        if not validated_sentences:
            raise HTTPException(status_code=400, detail="No valid sentences found to summarize.")

        semantic = SemanticGraph()
        scores, embeddings = semantic.build_graph(validated_sentences)
        optimizer = OptimizationEngine(strategy=strategy)
        optimized_sentences = optimizer.optimize(validated_sentences, scores, embeddings)
        generator = TargetGenerator()
        summary = generator.generate(optimized_sentences, mode=mode)

        response_data = {
            "summary": summary,
            "metrics": {
                "raw_sentences": len(sentences),
                "validated_sentences": len(validated_sentences),
                "optimized_sentences": len(optimized_sentences)
            }
        }

        final_answer = summary
        if query and query.strip() and QueryCompiler:
            qc = QueryCompiler()
            qc.build_index(validated_sentences, embeddings)
            answer = qc.answer(query)
            response_data["answer"] = answer
            final_answer += f"\n\n**Q: {query}**\n**A:** {answer}"
            title = query[:30] + "..." if len(query) > 30 else query
        else:
            title = file_name if file else "Pasted Text Analysis"

        # Save to DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        sid = None
        if session_id and session_id != "null" and session_id != "":
            sid = int(session_id)
            c.execute('SELECT id FROM sessions WHERE id = ? AND user_id = ?', (sid, user_id))
            if not c.fetchone():
                sid = None
                
        if not sid:
            c.execute('INSERT INTO sessions (user_id, title, created_at) VALUES (?, ?, ?)', 
                      (user_id, title, datetime.utcnow()))
            sid = c.lastrowid
            
        # Insert user message
        user_msg = f"[File: {file_name}] " if file else f"[Text Input: {text[:50]}...] "
        if query:
            user_msg += f"\nQuery: {query}"
            
        c.execute('INSERT INTO history (session_id, role, content, created_at) VALUES (?, ?, ?, ?)', 
                  (sid, "user", user_msg.strip(), datetime.utcnow()))
                  
        # Insert assistant message
        c.execute('INSERT INTO history (session_id, role, content, created_at) VALUES (?, ?, ?, ?)', 
                  (sid, "assistant", final_answer, datetime.utcnow()))
                  
        conn.commit()
        conn.close()

        response_data["session_id"] = sid
        return JSONResponse(content=response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
