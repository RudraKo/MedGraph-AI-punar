import re

class TextCleaner:
    """
    Exposes pure functions for normalizing raw Tesseract OCR output.
    """
    
    @staticmethod
    def clean_ocr_text(raw_text: str) -> str:
        """
        Accepts raw string from Tesseract and sanitizes it for exact
        or fuzzy string matching.
        
        Steps:
        1. Replace newlines with spaces.
        2. Convert to uppercase.
        3. Strip all non-alphanumeric noise (keeps spaces).
        4. Collapse multiple spaces into a single space.
        
        Args:
            raw_text (str): The raw multiline string from Tesseract.
            
        Returns:
            str: A clean, single-line uppercase string with normalized spaces.
        """
        if not raw_text or not isinstance(raw_text, str):
            return ""

        # Remove newlines and tabs
        text = raw_text.replace('\n', ' ').replace('\t', ' ')
        
        # Convert to upper for uniform matching
        text = text.upper()
        
        # Keep only A-Z, 0-9, and spaces. Drops special chars like ™, ®, ©, punctuation
        text = re.sub(r'[^A-Z0-9\s]', '', text)
        
        # Collapse multiple spaces and strip exterior padding
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
