import docx
import os

def extract_text(file_path):
    if not os.path.exists(file_path):
        return f"File {file_path} not found."
    doc = docx.Document(file_path)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)

if __name__ == "__main__":
    content = ""
    content += "--- DocuCompiler.docx ---\n"
    content += extract_text("DocuCompiler.docx")
    content += "\n" + "="*50 + "\n"
    content += "--- Technological gaps.docx ---\n"
    content += extract_text("Technological gaps.docx")
    
    with open("references_text.txt", "w", encoding="utf-8") as f:
        f.write(content)
    print("Extracted to references_text.txt")
