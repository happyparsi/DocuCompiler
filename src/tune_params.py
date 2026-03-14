import time
import numpy as np
from src.benchmarks import BenchmarkRunner
from src.optimizer import OptimizationEngine
from src.evaluation import Evaluator
from typing import List, Dict

def tune():
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
    evaluator = Evaluator()
    
    strategies = ['balanced', 'moderate', 'conservative']
    thresholds = [0.7, 0.75, 0.8, 0.85]
    
    best_eff = -1
    best_params = {}
    
    print(f"{'Strategy':<12} | {'Thresh':<6} | {'R-L':<6} | {'Time':<6} | {'Eff'}")
    print("-" * 50)
    
    for strategy in strategies:
        for thresh in thresholds:
            # Inject params (hacky for tuning)
            runner.docu_components["optimizer"] = OptimizationEngine(strategy=strategy)
            # We also need to patch the redundancy threshold which is hardcoded in the method
            # For simplicity, let's just use the current code which I just set to 0.75
            # but for tuning I'll manually run the pipeline
            
            total_rouge = 0
            total_time = 0
            
            for item in subset:
                start_time = time.time()
                # Run Pipeline
                sentences = runner.docu_components["lexical"].analyze(item['article'])
                validated = runner.docu_components["structural"].parse(sentences)
                scores, embeddings = runner.docu_components["semantic"].build_graph(validated)
                
                # Manual optimization with custom threshold for tuning
                opt = runner.docu_components["optimizer"]
                # Override the internal loop to use our thresh
                final_selection = []
                selected_indices = set()
                ranked_sentences = sorted(validated, key=lambda s: scores.get(s['index'], 0.0), reverse=True)
                cutoff = max(int(len(validated) * opt.keep_ratio), 3)
                top_k = ranked_sentences[:cutoff]
                
                from sklearn.metrics.pairwise import cosine_similarity
                for sent in top_k:
                    idx = sent['index']
                    vec = embeddings[idx].reshape(1, -1)
                    is_redundant = False
                    for sel_idx in selected_indices:
                        sel_vec = embeddings[sel_idx].reshape(1, -1)
                        if cosine_similarity(vec, sel_vec)[0][0] > thresh:
                            is_redundant = True
                            break
                    if not is_redundant:
                        final_selection.append(sent)
                        selected_indices.add(idx)
                
                final_selection.sort(key=lambda s: s['index'])
                summary = runner.docu_components["generator"].generate(final_selection)
                rouge = evaluator.evaluate_summary(summary, item['highlights'])['rougeL']
                
                total_rouge += rouge
                total_time += (time.time() - start_time)
            
            avg_rouge = total_rouge / len(subset)
            avg_time = total_time / len(subset)
            eff = avg_rouge / avg_time
            
            print(f"{strategy:<12} | {thresh:<6.2f} | {avg_rouge:<6.4f} | {avg_time:<6.4f} | {eff:.4f}")
            
            if eff > best_eff:
                best_eff = eff
                best_params = {'strategy': strategy, 'thresh': thresh, 'rouge': avg_rouge, 'time': avg_time}

    print("-" * 50)
    print(f"Best Configuration: {best_params}")

if __name__ == "__main__":
    tune()
