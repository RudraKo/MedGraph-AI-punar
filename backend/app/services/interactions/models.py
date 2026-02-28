from enum import Enum
from pydantic import BaseModel

class SeverityLevel(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CONTRAINDICATED = "contraindicated"

class InteractionRecord(BaseModel):
    """
    Data Transfer Object (DTO) representing a single row from the 
    SQLite drug interaction database table.
    """
    drug_a: str
    drug_b: str
    severity: SeverityLevel
    explanation: str
