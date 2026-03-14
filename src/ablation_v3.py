from typing import List, Dict
import numpy as np
from src.lexical import LexicalAnalyzer
from src.structural import StructuralParser
from src.semantic import SemanticGraph
from src.optimizer import OptimizationEngine
from src.generator import TargetGenerator
from src.evaluation import Evaluator

class SystematicAblation:
    """Performs systematic ablation of DocuCompiler components."""

    def __init__(self, text: str, reference: str):
        self.text = text
        self.reference = reference
        self.evaluator = Evaluator()
        self.lexical = LexicalAnalyzer()
        self.structural = StructuralParser()
        self.sentences = self.lexical.analyze(text)
        self.validated = self.structural.parse(self.sentences)
        self.semantic = SemanticGraph()
        self.generator = TargetGenerator()

    def run_variant(self, name: str, use_optimization: bool = True, embedding_type: str = "MiniLM"):
        """Runs a specific DocuCompiler variant."""
        # Embeddings & Ranking
        if embedding_type == "MiniLM":
            scores, embeddings = self.semantic.build_graph(self.validated)
        else:
            # Simple TF-IDF ranking fallback logic inside ablation
            from sklearn.feature_extraction.text import TfidfVectorizer
            texts = [s['text'] for s in self.validated]
            vec = TfidfVectorizer()
            tfidf = vec.fit_transform(texts)
            scores_array = np.asarray(tfidf.sum(axis=1)).flatten()
            scores = {i: scores_array[i] for i in range(len(self.validated))}
            embeddings = tfidf.toarray()

        # Optimization
        if use_optimization:
            optimizer = OptimizationEngine()
            final_sentences = optimizer.optimize(self.validated, scores, embeddings)
        else:
            # Just take top 3 by rank without redundancy/DCE logic
            ranked = sorted(self.validated, key=lambda s: scores.get(s['index'], 0), reverse=True)
            final_sentences = sorted(ranked[:3], key=lambda s: s['index'])

        summary = self.generator.generate(final_sentences)
        rouge = self.evaluator.evaluate_summary(summary, self.reference)
        return rouge['rougeL']

    def run_all(self):
        print("Running Systematic Ablation Study...")
        results = {}
        results["Full Model (DocuCompiler)"] = self.run_variant("Full", True, "MiniLM")
        results["Without Optimization"] = self.run_variant("NoOpt", False, "MiniLM")
        results["TF-IDF Embeddings"] = self.run_variant("TFIDF", True, "TF-IDF")
        
        print("\nAblation Results (ROUGE-L):")
        print(f"{'Variant':<25} | {'ROUGE-L':<10}")
        print("-" * 40)
        for variant, score in results.items():
            print(f"{variant:<25} | {score:<10.4f}")
        return results

if __name__ == "__main__":
    test_article = "The Mars rover has discovered new evidence of ancient water on the Red Planet. Scientists from NASA reported that soil samples contain minerals that only form in the presence of liquid water. This discovery further strengthens the theory that Mars was once habitable."
    test_ref = "NASA's Mars rover finds evidence of ancient liquid water, suggesting past habitability."
    
    ablation = SystematicAblation(test_article, test_ref)
    ablation.run_all()
