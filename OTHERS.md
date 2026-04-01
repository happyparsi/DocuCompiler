# MODELS & OTHERS DOCUMENTATION

This document covers all the Core Machine Learning models, Optimizers, and NLP logic files residing inside the `src/` directory.

## Core System Integration (Data Flow)
The text goes through a strict sequence of transformations:
`File` -> `extractor.py` (Raw Text) -> `lexical.py` (Sentences) -> `structural.py` (Filtered Sentences) -> `semantic.py` (Embeddings + PageRank Score) -> `ir.py` (Saved DB State) -> `optimizer.py` (Top Ranked Sentences) -> `generator.py` (Summary Output). Separately, `query.py` takes embeddings to perform RAG (Retrieval-Augmented Generation).

---

## 1. `src/extractor.py`
**Purpose:** Reads raw text from different file types (PDF, DOCX, TXT).
**System Integration:** This is the entry point for all uploaded documents before NLP begins.

### Code Explanation
```python
import os
import fitz  # PyMuPDF library (PDF ke liye)
import docx  # python-docx library (Word Docs ke liye)

class BaseExtractor:
    # Ek 'blueprint' / parent class jispe baki extractors base hain (sirf rules banati hai)
    def extract(self, file_path: str):
        raise NotImplementedError("Subclasses must implement extract method.")

class PDFExtractor(BaseExtractor):
    def extract(self, file_path: str):
        # PyMuPDF se PDF kholi 
        doc = fitz.open(file_path)
        text = ""
        # Har page ki loop chalai: Text extract karke jodte jao
        for page in doc:
            text += page.get_text()
        return {"raw_text": text} 

class DOCXExtractor(BaseExtractor):
    def extract(self, file_path: str):
         # Word Document open kia
        doc = docx.Document(file_path)
        # Sare paragraphs ko "newline" se jod ke ek lamba text banaya
        text = "\n".join([para.text for para in doc.paragraphs])
        return {"raw_text": text} 

class TXTExtractor(BaseExtractor):
    def extract(self, file_path: str):
        try:
             # Normal text file ko UTF-8 se padho
            with open(file_path, 'r', encoding='utf-8') as f:
                return {"raw_text": f.read()}
        except UnicodeDecodeError:
            # Agar UTF-8 ne kaam nahi kiya toh Fallback karke Latin-1 format try karo (Puraney files me hota hai)
            with open(file_path, 'r', encoding='latin-1') as f:
                return {"raw_text": f.read()}

class SourceReader:
    # Factory pattern: Samajh kar extractor ko call karna file ke last part (.ext) se
    _EXTRACTORS = {
        '.pdf': PDFExtractor,
        '.docx': DOCXExtractor,
        '.txt': TXTExtractor
    }

    @classmethod
    def get_extractor(cls, file_path: str):
        ext = os.path.splitext(file_path)[1].lower()
        extractor_class = cls._EXTRACTORS.get(ext)
        if extractor_class: return extractor_class()
        else: raise ValueError(f"Unsupported file type: {ext}")

    @staticmethod
    def read(file_path: text):
        extractor = SourceReader.get_extractor(file_path)
        return extractor.extract(file_path) # Call kar diya!
```

---

## 2. `src/lexical.py`
**Purpose:** Splits long paragraphs into individual sentences.
**System Integration:** Passes sentences for filtering.

### Code Explanation
```python
import spacy
import nltk

class LexicalAnalyzer:
    def __init__(self, use_spacy: bool = True):
        self.use_spacy = use_spacy
        self.nlp = None
        if self.use_spacy:
            try:
                # English ka pre-trained NLP parser load kar rhe.. (SpaCy me default hota hai)
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                self.use_spacy = False # Agar fail hua (install nai hai) toh spaCy use mat karo
        
        if not self.use_spacy:
             # Agar SpaCy ni hai toh NLTK library (Punkt Tokenizer) ka model try karo
            nltk.download('punkt')

    def analyze(self, text: str):
        # 1. SpaCy/NLTK ka tokenizer use karo Text ko Sentences mein torne k liye
        if self.use_spacy:
            doc = self.nlp(text)
            raw_sentences = [sent.text for sent in doc.sents]
        else:
            raw_sentences = nltk.sent_tokenize(text)

        cleaned_sentences = []
        index = 0
        
        for sent in raw_sentences:
            # 2. Spaces aur kachra saaf kiya (Strip excessive whitespaces)
            clean_text = " ".join(sent.strip().split())
            
            # Agar sentence 5 words se kam ka hai toh vo kachra he hoga -> Continue (Hata do usko)
            word_count = len(clean_text.split())
            if not clean_text or word_count < 5:
                continue
            
            # Sentence ko append kiya Dictionary format mein (Index maintain rakhna zaruri hai aage result k liye)
            cleaned_sentences.append({"text": clean_text, "index": index, "original_text": sent})
            index += 1
            
        return cleaned_sentences
```

---

