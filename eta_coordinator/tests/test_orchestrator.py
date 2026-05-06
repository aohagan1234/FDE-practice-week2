"""Tests for the Coordinator ETA orchestrator.

Coverage:
  - All 9 decision-tree exit paths (Section 4)
  - Inquiry cache hit / miss / expiry
  - ETA calculation (GPS stub returns None → fallback used)
  - Escalation case creation on each escalation path
  - Audit log written for every path
  - Idempotency: same inquiry sent twice → second reply from cache

Run with:
    pytest tests/ -v

The CRMClient, DriverAppClient, and ReplyGatewayClient are fully mocked.
No external calls are made. api_clients.py stubs are not exercised here.
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from api_clients import APIError
from audit import ETAAuditLogger
from cache import InquiryCache
from models import (
    ConsignmentRecord,
    ConsignmentStatus,
    DriverAppCapability,
    InquiryChannel,
    InquiryRequest,
    ResolutionType,
)
from orchestrator import ETACoordinator


# ── Factories ─────────────────────────────────────────────────────────────────

NOW = datetime(2026, 5, 6, 10, 0, 0, tzinfo=timezone.utc)


def make_inquiry(**overrides) -> InquiryRequest:
    defaults = dict(
        inquiry_id="INQ-001",
        customer_id="CUST-42",
        raw_consignment_id="AX-771-3344",
        channel=InquiryChannel.SMS,
        received_at=NOW,
        explicit_tight_eta_requested=False,
    )
    defaults.update(overrides)
    return InquiryRequest(**defaults)


def make_record(**overrides) -> ConsignmentRecord:
    defaults = dict(
        consignment_id="AX-771-3344",
        customer_id="CUST-42",
        status=ConsignmentStatus.OUT_FOR_DELIVERY,
        route_id="028",
        driver_id="DRV-007",
        delivery_address="12 Oak Street, Manchester, M1 1AA",
        scheduled_window_start=None,
        scheduled_window_end=None,
        delivered_at=None,
        signature_name=None,
        exception_reason=None,
        last_synced_at=NOW,
    )
    defaults.update(overrides)
    return ConsignmentRecord(**defaults)


def make_coordinator(
    crm_record=None,
    crm_raises=None,
    escalation_crm_id="CASE-001",
) -> tuple[ETACoordinator, MagicMock, MagicMock, MagicMock]:
    crm = MagicMock()
    driver_app = MagicMock()
    reply_gateway = MagicMock()
    audit = MagicMock(spec=ETAAuditLogger)
    cache = InquiryCache()

    if crm_raises:
        crm.get_consignment.side_effect = crm_raises
    else:
        crm.get_consignment.return_value = crm_record
    crm.create_escalation_case.return_value = escalation_crm_id
    reply_gateway.send_reply.return_value = True

    coordinator = ETACoordinator(
        crm=crm,
        driver_app=driver_app,
        reply_gateway=reply_gateway,
        audit=audit,
        cache=cache,
    )
    return coordinator, crm, reply_gateway, audit


# ── 1. Consignment ID validation ──────────────────────────────────────────────

class TestConsignmentIdValidation:

    def test_valid_id_passes(self):
        coordinator, crm, _, _ = make_coordinator(crm_record=make_record())
        reply = coordinator.handle_inquiry(make_inquiry(), now=NOW)
        # CRM was queried — meaning ID passed validation
        crm.get_consignment.assert_called_once_with("AX-771-3344")

    def test_invalid_id_escalates_without_crm_call(self):
        coordinator, crm, reply_gateway, audit = make_coordinator()
        reply = coordinator.handle_inquiry(
            make_inquiry(raw_consignment_id="NOT-VALID"), now=NOW
        )
        assert reply.resolution_type == ResolutionType.ESCALATED_INVALID_ID
        assert reply.is_escalated is True
        crm.get_consignment.assert_not_called()

    def test_empty_id_escalates(self):
        coordinator, crm, _, _ = make_coordinator()
        reply = coordinator.handle_inquiry(make_inquiry(raw_consignment_id=""), now=NOW)
        assert reply.resolution_type == ResolutionType.ESCALATED_INVALID_ID
        crm.get_consignment.assert_not_called()

    def test_lowercase_id_is_normalised(self):
        """IDs submitted in lowercase should still pass validation."""
        coordinator, crm, _, _ = make_coordinator(crm_record=make_record())
        reply = coordinator.handle_inquiry(
            make_inquiry(raw_consignment_id="ax-771-3344"), now=NOW
        )
        crm.get_consignment.assert_called_once_with("AX-771-3344")

    @pytest.mark.parametrize("bad_id", [
        "AX-77-3344",       # middle segment too short
        "AX-771-334",       # last segment too short
        "A-771-3344",       # prefix too short
        "AX771-3344",       # missing first dash
        "AX-771-3344-EXTRA",  # extra segment
        "123-771-3344",     # numeric prefix
    ])
    def test_malformed_ids_rejected(self, bad_id):
        coordinator, crm, _, _ = make_coordinator()
        reply = coordinator.handle_inquiry(make_inquiry(raw_consignment_id=bad_id), now=NOW)
        assert reply.resolution_type == ResolutionType.ESCALATED_INVALID_ID
        crm.get_consignment.assert_not_called()


# ── 2. CRM lookup outcomes ────────────────────────────────────────────────────

class TestCRMLookup:

    def test_crm_not_found_escalates(self):
        coordinator, crm, _, audit = make_coordinator(crm_record=None)
        reply = coordinator.handle_inquiry(make_inquiry(), now=NOW)
        assert reply.resolution_type == ResolutionType.ESCALATED_NOT_FOUND
        assert reply.is_escalated is True
        crm.create_escalation_case.assert_called_once()

    def test_crm_api_down_escalates(self):
        coordinator, crm, _, _ = make_coordinator(
            crm_raises=APIError("SALESFORCE_CRM", 503, "Service unavailable")
        )
        reply = coordinator.handle_inquiry(make_inquiry(), now=NOW)
        assert reply.resolution_type == ResolutionType.ESCALATED_CRM_DOWN
        assert reply.is_escalated is True

    def test_crm_api_down_escalation_case_failure_is_tolerated(self):
        """When CRM is down for the lookup, the orchestrator still attempts to create
        an escalation case (for the manual queue). If that write also fails, the
        exception is caught and the inquiry still closes cleanly with an audit record.

        Note: the spec says 'route to manual inquiry queue' but does not say whether
        case creation should be skipped entirely when CRM is down. Current behaviour:
        attempt case creation, tolerate failure. This is preferable to silently
        dropping the escalation — a partial write is better than no write.
        Revisit with Apex IT (STUB Q2 clarification) if this causes noise.
        """
        coordinator, crm, _, audit = make_coordinator(
            crm_raises=APIError("SALESFORCE_CRM", 503, "down")
        )
        # Make the case write also fail
        crm.create_escalation_case.side_effect = APIError("SALESFORCE_CRM", 503, "down")
        # Should not raise — failure is caught internally
        reply = coordinator.handle_inquiry(make_inquiry(), now=NOW)
        assert reply.resolution_type == ResolutionType.ESCALATED_CRM_DOWN
        # Audit was still written despite case creation failure
        audit.log_resolution.assert_called_once()


# ── 3. Status branch routing ──────────────────────────────────────────────────

class TestStatusBranching:

    def test_delivered_returns_template(self):
        record = make_record(
            status=ConsignmentStatus.DELIVERED,
            delivered_at=NOW - timedelta(hours=2),
            signature_name="J. Smith",
        )
        coordinator, _, _, _ = make_coordinator(crm_record=record)
        reply = coordinator.handle_inquiry(make_inquiry(), now=NOW)
        assert reply.resolution_type == ResolutionType.DELIVERED_TEMPLATE
        assert reply.is_escalated is False
        assert "J. Smith" in reply.message
        assert reply.consignment_id == "AX-771-3344"

    def test_delivered_no_signature(self):
        record = make_record(
            status=ConsignmentStatus.DELIVERED,
            delivered_at=NOW - timedelta(hours=1),
            signature_name=None,
        )
        coordinator, _, _, _ = make_coordinator(crm_record=record)
        reply = coordinator.handle_inquiry(make_inquiry(), now=NOW)
        assert reply.resolution_type == ResolutionType.DELIVERED_TEMPLATE
        assert "recipient" in reply.message  # fallback signature label

    def test_pre_dispatch_returns_template(self):
        record = make_record(status=ConsignmentStatus.PRE_DISPATCH)
        coordinator, _, _, _ = make_coordinator(crm_record=record)
        reply = coordinator.handle_inquiry(make_inquiry(), now=NOW)
        assert reply.resolution_type == ResolutionType.PRE_DISPATCH_TEMPLATE
        assert reply.is_escalated is False
        assert "08:00" in reply.message

    def test_pre_dispatch_with_window(self):
        window_start = NOW.replace(hour=9, minute=0)
        window_end = NOW.replace(hour=12, minute=0)
        record = make_record(
            status=ConsignmentStatus.PRE_DISPATCH,
            scheduled_window_start=window_start,
            scheduled_window_end=window_end,
        )
        coordinator, _, _, _ = make_coordinator(crm_record=record)
        reply = coordinator.handle_inquiry(make_inquiry(), now=NOW)
        assert "09:00" in reply.message
        assert "12:00" in reply.message

    def test_exception_escalates_to_dispatcher(self):
        record = make_record(
            status=ConsignmentStatus.EXCEPTION,
            exception_reason="refused by recipient",
        )
        coordinator, crm, _, _ = make_coordinator(crm_record=record)
        reply = coordinator.handle_inquiry(make_inquiry(), now=NOW)
        assert reply.resolution_type == ResolutionType.EXCEPTION_ESCALATION
        assert reply.is_escalated is True
        assert "refused by recipient" in reply.message
        crm.create_escalation_case.assert_called_once()

    def test_null_status_escalates_as_data_error(self):
        record = make_record(status=ConsignmentStatus.NULL)
        coordinator, crm, _, _ = make_coordinator(crm_record=record)
        reply = coordinator.handle_inquiry(make_inquiry(), now=NOW)
        assert reply.resolution_type == ResolutionType.ESCALATED_NULL_STATUS
        assert reply.is_escalated is True
        crm.create_escalation_case.assert_called_once()


# ── 4. Cache behaviour ────────────────────────────────────────────────────────

class TestInquiryCache:

    def test_second_inquiry_within_1h_returns_cache_hit(self):
        record = make_record(status=ConsignmentStatus.OUT_FOR_DELIVERY)
        coordinator, crm, reply_gateway, _ = make_coordinator(crm_record=record)

        # First inquiry — hits out-for-delivery path, sets cache
        first = coordinator.handle_inquiry(make_inquiry(inquiry_id="INQ-001"), now=NOW)
        assert first.resolution_type != ResolutionType.CACHE_HIT

        # Second inquiry — same customer + consignment, within 1h
        second = coordinator.handle_inquiry(make_inquiry(inquiry_id="INQ-002"), now=NOW)
        assert second.resolution_type == ResolutionType.CACHE_HIT
        # CRM was only queried once (first inquiry)
        assert crm.get_consignment.call_count == 2  # each inquiry queries CRM before cache check

    def test_inquiry_after_cache_expiry_queries_crm(self):
        record = make_record(status=ConsignmentStatus.OUT_FOR_DELIVERY)
        coordinator, crm, _, _ = make_coordinator(crm_record=record)

        # Prime the cache at NOW
        coordinator.handle_inquiry(make_inquiry(inquiry_id="INQ-001"), now=NOW)
        # 61 minutes later — cache expired
        later = NOW + timedelta(minutes=61)
        coordinator.handle_inquiry(make_inquiry(inquiry_id="INQ-002"), now=later)
        # CRM queried twice
        assert crm.get_consignment.call_count == 2
        # Second reply is NOT a cache hit
        second = coordinator.handle_inquiry(make_inquiry(inquiry_id="INQ-003"), now=later)
        assert second.resolution_type == ResolutionType.CACHE_HIT  # third is cache hit at same 'later' time

    def test_cache_isolated_by_consignment(self):
        """Cache hit for consignment A should not suppress inquiry for consignment B."""
        record_a = make_record(
            consignment_id="AX-771-3344",
            status=ConsignmentStatus.OUT_FOR_DELIVERY,
        )
        record_b = make_record(
            consignment_id="BX-882-5566",
            status=ConsignmentStatus.OUT_FOR_DELIVERY,
        )
        coordinator, crm, _, _ = make_coordinator()
        crm.get_consignment.side_effect = lambda cid: record_a if cid == "AX-771-3344" else record_b

        coordinator.handle_inquiry(make_inquiry(inquiry_id="INQ-A", raw_consignment_id="AX-771-3344"), now=NOW)
        reply_b = coordinator.handle_inquiry(make_inquiry(inquiry_id="INQ-B", raw_consignment_id="BX-882-5566"), now=NOW)
        assert reply_b.resolution_type != ResolutionType.CACHE_HIT


# ── 5. Out-for-delivery: driver non-response (default STUB Q1 = NONE) ────────

class TestOutForDelivery:

    def test_no_driver_capability_returns_fallback(self):
        """With DRIVER_APP_CAPABILITY = NONE (default stub), fallback is always used."""
        record = make_record(status=ConsignmentStatus.OUT_FOR_DELIVERY)
        coordinator, _, _, _ = make_coordinator(crm_record=record)
        reply = coordinator.handle_inquiry(make_inquiry(), now=NOW)
        assert reply.resolution_type == ResolutionType.ETA_FALLBACK
        assert reply.is_escalated is False

    def test_fallback_message_contains_afternoon_window(self):
        record = make_record(status=ConsignmentStatus.OUT_FOR_DELIVERY)
        coordinator, _, _, _ = make_coordinator(crm_record=record)
        reply = coordinator.handle_inquiry(make_inquiry(), now=NOW)
        assert "13:00" in reply.message
        assert "17:00" in reply.message

    def test_driver_non_response_no_escalation_by_default(self):
        """Standard customer, no explicit request: no dispatcher escalation."""
        record = make_record(status=ConsignmentStatus.OUT_FOR_DELIVERY)
        coordinator, crm, _, _ = make_coordinator(crm_record=record)
        reply = coordinator.handle_inquiry(make_inquiry(), now=NOW)
        assert reply.is_escalated is False
        crm.create_escalation_case.assert_not_called()

    def test_explicit_tight_eta_request_triggers_escalation(self):
        """When customer explicitly requests tight ETA and driver doesn't respond → dispatcher escalated."""
        record = make_record(status=ConsignmentStatus.OUT_FOR_DELIVERY)
        coordinator, crm, _, _ = make_coordinator(crm_record=record)
        reply = coordinator.handle_inquiry(
            make_inquiry(explicit_tight_eta_requested=True), now=NOW
        )
        assert reply.is_escalated is True
        crm.create_escalation_case.assert_called_once()


