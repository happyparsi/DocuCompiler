import argparse
import os
import sys
import numpy as np
from src.extractor import SourceReader
from src.lexical import LexicalAnalyzer
from src.structural import StructuralParser
from src.semantic import SemanticGraph
from src.ir import SemanticIR
from src.optimizer import OptimizationEngine
from src.generator import TargetGenerator
try:
    from src.query import QueryCompiler
except ImportError:
    QueryCompiler = None

def main():
    parser = argparse.ArgumentParser(description="DocuCompiler: A modular document compiler system.")
    parser.add_argument("--input", required=True, help="Path to input document (PDF, DOCX, TXT)")
    parser.add_argument("--query", help="User question for QA")
    parser.add_argument("--strategy", default="moderate", choices=["aggressive", "moderate", "conservative"], help="Optimization strategy")
    parser.add_argument("--mode", default="paragraph", choices=["paragraph", "bullet"], help="Summary output mode")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)

    print(f"Starting DocuCompiler pipeline for: {args.input}")

    # Phase 1: Source Reader
    print("Phase 1: Reading source...")
    try:
        source_data = SourceReader.read(args.input)
        raw_text = source_data.get("raw_text", "")
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Phase 2: Lexical Analysis
    print("Phase 2: Lexical analysis...")
    lexical = LexicalAnalyzer(use_spacy=True)
    sentences = lexical.analyze(raw_text)
    print(f"  - Extracted {len(sentences)} raw sentences.")

    # Phase 3: Structural Parsing
    print("Phase 3: Structural parsing...")
    structural = StructuralParser()
    validated_sentences = structural.parse(sentences)
    print(f"  - Retained {len(validated_sentences)} validated sentences.")

    # Phase 4: Semantic Graph
    print("Phase 4: Building semantic graph (this may take a moment)...")
    semantic = SemanticGraph()
    scores, embeddings = semantic.build_graph(validated_sentences)
    print("  - Graph built and PageRank computed.")

    # Phase 5: Build S-IR
    print("Phase 5: Persisting to S-IR...")
    ir = SemanticIR()
    ir.save(validated_sentences, scores, embeddings)
    print("  - Saved to 'docucompiler.db'.")

    # Phase 6: Semantic Optimization
    print(f"Phase 6: Optimizing with strategy '{args.strategy}'...")
    optimizer = OptimizationEngine(strategy=args.strategy)
    optimized_sentences = optimizer.optimize(validated_sentences, scores, embeddings)
    print(f"  - Selected {len(optimized_sentences)} sentences.")

    # Phase 7: Target Generator
    print("Phase 7: Generating summary...")
    generator = TargetGenerator()
    summary = generator.generate(optimized_sentences, mode=args.mode)
    
    print("\n" + "="*40)
    print("SUMMARY")
    print("="*40)
    print(summary)
    print("="*40 + "\n")

    # Phase 8: Query Compiler (QA)
    if args.query:
        print("Phase 8: Processing query...")
        if QueryCompiler:
            try:
                qc = QueryCompiler()
                qc.build_index(validated_sentences, embeddings)
                answer = qc.answer(args.query)
                print("\n" + "?"*40)
                print(f"Question: {args.query}")
                print(f"Answer: {answer}")
                print("?"*40 + "\n")
            except ImportError:
                print("Error: QA dependencies not installed.")
        else:
            print("Error: QueryCompiler not available (missing dependencies).")

    print("\nDocuCompiler pipeline completed successfully.")

if __name__ == "__main__":
    main()
