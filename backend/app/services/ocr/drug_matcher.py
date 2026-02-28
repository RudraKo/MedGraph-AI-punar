from typing import List, Tuple, Optional
from rapidfuzz import process, fuzz

class DrugMatcher:
    """
    Fuzzy string matching for drug interactions using rapidfuzz C++ bindings
    for maximum performance over large datasets.
    """
    
    # Define the minimum confidence score (0.0 to 1.0) to consider a match valid.
    # A score of 0.65 allows for severe multi-character misreads by Tesseract 
    # (e.g., 'AM0XIC1LL1N 500 MG' extracting to 'AMOXICILLIN').
    MIN_CONFIDENCE_THRESHOLD = 0.65
    
    @staticmethod
    def match_drug(extracted_text: str, known_drugs: List[str]) -> Optional[Tuple[str, float]]:
        """
        Calculates the Levenshtein-based similarity between the extracted
        text and the known drug database.
        
        Args:
            extracted_text (str): The sanitized OCR output.
            known_drugs (List[str]): A list of uppercase valid drug names retrieved from the database.
            
        Returns:
            Optional[Tuple[str, float]]: A tuple containing the best matched drug
            and its raw confidence score, or None if the threshold was not met.
        """
        if not extracted_text or not known_drugs:
            return None

        # Extract best match using the partial_ratio scorer (handles substring alignment
        # and ignores noise like ' 500 MG' appended to the actual drug name)
        # Returns a tuple of (MatchString, Score[0-100], Index)
        match_result = process.extractOne(
            query=extracted_text, 
            choices=known_drugs, 
            scorer=fuzz.partial_ratio
        )
        
        if not match_result:
            return None
            
        matched_string, unnormalized_score, _ = match_result
        
        # Rapidfuzz returns 0-100, normalize to 0.0-1.0 to match our API contract
        confidence_score = unnormalized_score / 100.0
        
        if confidence_score >= DrugMatcher.MIN_CONFIDENCE_THRESHOLD:
            return (matched_string, confidence_score)
            
        return None
