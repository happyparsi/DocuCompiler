import spacy # Bahut hi Zabardast NLP Machine Learning Library Engish samajhene ke liye
import nltk # Natural Language Toolkit (SpaCy ka chota sasta aur Purana alternative)
from typing import List, Dict, Optional # Types batane ke lie code mein

class LexicalAnalyzer:
    """Analyzes text to extract clean sentences."""
    # Is class ka aik hee maksad he "Lamba Paragraph" -> "Alaag Alag Sentences ki List"!!
    
    def __init__(self, use_spacy: bool = True):
        # Settings: Kya main Spacy Engine Use kroon? Default (yes)
        self.use_spacy = use_spacy
        self.nlp = None
        
        if self.use_spacy:
            try:
                # SpaCy ka C-language based fast English Pretrained-Model memory n laya!
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                # Ho skata e programmer ny Install ki ha na ho Download command bhool gye Hon terminal pe...
                print("Warning: spaCy model 'en_core_web_sm' not found. Falling back to NLTK.")
                self.use_spacy = False # Fallback : Ghabrana nahi ha! SpaCy ko OFF kia! NLTk lagayenge
        
        if not self.use_spacy:
            # Agar Spacy Ni chalra to NLTK se Sentences Break Karenge.
            try:
                # Pehle nltK ka package dhoonndo 'punkt' .. punkt sentences toor ta haa
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                # Nahi hy machine pr tou chupke se Download mardoo Server shuru hony par
                print("Downloading NLTK punkt tokenizer...")
                nltk.download('punkt')

    def analyze(self, text: str) -> List[Dict[str, any]]:
        """
        Tokenize text into sentences and clean them.
        Returns a list of dicts with keys: 'text', 'index', 'original_text'.
        """
        # STEP 1. TOKENIZE -> String Torney wala step
        if self.use_spacy:
            # SpaCy text padhe ga aur samajh k Sents bnaega. 
            # Faaida: ". " (Dot aur space) ke elawa mr. ms. acronyms b samjheyga without Galat tore.
            doc = self.nlp(text)
            raw_sentences = [sent.text for sent in doc.sents]
        else:
            # NLTK ka fast model text Tor rha h "List" mn.
            raw_sentences = nltk.sent_tokenize(text)

        cleaned_sentences = []
        index = 0 # Sentence Ka Number Tracking Taaqey asani hoh
        
        for sent in raw_sentences:
            # STEP 2. CLEAN -> HAr tutey huy tukry pe Safaee kroo
            
            clean_text = sent.strip() # Daaen - baaein se extra Fuzool k Spces aur Line breaks hata deyye
            
            # Agar khali string reh gae space mitany key baad tu isey Ignore kerdoo!!
            if not clean_text:
                continue
            
            # "Join(split())" -> Agr kisi jagah bohat sary 'spaces'  hi dal di he kissy pagle naey? unko Sirf 'ek' Space me badel dena ha
            clean_text = " ".join(clean_text.split())
            
            # Kitne alafaz they ye ginn lo.
            word_count = len(clean_text.split())
            
            # Heuristic Logic : Agar 5 lafaz se kum hy line.. tu matlab koi Page Number (e.g 1,2,xxi) ya small Fltu heading hai (Eg "Chapter 1"). Summarize Q kerun Usko bhla??? Daal do Garbage me!!
            if word_count < 5:
                continue
            
            # Achi aur Valid line Dictionary List mei Jorr do. "Original " ko rakhlo kiunke UI pr dikhane aur bad me Debug krna k am asjkta 
            cleaned_sentences.append({
                "text": clean_text,
                "index": index,
                "original_text": sent
            })
            
            index += 1 # Agli Line ka Number Ab 1 he phr 2 etc.
            
        return cleaned_sentences # Ylo bhai Saf Sutri Lineein Le Jao Backend ko!
