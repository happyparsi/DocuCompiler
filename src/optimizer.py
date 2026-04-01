from typing import List, Dict, Tuple
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class OptimizationEngine:
    """Optimizes the selected sentences for the summary."""
    # SemanticGraph model ne sbko Score dekar kaam khtm krlia 
    # Ab is class ki Logic ye choose karie gi k Kitne Sentences or Konsy Sentences Final Summary me Jaengay aur kin ko Delete marenge!

    # STRATEGY LIST: Ratio (Percentage) decide karta ha:
    STRATEGIES = {
        'aggressive': 0.15,  # Choti summary (Dadaagiri!) - sirf top 15% sentences uthao
        'balanced': 0.25,    # Thora ziyadas (25% top scores wali lines rakhlo!)
        'moderate': 0.35,    # Average Default value..
        'conservative': 0.50 # Badi summary - 50% sentences rakhlo aur details de do usko!
    }
    
    def __init__(self, strategy: str = 'balanced', redundancy_threshold: float = 0.75):
        # Jab class shuru ho...
        if strategy not in self.STRATEGIES:
            raise ValueError(f"Unknown strategy: {strategy}")
        self.strategy = strategy
        self.keep_ratio = self.STRATEGIES[strategy] # Limit nikal ly!
        
        # Ye ek formula hay.. Aggr koi bhi 2 sentences ka CosineAngle aaps mei 0.75 yani 75% Match kr jaye..
        # Tou unmy say Kisi ek ko DELETE kr den gy... Kiounky wo same baat Ghuma kr dubara bol rhy hn..  Humari Summary BORING hojai ge werna Redundant (Fuzol) c
        self.redundancy_threshold = redundancy_threshold

    def optimize(self, sentences: List[Dict[str, any]], scores: Dict[int, float], embeddings: np.ndarray) -> List[Dict[str, any]]:
        """
        Applies dead code elimination and redundancy removal.
        """
        # STEP 1: DEAD CODE ELIMINATION (Jo Score me zero hn, Ya jo Limit se gier gye.. unko bahar nikalo!!)
        
        # Sentnces ko sort kae do List me... Lekin highest score (Importatnce) se leker lowest Score ki trf . (Descending)
        ranked_sentences = sorted(
            sentences, 
            key=lambda s: scores.get(s['index'], 0.0), 
            reverse=True # ulti order me highest frst!
        )
        
        num_sentences = len(sentences)
        
        # Ab check kr rhy k Docuemnt original kesi hy? Us hisaab se strategy theek hy?
        dynamic_ratio = self.keep_ratio
        if num_sentences < 10:
            # Agr Document intahi chota hy, aur limit b 15% (Agressive) lagy hoi, tou summary me 1 he line bach jayge lol.
            # Iss liy Ratio ko thora Bara kardo X2 mar kr.. Magr 100% se kabi bhrny mt dena!!
            dynamic_ratio = min(1.0, self.keep_ratio * 2.0)
        elif num_sentences < 30:
            dynamic_ratio = min(1.0, self.keep_ratio * 1.5)
        elif num_sentences > 100:
            # Bahut Baray paragraph document (Hazar line) ke lye 50%(Conservativ) lagatey tou wo Bht bdi summary bun jati.. 0.8X karke 20% Minus kro cutoff!
            dynamic_ratio = self.keep_ratio * 0.8
            
        # Pata karo Kitni line bachngi Ratio lagney k baaad
        cutoff_index = int(num_sentences * dynamic_ratio)
        # Kam az kam 3 sentence tu dikahao gaaareb ko!!!!
        cutoff_index = max(cutoff_index, 3) 
        
        # Python Slice Lga ke Top-K line uthaleen !! Fuzool line gyii bhar mieeee!
        top_k_sentences = ranked_sentences[:cutoff_index]
        
        # STEP 2: REDUNDANCY REMOVAL
        
        final_selection = []
        selected_indices = set()
        
        # Har Highest score sentence pe dekha. (Kahi purana bnda hy wesi hIbt to nhi bol rhha)?
        for sent in top_k_sentences:
            idx = sent['index']
            is_redundant = False # start m False maan lia
            
            # Sentence ko uska Vector dya 1x384 Tensor ki sakall m cosn() lagnye k lie
            vec = embeddings[idx].reshape(1, -1)
            
            # Jitny select kr liyn hen un pr loop lagay!! k koi duplicate ya same matlab baalt bat to ni karha>?!
            for sel_idx in selected_indices:
                sel_vec = embeddings[sel_idx].reshape(1, -1)
                sim = cosine_similarity(vec, sel_vec)[0][0] # cosine lgao !!
                
                # Kya match huwa ??
                if sim > self.redundancy_threshold: 
                    is_redundant = True # pakrda gaiye!! 
                    break # Age check maat kar... Redundant hai tou agay nikal!
            
            # Agar koi Redundant cheez Ni huwi tu isko BAAzzat Izzzat Summary ki List men Daal dalo!!
            if not is_redundant:
                final_selection.append(sent)
                selected_indices.add(idx)
                
        # Akhree baat.... Line Score ki basis men Upar nech ho gi hn... Unhe wapas Readabelity kelye Document ki line series [index 0 , 1 ...N] me sort Kro
        # werna summary k matlab barabaat!!!
        final_selection.sort(key=lambda s: s['index'])
        
        return final_selection # Aur yeh Rahi ap ki optimized Smart summary !! JAI HIND.
