"""Data models for the Coordinator ETA agent.

All types are derived directly from DELIVERABLE-4 (Agent Purpose Document).
No fields have been added beyond what the spec requires.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# ── Enumerations ─────────────────────────────────────────────────────────────

class ConsignmentStatus(str, Enum):
    """Canonical CRM status values (Section 7, status enum)."""
    PRE_DISPATCH = "pre-dispatch"
    OUT_FOR_DELIVERY = "out-for-delivery"
    DELIVERED = "delivered"
    EXCEPTION = "exception"
    NULL = "null"


class InquiryChannel(str, Enum):
    """Customer-facing channels through which inquiries arrive."""
    SMS = "sms"
    APP = "app"
    EMAIL = "email"
    PHONE = "phone"


class ResolutionType(str, Enum):
    """How the inquiry was closed — used in the audit log."""
    DELIVERED_TEMPLATE = "delivered_template"
    PRE_DISPATCH_TEMPLATE = "pre_dispatch_template"
    EXCEPTION_ESCALATION = "exception_escalation"
    CACHE_HIT = "cache_hit"
    ETA_DRIVER_RESPONSE = "eta_driver_response"
    ETA_FALLBACK = "eta_fallback"
    ESCALATED_NOT_FOUND = "escalated_not_found"
    ESCALATED_NULL_STATUS = "escalated_null_status"
    ESCALATED_INVALID_ID = "escalated_invalid_id"
    ESCALATED_CRM_DOWN = "escalated_crm_down"


class DriverAppCapability(str, Enum):
    """
    Driver app API surface — LOW confidence per Section 7.

    STUB Q1: Clarify which capability is available before implementing
    _calculate_eta_from_gps() and _parse_driver_message().
    Options:
      GPS   — app exposes /driver/{id}/location returning lat/lng + stops_remaining
      MSG   — app supports async message send/receive only; ETA parsed from free text
      NONE  — no driver app API; CRM-only fallback always used
    """
    GPS = "gps"
    MSG = "msg"
    NONE = "none"


class EscalationQueue(str, Enum):
    """Queues to which escalation cases are routed in CRM."""
    MANUAL_LOOKUP = "manual_lookup"
    DISPATCHER = "dispatcher"
    MANUAL_AGENT = "manual_agent"   # CRM API failover queue
    DATA_ERROR = "data_error"


# ── Core data types ───────────────────────────────────────────────────────────

@dataclass
class ConsignmentRecord:
    """CRM consignment record returned by Salesforce REST API."""
    consignment_id: str
    customer_id: str
    status: ConsignmentStatus
    route_id: Optional[str]
    driver_id: Optional[str]
    delivery_address: str
    scheduled_window_start: Optional[datetime]
    scheduled_window_end: Optional[datetime]
    # Set when status == delivered
    delivered_at: Optional[datetime] = None
    signature_name: Optional[str] = None
    # Set when status == exception
    exception_reason: Optional[str] = None
    # Timestamp of last CRM sync from driver app (5-10 min lag per spec)
    last_synced_at: Optional[datetime] = None


@dataclass
class InquiryRequest:
    """Inbound ETA inquiry from a customer."""
    inquiry_id: str
    customer_id: str
    raw_consignment_id: str           # As received — may be malformed
    channel: InquiryChannel
    received_at: datetime
    # Optional: set if customer explicitly requested tight ETA (Q3 stub)
    explicit_tight_eta_requested: bool = False


@dataclass
class DriverLocation:
    """
    Driver location/ETA response.

    STUB Q1: Schema depends on driver app capability:
      GPS mode  — lat, lng, stops_remaining are populated; raw_message is None
      MSG mode  — raw_message is populated; lat/lng/stops_remaining are None
      NONE mode — this object is never constructed; fallback used directly
    """
    driver_id: str
    responded_at: datetime
    # GPS branch
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    stops_remaining: Optional[int] = None
    # MSG branch
    raw_message: Optional[str] = None


@dataclass
class ETAReply:
    """The reply sent to the customer."""
    inquiry_id: str
    consignment_id: str
    customer_id: str
    channel: InquiryChannel
    message: str
    resolution_type: ResolutionType
    is_escalated: bool
    sent_at: datetime


@dataclass
class EscalationCase:
    """CRM escalation case written to the dispatcher/manual queue."""
    case_id: str
    consignment_id: str
    customer_id: str
    queue: EscalationQueue
    reason: str
    created_at: datetime
    # Populated after CRM write succeeds
    crm_case_id: Optional[str] = None


@dataclass
class CacheEntry:
    """Inquiry deduplication cache entry (in-memory; replace with Redis in prod)."""
    customer_id: str
    consignment_id: str
    reply_message: str
    resolution_type: ResolutionType
    cached_at: datetime


@dataclass
class AuditEntry:
    """One audit record per inquiry — written for every resolution path."""
    inquiry_id: str
    consignment_id: str
    customer_id: str
    channel: str
    resolution_type: str
    is_escalated: bool
    driver_responded: Optional[bool]   # None if driver not contacted
    crm_status_at_query: Optional[str]
    duration_seconds: float
    timestamp: datetime
    error: Optional[str] = None
