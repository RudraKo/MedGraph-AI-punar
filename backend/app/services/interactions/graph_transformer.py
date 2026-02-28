from typing import List, Dict, Any, Set
from app.services.interactions.interaction_engine import SeverityLevel

class GraphTransformer:
    """
    Adapter service that transforms the raw output of the Interaction Engine
    into a structured JSON payload specifically formatted for Cytoscape.js
    frontend rendering.
    """
    
    # Predefined UI color mapping based on clinical severity
    SEVERITY_COLOR_MAP = {
        SeverityLevel.MILD: "green",
        SeverityLevel.MODERATE: "yellow",
        SeverityLevel.SEVERE: "red",
        SeverityLevel.CONTRAINDICATED: "black"
    }

    @classmethod
    def to_cytoscape(cls, prescribed_drugs: List[str], interactions: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Converts clinical domain data into a Graph UI schema.
        
        Args:
            prescribed_drugs: The full list of medications evaluated.
            interactions: The exact 'interactions' array returned from `InteractionEngine.analyze_prescription`.
            
        Returns:
            Cytoscape-compliant JSON containing 'nodes' and 'edges'.
        """
        cytoscape_data: Dict[str, List[Dict[str, Any]]] = {
            "nodes": [],
            "edges": []
        }
        
        # 1. Enforce Node Uniqueness O(N)
        # Convert all to uppercase to ensure case-insensitive deduplication
        unique_nodes: Set[str] = {drug.upper() for drug in prescribed_drugs}
        
        # We also need to guarantee any drug cited in an edge exists as a node, 
        # even if somehow missed in the main prescription list (defensive data mapping).
        for interaction in interactions:
            unique_nodes.add(interaction["drug_a"].upper())
            unique_nodes.add(interaction["drug_b"].upper())
            
        # Parse into Cytoscape Node schema
        for drug in unique_nodes:
            cytoscape_data["nodes"].append({
                "data": { "id": drug }
            })
            
        # 2. Build Directed Edges O(E)
        for interaction in interactions:
            raw_severity = interaction["severity"]
            
            # Map the raw string back to the Enum to pull the Hex Color
            # (Allows fallback to gray if UI data contract ever misaligns)
            try:
                severity_enum = SeverityLevel(raw_severity)
                edge_color = cls.SEVERITY_COLOR_MAP[severity_enum]
            except ValueError:
                edge_color = "gray"
                
            cytoscape_data["edges"].append({
                "data": {
                    "source": interaction["drug_a"].upper(),
                    "target": interaction["drug_b"].upper(),
                    "severity": raw_severity,
                    "color": edge_color,
                    # We pass the explanation down so Cytoscape can render tooltips when edges are clicked
                    "explanation": interaction["explanation"]
                }
            })
            
        return cytoscape_data
