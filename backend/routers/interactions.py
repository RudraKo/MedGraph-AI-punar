from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from backend.db import db

router = APIRouter(prefix="/interactions", tags=["interactions"])

class InteractionRequest(BaseModel):
    drug_ids: List[str]

@router.post("/check")
async def check_interactions(req: InteractionRequest):
    nodes = []
    edges = []
    interactions = []
    severity_summary = {"Contraindicated": 0, "Major": 0, "Moderate": 0, "Minor": 0}
    
    for d_id in req.drug_ids:
        nodes.append({"data": {"id": d_id, "label": d_id, "brand_name": d_id, "drug_class": "Unknown"}})
        
    for i in range(len(req.drug_ids)):
        for j in range(i+1, len(req.drug_ids)):
            d1 = req.drug_ids[i]
            d2 = req.drug_ids[j]
            inter = await db.interactions.find_one({"$or": [
                {"drug_1": d1, "drug_2": d2},
                {"drug_1": d2, "drug_2": d1}
            ]})
            if inter:
                sev = inter.get("severity", "Moderate")
                if sev in severity_summary:
                    severity_summary[sev] += 1
                edge_data = {
                    "id": f"{d1}-{d2}",
                    "source": d1,
                    "target": d2,
                    "severity_label": sev,
                    "mechanism": inter.get("description", "Unknown interaction"),
                    "recommendation": "Consult doctor"
                }
                edges.append({"data": edge_data})
                interactions.append(edge_data)

    return {
        "risk_score": len(interactions) * 2.5,
        "interaction_count": len(interactions),
        "graph": {"nodes": nodes, "edges": edges},
        "severity_summary": severity_summary,
        "interactions": interactions
    }