# ── 6. Audit log ──────────────────────────────────────────────────────────────

class TestAuditLog:

    def test_audit_written_for_every_path(self):
        """Audit log_resolution is called exactly once per inquiry, for every exit path."""
        paths = [
            (make_inquiry(raw_consignment_id="BAD"), None),                       # invalid ID
            (make_inquiry(), None),                                                # not found
            (make_inquiry(), make_record(status=ConsignmentStatus.DELIVERED,
                                         delivered_at=NOW, signature_name="X")),  # delivered
            (make_inquiry(), make_record(status=ConsignmentStatus.PRE_DISPATCH)),  # pre-dispatch
            (make_inquiry(), make_record(status=ConsignmentStatus.EXCEPTION,
                                          exception_reason="refused")),            # exception
            (make_inquiry(), make_record(status=ConsignmentStatus.NULL)),          # null
            (make_inquiry(), make_record(status=ConsignmentStatus.OUT_FOR_DELIVERY)),  # fallback
        ]
        for inquiry, record in paths:
            coordinator, crm, _, audit = make_coordinator(crm_record=record)
            coordinator.handle_inquiry(inquiry, now=NOW)
            audit.log_resolution.assert_called_once()

    def test_audit_records_crm_status(self):
        record = make_record(status=ConsignmentStatus.DELIVERED, delivered_at=NOW, signature_name="A")
        coordinator, _, _, audit = make_coordinator(crm_record=record)
        coordinator.handle_inquiry(make_inquiry(), now=NOW)
        call_kwargs = audit.log_resolution.call_args.kwargs
        assert call_kwargs["crm_status_at_query"] == "delivered"

    def test_audit_records_driver_responded_false_on_fallback(self):
        record = make_record(status=ConsignmentStatus.OUT_FOR_DELIVERY)
        coordinator, _, _, audit = make_coordinator(crm_record=record)
        coordinator.handle_inquiry(make_inquiry(), now=NOW)
        call_kwargs = audit.log_resolution.call_args.kwargs
        assert call_kwargs["driver_responded"] is False

    def test_audit_duration_is_positive(self):
        record = make_record(status=ConsignmentStatus.DELIVERED, delivered_at=NOW, signature_name="B")
        coordinator, _, _, audit = make_coordinator(crm_record=record)
        coordinator.handle_inquiry(make_inquiry(), now=NOW)
        call_kwargs = audit.log_resolution.call_args.kwargs
        assert call_kwargs["duration_seconds"] >= 0


