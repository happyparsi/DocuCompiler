import pypandoc
import sys
import os

md_file = r"C:\Users\ACER\.gemini\antigravity\brain\4117fa31-0eed-479d-b5cc-011017935cfa\Web_Technology_Lab_Notes.md"
docx_file = r"c:\Users\ACER\OneDrive\Desktop\DocuCompiler\Web_Technology_Lab_Notes.docx"

try:
    print("Checking for pandoc installation...")
    try:
        pypandoc.get_pandoc_version()
        print("Pandoc is already installed.")
    except Exception:
        print("Pandoc not found. Downloading pandoc...")
        pypandoc.download_pandoc()
        print("Pandoc downloaded successfully.")
        
    print("Converting markdown to docx...")
    pypandoc.convert_file(md_file, 'docx', outputfile=docx_file)
    print(f"Conversion successful. Saved to {docx_file}")
except Exception as e:
    print(f"Error during conversion: {e}")
    sys.exit(1)
