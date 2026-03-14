import spacy
import pytextrank
from src.baselines import ExtractiveBaselines
from src.lexical import LexicalAnalyzer
from src.semantic import SemanticGraph
from src.optimizer import OptimizationEngine
from src.generator import TargetGenerator

def test_minimal():
    print("Testing DocuCompiler components...")
    text = "The Mars rover has discovered new evidence of ancient water on the Red Planet. Scientists from NASA reported that soil samples contain minerals that only form in the presence of liquid water."
    
    lex = LexicalAnalyzer()
    sentences = lex.analyze(text)
    print(f"Sentences: {len(sentences)}")
    
    sem = SemanticGraph()
    scores, embeddings = sem.build_graph(sentences)
    print(f"Graph scores: {len(scores)}")
    
    opt = OptimizationEngine()
    final = opt.optimize(sentences, scores, embeddings)
    print(f"Optimized sentences: {len(final)}")
    
    gen = TargetGenerator()
    summary = gen.generate(final)
    print(f"Summary: {summary}")

def test_baselines():
    print("\nTesting Baselines...")
    text = "Artificial Intelligence is a field of computer science. It focuses on creating intelligent agents. Ethical considerations are important."
    
    eb = ExtractiveBaselines()
    try:
        tr = eb.textrank_summary(text)
        print(f"TextRank: {tr}")
    except Exception as e:
        print(f"TextRank failed: {e}")
        
    ti = eb.tfidf_summary(text)
    print(f"TF-IDF: {ti}")

if __name__ == "__main__":
    test_minimal()
    test_baselines()
