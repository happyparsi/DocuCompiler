import spacy
import nltk
from typing import List, Dict, Optional

class LexicalAnalyzer:
    """Analyzes text to extract clean sentences."""
    
    def __init__(self, use_spacy: bool = True):
        self.use_spacy = use_spacy
        self.nlp = None
        if self.use_spacy:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: spaCy model 'en_core_web_sm' not found. Falling back to NLTK.")
                self.use_spacy = False
        
        if not self.use_spacy:
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                print("Downloading NLTK punkt tokenizer...")
                nltk.download('punkt')

    def analyze(self, text: str) -> List[Dict[str, any]]:
        """
        Tokenize text into sentences and clean them.
        Returns a list of dicts with keys: 'text', 'index', 'original_text'.
        """
        # 1. Tokenize
        if self.use_spacy:
            doc = self.nlp(text)
            raw_sentences = [sent.text for sent in doc.sents]
        else:
            raw_sentences = nltk.sent_tokenize(text)

        cleaned_sentences = []
        index = 0
        
        for sent in raw_sentences:
            # 2. Clean
            clean_text = sent.strip()
            
            # Remove empty lines
            if not clean_text:
                continue
            
            # Strip excessive whitespace
            clean_text = " ".join(clean_text.split())
            
            # Remove very short sentences (< 5 words)
            word_count = len(clean_text.split())
            if word_count < 5:
                continue
            
            cleaned_sentences.append({
                "text": clean_text,
                "index": index,
                "original_text": sent
            })
            index += 1
            
        return cleaned_sentences

if __name__ == "__main__":
    # Test
    text = """
    This is a test. 
    It has multiple lines.
    
    Short.
    This sentence is long enough to be kept.
    """
    analyzer = LexicalAnalyzer()
    results = analyzer.analyze(text)
    for res in results:
        print(res)
