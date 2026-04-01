import os # Operating system ke folders/files command (jaise path check, temporary file delete)
import sqlite3 # Database management ke liye SQLite import kar rahe hain (users/history idhar save hogi)
import hashlib # Password ko secure/hash karne ke liye cryptography
import secrets # Random secure URL-safe strings banane ke liye (Login tokens banayenge)
from datetime import datetime # Date aur Time nikalne ke liye (Jaise message kab aya? Token kab bana?)

# FastAPI Framework ki sab zaruri cheezein import kar rahe hain:
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Header
from fastapi.responses import JSONResponse, FileResponse # HTML page aur JSON data frontend ko wapas bhejne ke liye
from fastapi.staticfiles import StaticFiles # Taki /static/ folder ka css aur js directly frontend ko mil sake
from fastapi.middleware.cors import CORSMiddleware # React/JS frontend kisi aur port se Request bheje, toh block na ho isliye CORS setup
import tempfile # Computer ki memory me temporary (kuch waqt ke liye) files banan aur delete karna
import uvicorn # FastAPI server start aur run karne wala engine

# DocuCompiler ke hamare khud ke AI/NLP modules 'src' folder se import kar rahe hain
from src.extractor import SourceReader # File padhne ke liye read()
from src.lexical import LexicalAnalyzer # Lambi lines ko chote sentences me break karne ka tool
from src.structural import StructuralParser # Kacra symbols wagera dhundh kar Sentences filter marne k lie
from src.semantic import SemanticGraph # PageRank or Vectors (Embeddings) ke through importance ka pta lagana 
from src.ir import SemanticIR # Processing k beech data ko save kar k rakhna SQLite DB mein
from src.optimizer import OptimizationEngine # Jo fuzool Duplicate baatein ho unko summary matrix se delete marna
from src.generator import TargetGenerator # Bachi kuchi kam ki lines ko paragraphs ya bullets me likhe dena

try:
    # QueryCompiler FAISS aur T5 model use krta hy, Agr machine pe transformers library na hui tou Exception se App band ni hogi
    from src.query import QueryCompiler 
except ImportError:
    QueryCompiler = None # Na hone pe None Value Set

# Database file ka naam! Yahan saray users/tokens/chats honge.
DB_PATH = "app.db"

