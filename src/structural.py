from typing import List, Dict # Python typing madadgaar
import re # Regular Expressions (Pattrens dhoondane ki Library)

class StructuralParser:
    """Filters sentences based on structural rules."""
    # Ye parser Lexical k baad chalta he .iska Kaam Text ke Content Shape (structure) ko test kena 

    def parse(self, sentences: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Filters sentences to remove duplicates and noise.
        """
        seen_texts = set() # SET: ek data structure ha jisme duplicate Cheez nahi rakh skty (Bahut taiz Search krta hai List se!)
        validated_sentences = []

        for sent in sentences:
            text = sent.get("text", "") # Text nikala Dict se, ager ni mila tu Error nahi dga ,khale sTring"" de ga default.
            
            # FILTER 1: Remove duplicates (Duplicate baatein hatao)
            # Agar hum ny set me abhi abhi ye text save kerlya tha...
            if text in seen_texts:
                continue # To is current wali line ko skips Maroo (Qk PDF headers 5th dfa aya hoga Page k top se lol). 
                
            seen_texts.add(text) # Pehlie Dfa dekh ahe to "Set" mei yaad dasht liy save kraa.
            
            # FILTER 2: Remove noisy lines (Symbolic Kachre wali lines nikaalo)
            # Findall: RegEx =>  [^\w\s] -> Iska maktlab "Aisy charcters laao joo Naa (^) Word(\w) ho aur nAa hei space (\s) ho!" . Yaani -> @#$%^&*()-=+/\|][{}  etc
            symbol_count = len(re.findall(r'[^\w\s]', text))
            
            # Agar Maths ka equation / code / table huwa.. tu un me Words kam, symbols jyada hungay -> Ratio check lgaee!. 
            if symbol_count / len(text) > 0.3:  # Heuristic Formula: Agar >30% line mei ye ajeeb o garib nakshay hyn ? Fail.
                continue
            
            # FILTER 3: Basic length filtering (Lexical ne ALfaz ko dekha tha, ye Character lambi ko dekhyga)
            if len(text) < 10:  # Agar string sirfff "A. B." hy .. tu Character Length 5 hai.. To meaningfull kese hoi? Reject.
                continue

            # Pass Hogayi Line sab test !!! Usko pakrr lioo aaghy bjhne kliy!!
            validated_sentences.append(sent)

        # Kacra door ho chuka hai, return saaf stuff for Next Pipeline. 
        return validated_sentences
