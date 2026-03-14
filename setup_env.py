import nltk
import spacy
import sys
import subprocess

def download_nltk_data():
    print("Downloading NLTK data...")
    nltk.download('punkt')
    nltk.download('punkt_tab')
    print("NLTK data downloaded.")

def download_spacy_model():
    print("Downloading spaCy model en_core_web_sm...")
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("spaCy model downloaded.")
    except subprocess.CalledProcessError:
        print("Failed to download spaCy model. Please run 'python -m spacy download en_core_web_sm' manually.")

if __name__ == "__main__":
    try:
        download_nltk_data()
        download_spacy_model()
        print("\nAll setup steps completed successfully!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