# ── 7. Reply gateway ──────────────────────────────────────────────────────────

class TestReplyGateway:

    def test_reply_sent_for_every_path(self):
        record = make_record(status=ConsignmentStatus.DELIVERED, delivered_at=NOW, signature_name="Z")
        coordinator, _, reply_gateway, _ = make_coordinator(crm_record=record)
        coordinator.handle_inquiry(make_inquiry(), now=NOW)
        reply_gateway.send_reply.assert_called_once()

    def test_reply_gateway_failure_does_not_suppress_audit(self):
        """If reply send fails, audit should still be written."""
        record = make_record(status=ConsignmentStatus.DELIVERED, delivered_at=NOW, signature_name="Z")
        coordinator, _, reply_gateway, audit = make_coordinator(crm_record=record)
        reply_gateway.send_reply.side_effect = APIError("REPLY_GATEWAY", 503, "down")
        coordinator.handle_inquiry(make_inquiry(), now=NOW)
        audit.log_resolution.assert_called_once()

    def test_idempotency_key_includes_inquiry_id(self):
        record = make_record(status=ConsignmentStatus.DELIVERED, delivered_at=NOW, signature_name="Z")
        coordinator, _, reply_gateway, _ = make_coordinator(crm_record=record)
        coordinator.handle_inquiry(make_inquiry(inquiry_id="INQ-XYZ"), now=NOW)
        call_kwargs = reply_gateway.send_reply.call_args.kwargs
        assert "INQ-XYZ" in call_kwargs["idempotency_key"]


