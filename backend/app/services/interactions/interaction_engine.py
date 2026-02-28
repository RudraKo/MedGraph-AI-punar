from typing import List, Dict, Any, Tuple
from collections import defaultdict
from itertools import combinations
from app.services.interactions.models import SeverityLevel, InteractionRecord
from app.services.interactions.scoring_strategies import RiskScoringStrategy, ExponentialRiskStrategy

class InteractionEngine:
    """
    A deterministic graph-based drug interaction engine.
    
    This operates entirely in memory using standard Python data structures 
    (Adjacency Lists via Dicts) mapping exact clinical constraints.
    It contains zero ML black-box logic, ensuring 100% explainable and 
    accountable clinical scoring.
    """
    
    # Static weights defined by the clinical requirement contract
    SEVERITY_WEIGHTS = {
        SeverityLevel.MILD: 1,
        SeverityLevel.MODERATE: 2,
        SeverityLevel.SEVERE: 4,
        SeverityLevel.CONTRAINDICATED: 5
    }

    def __init__(self, scoring_strategy: RiskScoringStrategy = None):
        """
        Inject scoring strategy via constructor (Strategy Pattern).
        Defaults to ExponentialRiskStrategy if none provided.
        """
        self.scoring_strategy = scoring_strategy or ExponentialRiskStrategy()

    def _build_adjacency_graph(self, records: List[InteractionRecord]) -> Dict[str, Dict[str, InteractionRecord]]:
        """
        Builds an undirected adjacency graph from the flat database records.
        """
        graph = defaultdict(dict)
        for record in records:
            drug_a = record.drug_a.strip().upper()
            drug_b = record.drug_b.strip().upper()
            
            graph[drug_a][drug_b] = record
            graph[drug_b][drug_a] = record
            
        return graph

    def analyze_prescription(
        self, 
        prescribed_drugs: List[str], 
        db_records: List[InteractionRecord]
    ) -> Dict[str, Any]:
        """
        Detects all pairwise conflicts and computes risk metadata using the injected strategy.
        """
        # 1. Build the O(1) lookup graph
        graph = self._build_adjacency_graph(db_records)
        
        # Normalize and deduplicate
        unique_drugs = list({d.strip().upper() for d in prescribed_drugs})
        
        interactions_found = []
        total_raw_weight = 0
        severity_counts = {level.value: 0 for level in SeverityLevel}
        
        # 2. Pairwise Detection
        for drug_x, drug_y in combinations(unique_drugs, 2):
            if drug_y in graph.get(drug_x, {}):
                conflict = graph[drug_x][drug_y]
                
                interactions_found.append({
                    "drug_a": drug_x,
                    "drug_b": drug_y,
                    "severity": conflict.severity.value,
                    "explanation": conflict.explanation
                })
                
                # Update counters and weight
                total_raw_weight += self.SEVERITY_WEIGHTS[conflict.severity]
                severity_counts[conflict.severity.value] += 1

        # 3. Use Strategy for Scoring and Categorization
        scoring_result = self.scoring_strategy.calculate(total_raw_weight, severity_counts)

        # 4. Final Response Payload (Extended as requested)
        return {
            "interactions": interactions_found,
            "risk_score": scoring_result.normalized_score,
            "severity_summary": scoring_result.clinical_band,  # Mapping for backward compatibility
            "clinical_band": scoring_result.clinical_band,
            "raw_weight": scoring_result.raw_weight,
            "severity_counts": scoring_result.severity_counts,
            "dominant_severity_driver": scoring_result.dominant_severity_driver,
            "explanation": scoring_result.explanation
        }
