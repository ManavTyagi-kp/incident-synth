from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class Severity(str, Enum):
    SEV1 = "SEV1"
    SEV2 = "SEV2"
    SEV3 = "SEV3"
    SEV4 = "SEV4"

class TimelineEvent(BaseModel):
    timestamp: str
    actor: str
    event: str

class ActionItem(BaseModel):
    title: str
    owner: Optional[str] = None
    priority: str = Field(..., pattern="^(P0|P1|P2|P3)$")
    category: str

class Postmortem(BaseModel):
    incident_title: str
    severity: Severity
    summary: str
    root_cause: str
    contributing_factors: List[str] = []
    timeline: List[TimelineEvent]
    action_items: List[ActionItem]
    services_affected: List[str] = []
    detection_method: Optional[str] = None
    resolution_time_minutes: Optional[int] = None