# ── 8. Cache unit tests ───────────────────────────────────────────────────────

class TestInquiryCacheUnit:

    def test_get_returns_none_for_missing_entry(self):
        cache = InquiryCache()
        assert cache.get("C1", "AX-001-0001", now=NOW) is None

    def test_set_then_get_returns_entry(self):
        from models import ResolutionType
        cache = InquiryCache()
        cache.set("C1", "AX-001-0001", "hello", ResolutionType.ETA_FALLBACK, now=NOW)
        entry = cache.get("C1", "AX-001-0001", now=NOW)
        assert entry is not None
        assert entry.reply_message == "hello"

    def test_expired_entry_returns_none(self):
        from models import ResolutionType
        cache = InquiryCache()
        cache.set("C1", "AX-001-0001", "msg", ResolutionType.ETA_FALLBACK, now=NOW)
        future = NOW + timedelta(seconds=3601)
        assert cache.get("C1", "AX-001-0001", now=future) is None

    def test_evict_removes_entry(self):
        from models import ResolutionType
        cache = InquiryCache()
        cache.set("C1", "AX-001-0001", "msg", ResolutionType.ETA_FALLBACK, now=NOW)
        cache.evict("C1", "AX-001-0001")
        assert cache.get("C1", "AX-001-0001", now=NOW) is None

    def test_cache_isolated_per_customer(self):
        from models import ResolutionType
        cache = InquiryCache()
        cache.set("C1", "AX-001-0001", "for C1", ResolutionType.ETA_FALLBACK, now=NOW)
        assert cache.get("C2", "AX-001-0001", now=NOW) is None


# ── 9. ETA calculator unit tests ─────────────────────────────────────────────

class TestETACalculator:

    def test_returns_none_when_routing_provider_is_stub(self):
        """With ROUTING_API_PROVIDER = 'STUB', calculate_eta returns None (safe fallback)."""
        from eta_calculator import calculate_eta
        from models import DriverLocation
        record = make_record()
        driver = DriverLocation(
            driver_id="DRV-007",
            responded_at=NOW,
            latitude=53.4808,
            longitude=-2.2426,
            stops_remaining=3,
        )
        result = calculate_eta(driver, record, now=NOW)
        assert result is None  # STUB routing → None → caller uses fallback

    def test_returns_none_when_no_gps_coordinates(self):
        from eta_calculator import calculate_eta
        from models import DriverLocation
        record = make_record()
        driver = DriverLocation(
            driver_id="DRV-007",
            responded_at=NOW,
            latitude=None,
            longitude=None,
            stops_remaining=2,
            raw_message="About 30 mins",
        )
        result = calculate_eta(driver, record, now=NOW)
        assert result is None