## 3. `src/structural.py`
**Purpose:** A simpler heuristic filter to drop tables, duplicate sentences, or symbols. 
**System Integration:** Follows Lexical output.

### Code Explanation
```python
import re

class StructuralParser:
    def parse(self, sentences):
        seen_texts = set()  # Duplicates track karne ke lie Set banaya
        validated_sentences = []

        for sent in sentences:
            text = sent.get("text", "")
            
            # 1. Agar ye line dobara aayi hai toh hatao (Skip)
            if text in seen_texts: continue
            seen_texts.add(text)
            
            # 2. Regular Expression se pata lagaya ki words/alphabets chod kar baaki special symbols kitne hai
            # Agar 30% se zayada symbols hain puri line me toh woh formula/table hoga -> Fenk do
            symbol_count = len(re.findall(r'[^\w\s]', text))
            if symbol_count / len(text) > 0.3:  
                continue

            validated_sentences.append(sent)

        return validated_sentences
```

---

## 4. `src/semantic.py` (THE ML GRAPH)
**Purpose:** Embeds sentences into vectors using SentenceTransformers and ranks them.
**Hyperparameters:** Model = `all-MiniLM-L6-v2`, `similarity_threshold` = 0.2.

### Code Explanation
```python
import networkx as nx
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class SemanticGraph:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        # HuggingFace ka Deep Learning Model load ko (Vectors/Embeddings bnanay k liye)
        self.model = SentenceTransformer(model_name)

    def build_graph(self, sentences, similarity_threshold=0.2):
        if not sentences: return {}

        texts = [s['text'] for s in sentences]
        
        # Har sentence ko 384-dimensional List (Vector) me Convert kiya
        embeddings = self.model.encode(texts)
        
        # Har Sentences ki aapas me Similarity measure karo (Matrix Form mei, e.g 1vs2, 1vs3.. Score nikalna)
        sim_matrix = cosine_similarity(embeddings)
        
        # NetworkX Graph Banao (Lines = Nodes, Aapas me connection (similarity) = Edges)
        nx_graph = nx.Graph()
        num_sentences = len(sentences)
        
        for i in range(num_sentences):
            nx_graph.add_node(i)
            # Loop for checking upper triangle of Matrix
            for j in range(i + 1, num_sentences):
                score = sim_matrix[i][j]
                
                # Agar lines same lagi thori bohat (score > 0.2 threshold) toh "Dosti" (edge) bana do
                if score > similarity_threshold:
                    nx_graph.add_edge(i, j, weight=score)
        
        # GOOGLE ka PageRank Algorithm chalao! 
        # Jo node (sentence) sab se zyada doosre sentences se connected hoga, uska Score sabse High hoga!
        scores = nx.pagerank(nx_graph)
            
        return scores, embeddings
```

---

## 5. `src/ir.py` (Intermediate Storage)
**Purpose:** Allows saving machine learning variables (Embeddings and Scores) to the database securely.
**System Integration:** It uses `docucompiler.db` to save data inside SQLite.
```python
import sqlite3, json

class SemanticIR:
    # Semantic Intermediate Representation Database Class
    def save(self, sentences, scores, embeddings):
        conn = sqlite3.connect("docucompiler.db")
        c = conn.cursor()
        
        for i, sent in enumerate(sentences):
            # Database mein Text aur PageRank ka Score Save kia
            idx = sent['index']
            text = sent['text']
            score = scores.get(idx, 0.0)
            
            c.execute("INSERT INTO sentences (original_index, text, score) VALUES (?, ?, ?)", (idx, text, score))
            sent_db_id = c.lastrowid
            
            # Embeddings Arrays hote hain. Unhe Database string JSON type accept karti hai isliye json.dumps kiya
            vector_json = json.dumps(embeddings[i].tolist())
            c.execute("INSERT INTO embeddings (sentence_id, vector) VALUES (?, ?)", (sent_db_id, vector_json))
            
        conn.commit()
        conn.close()
```

---

## 6. `src/optimizer.py` (Decision Logic)
**Purpose:** Chooses the final summary sentences by dropping redundant things.
**Hyperparameters:** Strategy cuts at Top `15%`, `25%`, `35%`, `50%`. Redundancy cap at `0.75` (Cosine Cos).

