from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Optional


class Channel(str, Enum):
    SMS = "SMS"
    EMAIL = "email"
    PHONE = "phone"


class EscalationType(str, Enum):
    POOL_EXHAUSTED = "pool_exhausted"
    INTAKE_PARSING_AMBIGUITY = "intake_parsing_ambiguity"
    DATA_SOURCE_UNAVAILABLE = "data_source_unavailable"


@dataclass
class NoShowRecord:
    facility_type: str
    date: date


@dataclass
class ContactDetail:
    channel: Channel
    address: str
    preferred: bool


@dataclass
class Candidate:
    nurse_id: str
    credentials: list[str]
    proximity_miles: float
    in_active_outreach: bool
    contact_details: list[ContactDetail] = field(default_factory=list)
    response_rate: Optional[float] = None  # 0.0–1.0; None = no historical data
    no_show_history: list[NoShowRecord] = field(default_factory=list)


@dataclass
class PlacementRecord:
    facility_type: str
    nurse_id: str


@dataclass
class RankedCandidate:
    nurse_id: str
    rank: int
    rationale: str
    in_active_outreach: bool  # always False at ranking time; parallel outreach sets to True on send


@dataclass
class RankingResult:
    job_order_id: str
    ranked_candidates: list[RankedCandidate]
    ranking_timestamp: datetime
    escalation_type: Optional[EscalationType] = None
