import re

def levenshtein(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

class IndianPlateNormalizer:
    """
    Advanced normalizer for Indian High Security Registration Plates (HSRP).
    Handles standard formats and Bharat (BH) series.
    Applies contextual character corrections and supports fuzzy matching.
    """
    
    # Matches GJ01ER8842, DL10A1234, etc.
    REGULAR_PATTERN = re.compile(r"^([A-Z]{2})(\d{1,2})([A-Z]{1,3})?(\d{1,4})$")
    # Matches 22BH1234AA
    BHARAT_PATTERN = re.compile(r"^(\d{2})(BH)(\d{4})([A-Z]{1,2})$")

    @classmethod
    def normalize(cls, raw_text: str) -> str:
        # 1. Sanitize
        cleaned = re.sub(r'[^A-Za-z0-9]', '', raw_text).upper()
        if len(cleaned) < 6:
            return cleaned

        # 2. Heuristic Contextual Corrections
        # We need to guess if it's BH series or regular.
        # BH series starts with 2 numbers (Year) then 'BH'
        if len(cleaned) >= 8 and cleaned[2:4] in ["BH", "8H", "B4"]:
            return cls._normalize_bharat(cleaned)
        else:
            return cls._normalize_regular(cleaned)

    @classmethod
    def _normalize_regular(cls, text: str) -> str:
        # Expected: Letter(2) + Digit(1-2) + Letter(0-3) + Digit(1-4)
        # We'll do simple position-based substitution assuming standard 10-char format
        # If length is slightly off, we do our best.
        if len(text) < 4:
            return text
            
        state_code = cls._to_letters(text[0:2])
        rto_code = cls._to_digits(text[2:4]) if len(text) >= 4 else text[2:]
        
        remainder = text[4:]
        series = ""
        unique = ""
        
        # Walk backwards to find the 4 digits
        for i in range(len(remainder)-1, -1, -1):
            if remainder[i].isdigit() or remainder[i] in ['O','Q','D','I','L','Z','B','S']:
                unique = remainder[i] + unique
            else:
                series = remainder[:i+1]
                break
                
        series = cls._to_letters(series)
        
        # Ensure unique is max 4, mostly digits
        if len(unique) > 4:
            series += cls._to_letters(unique[:-4])
            unique = unique[-4:]
            
        unique = cls._to_digits(unique)
        
        return state_code + rto_code + series + unique

    @classmethod
    def _normalize_bharat(cls, text: str) -> str:
        # Expected: YY BH #### XX
        if len(text) < 6:
            return text
            
        year = cls._to_digits(text[0:2])
        bh = "BH"
        
        remainder = text[4:]
        unique = ""
        series = ""
        
        if len(remainder) >= 4:
            unique = cls._to_digits(remainder[0:4])
            series = cls._to_letters(remainder[4:])
        else:
            unique = cls._to_digits(remainder)
            
        return year + bh + unique + series

    @classmethod
    def is_valid_format(cls, normalized_text: str) -> bool:
        if cls.REGULAR_PATTERN.match(normalized_text):
            return True
        if cls.BHARAT_PATTERN.match(normalized_text):
            return True
        return False

    @staticmethod
    def _to_letters(text: str) -> str:
        return text.translate(str.maketrans("012856", "OIZBSG"))
        
    @staticmethod
    def _to_digits(text: str) -> str:
        return text.translate(str.maketrans("OQDI LZBS", "0001 1285"))

    @classmethod
    def fuzzy_match(cls, normalized_read: str, watchlist_plates: list[str]) -> tuple[bool, str, float]:
        """
        Returns (is_match, matched_plate, confidence_penalty)
        If exact match, penalty = 0.0
        If distance == 1, penalty = 0.1
        """
        for w_plate in watchlist_plates:
            if normalized_read == w_plate:
                return True, w_plate, 0.0
                
            dist = levenshtein(normalized_read, w_plate)
            if dist == 1:
                return True, w_plate, 0.1 # 10% penalty
                
        return False, "", 0.0
