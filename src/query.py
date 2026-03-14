import numpy as np
from typing import List, Dict
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    from transformers import T5Tokenizer, T5ForConditionalGeneration
    import torch
except ImportError:
    print("Warning: QA dependencies (faiss, transformers, torch) not installed.")
    faiss = None

class QueryCompiler:
    """QA System using FAISS and T5."""
    
    def __init__(self, embedding_model_name: str = 'all-MiniLM-L6-v2', 
                 qa_model_name: str = 't5-small'):
        if faiss is None:
            raise ImportError("faiss, transformers, or torch not installed.")
            
        print("Loading QA models...")
        self.encoder = SentenceTransformer(embedding_model_name)
        self.tokenizer = T5Tokenizer.from_pretrained(qa_model_name, legacy=False)
        self.model = T5ForConditionalGeneration.from_pretrained(qa_model_name)
        self.index = None
        self.sentences = []

    def build_index(self, sentences: List[Dict[str, any]], embeddings: np.ndarray):
        """Builds FAISS index from sentences and embeddings."""
        self.sentences = sentences
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))

    def retrieve(self, query: str, k: int = 3) -> List[str]:
        """Retrieves top-k relevant sentences for a query."""
        if not self.index:
            raise ValueError("Index not built.")
            
        query_vec = self.encoder.encode([query]).astype('float32')
        distances, indices = self.index.search(query_vec, k)
        
        results = []
        for idx in indices[0]:
            if idx < len(self.sentences):
                results.append(self.sentences[idx]['text'])
        return results

    def answer(self, query: str, k: int = 3) -> str:
        """Generates an answer to the query using context from retrieved sentences."""
        context_sentences = self.retrieve(query, k)
        context = " ".join(context_sentences)
        
        input_text = f"question: {query} context: {context}"
        input_ids = self.tokenizer(input_text, return_tensors="pt").input_ids
        
        outputs = self.model.generate(input_ids, max_length=100)
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return answer

if __name__ == "__main__":
    # Test requires extensive dependencies
    pass
