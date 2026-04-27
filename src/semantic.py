import networkx as nx # Complex Networks aur Graph Algortihm banane (Like PageRank) k liye
from sentence_transformers import SentenceTransformer # AI Model jo Strings ko Vectors (Numbers) mein Convert krta hai
from sklearn.metrics.pairwise import cosine_similarity # Do lines kitna apas mei Match (similar) keti hn? Yeh check krti hai lib
from typing import List, Dict # Typehinting ki lie!
import numpy as np # Fast Numbers processing (AI data Tensors hta h isliye Numpy Arrays laazmi ha Vector ko hold krne)

class SemanticGraph:
    """Builds a semantic graph from sentences and computes importance scores."""
    # Semantic matlab meaning. Sentence Graph matlb jese "Facebook Friends" hote hen jo jitna juri hoga wo "Importnt" Hoga PageRank me

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        # MiniLM bohut chota model hy jaldi CPU p kaam krta h.. Usay download kr k self.model me save rkh liya.
        self.model = SentenceTransformer(model_name)

    def build_graph(self, sentences: List[Dict[str, any]], similarity_threshold: float = 0.2) -> Dict[int, float]:
        """
        Builds graph and computes PageRank scores.
        Returns a dict mapping sentence index to importance score.
        """
        if not sentences:
            return {} # Galtiyan control!

        # List of Dictionary se sirf "text" wali keys ko bahir Nikaal liya.
        texts = [s['text'] for s in sentences]
        
        # Ye sabse slow step hoga! Hazaroo lines ko 384-Dimensions (384 Length array) me Numeric Encode Kardia.  -> embeddings variable me!
        embeddings = self.model.encode(texts)
        
        # Ab Un lines k apas me 'Cosine Angle' Find karo (Maths wali Trick).
        # Agar Lines similar hen to value 1 k kareeb hogi Warna 0. 
        # Is se ek 2D Grid bnjyge.. matrix [Row][Column]  i,e.  Sent_1 vs Sent_2 => 0.83 Similarity
        sim_matrix = cosine_similarity(embeddings)
        
        # Nodes aur Edges bnane ke liye "NetworkX" Graph start kiya Khali abhi..
        nx_graph = nx.Graph()
        
        num_sentences = len(sentences)
        for i in range(num_sentences):
            # i = line number = Node graph me
            nx_graph.add_node(i)
            
            # Dusri loop usay aagay wale (i+1) sentences par chlegi. 
            # Pechi wli lines Check keni zarurt ni h kiun ke [a vs b] hy tu  [b vs a] ka score same hota e Matrix m.
            for j in range(i + 1, num_sentences):
                score = sim_matrix[i][j]
                
                # Kya do lineain ek doosre sy thora bhu ta'luq (Similarity) Rakhti hn?? Threshold = 0.2 (20%).
                if score > similarity_threshold:
                    # Agar Match hu gaya TO dono (i aur j) k waqt ek pull (Edge) Bnaado.. Or is Dosti ki taqat (Weight) Set kr do 'score' wali
                    nx_graph.add_edge(i, j, weight=score)
        
        # ---GOOGLE KA SEARCH ENGINE ALGO -> PAGERANK ---
        try:
            # Hum graph me PageRank dorah rye. Jo sentence Graph mein "SAB SE ZYADA" Doosre Importnt Sentenecs say Juda ho Gaaa...
            # Us "Node" ka Score High hujai gA!! Matlab wo baat Pury documnt ka MAIn-IDEA (Summary center) hy!
            scores = nx.pagerank(nx_graph)
        except nx.PowerIterationFailedConvergence: # Exception.. jb maths phat jay.. Failed to converged?
            # Aisa bahut rare hy jab Sab Lines bilkul alag baat kri hn or Dosti No... Toh phr Sabko equal importance = 1/N Dedo chup krke. :) 
             scores = {i: 1.0/num_sentences for i in range(num_sentences)}
            
        return scores, embeddings # Top Sentences aur sath hi Vector wapis lauta diy.
