import time
import psutil
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.semantic import SemanticGraph
from src.lexical import LexicalAnalyzer
from src.structural import StructuralParser
from src.extractor import SourceReader
import numpy as np

class AblationStudy:
    """Performs ablation studies and performance measurements."""

    def __init__(self, text: str):
        self.text = text
        self.lexical = LexicalAnalyzer()
        self.structural = StructuralParser()
        self.sentences = self.lexical.analyze(text)
        self.validated_sentences = self.structural.parse(self.sentences)
        self.sentence_texts = [s['text'] for s in self.validated_sentences]

    def measure_tfidf(self):
        """Measures TF-IDF based graph construction."""
        start_time = time.time()
        start_mem = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
        
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(self.sentence_texts)
        sim_matrix = cosine_similarity(tfidf_matrix)
        
        end_time = time.time()
        end_mem = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
        
        return {
            "method": "TF-IDF",
            "time_sec": end_time - start_time,
            "mem_usage_mb": end_mem - start_mem
        }

    def measure_minilm(self):
        """Measures MiniLM based graph construction."""
        start_time = time.time()
        start_mem = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
        
        sg = SemanticGraph()
        _, _ = sg.build_graph(self.validated_sentences)
        
        end_time = time.time()
        end_mem = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
        
        return {
            "method": "MiniLM",
            "time_sec": end_time - start_time,
            "mem_usage_mb": end_mem - start_mem
        }

    def run(self):
        print("Running Ablation Study...")
        tfidf_res = self.measure_tfidf()
        minilm_res = self.measure_minilm()
        
        print("\nResults:")
        print(f"{'Method':<10} | {'Time (s)':<10} | {'Mem (MB)':<10}")
        print("-" * 35)
        for res in [tfidf_res, minilm_res]:
            print(f"{res['method']:<10} | {res['time_sec']:<10.4f} | {res['mem_usage_mb']:<10.4f}")

if __name__ == "__main__":
    # Load sample text
    with open("sample.txt", "r") as f:
        text = f.read()
    
    study = AblationStudy(text)
    study.run()
