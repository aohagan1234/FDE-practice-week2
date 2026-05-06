"""API client stubs for the Coordinator ETA agent.

Three integrations:
  1. CRMClient       — Salesforce REST API (confirmed available, Section 7)
  2. DriverAppClient — Driver app messaging/GPS (LOW confidence, Section 7)
  3. ReplyGateway    — Customer reply channel (STUB Q2 — gateway unconfirmed)

Replace NotImplementedError bodies with real HTTP calls before deploying.
Retry logic lives in BaseAPIClient._request_with_retry.
"""
from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from typing import Optional

from models import (
    ConsignmentRecord,
    ConsignmentStatus,
    DriverLocation,
    EscalationCase,
    InquiryChannel,
)

logger = logging.getLogger(__name__)


# ── Base infrastructure ───────────────────────────────────────────────────────

class APIError(Exception):
    """Raised by any API client on HTTP error or connectivity failure."""

    def __init__(self, system: str, status_code: int, message: str) -> None:
        self.system = system
        self.status_code = status_code
        super().__init__(f"[{system}] HTTP {status_code}: {message}")


class BaseAPIClient(ABC):
    system_name: str

    def _request_with_retry(self, fn, max_retries: int = 3, base_wait: int = 5):
        """Exponential-backoff retry on 5xx errors. 4xx errors are not retried."""
        last_error: Optional[Exception] = None
        for attempt in range(max_retries):
            try:
                return fn()
            except APIError as exc:
                last_error = exc
                if exc.status_code >= 500 and attempt < max_retries - 1:
                    wait = base_wait * (2 ** attempt)
                    logger.warning(
                        "%s: attempt %d failed (HTTP %d), retrying in %ds",
                        self.system_name, attempt + 1, exc.status_code, wait,
                    )
                    time.sleep(wait)
                else:
                    raise
        raise last_error  # type: ignore[misc]


# ── 1. CRM Client (Salesforce REST) ──────────────────────────────────────────

class CRMClient(BaseAPIClient):
    """Salesforce REST API for consignment lookup and escalation case creation.

    API surface: confirmed available (Section 7).
    Freshness: 5-10 min lag from driver app sync (Section 7).

    Production endpoints (replace stubs below):
      GET  /sobjects/Consignment__c/{id}   → ConsignmentRecord
      POST /sobjects/Case/                  → {id: str}  (escalation case)

    Auth: OAuth 2.0 client-credentials (Bearer token from /services/oauth2/token)
    Rate limit: not specified — monitor and apply backoff if 429 received.
    SLA: MEDIUM confidence (CRM_BASE_URL / credentials are STUB — see config.py)
    """
    system_name = "SALESFORCE_CRM"

    def get_consignment(self, consignment_id: str) -> Optional[ConsignmentRecord]:
        """Fetch the consignment record by ID.

        Returns None if the consignment does not exist (CRM 404).
        Raises APIError for connectivity failures or unexpected errors.
        """
        raise NotImplementedError(
            "Replace with: GET {CRM_BASE_URL}/sobjects/Consignment__c/{consignment_id} "
            "Return ConsignmentRecord mapped from JSON response. "
            "Return None on HTTP 404 (not-found is a normal condition, not an error)."
        )

    def create_escalation_case(self, case: EscalationCase) -> str:
        """Write an escalation case to Salesforce and return the CRM case ID.

        Raises APIError on failure — caller must handle and fall back to
        logging-only mode if CRM is unavailable.
        """
        raise NotImplementedError(
            "Replace with: POST {CRM_BASE_URL}/sobjects/Case/ "
            "Body: {Subject, Description, RecordType.Name=CRM_ESCALATION_RECORD_TYPE, "
            "       Queue__c=case.queue.value, Consignment_ID__c=case.consignment_id} "
            "Return response['id'] as the CRM case ID."
        )

    def get_customer_tier(self, customer_id: str) -> Optional[str]:
        """
        Return the customer's tier/VIP flag from the CRM Account record.

        STUB Q3: Field name and valid values are unconfirmed.
        Replace VIP_CRM_FIELD_NAME and VIP_TIER_VALUE in config.py once confirmed.
        Returns None if the customer record is not found.
        """
        raise NotImplementedError(
            "STUB Q3: Confirm VIP_CRM_FIELD_NAME with Apex Distribution. "
            "Replace with: GET {CRM_BASE_URL}/sobjects/Account/{customer_id} "
            "Return record[VIP_CRM_FIELD_NAME]."
        )