def init_db():
    # 1. Database connection khola
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 2. 'users' naam ki Table (Jisme id, name, email aur unka hide kiya gaya password hoga)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        email TEXT UNIQUE,
        password_hash TEXT
    )''')
    
    # 3. 'tokens' (Jo har login hone pe naya code dega token verification ke lie)
    c.execute('''CREATE TABLE IF NOT EXISTS tokens (
        token TEXT PRIMARY KEY,
        user_id INTEGER,
        created_at DATETIME
    )''')
    
    # 4. 'sessions' Table: Sidebar k chat-history ke Titles k lie 
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        created_at DATETIME
    )''')
    
    # 5. 'history' Table: Users and AI ki actual batein us specific chat k mutaliq
    c.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        role TEXT,
        content TEXT,
        created_at DATETIME
    )''')
    
    # Seed user: Testing ke liye default account paras_rawal117 bana rahe hain
    c.execute('SELECT id FROM users WHERE name = ?', ('paras_rawal117',))
    if not c.fetchone(): # Agar user na mile toh seed karo
        hashed = hashlib.sha256('Rawal@117'.encode()).hexdigest() # Demo password Rawal@117
        c.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', 
                  ('paras_rawal117', 'parasrawal117@gmail.com', hashed))
    
    # Database ki sari tables/data memory me Save kr di
    conn.commit()
    conn.close()

# FastAPI launch se pehle Database k tables Ensure (initialize) karlye 
init_db()

# Application shuru ho rahi hai 
app = FastAPI(title="DocuCompiler API")

# API Security and Origin (CORS Policies), '*' matlab kahin se bhi requests ajaein
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agar 'static' folder na ho toh bana de wrna file not found ai ga!
os.makedirs("static", exist_ok=True)
# App.mount ka use karke Frontend File linking set kr di
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_root():
    # Jab user browser me localhost 8000 pe jayega, toh ye html UI File bhej dega Browser main render krne.
    return FileResponse("static/index.html")

def get_db():
    # Database connection banane ka Helper function (Easy way to get DB)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Taakey records Dictionary ke form me ai List of tuples ki bajae!
    try:
        yield conn # Function yahin hold p rehta jab tk Doosra kam kr raha hota h
    finally:
        conn.close()

def get_current_user(authorization: str = Header(None)):
    # Frontend jo Bearer token Header me bhejta he usko check karna k kya admi ne thek login kia?
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token") # Error thek token na dene par!
    
    token = authorization.split(" ")[1] # "Bearer sd8sdf87" me se "sd8sdf87" alag nikala
    
    # Token dhoondo user id janne ke lie!
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT user_id FROM tokens WHERE token = ?', (token,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=401, detail="Invalid token") # Token fake hai
    return row[0] # User ki ID wapas dedena (Example: Id is 1)

@app.post("/api/signup")
def signup(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    # Signup request Backend me receive krli Form data se
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # DB me check kia kya same naam ka Account already mojod to nahi hai?
    c.execute('SELECT id FROM users WHERE name = ? OR email = ?', (name, email))
    if c.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="User with that name or email already exists")
    
    # Password Hash kia usko normal alphabets mi database m rkhna is Not Safe. 
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    # Naya account Save / register kr diay!
    c.execute('INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)', (name, email, hashed))
    conn.commit()
    conn.close()
    return {"message": "User created successfully"}

@app.post("/api/login")
def login(name: str = Form(...), password: str = Form(...)):
    # Simple form me username or pass le k Log In Logic!
    hashed = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Query ki password aur userName thek bhi dya he User ney ya nai?
    c.execute('SELECT id, name FROM users WHERE (name = ? OR email = ?) AND password_hash = ?', (name, name, hashed))
    user = c.fetchone()
    
    if not user:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid username, email, or password") # Ghalat hone pr Throw Error
    
    user_id = user[0]
    # Naya aur Random token bnaya, Jise session maintain rahey (Cookies ki Trah)
    token = secrets.token_urlsafe(32)
    c.execute('INSERT INTO tokens (token, user_id, created_at) VALUES (?, ?, ?)', 
              (token, user_id, datetime.utcnow()))
    conn.commit()
    conn.close()
    
    # Khushi se token aur Username return kro
    return {"token": token, "name": user[1]}

@app.get("/api/me")
def get_me(user_id: int = Depends(get_current_user)):
    # Token de k User Apna naam mangega (UI me Dikhane k Lie)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name, email FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return {"name": user[0], "email": user[1]}

@app.get("/api/sessions")
def get_sessions(user_id: int = Depends(get_current_user)):
    # Side-bar me Prawni chat dikhani ki Database ki Query lagani padegi!
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # List nikalo Session Table se sabse naye pehaley aein gay DESC k sath.
    c.execute('SELECT id, title, created_at FROM sessions WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    sessions = [dict(row) for row in c.fetchall()] # Lists k andr Dict!
    conn.close()
    return sessions

@app.get("/api/sessions/{session_id}")
def get_session_history(session_id: int, user_id: int = Depends(get_current_user)):
    # Jab Chat ki history pe Click maro tu Specific "Messages" a jayn Gay chat ki 
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('SELECT * FROM sessions WHERE id = ? AND user_id = ?', (session_id, user_id))
    if not c.fetchone(): # Security check (Kya ye session tumahara he b tha? Agar nai To error do)
        conn.close()
        raise HTTPException(status_code=404, detail="Session not found")
        
    c.execute('SELECT role, content, created_at FROM history WHERE session_id = ? ORDER BY created_at ASC', (session_id,))
    history = [dict(row) for row in c.fetchall()]
    conn.close()
    return history

@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: int, user_id: int = Depends(get_current_user)):
    # SideBar se cross click marne pr DB se pura record Delete Krney ki Query!
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id FROM sessions WHERE id = ? AND user_id = ?', (session_id, user_id))
    if not c.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Session not found")
        
    c.execute('DELETE FROM history WHERE session_id = ?', (session_id,)) # Chat messages ko pehle mitao
    c.execute('DELETE FROM sessions WHERE id = ?', (session_id,)) # Chat K TItle/session ko mitao
    conn.commit()
    conn.close()
    return {"message": "Session deleted"}

# --- MAIN ENGINE ENDPOINT --- 
@app.post("/api/summarize") # App ki Sub Se Bari APi (Post Method) Jismein Sara kaam hoga.
async def summarize(
    file: UploadFile = File(None), # Ya tu File Upload ki hogi.
    text: str = Form(None), # Ya tu koi Message Bheja Hoga.
    query: str = Form(None), # Optional: user ko kuch alag se sawal jwab pouchney hun gay "QA".
    strategy: str = Form("moderate"), # Summary lambi karni he ya shotr? default "Moderate".
    mode: str = Form("paragraph"), # Display kesay karni he bullet wagera ki surrat? default "paragraph".
    session_id: str = Form(None), # Ye purani Chat me Jawab dena he ki Nai ChAt shuru honi iske liey Track rakho
    user_id: int = Depends(get_current_user) # Backend Auth zruri hi is endpoint ko chlney ke liye
):
    if not file and not text:
         # error ager dono hi fields khali bhej di user ny.
        raise HTTPException(status_code=400, detail="Must provide either a file or text.")
    
    raw_text = ""
    file_name = "Text Input"
    temp_path = None
    
    try:
        # Step A: Agar File Ii hai, Tu file Read karo
        if file:
            file_name = file.filename
            suffix = os.path.splitext(file.filename)[1] # Check if pdf/docx/txt hy?
            
            # Temporary tor pr File Server ma banai taky Extractor usko parse kr sakkey
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                content = await file.read() # File K andar ke kaghzat perhaien 
                tmp.write(content)
                temp_path = tmp.name # Location noted
            
            # NLP P-1: Extractor se bol kr Text Nikalwaya
            source_data = SourceReader.read(temp_path)
            raw_text = source_data.get("raw_text", "")
        else:
            # Agar file ni thi toh Input field ki raw string he Text Hy
            raw_text = text

        if not raw_text.strip():
             # Padhne k baad pata chala File tou khali hy!!? Dafa Karo isko error dy k.
             raise HTTPException(status_code=400, detail="Extracted text is empty.")

        # NLP P-2: Para ko Tor kr sentence BNanay wala step 
        lexical = LexicalAnalyzer(use_spacy=True)
        sentences = lexical.analyze(raw_text)
        
        # NLP P-3: Khali awaz, signs, duplicates or Kachra ko Clean kiya
        structural = StructuralParser()
        validated_sentences = structural.parse(sentences)
        
        if not validated_sentences:
            raise HTTPException(status_code=400, detail="No valid sentences found to summarize.")

        # NLP P-4: Sentence Transformer + PageRAnka Algorithm Graph k lie run kiya 
        semantic = SemanticGraph()
        scores, embeddings = semantic.build_graph(validated_sentences) # Values AI se genralized huee aur nikal ae
        
        # NLP P-5: Jo sentences boht low score the (bekar the) unho cut/ drop mar do
        optimizer = OptimizationEngine(strategy=strategy)
        optimized_sentences = optimizer.optimize(validated_sentences, scores, embeddings) 
        
        # NLP P-6: Bachi lines ko Phir se ek lamba sentence bana do.
        generator = TargetGenerator()
        summary = generator.generate(optimized_sentences, mode=mode)

        # JSON response k lye dictionary k format me dalo Data
        response_data = {
            "summary": summary,
            "metrics": {
                "raw_sentences": len(sentences),
                "validated_sentences": len(validated_sentences),
                "optimized_sentences": len(optimized_sentences)
            }
        }

        final_answer = summary
        
        # NLP P-7 (OPTIONAL) QA SYSTEM: Agr User Query kre tu Usk Jawab do is summary per
        if query and query.strip() and QueryCompiler:
            qc = QueryCompiler()
            qc.build_index(validated_sentences, embeddings) # Vectors Search index bano (Database jesa Fast system)
            answer = qc.answer(query) # User k "Query" ko Match kr k RAG framework me T5 language Model ka ans nikallo
            response_data["answer"] = answer
            final_answer += f"\n\n**Q: {query}**\n**A:** {answer}" # String Concat kr di!
            
            # Session ka naam wahi rakh do jo user ni Pocha takke Sidebar k Title acha bneye
            title = query[:30] + "..." if len(query) > 30 else query
        else:
             # Agr koi sawaal Poucha hi nahi toh Default Title!
            title = file_name if file else "Pasted Text Analysis"

        # -DATABASE LOGICS FOR CHAT-
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        sid = None
        # Agar purana chat tha?
        if session_id and session_id != "null" and session_id != "":
            sid = int(session_id)
            c.execute('SELECT id FROM sessions WHERE id = ? AND user_id = ?', (sid, user_id))
            if not c.fetchone(): # Us session ma User ne ungli tou nhi ke thi khud hi Id daal kr? Test karo.
                sid = None
                
        # Agar Purana chaT id pehle nahi diya toh Naya Chat Create kero DB me
        if not sid:
            c.execute('INSERT INTO sessions (user_id, title, created_at) VALUES (?, ?, ?)', 
                      (user_id, title, datetime.utcnow()))
            sid = c.lastrowid # Wo jo abi Insert huyiuski Id dedo mujhe!
            
        # USER_MESSAGE SAVED: UI pe joh usne send Button DBya tab Bheja tha 
        user_msg = f"[File: {file_name}] " if file else f"[Text Input: {text[:50]}...] "
        if query:
            user_msg += f"\nQuery: {query}"
            
        c.execute('INSERT INTO history (session_id, role, content, created_at) VALUES (?, ?, ?, ?)', 
                  (sid, "user", user_msg.strip(), datetime.utcnow()))
                  
        # ASSISTANT_MESSAGE SAVED: App ki AI ne jo response generate kerwayhi thi Wo bhi history me gai!
        c.execute('INSERT INTO history (session_id, role, content, created_at) VALUES (?, ?, ?, ?)', 
                  (sid, "assistant", final_answer, datetime.utcnow()))
                  
        conn.commit()
        conn.close()

        response_data["session_id"] = sid # Har API response k satha btana Zaruri he usko k Naya session konsa h.
        return JSONResponse(content=response_data) # Aur Ye JSON banky UI ki Taraf Fly KAr chukaa!!!

    except Exception as e:
        # Error Catch karna API k Break hone se bhter hai
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup Process (System ki disk Bhar sakti ha Agar ye na mitaao tu..)
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    # Main Python Runing Module! Uvicorn HTTP Server Ko port=8000 pe Shuru Kre gaa. (reload=True kero if Dev Me Ho Tuh!)
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
