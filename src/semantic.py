import networkx as nx
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import numpy as np

class SemanticGraph:
    """Builds a semantic graph from sentences and computes importance scores."""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def build_graph(self, sentences: List[Dict[str, any]], similarity_threshold: float = 0.2) -> Dict[int, float]:
        """
        Builds graph and computes PageRank scores.
        Returns a dict mapping sentence index to importance score.
        """
        if not sentences:
            return {}

        texts = [s['text'] for s in sentences]
        # Encode sentences
        embeddings = self.model.encode(texts)
        
        # Compute cosine similarity matrix
        sim_matrix = cosine_similarity(embeddings)
        
        # Build graph
        nx_graph = nx.Graph()
        
        num_sentences = len(sentences)
        for i in range(num_sentences):
            nx_graph.add_node(i)
            for j in range(i + 1, num_sentences):
                score = sim_matrix[i][j]
                if score > similarity_threshold:
                    nx_graph.add_edge(i, j, weight=score)
        
        # Compute PageRank
        try:
            scores = nx.pagerank(nx_graph)
        except nx.PowerIterationFailedConvergence:
            # Fallback if convergence fails, though rare for undirected graphs
             scores = {i: 1.0/num_sentences for i in range(num_sentences)}
            
        return scores, embeddings

if __name__ == "__main__":
    # Test (requires model download on first run)
    sentences = [
        {"text": "Artificial intelligence is a branch of computer science.", "index": 0},
        {"text": "It involves creating agents that can reason.", "index": 1},
        {"text": "Machine learning is a subset of AI.", "index": 2},
        {"text": "Bananas are yellow.", "index": 3}  # Unrelated
    ]
    try:
        sg = SemanticGraph()
        scores, _ = sg.build_graph(sentences)
        print("Scores:", scores)
    except Exception as e:
        print(f"Test failed: {e}")
