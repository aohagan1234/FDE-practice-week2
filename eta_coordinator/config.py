"""Configuration constants for the Coordinator ETA agent.

All values are sourced directly from the Agent Purpose Document (DELIVERABLE-4).
Constants that depend on unconfirmed assumptions are marked with STUB comments.
"""
from __future__ import annotations

from models import DriverAppCapability, EscalationQueue

# ── Timing thresholds (Section 2 / Section 3) ────────────────────────────────

# How long to wait for a driver response before using the fallback window
DRIVER_RESPONSE_TIMEOUT_SECONDS = 120  # 2 min (Section 2.2 / Section 3.2)

# Total allowed time from inquiry receipt to reply sent (P50 target = 5 min)
REPLY_SLA_SECONDS = 300

# Deduplication window: same customer + consignment within this window → cache hit
CACHE_TTL_SECONDS = 3600  # 1 hour (Section 2.1 / Section 3.1)

# How many rapid repeat inquiries trigger the "multiple rapid inquiries" note
RAPID_INQUIRY_THRESHOLD = 3

# ── ETA calculation constants ─────────────────────────────────────────────────
# STUB Q4: These values must be confirmed with Apex Distribution operations team.
# avg_stop_duration_minutes: average time the driver spends per delivery stop.
# routing_api: which routing service is used for travel-time calculation.
# stops_remaining_unit: "consignment" or "route_waypoint" — affects count source.

AVG_STOP_DURATION_MINUTES = 10    # STUB Q4: Confirm with Apex Ops
ROUTING_API_PROVIDER = "STUB"     # STUB Q4: "google_maps" | "here" | "internal"
STOPS_REMAINING_UNIT = "STUB"     # STUB Q4: "consignment" | "route_waypoint"

# ── Driver app capability flag ────────────────────────────────────────────────
# STUB Q1: Set this to GPS, MSG, or NONE once driver app API surface is confirmed.
# Controls which branch of _contact_driver() is executed.
DRIVER_APP_CAPABILITY = DriverAppCapability.NONE  # STUB Q1: update after confirmation

# ── Fallback ETA window (Section 2.2 / Section 3.1) ─────────────────────────
# Used when driver does not respond within DRIVER_RESPONSE_TIMEOUT_SECONDS.
FALLBACK_WINDOW_START = "13:00"
FALLBACK_WINDOW_END = "17:00"
FALLBACK_WINDOW_LABEL = "afternoon 13:00–17:00"

# ── VIP / tier configuration ──────────────────────────────────────────────────
# Phase 2 only. VIP-tier dispatcher escalation is deferred until CRM field is confirmed
# (D6 Q3). Phase 1 dispatcher escalation triggers only on explicit_tight_eta_requested.
VIP_CRM_FIELD_NAME = "STUB"   # Phase 2: confirm field name (e.g. "Customer_Tier__c")
VIP_TIER_VALUE = "STUB"       # Phase 2: confirm value (e.g. "VIP" | "Gold" | "Premium")

# ── Intent detection keywords (Section 2.1) ───────────────────────────────────
# Keyword list for detecting explicit tight-ETA requests from customer messages.
# If any keyword appears in the lowercased message → explicit_tight_eta_requested = True.
TIGHT_ETA_KEYWORDS: frozenset[str] = frozenset({
    "urgent",
    "exact time",
    "precise",
    "exactly when",
    "need to know",
    "need an exact",
    "by ",           # catches "by 2pm", "by noon", etc.
})

# ── Escalation queue routing (Section 3.1) ───────────────────────────────────
ESCALATION_ROUTING: dict[str, dict] = {
    "not_found": {
        "queue": EscalationQueue.MANUAL_LOOKUP,
        "reason_template": "Consignment {consignment_id} not found in CRM. Manual shipper lookup required.",
    },
    "null_status": {
        "queue": EscalationQueue.DATA_ERROR,
        "reason_template": "CRM status missing for consignment {consignment_id}. CRM sync issue suspected.",
    },
    "exception": {
        "queue": EscalationQueue.DISPATCHER,
        "reason_template": "Consignment {consignment_id} flagged as exception: {exception_reason}.",
    },
    "driver_non_responsive_vip": {
        "queue": EscalationQueue.DISPATCHER,
        "reason_template": "Driver non-responsive for consignment {consignment_id}. Customer is VIP or requested tight ETA.",
    },
    "crm_api_down": {
        "queue": EscalationQueue.MANUAL_AGENT,
        "reason_template": "Salesforce REST API unavailable. Inquiry {inquiry_id} requires manual handling.",
    },
    "invalid_id": {
        "queue": EscalationQueue.MANUAL_LOOKUP,
        "reason_template": "Consignment ID '{raw_id}' failed format validation. Manual check required.",
    },
}

# ── Reply channel gateway ─────────────────────────────────────────────────────
# STUB Q2: Replace with actual gateway configuration once channel routing is confirmed.
# Options: single Twilio gateway, per-channel routing table, internal message bus.
REPLY_GATEWAY = "STUB"  # STUB Q2: "twilio" | "per_channel" | "internal_bus"

# ── Salesforce CRM configuration ─────────────────────────────────────────────
# STUB (credentials only — API surface is confirmed per Section 7)
CRM_BASE_URL = "STUB"           # e.g. "https://apex.my.salesforce.com/services/data/v58.0"
CRM_CLIENT_ID = "STUB"          # OAuth 2.0 client-credentials
CRM_CLIENT_SECRET = "STUB"
CRM_ESCALATION_RECORD_TYPE = "ETA_Escalation"

# ── Consignment ID validation ─────────────────────────────────────────────────
# Pattern: two letters, dash, three digits, dash, four digits (e.g. AX-771-3344)
# Derived from the example in Section 3.2 of the spec.
CONSIGNMENT_ID_PATTERN = r"^[A-Z]{2}-\d{3}-\d{4}$"
