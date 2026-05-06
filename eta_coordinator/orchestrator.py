"""Coordinator ETA Orchestrator — implements the full decision tree from Section 4.

Decision tree (reproduced from the spec):

    START: Customer inquiry received (SMS/call/app)
      ├─→ Parse consignment ID
      │    ├─→ Invalid format? → Escalate
      │    └─→ Valid → Continue
      ├─→ Query CRM
      │    ├─→ Not found? → Escalate to manual lookup
      │    └─→ Found → Continue
      ├─→ Check status
      │    ├─→ delivered    → Return delivery time + signature; CLOSE
      │    ├─→ pre-dispatch → Return next-day window; CLOSE
      │    ├─→ exception    → Return reason + escalate to dispatcher; CLOSE
      │    ├─→ null         → Escalate (data error); CLOSE
      │    └─→ out-for-delivery → Continue
      ├─→ Check inquiry cache (<1h ago?)
      │    ├─→ Cache hit → Reply from cache; CLOSE
      │    └─→ No cache → Continue
      ├─→ Query driver (async message)
      │    ├─→ Driver responds <2 min → Calculate ETA; Reply tight window; CLOSE
      │    └─→ No response → Reply fallback window; Optional dispatcher escalation; CLOSE
    END

Workflow-handled paths (deterministic, no LLM): all status branches.
LLM agent layer: not used in Phase 1 — all paths in 2a + 2b are rule-based.
"""
from __future__ import annotations

import logging
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from api_clients import APIError, CRMClient, DriverAppClient, ReplyGatewayClient
from audit import ETAAuditLogger
from cache import InquiryCache
from config import (
    CONSIGNMENT_ID_PATTERN,
    DRIVER_APP_CAPABILITY,
    DRIVER_RESPONSE_TIMEOUT_SECONDS,
    ESCALATION_ROUTING,
    TIGHT_ETA_KEYWORDS,
    VIP_CRM_FIELD_NAME,
    VIP_TIER_VALUE,
)
from eta_calculator import calculate_eta
from models import (
    ConsignmentRecord,
    ConsignmentStatus,
    DriverAppCapability,
    EscalationCase,
    EscalationQueue,
    ETAReply,
    InquiryRequest,
    ResolutionType,
)
from templates import (
    render_crm_unavailable,
    render_delivered,
    render_eta_driver_response,
    render_eta_fallback,
    render_exception,
    render_invalid_id,
    render_not_found,
    render_null_status,
    render_pre_dispatch,
)

logger = logging.getLogger(__name__)


