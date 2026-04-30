from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Optional


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"


TERMINAL_STATUSES = {TaskStatus.COMPLETE, TaskStatus.SKIPPED}


class HireStatus(str, Enum):
    ONBOARDING = "ONBOARDING"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"


class EscalationType(str, Enum):
    I9_AT_RISK = "I9_AT_RISK"
    I9_VIOLATION = "I9_VIOLATION"
    TASK_OVERDUE_72H = "TASK_OVERDUE_72H"
    TASK_BLOCKED_UNRESOLVED = "TASK_BLOCKED_UNRESOLVED"
    ROLE_NOT_MAPPED = "ROLE_NOT_MAPPED"
    SYSTEM_UNAVAILABLE = "SYSTEM_UNAVAILABLE"
    NO_ELIGIBLE_BUDDY = "NO_ELIGIBLE_BUDDY"
    SENIORITY_GAP = "SENIORITY_GAP"
    COMPLIANCE_TRACK_UNCLEAR = "COMPLIANCE_TRACK_UNCLEAR"
    DEADLINE_CALC_ERROR = "DEADLINE_CALC_ERROR"
    DATA_INTEGRITY_ERROR = "DATA_INTEGRITY_ERROR"


class EscalationSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EscalationStatus(str, Enum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"


class OwnerType(str, Enum):
    SYSTEM = "SYSTEM"
    HR_OPS = "HR_OPS"
    MANAGER = "MANAGER"
    IT = "IT"
    COMPLIANCE = "COMPLIANCE"


class DeliveryStatus(str, Enum):
    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    BOUNCED = "BOUNCED"
    SPAM_TRAPPED = "SPAM_TRAPPED"
    FAILED = "FAILED"


@dataclass
class Hire:
    hire_id: str
    first_name: str
    last_name: str
    role: str
    department: str
    start_date: date
    hire_type: str  # "EMPLOYEE" or "CONTRACTOR"
    manager_id: str
    manager_email: str
    status: HireStatus
    office_location: str
    seniority_level: int
    created_at: datetime

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass
class TaskType:
    task_type: str
    category: str  # PRE_DAY_1, POST_DAY_1, ONGOING
    offset_days: Optional[int]
    owner_type: OwnerType
    source_system: str
    applies_to_hire_types: list[str] = field(default_factory=lambda: ["EMPLOYEE", "CONTRACTOR"])


@dataclass
class Task:
    task_id: str
    hire_id: str
    task_type: str
    category: str
    status: TaskStatus
    deadline: datetime
    owner_type: OwnerType
    owner_id: Optional[str]
    source_system: str
    data_freshness: datetime
    blocked_reason: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime] = None
    last_reminder_sent_at: Optional[datetime] = None
    overdue_hours: float = 0.0

    @property
    def is_terminal(self) -> bool:
        return self.status in TERMINAL_STATUSES


@dataclass
class Escalation:
    escalation_id: str
    hire_id: str
    escalation_type: EscalationType
    severity: EscalationSeverity
    route_to: list[str]
    route_to_emails: list[str]
    message: str
    created_at: datetime
    status: EscalationStatus = EscalationStatus.OPEN
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


@dataclass
class Reminder:
    reminder_id: str
    hire_id: str
    task_id: str
    recipient_email: str
    recipient_type: str
    subject: str
    body: str
    delivery_status: DeliveryStatus
    sent_at: Optional[datetime] = None
    delivery_error: Optional[str] = None


@dataclass
class ITProvisioningRequest:
    request_id: str
    hire_id: str
    role: str
    access_package_id: str
    access_package_name: str
    requested_by: str
    requested_at: datetime
    external_request_id: Optional[str] = None
    status: str = "PENDING_APPROVAL"


@dataclass
class AuditEntry:
    action_type: str
    timestamp: datetime
    status: str
    hire_id: Optional[str] = None
    task_id: Optional[str] = None
    input_data: dict = field(default_factory=dict)
    output_data: dict = field(default_factory=dict)
    error: Optional[str] = None
