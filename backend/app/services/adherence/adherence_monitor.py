from typing import Dict, Any
from datetime import datetime, timezone
from app.domain.models.adherence import AdherenceStatusStr
from app.repositories.adherence_repo import AdherenceRepository

class AdherenceMonitorService:
    """
    Business logic layer for patient adherence compliance.
    
    Evaluates medication confirmations/misses against configurable policies
    (e.g., triggering Guardian safety alerts on 3 consecutive global misses).
    """
    
    # Policy Configurations
    CONSECUTIVE_MISS_THRESHOLD = 3
    
    def __init__(self, adherence_repo: AdherenceRepository):
        self.repo = adherence_repo

    def process_medication_event(
        self, 
        patient_id: str, 
        medication_name: str, 
        scheduled_time: datetime,
        status: AdherenceStatusStr
    ) -> Dict[str, Any]:
        """
        Logs a patient's medication status and enforces the Guardian escalations pipeline.
        
        Args:
            patient_id: Identifier for the patient.
            medication_name: The drug they were supposed to take.
            scheduled_time: When it was prescribed.
            status: 'TAKEN' or 'MISSED'.
            
        Returns:
            JSON-serializable summary of the system state and any fired flags.
        """
        # 1. Persist the log event
        self.repo.log_adherence(patient_id, medication_name, scheduled_time, status)
        
        # We start by drafting the response envelope
        response_envelope = {
            "patient_id": patient_id,
            "status_logged": status.value,
            "consecutive_misses": 0,
            "guardian_alert_triggered": False,
            "notes": "Adherence logged successfully."
        }
        
        # 2. Re-calculate the current consecutive Miss pipeline
        current_misses = self.repo.get_recent_misses_count(patient_id)
        response_envelope["consecutive_misses"] = current_misses
        
        # 3. Policy Evaluation
        if status == AdherenceStatusStr.TAKEN:
            pass # Reset implicit via the repository query
            
        elif status == AdherenceStatusStr.MISSED:
            if current_misses >= self.CONSECUTIVE_MISS_THRESHOLD:
                # 4. Debounce check: Has the guardian already been alerted about this streak?
                if not self.repo.has_active_consecutive_miss_alert(patient_id):
                    # Fire new alert tracking
                    self.repo.create_guardian_alert(patient_id, "CONSECUTIVE_MISSES")
                    
                    response_envelope["guardian_alert_triggered"] = True
                    response_envelope["notes"] = f"CRITICAL: {current_misses} consecutive misses reached. First-time alert triggered for guardian."
                    # TODO (External Integration Target): In a real app we would fire an SMS job via Twilio async here.
                else:
                    response_envelope["notes"] = f"WARNING: {current_misses} consecutive misses reached. Guardian already has an active, unacknowledged alert. Skipping redundant notification."
            else:
                response_envelope["notes"] = f"Miss logged. {self.CONSECUTIVE_MISS_THRESHOLD - current_misses} more will trigger a guardian alert."
                
        return response_envelope
