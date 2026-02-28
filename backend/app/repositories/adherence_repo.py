from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime, timezone

from app.domain.models.adherence import AdherenceLog, GuardianAlert, AdherenceStatusStr

class AdherenceRepository:
    """
    Abstractions for SQLite Adherence queries, separating SQL from pure Service logic.
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    def log_adherence(self, patient_id: str, medication_name: str, scheduled_time: datetime, status: AdherenceStatusStr) -> AdherenceLog:
        """Saves a new medication adherence event log."""
        log = AdherenceLog(
            patient_id=patient_id,
            medication_name=medication_name,
            scheduled_time=scheduled_time,
            status=status
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
        
    def get_recent_misses_count(self, patient_id: str) -> int:
        """
        Dynamically calculates how many *consecutive* misses have occurred globally
        for this patient across all their medications recently.
        
        It looks back chronologically from the present. The counter stops as soon as it
        encounters a 'TAKEN' status.
        """
        # Fetch a reasonable window to avoid loading massive history (e.g. last 10 logs)
        recent_logs = self.db.query(AdherenceLog)\
            .filter(AdherenceLog.patient_id == patient_id)\
            .order_by(desc(AdherenceLog.timestamp))\
            .limit(10)\
            .all()
            
        consecutive_misses = 0
        for log in recent_logs:
            if log.status == AdherenceStatusStr.MISSED:
                consecutive_misses += 1
            elif log.status == AdherenceStatusStr.TAKEN:
                # Sequence broken
                break
                
        return consecutive_misses
        
    def has_active_consecutive_miss_alert(self, patient_id: str) -> bool:
        """
        Checks if there is already an unacknowledged alert for consecutive misses
        to prevent spamming the guardian.
        """
        alert = self.db.query(GuardianAlert)\
            .filter(
                GuardianAlert.patient_id == patient_id,
                GuardianAlert.alert_type == "CONSECUTIVE_MISSES",
                GuardianAlert.is_active == True
            )\
            .first()
            
        return alert is not None
        
    def create_guardian_alert(self, patient_id: str, alert_type: str = "CONSECUTIVE_MISSES") -> GuardianAlert:
        """Fires off a tracking row to represent an SMS/Push notification sent to the Guardian."""
        alert = GuardianAlert(
            patient_id=patient_id,
            alert_type=alert_type,
            is_active=True
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert
