import time
import psutil
import os
import json
import numpy as np
from src.extractor import SourceReader
from src.lexical import LexicalAnalyzer
from src.structural import StructuralParser
from src.semantic import SemanticGraph
from src.ir import SemanticIR
from src.optimizer import OptimizationEngine
from src.generator import TargetGenerator
from src.baselines import ExtractiveBaselines, AbstractiveBaselines
from src.evaluation import Evaluator
from typing import List, Dict

class BenchmarkRunner:
    """Orchestrates comparative benchmarks between DocuCompiler and Baselines."""

    def __init__(self):
        self.evaluator = Evaluator()
        self.docu_components = {
            "lexical": LexicalAnalyzer(),
            "structural": StructuralParser(),
            "semantic": SemanticGraph(),
            "optimizer": OptimizationEngine(strategy='balanced', redundancy_threshold=0.75),
            "generator": TargetGenerator()
        }
        self.ext_baselines = ExtractiveBaselines()
        # Abstractive baselines are loaded on demand due to memory

    def measure_docu_compiler(self, text: str) -> Dict[str, any]:
        """Measures DocuCompiler performance on a piece of text."""
        start_time = time.time()
        process = psutil.Process(os.getpid())
        start_mem = process.memory_info().rss
        
        # Run Pipeline
        sentences = self.docu_components["lexical"].analyze(text)
        validated = self.docu_components["structural"].parse(sentences)
        scores, embeddings = self.docu_components["semantic"].build_graph(validated)
        
        optimized = self.docu_components["optimizer"].optimize(validated, scores, embeddings)
        summary = self.docu_components["generator"].generate(optimized)
        
        end_time = time.time()
        end_mem = process.memory_info().rss
        
        return {
            "summary": summary,
            "time": end_time - start_time,
            "memory_mb": (end_mem - start_mem) / (1024 * 1024)
        }

    def run_benchmark(self, dataset: List[Dict[str, str]]):
        """Runs the full benchmark suite on the provided dataset."""
        results = []
        
        for i, item in enumerate(dataset):
            print(f"Processing sample {i+1}/{len(dataset)}...")
            text = item['article']
            reference = item['highlights']
            
            # 1. DocuCompiler
            docu_res = self.measure_docu_compiler(text)
            docu_rouge = self.evaluator.evaluate_summary(docu_res['summary'], reference)
            
            # 2. TextRank Baseline
            tr_start = time.time()
            tr_summary = self.ext_baselines.textrank_summary(text)
            tr_time = time.time() - tr_start
            tr_rouge = self.evaluator.evaluate_summary(tr_summary, reference)
            
            # 3. TF-IDF Baseline
            ti_start = time.time()
            ti_summary = self.ext_baselines.tfidf_summary(text)
            ti_time = time.time() - ti_start
            ti_rouge = self.evaluator.evaluate_summary(ti_summary, reference)
            
            sample_results = {
                "id": i,
                "docu": {**docu_rouge, "time": docu_res['time']},
                "textrank": {**tr_rouge, "time": tr_time},
                "tfidf": {**ti_rouge, "time": ti_time}
            }
            results.append(sample_results)
            
        return results

    def print_table(self, results):
        """Averages results and prints a research-grade table."""
        metrics = ['rouge1', 'rouge2', 'rougeL', 'time']
        models = ['docu', 'textrank', 'tfidf']
        
        summary_avg = {}
        for model in models:
            summary_avg[model] = {m: np.mean([r[model][m] for r in results]) for m in metrics}
            # Efficiency Score = ROUGE-L / Time
            summary_avg[model]['efficiency'] = summary_avg[model]['rougeL'] / summary_avg[model]['time'] if summary_avg[model]['time'] > 0 else 0

        print("\n" + "="*70)
        print(f"{'Model':<15} | {'R-1':<7} | {'R-2':<7} | {'R-L':<7} | {'Time (s)':<10} | {'Eff. Score':<10}")
        print("-" * 70)
        for model, values in summary_avg.items():
            print(f"{model.upper():<15} | {values['rouge1']:<7.4f} | {values['rouge2']:<7.4f} | {values['rougeL']:<7.4f} | {values['time']:<10.4f} | {values['efficiency']:<10.4f}")
        print("="*70 + "\n")

if __name__ == "__main__":
    # Sample subset of CNN/DailyMail style data
    subset = [
        {
            "article": "The Mars rover has discovered new evidence of ancient water on the Red Planet. Scientists from NASA reported that soil samples contain minerals that only form in the presence of liquid water. This discovery further strengthens the theory that Mars was once habitable. Future missions will focus on searching for signs of microbial life.",
            "highlights": "NASA's Mars rover finds evidence of ancient liquid water in soil minerals, suggesting past habitability."
        },
        {
            "article": "Global stock markets rallied today following a positive jobs report in the United States. The Dow Jones Industrial Average rose by 2%, while European indices saw similar gains. Analysts attribute the surge to investor confidence in the recovering economy. Central banks indicated they might keep interest rates steady for the next quarter.",
            "highlights": "Stock markets rise globally after strong US jobs report builds investor confidence."
        }
    ]
    
    runner = BenchmarkRunner()
    results = runner.run_benchmark(subset)
    runner.print_table(results)
