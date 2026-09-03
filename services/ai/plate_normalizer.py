import re

class PlateNormalizer:
    """
    Cleans and normalizes raw OCR text into valid Indian license plate formats.
    """
    
    # Standard Indian Plate format e.g. GJ01AB1234
    # State (2) + District (1-2) + Series (1-3) + Number (1-4)
    # We are very loose to accommodate OCR errors, but strict enough to reject random text
    INDIAN_PLATE_PATTERN = re.compile(r"^[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{1,4}$")

    @classmethod
    def normalize(cls, raw_text: str) -> str:
        """
        Takes raw OCR string, upper-cases it, and strips non-alphanumeric characters.
        If it loosely fits an Indian registration pattern, it's considered normalized.
        """
        # 1. Clean up characters
        cleaned = re.sub(r'[^A-Za-z0-9]', '', raw_text).upper()
        
        # 2. Heuristic corrections (e.g. OCR misread '0' as 'O', '1' as 'I' etc.)
        # In Indian plates, first two are ALWAYS letters (State code)
        if len(cleaned) >= 2:
            cleaned = cls._correct_letters(cleaned[0:2]) + cleaned[2:]
            
        # The next 1-2 characters should be digits (District code)
        # But this is tricky without full context, so we'll leave aggressive replacement
        # to a minimum to avoid corrupting good reads.
        
        return cleaned
        
    @classmethod
    def is_valid_format(cls, normalized_text: str) -> bool:
        """
        Returns True if the string roughly matches an Indian vehicle plate structure.
        """
        # Ex: GJ01AB1234 -> Length ~8-10
        if len(normalized_text) < 7 or len(normalized_text) > 10:
            return False
            
        # Must start with two letters (State code)
        if not normalized_text[0:2].isalpha():
            return False
            
        # Must end with digits
        if not normalized_text[-1].isdigit():
            return False
            
        return True

    @staticmethod
    def _correct_letters(text: str) -> str:
        return text.replace("0", "O").replace("1", "I").replace("8", "B").replace("6", "G")
