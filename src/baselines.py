import pytextrank
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from typing import List, Dict

class ExtractiveBaselines:
    """Implementations of standard extractive summarization baselines."""
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
            self.nlp.add_pipe("textrank")
        except Exception:
            # Fallback if textrank or spacy is not configured
            pass

    def textrank_summary(self, text: str, top_k: int = 3) -> str:
        """Standard TextRank using pytextrank."""
        doc = self.nlp(text)
        sentences = [sent.text for sent in doc._.textrank.summary(limit_sentences=top_k)]
        return " ".join(sentences)

    def tfidf_summary(self, text: str, top_k: int = 3) -> str:
        """TF-IDF sentence ranking baseline."""
        doc = self.nlp(text)
        sentences = [sent.text for sent in doc.sents]
        if len(sentences) <= top_k:
            return " ".join(sentences)
            
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(sentences)
        
        # Calculate importance as the sum of TF-IDF scores for words in the sentence
        importance = np.asarray(tfidf_matrix.sum(axis=1)).flatten()
        top_indices = importance.argsort()[-top_k:][::-1]
        top_indices.sort() # Keep original order
        
        return " ".join([sentences[i] for i in top_indices])

class AbstractiveBaselines:
    """Wrappers for abstractive baselines (T5, BART)."""
    
    def __init__(self, model_type: str = "t5-small"):
        self.model_type = model_type
        print(f"Loading abstractive baseline: {model_type}...")
        self.summarizer = pipeline("summarization", model=model_type, device=-1) # CPU only

    def summarize(self, text: str, max_length: int = 150) -> str:
        """Generates summary using the loaded transformer model."""
        result = self.summarizer(text, max_length=max_length, min_length=30, do_sample=False)
        return result[0]['summary_text']

if __name__ == "__main__":
    # Quick test
    test_text = """
    Artificial Intelligence is a field of computer science. 
    It focuses on creating intelligent agents. 
    These agents can solve complex problems autonomously.
    Machine learning and Deep learning are parts of AI.
    Ethical considerations are important in AI development.
    """
    
    eb = ExtractiveBaselines()
    print("TextRank:", eb.textrank_summary(test_text))
    print("TF-IDF:", eb.tfidf_summary(test_text))
    
    # Skipping heavy models in main test to avoid long execution, 
    # but they are ready for Benchmarking.