# ── 2. Driver App Client ──────────────────────────────────────────────────────

class DriverAppClient(BaseAPIClient):
    """Async messaging (and optionally GPS) interface to the driver app.

    STUB Q1: API surface is LOW confidence. Three possible capabilities:
      DriverAppCapability.GPS  — GPS endpoint available; implement get_driver_location()
      DriverAppCapability.MSG  — messaging only; implement send_message() + poll_reply()
      DriverAppCapability.NONE — no API; this client is never called

    Set DRIVER_APP_CAPABILITY in config.py once confirmed with Apex IT.

    Before implementing, also confirm:
      - Authentication mechanism (API key? OAuth? Device token?)
      - Whether send_message() is fire-and-forget or returns a message ID for polling
      - Reply message format: structured JSON or free-text from driver
    """
    system_name = "DRIVER_APP"

    def send_eta_request(self, driver_id: str, consignment_id: str) -> Optional[str]:
        """Send an ETA request message to the driver.

        STUB Q1: Implement for MSG and GPS modes.
        Returns a message/request ID that can be polled, or None if fire-and-forget.
        """
        raise NotImplementedError(
            "STUB Q1: Confirm driver app API surface (GPS / MSG / NONE). "
            "MSG mode: POST /messages → {driver_id, text} → {message_id} "
            "GPS mode: this method may not be needed — call get_driver_location() directly."
        )

    def poll_reply(self, driver_id: str, request_id: Optional[str]) -> Optional[DriverLocation]:
        """Poll for the driver's ETA reply.

        STUB Q1: Called every ~10s for up to DRIVER_RESPONSE_TIMEOUT_SECONDS.
        MSG mode: parse free-text reply from driver to extract ETA.
        GPS mode: call get_driver_location() instead.

        STUB Q1 (MSG sub-case): The driver reply format is unconfirmed.
        Options:
          Structured JSON: {"eta_minutes": 45, "stops_remaining": 3}
          Free text:       "About 45 mins, got 3 more stops"  (requires NLP parsing)
        If free-text, an LLM extraction step is needed — flag this for build review.
        """
        raise NotImplementedError(
            "STUB Q1: Confirm reply format from driver app. "
            "If structured JSON: parse directly into DriverLocation. "
            "If free text: use an LLM extraction call (add to orchestrator.py)."
        )

    def get_driver_location(self, driver_id: str) -> Optional[DriverLocation]:
        """Fetch current GPS location and stops remaining.

        STUB Q1: Only available if DRIVER_APP_CAPABILITY == GPS.
        GPS endpoint schema and auth are unconfirmed.
        Returns None if driver has no active location fix.
        """
        raise NotImplementedError(
            "STUB Q1: Only implement if GPS capability confirmed. "
            "GET /drivers/{driver_id}/location "
            "Return DriverLocation(lat, lng, stops_remaining, ...)."
        )


# ── 3. Reply Gateway (customer-facing channel) ───────────────────────────────

class ReplyGatewayClient(BaseAPIClient):
    """Send reply messages to customers via their original inquiry channel.

    STUB Q2: Gateway implementation is unconfirmed. Options:
      (a) Single Twilio gateway for all channels (SMS + email via Twilio SendGrid)
      (b) Per-channel routing: Twilio for SMS, SendGrid/SES for email, push for app
      (c) Internal message bus

    Before implementing send_reply(), confirm:
      - Gateway vendor and API endpoint
      - Authentication (API key / OAuth)
      - Whether the same send() method works for all InquiryChannel variants
      - Rate limits and delivery receipt mechanism (needed for audit log)
    """
    system_name = "REPLY_GATEWAY"

    def send_reply(
        self,
        customer_id: str,
        channel: InquiryChannel,
        message: str,
        idempotency_key: str,
    ) -> bool:
        """Send the ETA reply to the customer on their original channel.

        STUB Q2: Implementation depends on gateway selection.
        Returns True on successful send, False on soft failure.
        Raises APIError on hard failure (caller will log and fall back to audit-only).

        idempotency_key format: "reply:{inquiry_id}" — prevents double-sends
        on retry after a partial failure.
        """
        raise NotImplementedError(
            "STUB Q2: Confirm reply gateway with Apex Distribution IT. "
            "Implement channel-specific send logic: "
            "  SMS   → Twilio Messages API (or equivalent) "
            "  EMAIL → SendGrid / SES / MS Graph "
            "  APP   → push notification endpoint "
            "  PHONE → log only; human callback not automated"
        )
