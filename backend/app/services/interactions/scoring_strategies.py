from abc import ABC, abstractmethod
import math
from typing import Dict, Any, List
from pydantic import BaseModel
from app.services.interactions.models import SeverityLevel

class ScoringResult(BaseModel):
    raw_weight: int
    normalized_score: int
    clinical_band: str
    severity_counts: Dict[str, int]
    dominant_severity_driver: str
    explanation: str

class RiskScoringStrategy(ABC):
    @abstractmethod
    def calculate(self, raw_weight: int, severity_counts: Dict[str, int]) -> ScoringResult:
        pass

class ExponentialRiskStrategy(RiskScoringStrategy):
    """
    Deterministic asymptotic risk scoring strategy.
    
    Uses exponential decay: Score = 100 * (1 - e^(-k * W))
    Capped at 100.
    Floor of 80 if contraindicated interactions exist.
    """
    K_FACTOR = 0.322
    
    def calculate(self, raw_weight: int, severity_counts: Dict[str, int]) -> ScoringResult:
        has_contraindicated = severity_counts.get(SeverityLevel.CONTRAINDICATED.value, 0) > 0
        
        # 1. Calculate Base Normalized Score
        if raw_weight == 0:
            normalized = 0
        else:
            normalized = round(100 * (1 - math.exp(-self.K_FACTOR * raw_weight)))
            
        # 2. Apply "Contraindicated Floor" Rule
        # "Modify scoring engine so that if any contraindicated interaction exists, minimum score returned is 80."
        if has_contraindicated and normalized < 80:
            normalized = 80
            
        normalized = min(100, normalized)
        
        # 3. Determine Clinical Band
        if normalized < 25:
            band = "Low"
        elif normalized < 50:
            band = "Moderate"
        elif normalized < 80:
            band = "High"
        else:
            band = "Critical"
            
        # 4. Find Dominant Severity Driver
        dominant = "none"
        # Ordered by clinical importance
        for level in [SeverityLevel.CONTRAINDICATED, SeverityLevel.SEVERE, SeverityLevel.MODERATE, SeverityLevel.MILD]:
            if severity_counts.get(level.value, 0) > 0:
                dominant = level.value
                break
                
        # 5. Build Explanation
        if raw_weight == 0:
            explanation = "No known pharmacological interactions detected between the prescribed medications."
        else:
            active_severities = [f"{count} {level}" for level, count in severity_counts.items() if count > 0]
            explanation = f"Detected {', '.join(active_severities)} interactions. Dominant clinical risk: {dominant.upper()}."
            if has_contraindicated:
                explanation += " WARNING: Potential terminal risk detected."

        return ScoringResult(
            raw_weight=raw_weight,
            normalized_score=normalized,
            clinical_band=band,
            severity_counts=severity_counts,
            dominant_severity_driver=dominant,
            explanation=explanation
        )
