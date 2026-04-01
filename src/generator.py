from typing import List, Dict # Typing support k lye lagaya hai..

class TargetGenerator:
    """Generates summaries from optimized sentences."""
    # Ye bohut hi asan aur akhri step ki Class hai! Iska kaam sirf itna ha ke bikhre hue top sentences ko 
    # wapas eik Single Text (Summary) me jod de... Taqe User ko Display ho sakay!

    def generate(self, sentences: List[Dict[str, any]], mode: str = 'paragraph') -> str:
        """
        Generates a summary.
        Mode: 'paragraph' or 'bullet'.
        """
        if not sentences:
            # Agar kisi wajah se khali file agae tou error dene ki bjaa khud chup hojao...
            return ""
            
        # UI/Backend ya main.py se mode pass hota hai! ('bullet' chahyeye yaa phr 'paragraph' ?)
        
        # SAAAWAL: Agar sentences list upar nichey hoi wese tu optimizer me set ki th per agr bhul jye tu?
        # JAAWAB: Sort_By Original Document ka line-number. Takay Kahani ka sense bane! Start-Middle-End :)
        sorted_sentences = sorted(sentences, key=lambda s: s['index'])
        
        # For Loop in Single Line (List comprehension): "Index, text, org_text" wali Dictionary se.. 
        # srf 'Text' wala hissa nikal k Ek Simple English Lines ki List Bana lo.
        texts = [s['text'] for s in sorted_sentences]
        
        # Ab Joda Jori keroo!
        if mode == 'bullet':
            # Agar 'bullet' likha gaya, tou har sentence ke shuru me "\n- " (Slash-N Enter deta h aur dash bullet bntha hy) laga kar jod do.
            return "\n".join([f"- {text}" for text in texts])
        else:
            # Verna bas Normal paragraphs ki tarhan aapas me eik 'Space' dekar jodta ja!
            return " ".join(texts)

if __name__ == "__main__":
    # Example test krna ho terminal me 'python src/generator.py' likh ker Tu ye chalega!
    sents = [
        {"index": 0, "text": "Me aik sentence hu."},
        {"index": 5, "text": "Ur me aakhri sentence hu."}
    ]
    gen = TargetGenerator()
    print("Paragraph:\n", gen.generate(sents, 'paragraph'))
    print("\nBullet:\n", gen.generate(sents, 'bullet'))
