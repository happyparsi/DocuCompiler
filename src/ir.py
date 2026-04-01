import sqlite3 # Database file bnany kr lye
import json # Json string convertor
import numpy as np # arrays kelye
from typing import List, Dict, Optional # Types
import os 

class SemanticIR:
    """
    Semantic Intermediate Representation (S-IR).
    Stores sentences, scores, embeddings, and metadata.
    """
    # Is IR Database ka maskad Hy k NLP Phase k beech mein Server Crash hojaye to DB m sari progress mahfouz ho 
    # Ya phr ChatHistory jab mangy Summary dubata tao pury ML steps dubara chlaney ki zerorrt Na prey!!! Speedup kely

    def __init__(self, db_path: str = "docucompiler.db"):
        self.db_path = db_path # DB file name
        self._init_db() # Banate hi table tayar

    def _init_db(self):
        # Database setup: Sqlite connect 
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 1. Sentences list jisme Har Line ko "Score" b mila huwa hy
        c.execute('''CREATE TABLE IF NOT EXISTS sentences
                     (id INTEGER PRIMARY KEY, 
                      original_index INTEGER,  
                      text TEXT, 
                      score REAL)''')
        
        # 2. Vector table: Ye QA (Query/Sawalo) me Kaam aayenge dobara T5 model mein Fast FAISS Search kliye
        # Embeddings ko BLOB format men rakhna chiyea, pero Simple Rakhny k liye unhe list sy JSON Text/String bnke rkha hy ID k sath foreign key m
        c.execute('''CREATE TABLE IF NOT EXISTS embeddings
                     (sentence_id INTEGER, 
                      vector TEXT,
                      FOREIGN KEY(sentence_id) REFERENCES sentences(id))''')
                      
        # 3. Extra info ki table k liye 
        c.execute('''CREATE TABLE IF NOT EXISTS metadata
                     (key TEXT PRIMARY KEY, value TEXT)''')
                     
        conn.commit()
        conn.close()

    def save(self, sentences: List[Dict[str, any]], scores: Dict[int, float], embeddings: np.ndarray):
        """Persist S-IR to SQLite."""
        
        # Clean start: Agar pehayl db tha tou abhi Naya bnaaynge Delete marker prototype ki asani krlye
        if os.path.exists(self.db_path):
            os.remove(self.db_path) 
            self._init_db()
            
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        for i, sent in enumerate(sentences):
            idx = sent['index']
            text = sent['text']
            
            # Agar graph m wo sentence isolate tah to uska score 0 hoga! 
            score = scores.get(idx, 0.0) 
            
            c.execute("INSERT INTO sentences (original_index, text, score) VALUES (?, ?, ?)",
                      (idx, text, score))
            sent_db_id = c.lastrowid # Foreign Key Relation Bnaneny k lie ID mgy gy DB se !
            
            # Embedding ko Json List me Badalna kion k Numpy Type sqllite me direclty NAHii ja sakti !!!
            vector_json = json.dumps(embeddings[i].tolist())
            c.execute("INSERT INTO embeddings (sentence_id, vector) VALUES (?, ?)",
                      (sent_db_id, vector_json))
            
        conn.commit()
        conn.close()

    def load(self):
        """Load S-IR from SQLite."""
        # Agar Load karana par hy kabhi wapis? 
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        sentences = []
        c.execute("SELECT original_index, text, score FROM sentences ORDER BY original_index")
        rows = c.fetchall()
        
        for r in rows:
             # Dict format ban k vapis wesa ho jaige Jsey chhora th !!
            sentences.append({
                "index": r[0],
                "text": r[1],
                "score": r[2]
            })
        
        conn.close()
        return sentences
