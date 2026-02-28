from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class AdherenceStatusStr(str, enum.Enum):
    TAKEN = "TAKEN"
    MISSED = "MISSED"

class AdherenceLog(Base):
    __tablename__ = "adherence_logs"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, index=True, nullable=False)
    medication_name = Column(String, index=True, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    
    # Store standard UTC timestamps
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    status = Column(SQLEnum(AdherenceStatusStr), nullable=False)


class GuardianAlert(Base):
    __tablename__ = "guardian_alerts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, index=True, nullable=False)
    
    # E.g., "CONSECUTIVE_MISSES"
    alert_type = Column(String, nullable=False)
    
    # Used to track if the guardian has acknowledged the alert yet
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