### Code Explanation
```python
from sklearn.metrics.pairwise import cosine_similarity

class OptimizationEngine:
    # 4 tarah k strategies di hain user k liye
    STRATEGIES = {
        'aggressive': 0.15,  # Choti summary (Dadaagiri!) - sirf top 15% sentences uthao
        'balanced': 0.25,
        'moderate': 0.35,
        'conservative': 0.50 # Badi summary - 50% sentences rakhlo
    }
    
    def __init__(self, strategy='balanced', redundancy_threshold=0.75):
        self.keep_ratio = self.STRATEGIES[strategy]
        self.redundancy_threshold = redundancy_threshold # 0.75 yani 75% se zyada similarity ni allowdeni!

    def optimize(self, sentences, scores, embeddings):
        # 1. Score k based Sentence ko descending order mein Sort kia (Highest Score wala sabse uppar ayega!)
        ranked_sentences = sorted(sentences, key=lambda s: scores.get(s['index'], 0.0), reverse=True)
        
        num_sentences = len(sentences)
        dynamic_ratio = self.keep_ratio
        
        # Document ki length ko dekh ke thodi logic badal rahe hain.
        # Chota Doc = Thora jyada text rkho. Lamba Doc = Ratio thori kam karo werna summary bari hogi
        if num_sentences < 10: dynamic_ratio = min(1.0, self.keep_ratio * 2.0)
        elif num_sentences > 100: dynamic_ratio = self.keep_ratio * 0.8
            
        cutoff_index = max(int(num_sentences * dynamic_ratio), 3) # Minimum 3 lines humesha rakho
        top_k_sentences = ranked_sentences[:cutoff_index] # Ab array truncate kar do (sirf top k bache!)
        
        final_selection = []
        selected_indices = set()
        
        # 2. Redundancy Removal (Ye loop check karegi ki koi 2 select kiye gaye sentence lagh-bhagh Same baatein toh nhi kar rahe?)
        for sent in top_k_sentences:
            idx = sent['index']
            is_redundant = False
            
            vec = embeddings[idx].reshape(1, -1) # Us lines ka Tensor Vector nikaalo
            
            for sel_idx in selected_indices:
                sel_vec = embeddings[sel_idx].reshape(1, -1) 
                # Dono vectors ka 'Dot Product' / Cosine Angle check karo
                sim = cosine_similarity(vec, sel_vec)[0][0] 
                
                # Agar result .75 se jada h yani 75% baatain match kr gai -> Reject Maaroo (is_redundant = True)!!
                if sim > self.redundancy_threshold: 
                    is_redundant = True
                    break
            
            if not is_redundant:
                final_selection.append(sent)
                selected_indices.add(idx)
                
        # Jab chunav pura hu gya, toh Sentence Numbers (Index) k hisaab se phir se sort karo.
        # Flow set rhe taaki End User ko Padhne me sense bane
        final_selection.sort(key=lambda s: s['index'])
        return final_selection
```

---

## 7. `src/generator.py`
**Purpose**: Combines final strings.

```python
class TargetGenerator:
    def generate(self, sentences, mode='paragraph'):
        # Mode pass hota h UI Se -> agr paragraph form hai toh saari lines apas me space se join krdega
        # Aur "Bullet" pass huya toh "/n- " karke har line k piche Dash add kr dega
        texts = [s['text'] for s in sentences]
        if mode == 'bullet':
            return "\n".join([f"- {text}" for text in texts])
        else:
            return " ".join(texts)
```

---

## 8. `src/query.py` (QA GENERATOR)
**Purpose:** Answers questions against a specific document. Uses RAG technique.
**Model:** Faiss index, `T5-small` language model.
```python
import faiss
from sentence_transformers import SentenceTransformer
from transformers import T5Tokenizer, T5ForConditionalGeneration

class QueryCompiler:
    def __init__(self, embedding_model='all-MiniLM-L6-v2', qa_model='t5-small'):
        # NLP QA Model or Embedding Encoder dono load ho k memory mein ayenge
        self.encoder = SentenceTransformer(embedding_model)
        self.tokenizer = T5Tokenizer.from_pretrained(qa_model, legacy=False)
        self.model = T5ForConditionalGeneration.frompretrained(qa_model)
        self.index = None

    def build_index(self, sentences, embeddings):
        self.sentences = sentences
        
        # Index Banaanay K liye FAISS library (Facebook AI Search) ka use karo (bohat super fast hai!)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32')) # DB mei Save!

    def retrieve(self, query, k=3):
        # 1. User k question ko Vector/Numbers mei badal lo
        query_vec = self.encoder.encode([query]).astype('float32')
        
        # 2. FAISS Index se poochi gai baat ke sabse qareebi Top-3 (k=3) match karne waley sentences uthao "Context" bananey k lie
        distances, indices = self.index.search(query_vec, k)
        
        results = [self.sentences[idx]['text'] for idx in indices[0] if idx < len(self.sentences)]
        return results

    def answer(self, query, k=3):
        context_sentences = self.retrieve(query, k)
        context = " ".join(context_sentences)
        
        # T5 Model input is tarah leta hai: "question: {sawal}? context: {kahaani...}"  
        input_text = f"question: {query} context: {context}"
        
        # Strings ko T5 Tensor Ids mein Decode kar dia
        input_ids = self.tokenizer(input_text, return_tensors="pt").input_ids
        
        # Model generate karega answer (Inference Run hogai!)
        outputs = self.model.generate(input_ids, max_length=100)
        
        # Jo Tensor Output me mila, usy Wapas English Text (Strings) me Encode kar diya
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return answer
```
