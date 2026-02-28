from typing import Dict, Any, List
from app.services.interactions.graph_transformer import GraphTransformer
from app.services.interactions.interaction_engine import SeverityLevel

def test_cytoscape_transformer():
    # 1. Mock Prescription (from Request Input)
    prescribed_drugs = ["Aspirin", "Warfarin", "Vitamin C"]
    
    # 2. Mock InterationEngine Output
    mock_interactions: List[Dict[str, Any]] = [
        {
            "drug_a": "ASPIRIN",
            "drug_b": "WARFARIN",
            "severity": "severe",   # Should map to red
            "explanation": "Severe bleeding risk"
        },
        {
            "drug_a": "ASPIRIN",
            "drug_b": "IBUPROFEN",  # Not in the prescribed list, testing defensive extraction
            "severity": "mild",     # Should map to green
            "explanation": "Minor stomach irritation"
        }
    ]
    
    print(f"Transforming Interaction Output Array into Cytoscape Graph...")
    
    # 3. Execution
    cytoscape_json = GraphTransformer.to_cytoscape(prescribed_drugs, mock_interactions)
    
    import json
    print("\nAPI Response Envolope:")
    print(json.dumps(cytoscape_json, indent=2))
    
    # Validation 1: Node Uniqueness and Defensive Harvesting
    nodes = cytoscape_json["nodes"]
    # We expect 4 total nodes: Aspirin, Warfarin, Vitamin C (Prescribed), AND Ibuprofen (Harvested from Edge)
    assert len(nodes) == 4
    
    node_ids = {n["data"]["id"] for n in nodes}
    assert "IBUPROFEN" in node_ids
    assert "VITAMIN C" in node_ids
    assert "ASPIRIN" in node_ids
    assert "WARFARIN" in node_ids
    
    # Validation 2: Edge Mapping
    edges = cytoscape_json["edges"]
    assert len(edges) == 2
    
    # Severe edge should be red
    severe_edge = next(e for e in edges if e["data"]["severity"] == "severe")
    assert severe_edge["data"]["color"] == "red"
    assert "explanation" in severe_edge["data"]
    
    # Mild edge should be green
    mild_edge = next(e for e in edges if e["data"]["severity"] == "mild")
    assert mild_edge["data"]["color"] == "green"
    
    print("\n✅ Cytoscape Component Transformer verified successfully.")
    print("✅ Clinical Enums accurately mapped to UI color bindings.")

if __name__ == "__main__":
    test_cytoscape_transformer()