class ETACoordinator:
    """Main orchestrator class.

    Instantiated once at startup and called once per incoming inquiry.
    Thread-safety: the inquiry cache uses an in-memory dict — replace with
    Redis before running multiple concurrent instances.
    """

    def __init__(
        self,
        crm: CRMClient,
        driver_app: DriverAppClient,
        reply_gateway: ReplyGatewayClient,
        audit: ETAAuditLogger,
        cache: Optional[InquiryCache] = None,
    ) -> None:
        self._crm = crm
        self._driver_app = driver_app
        self._reply_gateway = reply_gateway
        self._audit = audit
        self._cache = cache or InquiryCache()

    # ── Main entry point ──────────────────────────────────────────────────────

    def handle_inquiry(
        self,
        inquiry: InquiryRequest,
        now: Optional[datetime] = None,
    ) -> ETAReply:
        """Process one ETA inquiry end-to-end. Returns the reply sent to the customer.

        This is the only public method on the class. All internal steps are private.
        Every exit path writes an audit record before returning.
        """
        now = now or datetime.now(timezone.utc)
        started_at = time.monotonic()

        # Step 1: Validate consignment ID format
        if not self._is_valid_consignment_id(inquiry.raw_consignment_id):
            return self._close(
                inquiry=inquiry,
                consignment_id=inquiry.raw_consignment_id,
                message=render_invalid_id(inquiry.raw_consignment_id),
                resolution=ResolutionType.ESCALATED_INVALID_ID,
                is_escalated=True,
                started_at=started_at,
                now=now,
                escalation_key="invalid_id",
                escalation_kwargs={"raw_id": inquiry.raw_consignment_id},
            )

        consignment_id = inquiry.raw_consignment_id.upper().strip()

        # Step 2: Query CRM
        try:
            record = self._crm.get_consignment(consignment_id)
        except APIError as exc:
            logger.error("CRM unavailable for inquiry %s: %s", inquiry.inquiry_id, exc)
            return self._close(
                inquiry=inquiry,
                consignment_id=consignment_id,
                message=render_crm_unavailable(consignment_id),
                resolution=ResolutionType.ESCALATED_CRM_DOWN,
                is_escalated=True,
                started_at=started_at,
                now=now,
                escalation_key="crm_api_down",
                escalation_kwargs={"inquiry_id": inquiry.inquiry_id},
            )

        if record is None:
            return self._close(
                inquiry=inquiry,
                consignment_id=consignment_id,
                message=render_not_found(consignment_id),
                resolution=ResolutionType.ESCALATED_NOT_FOUND,
                is_escalated=True,
                started_at=started_at,
                now=now,
                escalation_key="not_found",
                escalation_kwargs={"consignment_id": consignment_id},
            )

        # Step 3: Branch on CRM status
        if record.status == ConsignmentStatus.DELIVERED:
            return self._close(
                inquiry=inquiry,
                consignment_id=consignment_id,
                message=render_delivered(record),
                resolution=ResolutionType.DELIVERED_TEMPLATE,
                is_escalated=False,
                started_at=started_at,
                now=now,
                crm_status=record.status.value,
            )

        if record.status == ConsignmentStatus.PRE_DISPATCH:
            return self._close(
                inquiry=inquiry,
                consignment_id=consignment_id,
                message=render_pre_dispatch(record),
                resolution=ResolutionType.PRE_DISPATCH_TEMPLATE,
                is_escalated=False,
                started_at=started_at,
                now=now,
                crm_status=record.status.value,
            )

        if record.status == ConsignmentStatus.EXCEPTION:
            return self._close(
                inquiry=inquiry,
                consignment_id=consignment_id,
                message=render_exception(record),
                resolution=ResolutionType.EXCEPTION_ESCALATION,
                is_escalated=True,
                started_at=started_at,
                now=now,
                crm_status=record.status.value,
                escalation_key="exception",
                escalation_kwargs={
                    "consignment_id": consignment_id,
                    "exception_reason": record.exception_reason or "unknown reason",
                },
            )

        if record.status == ConsignmentStatus.NULL:
            return self._close(
                inquiry=inquiry,
                consignment_id=consignment_id,
                message=render_null_status(consignment_id),
                resolution=ResolutionType.ESCALATED_NULL_STATUS,
                is_escalated=True,
                started_at=started_at,
                now=now,
                crm_status=record.status.value,
                escalation_key="null_status",
                escalation_kwargs={"consignment_id": consignment_id},
            )

        # Step 4: out-for-delivery — check cache before contacting driver
        assert record.status == ConsignmentStatus.OUT_FOR_DELIVERY

        cached = self._cache.get(inquiry.customer_id, consignment_id, now=now)
        if cached is not None:
            return self._close(
                inquiry=inquiry,
                consignment_id=consignment_id,
                message=cached.reply_message,
                resolution=ResolutionType.CACHE_HIT,
                is_escalated=False,
                started_at=started_at,
                now=now,
                crm_status=record.status.value,
            )

        # Step 5: Contact driver (async)
        return self._handle_out_for_delivery(
            inquiry=inquiry,
            record=record,
            consignment_id=consignment_id,
            started_at=started_at,
            now=now,
        )

    # ── Out-for-delivery flow (Section 2.2 / Section 3.2) ────────────────────

    def _handle_out_for_delivery(
        self,
        inquiry: InquiryRequest,
        record: ConsignmentRecord,
        consignment_id: str,
        started_at: float,
        now: datetime,
    ) -> ETAReply:
        """Contact driver and reply with tight ETA or fallback.

        If DRIVER_APP_CAPABILITY is NONE — skip driver contact entirely and
        use fallback window. This is the safe default until Q1 is resolved.
        """
        driver_responded = False
        driver_location = None

        if DRIVER_APP_CAPABILITY != DriverAppCapability.NONE and record.driver_id:
            driver_location = self._contact_driver(
                driver_id=record.driver_id,
                consignment_id=consignment_id,
            )
            driver_responded = driver_location is not None
        else:
            logger.debug(
                "Driver contact skipped: capability=%s driver_id=%s",
                DRIVER_APP_CAPABILITY.value,
                record.driver_id,
            )

        if driver_responded and driver_location is not None:
            if driver_location.latitude is not None:
                # GPS mode: attempt tight ETA calculation
                eta_dt = calculate_eta(driver_location, record, now=now)
                if eta_dt is not None:
                    message = render_eta_driver_response(record, eta_dt)
                    resolution = ResolutionType.ETA_DRIVER_RESPONSE
                else:
                    # GPS present but routing API failed — fall back
                    message = render_eta_fallback(record)
                    resolution = ResolutionType.ETA_FALLBACK
                    driver_responded = False
            else:
                # MSG mode: driver confirmed delivery is proceeding; no GPS to calculate
                # from. Use fallback window per Section 2.2 MSG mode rule.
                message = render_eta_fallback(record, driver_confirmed=True)
                resolution = ResolutionType.ETA_FALLBACK
        else:
            message = render_eta_fallback(record)
            resolution = ResolutionType.ETA_FALLBACK

        # Cache the reply to suppress duplicates within the next hour
        self._cache.set(
            customer_id=inquiry.customer_id,
            consignment_id=consignment_id,
            reply_message=message,
            resolution_type=resolution,
            now=now,
        )

        # Optional dispatcher escalation for VIP / explicit tight-ETA request
        # when driver was non-responsive (Section 3.2: 10% path)
        should_escalate_to_dispatcher = (
            not driver_responded
            and self._should_escalate_to_dispatcher(inquiry)
        )

        return self._close(
            inquiry=inquiry,
            consignment_id=consignment_id,
            message=message,
            resolution=resolution,
            is_escalated=should_escalate_to_dispatcher,
            started_at=started_at,
            now=now,
            crm_status=record.status.value,
            driver_responded=driver_responded,
            escalation_key="driver_non_responsive_vip" if should_escalate_to_dispatcher else None,
            escalation_kwargs={"consignment_id": consignment_id} if should_escalate_to_dispatcher else None,
        )

    def _contact_driver(
        self, driver_id: str, consignment_id: str
    ) -> None:
        """Send ETA request to driver and wait up to DRIVER_RESPONSE_TIMEOUT_SECONDS.

        Returns DriverLocation if driver responds in time, None otherwise.

        STUB Q1: Set DRIVER_APP_CAPABILITY in config once confirmed:
          GPS  — app exposes GPS endpoint; DriverLocation.latitude/longitude populated.
                 calculate_eta() produces tight window.
          MSG  — app supports async messaging only; DriverLocation.raw_message populated.
                 Caller treats any response as "delivery proceeding normally" and uses
                 fallback window (Section 2.2 MSG mode rule — no free-text ETA parsing
                 in Phase 1; deferred to Phase 2).
          NONE — no driver app API; falls through to fallback window immediately.
        """
        # STUB Q1: uncomment and adapt the appropriate branch once capability confirmed.
        #
        # if DRIVER_APP_CAPABILITY == DriverAppCapability.GPS:
        #     try:
        #         return self._driver_app.get_driver_location(driver_id)
        #     except APIError:
        #         return None
        #
        # elif DRIVER_APP_CAPABILITY == DriverAppCapability.MSG:
        #     try:
        #         request_id = self._driver_app.send_eta_request(driver_id, consignment_id)
        #     except APIError:
        #         return None
        #     deadline = time.monotonic() + DRIVER_RESPONSE_TIMEOUT_SECONDS
        #     poll_interval = 10
        #     while time.monotonic() < deadline:
        #         try:
        #             reply = self._driver_app.poll_reply(driver_id, request_id)
        #             if reply is not None:
        #                 return reply  # raw_message populated; caller uses fallback window
        #         except APIError:
        #             pass
        #         time.sleep(poll_interval)
        #     return None  # timed out

        logger.debug(
            "_contact_driver: DRIVER_APP_CAPABILITY=NONE (STUB Q1). "
            "Returning None — caller will use fallback window."
        )
        return None

    # ── VIP / explicit-request check (Section 3.2, 10% escalation path) ───────

    def _should_escalate_to_dispatcher(self, inquiry: InquiryRequest) -> bool:
        """Return True if this non-responsive-driver case warrants dispatcher escalation.

        Phase 1: escalate only when customer explicitly requested a tight ETA
        (detected via keyword match — see detect_explicit_tight_eta_request()).

        Phase 2: add VIP-tier check once CRM field name is confirmed (D6 Q3).
        Stub kept below for reference but intentionally inactive.
        """
        if inquiry.explicit_tight_eta_requested:
            return True

        # Phase 2 placeholder: VIP tier check via CRM.
        # Activate once VIP_CRM_FIELD_NAME / VIP_TIER_VALUE are confirmed.
        # try:
        #     tier = self._crm.get_customer_tier(inquiry.customer_id)
        #     return tier == VIP_TIER_VALUE
        # except APIError:
        #     return False
        return False

    @staticmethod
    def detect_explicit_tight_eta_request(raw_message: str) -> bool:
        """Keyword-based intent detection for explicit tight-ETA requests.

        Returns True if the customer's message contains any keyword from
        TIGHT_ETA_KEYWORDS (Section 2.1). No LLM inference — deterministic.
        Call this before constructing InquiryRequest to set the flag.
        """
        lowered = raw_message.lower()
        return any(kw in lowered for kw in TIGHT_ETA_KEYWORDS)

    # ── Escalation case creation ──────────────────────────────────────────────

    def _create_escalation(
        self,
        inquiry: InquiryRequest,
        consignment_id: str,
        escalation_key: str,
        kwargs: dict,
    ) -> Optional[EscalationCase]:
        """Write an escalation case to CRM. Returns the case, or None if CRM write fails."""
        routing = ESCALATION_ROUTING[escalation_key]
        reason = routing["reason_template"].format(**kwargs)
        case = EscalationCase(
            case_id=f"ESC-{uuid.uuid4().hex[:8]}",
            consignment_id=consignment_id,
            customer_id=inquiry.customer_id,
            queue=routing["queue"],
            reason=reason,
            created_at=datetime.now(timezone.utc),
        )
        try:
            crm_id = self._crm.create_escalation_case(case)
            case.crm_case_id = crm_id
            logger.info(
                "Escalation created: case_id=%s crm_id=%s queue=%s",
                case.case_id, crm_id, case.queue.value,
            )
        except APIError as exc:
            # CRM write failed — log and continue. Reply has already been sent.
            logger.error(
                "Failed to create escalation case for consignment %s: %s",
                consignment_id, exc,
            )
            case.crm_case_id = None
        return case

    # ── Final reply dispatch + audit ──────────────────────────────────────────

    def _close(
        self,
        inquiry: InquiryRequest,
        consignment_id: str,
        message: str,
        resolution: ResolutionType,
        is_escalated: bool,
        started_at: float,
        now: datetime,
        crm_status: Optional[str] = None,
        driver_responded: Optional[bool] = None,
        escalation_key: Optional[str] = None,
        escalation_kwargs: Optional[dict] = None,
    ) -> ETAReply:
        """Send reply, optionally create escalation case, write audit, return ETAReply."""

        # Send customer reply
        idempotency_key = f"reply:{inquiry.inquiry_id}"
        try:
            self._reply_gateway.send_reply(
                customer_id=inquiry.customer_id,
                channel=inquiry.channel,
                message=message,
                idempotency_key=idempotency_key,
            )
        except APIError as exc:
            logger.error(
                "Failed to send reply for inquiry %s: %s — reply not delivered",
                inquiry.inquiry_id, exc,
            )
            # Continue: audit and escalation still happen even if reply fails

        # Create escalation case in CRM if required
        if is_escalated and escalation_key and escalation_kwargs is not None:
            self._create_escalation(
                inquiry=inquiry,
                consignment_id=consignment_id,
                escalation_key=escalation_key,
                kwargs=escalation_kwargs,
            )

        duration = time.monotonic() - started_at

        # Write audit record
        self._audit.log_resolution(
            inquiry_id=inquiry.inquiry_id,
            consignment_id=consignment_id,
            customer_id=inquiry.customer_id,
            channel=inquiry.channel.value,
            resolution_type=resolution.value,
            is_escalated=is_escalated,
            duration_seconds=duration,
            driver_responded=driver_responded,
            crm_status_at_query=crm_status,
        )

        return ETAReply(
            inquiry_id=inquiry.inquiry_id,
            consignment_id=consignment_id,
            customer_id=inquiry.customer_id,
            channel=inquiry.channel,
            message=message,
            resolution_type=resolution,
            is_escalated=is_escalated,
            sent_at=now,
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _is_valid_consignment_id(raw_id: str) -> bool:
        """Validate consignment ID format against CONSIGNMENT_ID_PATTERN.

        Pattern: two uppercase letters, dash, three digits, dash, four digits.
        Example from spec Section 3.2: AX-771-3344
        Input is normalised to uppercase before matching.
        """
        if not raw_id or not raw_id.strip():
            return False
        return bool(re.match(CONSIGNMENT_ID_PATTERN, raw_id.strip().upper()))
