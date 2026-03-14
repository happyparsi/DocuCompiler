import time
import numpy as np
import matplotlib.pyplot as plt
from src.extractor import SourceReader
from src.lexical import LexicalAnalyzer
from src.structural import StructuralParser
from src.semantic import SemanticGraph
from src.optimizer import OptimizationEngine
from transformers import pipeline
import os
from typing import List

class ScalingAnalyzer:
    """Analyzes how models scale with the number of sentences."""

    def __init__(self):
        self.docu_lexical = LexicalAnalyzer()
        self.docu_semantic = SemanticGraph()
        self.docu_optimizer = OptimizationEngine()
        # Loading t5-small as the baseline for scaling
        print("Loading T5-small for scaling baseline...")
        self.t5 = pipeline("summarization", model="t5-small", device=-1)

    def generate_dummy_text(self, num_sentences: int) -> str:
        base_sentence = "Artificial intelligence enables machines to learn from experience and perform human-like tasks."
        return " ".join([base_sentence for _ in range(num_sentences)])

    def measure_docu(self, text: str):
        start = time.time()
        # DocuCompiler Pipeline (simplified for core scaling)
        sentences = self.docu_lexical.analyze(text)
        scores, embeddings = self.docu_semantic.build_graph(sentences)
        _ = self.docu_optimizer.optimize(sentences, scores, embeddings)
        return time.time() - start

    def measure_t5(self, text: str):
        start = time.time()
        # Transformer inference
        _ = self.t5(text, max_length=50, min_length=10, do_sample=False)
        return time.time() - start

    def run_analysis(self, sentence_counts: List[int]):
        results = {"docu": [], "t5": []}
        
        for count in sentence_counts:
            print(f"Testing scaling behavior with {count} sentences...")
            text = self.generate_dummy_text(count)
            
            # Measure DocuCompiler
            docu_time = self.measure_docu(text)
            results["docu"].append(docu_time)
            
            # Measure T5 (only if text is not too long for standard 512 token limit)
            if count <= 20: # Keep it reasonable for transformer baseline on CPU
                t5_time = self.measure_t5(text)
                results["t5"].append(t5_time)
            else:
                results["t5"].append(None)
                
        return results

    def display_results(self, sentence_counts, results):
        print("\nSCALING BEHAVIOR (Time in seconds)")
        print(f"{'Sentences':<10} | {'DocuCompiler':<12} | {'T5-Small':<12}")
        print("-" * 40)
        for i, count in enumerate(sentence_counts):
            t5_val = f"{results['t5'][i]:.4f}" if results['t5'][i] else "N/A"
            print(f"{count:<10} | {results['docu'][i]:<12.4f} | {t5_val:<12}")

if __name__ == "__main__":
    counts = [5, 10, 20, 50, 100]
    analyzer = ScalingAnalyzer()
    res = analyzer.run_analysis(counts)
    analyzer.display_results(counts, res)
