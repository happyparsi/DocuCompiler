import numpy as np # Numbers and arrays manage krny ke leay.. Tensors ko store krengay yahan par!
from typing import List, Dict # Code ko clearly hints dene ke liy

try:
    # QA (Question Answering) ka Jadu (Magic) in 3 libraries k oper based!!:
    # 1. FAISS -> Facebook ki Library hey. Hazaaro vectors/lines ko MilliSeconds me SEARCH kr leti hai! (RAG ki jaan)
    import faiss 
    # 2. SentenceTransformers -> Hamarey Sawal(query) ko Model ke bhasha yani 'Vectors(Numbers)' me badlegi.
    from sentence_transformers import SentenceTransformer
    # 3. T5 Model, T5Tokenizer, torch -> "T5" Google ka famous Text-to-Text Language model h AI ka... "Torch" Backend engine hy.
    from transformers import T5Tokenizer, T5ForConditionalGeneration
    import torch
except ImportError:
    # Ager User ny installation me pip install torch faiss nhi mara tha.. to warnning d kar aagy bahr jana
    print("Warning: QA dependencies (faiss, transformers, torch) not installed.")
    faiss = None # Check bnane ke lya flag False(none) krdia

class QueryCompiler:
    """QA System using FAISS and T5."""
    # Ye Chat ka Q&A logic Handle kre gaa (RAG = Retrieval Augmented Generation).

    def __init__(self, embedding_model_name: str = 'all-MiniLM-L6-v2', qa_model_name: str = 't5-small'):
        if faiss is None:
             # FAiss nh h To error hi d do agr user na Class call kry!
            raise ImportError("faiss, transformers, or torch not installed.")
            
        print("Loading QA models...")
        # 1. ENCODER: English lines ko => (1x384 Array)  Embeddings banayega (MiniLM chota aur fast hy).
        self.encoder = SentenceTransformer(embedding_model_name)
        
        # 2. TOKENIZER: T5 Model ko Words smj nahi ate.. Word ki "ID" samjh aatee hain like 240, 10... Tokenizer yhi kam krga
        self.tokenizer = T5Tokenizer.from_pretrained(qa_model_name, legacy=False)
        
        # 3. MODEL: Asli AI "Demagh"!! T5 Small wala dwnld krdia takke pc hang na ho!
        self.model = T5ForConditionalGeneration.from_pretrained(qa_model_name)
        
        self.index = None # Start main Faiss Database Khali
        self.sentences = [] # Document wali List idhr Save hongee class me

    def build_index(self, sentences: List[Dict[str, any]], embeddings: np.ndarray):
        """Builds FAISS index from sentences and embeddings."""
        self.sentences = sentences # Text ki lines class property me dalden
        
        # Vectors ka Length yani Shape(e.g 384) kia hi array ka? Wo index ko bathaa dyaa
        dimension = embeddings.shape[1] 
        
        # Naya Vector Database Memory start kia (L2 mtlab Euclidean Distance se 2 lines ki doori nappe ga)
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32')) # Or ye saary Array Floats m Table m Guss Gae!

    def retrieve(self, query: str, k: int = 3) -> List[str]:
        """Retrieves top-k relevant sentences for a query."""
        if not self.index:
            raise ValueError("Index not built.")
            
        # User ne jo Sawal (Query) pucha h, Oos sawaal ka Vector Number kya bnega wo Banao !!!
        query_vec = self.encoder.encode([query]).astype('float32') # (Text -> Math)
        
        # FAISS ko bola => "Mre Sawal k Vector ky sabse qareb tareen K=3 Matches dhondh kar lao DB se!"... 
        # wo Distances (Doorie) phekega aur Indices (Line k Numbers kya the?) bta daygaa
        distances, indices = self.index.search(query_vec, k)
        
        results = []
        # Ab FAiss ne Lines ki ID btain . Ham ny Array lookup k k wo Asal English TEXT line nikal li result me!
        for idx in indices[0]:
            if idx < len(self.sentences):
                results.append(self.sentences[idx]['text'])
        
        # Jwb: 3 most Matchihng linessss! "Context" K liye (Taky T5 model idhr Se Padh Kr JAwab tyyar kry!!)
        return results

    def answer(self, query: str, k: int = 3) -> str:
        """Generates an answer to the query using context from retrieved sentences."""
        
        # Faiss k retrieve function se Milti Jhulti kam ki info nikali.
        context_sentences = self.retrieve(query, k)
        
        # List of Strings ko 1 lambi String k paragraph me badal diya (Space dal k)
        context = " ".join(context_sentences)
        
        # **T5 MODEL KI TRICK**: T5 ko prompt ik khas format mi dena hta hi... 
        input_text = f"question: {query} context: {context}"
        
        # Strings ko Model ki samajh mai aane wli PyTorch Tensors ID me convert kardia Tokenizer ki maded sy.
        input_ids = self.tokenizer(input_text, return_tensors="pt").input_ids
        
        # AB MAGIC shuru! Model ko Input pakra do aur bolo SOCHO aur Ans likhdo... max_length limit dedi jwab barai krnr ko
        outputs = self.model.generate(input_ids, max_length=100)
        
        # Jo Result aaya, Wo wapas MATH numeric IDs mai tha... 
        # Tokenizer.Decode usy Dubara ENGLISH words main badalllll day gAa!
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return answer # Final Answer bhyyjj Doo user ko UI pr :D !!

if __name__ == "__main__":
    # Test requires extensive dependencies (torch faissa transformers download hoty hen tou manual ni krsghty yaha)
    pass
