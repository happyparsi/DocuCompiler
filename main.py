import argparse # Terminal commands aur arguments parse karne ke liye (jaise --input, --query)
import os # Operating system se related kaam karne ke liye (jaise file check/delete karna)
import sys # System-specific parameters aur functions ke liye (jaise program ko exit karna)
import numpy as np # Arrays aur mathematical calculations (vectors) handle karne ke liye

# Hamare apne banaye hue modules (DocuCompiler pipeline ke alag alag hisse) import kar rahe hain
from src.extractor import SourceReader # File (PDF/DOCX/TXT) se plain text nikalne ke liye
from src.lexical import LexicalAnalyzer # Lambe text ko alag-alag sentences mein todne ke liye
from src.structural import StructuralParser # Faltu cheezein (tables, symbols) aur duplicate sentences hatane ke liye
from src.semantic import SemanticGraph # Sentences ke meaning (embeddings) nikalne aur graph (PageRank) banane ke liye
from src.ir import SemanticIR # Processed data (embeddings, scores) ko format mein SQLite database me save karne ke liye
from src.optimizer import OptimizationEngine # Bekar (redundant) ya kam importance wale sentences drop karne ke liye
from src.generator import TargetGenerator # Bachi hui top lines ko jod kar final 'Summary' banane ke liye

try:
    # Question Answering (QA) feature ke liye module import
    from src.query import QueryCompiler 
except ImportError:
    # Agar Faiss/Transformers library install nahi hai, toh app crash na kare isliye None set kiya
    QueryCompiler = None 

def main():
    # Setup kar rahe hain ki terminal me help message kya dikhega
    parser = argparse.ArgumentParser(description="DocuCompiler: A modular document compiler system.")
    
    # User se file path lene ke liye zaruri (required) argument
    parser.add_argument("--input", required=True, help="Path to input document (PDF, DOCX, TXT)")
    
    # User se QA ke liye sawal (optional) lene ka argument
    parser.add_argument("--query", help="User question for QA")
    
    # Summary choti ya badi karni hai, uski strategy tay karne ke liye choices (default 'moderate' hai)
    parser.add_argument("--strategy", default="moderate", choices=["aggressive", "moderate", "conservative"], help="Optimization strategy")
    
    # Result paragraph mein chahiye ya bullet points mein
    parser.add_argument("--mode", default="paragraph", choices=["paragraph", "bullet"], help="Summary output mode")
    
    # Terminal mein jo arguments pass kiye gaye, unko padh (parse) liya
    args = parser.parse_args()

    # Pehle check karo ki jo file path --input mein diya hai, wo asal mein exist karta bhi hai ya nahi?
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1) # File nahi mili toh program error code (1) ke sath band kardo

    print(f"Starting DocuCompiler pipeline for: {args.input}")

    # Phase 1: Source Reader - File kholna aur padhna
    print("Phase 1: Reading source...")
    try:
        source_data = SourceReader.read(args.input) # SourceReader ko file pass karke Data extract kiya
        raw_text = source_data.get("raw_text", "") # Exact text nikala dictionary se
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Phase 2: Lexical Analysis - Badi kahani ko lines (sentences) me torna
    print("Phase 2: Lexical analysis...")
    lexical = LexicalAnalyzer(use_spacy=True) # SpaCy NLP tool start kiya
    sentences = lexical.analyze(raw_text) # Text dekar sentences ki list banai
    print(f"  - Extracted {len(sentences)} raw sentences.")

    # Phase 3: Structural Parsing - Fuzool lines / symbols hatana
    print("Phase 3: Structural parsing...")
    structural = StructuralParser()
    validated_sentences = structural.parse(sentences) # Saaf sentences return hue
    print(f"  - Retained {len(validated_sentences)} validated sentences.")

    # Phase 4: Semantic Graph - Samajhna ki konsi line sabse important hai (AI Magic)
    print("Phase 4: Building semantic graph (this may take a moment)...")
    semantic = SemanticGraph()
    scores, embeddings = semantic.build_graph(validated_sentences) # Har sentence ko numbers(embeds) aur PageRank Score diya
    print("  - Graph built and PageRank computed.")

    # Phase 5: Build S-IR - Data ko Database me persist/save karna
    print("Phase 5: Persisting to S-IR...")
    ir = SemanticIR()
    ir.save(validated_sentences, scores, embeddings) # Sqlite DB me table banake save maria
    print("  - Saved to 'docucompiler.db'.")

    # Phase 6: Semantic Optimization - Duplicate baatein kahne wali lines delete kardo (Drop redundancies)
    print(f"Phase 6: Optimizing with strategy '{args.strategy}'...")
    optimizer = OptimizationEngine(strategy=args.strategy) # Kaisi summary chahiye us hisaab se engine set kiya
    optimized_sentences = optimizer.optimize(validated_sentences, scores, embeddings) # Kam wali lines filter ho gayi!
    print(f"  - Selected {len(optimized_sentences)} sentences.")

    # Phase 7: Target Generator - Output dikhana (Paragraph / Bullet format me)
    print("Phase 7: Generating summary...")
    generator = TargetGenerator()
    summary = generator.generate(optimized_sentences, mode=args.mode) # Filtered lines ko jod diya space ya break laga ke
    
    # Final Summary screen par print ho rahi hai
    print("\n" + "="*40)
    print("SUMMARY")
    print("="*40)
    print(summary)
    print("="*40 + "\n")

    # Phase 8: Query Compiler (QA) - Agar user ne sawal pucha hai
    if args.query:
        print("Phase 8: Processing query...")
        if QueryCompiler:
            try:
                qc = QueryCompiler()
                qc.build_index(validated_sentences, embeddings) # Fast vector search ke lie Index banaya (FAISS wala)
                answer = qc.answer(args.query) # User ka sawal index se search karwake T5 model se jawaab Manga
                
                # Jawab screen pe dikhao
                print("\n" + "?"*40)
                print(f"Question: {args.query}")
                print(f"Answer: {answer}")
                print("?"*40 + "\n")
            except ImportError:
                print("Error: QA dependencies not installed.")
        else:
            print("Error: QueryCompiler not available (missing dependencies).")

    print("\nDocuCompiler pipeline completed successfully.")

# Jab command line se chalega tabhi main() function call hoga (doosri program se import par nahi chalega)
if __name__ == "__main__":
    main()
