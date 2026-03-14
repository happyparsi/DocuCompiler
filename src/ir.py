import sqlite3
import json
import numpy as np
from typing import List, Dict, Optional
import os

class SemanticIR:
    """
    Semantic Intermediate Representation (S-IR).
    Stores sentences, scores, embeddings, and metadata.
    """
    def __init__(self, db_path: str = "docucompiler.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Sentences table
        c.execute('''CREATE TABLE IF NOT EXISTS sentences
                     (id INTEGER PRIMARY KEY, 
                      original_index INTEGER, 
                      text TEXT, 
                      score REAL)''')
        
        # Embeddings table (stored as BLOB or JSON string - simplified for this prototype)
        # Using JSON string for portability and simplicity without extra dependencies if possible
        c.execute('''CREATE TABLE IF NOT EXISTS embeddings
                     (sentence_id INTEGER, 
                      vector TEXT,
                      FOREIGN KEY(sentence_id) REFERENCES sentences(id))''')
                      
        # Metadata table
        c.execute('''CREATE TABLE IF NOT EXISTS metadata
                     (key TEXT PRIMARY KEY, value TEXT)''')
                     
        conn.commit()
        conn.close()

    def save(self, sentences: List[Dict[str, any]], scores: Dict[int, float], embeddings: np.ndarray):
        """Persist S-IR to SQLite."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path) # Clean start for simplicity
            self._init_db()
            
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        for i, sent in enumerate(sentences):
            idx = sent['index']
            text = sent['text']
            score = scores.get(idx, 0.0) # Default to 0 if not ranked
            
            c.execute("INSERT INTO sentences (original_index, text, score) VALUES (?, ?, ?)",
                      (idx, text, score))
            sent_db_id = c.lastrowid
            
            # Save embedding
            vector_json = json.dumps(embeddings[i].tolist())
            c.execute("INSERT INTO embeddings (sentence_id, vector) VALUES (?, ?)",
                      (sent_db_id, vector_json))
            
        conn.commit()
        conn.close()

    def load(self):
        """Load S-IR from SQLite."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        sentences = []
        c.execute("SELECT original_index, text, score FROM sentences ORDER BY original_index")
        rows = c.fetchall()
        
        for r in rows:
            sentences.append({
                "index": r[0],
                "text": r[1],
                "score": r[2]
            })
            
        # Load embeddings if needed
        # ... (omitted for brevity unless required by optimized search)
        
        conn.close()
        return sentences

if __name__ == "__main__":
    # Test
    ir = SemanticIR("test_ir.db")
    sents = [{"index": 0, "text": "Test sentence."}, {"index": 1, "text": "Another one."}]
    scores = {0: 0.9, 1: 0.5}
    embeddings = np.array([[0.1, 0.2], [0.3, 0.4]])
    
    ir.save(sents, scores, embeddings)
    loaded = ir.load()
    print("Loaded:", loaded)
    
    if os.path.exists("test_ir.db"):
        os.remove("test_ir.db")
