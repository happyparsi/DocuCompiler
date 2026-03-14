from typing import List, Dict, Tuple
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class OptimizationEngine:
    """Optimizes the selected sentences for the summary."""
    
    STRATEGIES = {
        'aggressive': 0.05,  # Top 5%
        'balanced': 0.10,    # Top 10%
        'moderate': 0.15,    # Top 15%
        'conservative': 0.25 # Top 25%
    }
    
    def __init__(self, strategy: str = 'balanced', redundancy_threshold: float = 0.75):
        if strategy not in self.STRATEGIES:
            raise ValueError(f"Unknown strategy: {strategy}")
        self.strategy = strategy
        self.keep_ratio = self.STRATEGIES[strategy]
        self.redundancy_threshold = redundancy_threshold

    def optimize(self, sentences: List[Dict[str, any]], scores: Dict[int, float], embeddings: np.ndarray) -> List[Dict[str, any]]:
        """
        Applies dead code elimination and redundancy removal.
        """
        # 1. Dead Code Elimination (Rank-based filtering)
        # Sort sentences by score descending
        ranked_sentences = sorted(
            sentences, 
            key=lambda s: scores.get(s['index'], 0.0), 
            reverse=True
        )
        
        # Calculate cutoff
        num_sentences = len(sentences)
        cutoff_index = int(num_sentences * self.keep_ratio)
        cutoff_index = max(cutoff_index, 3) # Keep at least 3 sentences
        
        top_k_sentences = ranked_sentences[:cutoff_index]
        
        # 2. Redundancy Removal
        # Compute similarity matrix for top_k
        top_k_indices = [s['index'] for s in top_k_sentences]
        # Need to map sentence index to embedding index. 
        # Assuming input sentences list is 0..N aligned with embeddings 0..N
        # If input list is subset, we need mapping. 
        # For simplicity, assume 'sentences' passed here is the full list.
        
        final_selection = []
        selected_indices = set()
        
        # Re-sort by score to greedily pick best
        # top_k is already sorted by score
        
        for sent in top_k_sentences:
            idx = sent['index']
            # Check similarity with already selected
            is_redundant = False
            
            # Find embedding for current sent
            # Assuming embeddings is aligned with original list where index=i
            # If s['index'] is the index in original list, then embeddings[idx] is the vector
            vec = embeddings[idx].reshape(1, -1)
            
            for sel_idx in selected_indices:
                sel_vec = embeddings[sel_idx].reshape(1, -1)
                sim = cosine_similarity(vec, sel_vec)[0][0]
                
                if sim > self.redundancy_threshold: 
                    is_redundant = True
                    break
            
            if not is_redundant:
                final_selection.append(sent)
                selected_indices.add(idx)
                
        # Sort back to original order for coherent summary
        final_selection.sort(key=lambda s: s['index'])
        
        return final_selection

if __name__ == "__main__":
    # Test
    sentences = [
        {"index": 0, "text": "AI is great."},
        {"index": 1, "text": "AI is wonderful."}, # Should be redundant with 0
        {"index": 2, "text": "Bananas are yellow."},
        {"index": 3, "text": "The sky is blue."},
        {"index": 4, "text": "Machine learning is cool."},
        {"index": 5, "text": "Deep learning is a subset of ML."}
    ]
    scores = {0: 0.9, 1: 0.85, 2: 0.1, 3: 0.2, 4: 0.7, 5: 0.6}
    # Mock embeddings (random but with 0 and 1 close)
    embeddings = np.random.rand(6, 10)
    embeddings[1] = embeddings[0] + 0.01 # Very close
    
    opt = OptimizationEngine(strategy='conservative') # Keep top 25% of 6 = 1.5 -> 3 min
    res = opt.optimize(sentences, scores, embeddings)
    for r in res:
        print(r)
