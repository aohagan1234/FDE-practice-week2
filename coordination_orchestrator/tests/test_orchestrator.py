"""Tests for all 9 orchestrator activities.

Run with:  pytest tests/
"""
from __future__ import annotations

import sys
import os

# Allow imports from the parent coordination_orchestrator directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from api_clients import APIError, EmailClient
from audit import AuditLogger
from models import (
    EscalationType,
    Hire,
    HireStatus,
    OwnerType,
    Task,
    TaskStatus,
    TaskType,
)
from orchestrator import CoordinationOrchestrator


# ── Factories ────────────────────────────────────────────────────────────────

def make_hire(**overrides) -> Hire:
    defaults = dict(
        hire_id="HI-001",
        first_name="Alice",
        last_name="Johnson",
        role="Senior Consultant",
        department="Strategy",
        start_date=date(2025, 2, 17),
        hire_type="EMPLOYEE",
        manager_id="MGR-001",
        manager_email="manager@aldridge.com",
        status=HireStatus.ONBOARDING,
        office_location="Manchester",
        seniority_level=3,
        created_at=datetime(2025, 2, 3, tzinfo=timezone.utc),
    )
    defaults.update(overrides)
    return Hire(**defaults)


def make_task(**overrides) -> Task:
    defaults = dict(
        task_id="TASK-001",
        hire_id="HI-001",
        task_type="COMPLIANCE_TRAINING_ASSIGNED",
        category="PRE_DAY_1",
        status=TaskStatus.PENDING,
        deadline=datetime(2025, 2, 10, tzinfo=timezone.utc),
        owner_type=OwnerType.HR_OPS,
        owner_id=None,
        source_system="LMS",
        data_freshness=datetime(2025, 2, 9, tzinfo=timezone.utc),
        blocked_reason=None,
        created_at=datetime(2025, 2, 3, tzinfo=timezone.utc),
    )
    defaults.update(overrides)
    return Task(**defaults)


def make_task_type(**overrides) -> TaskType:
    defaults = dict(
        task_type="WELCOME_KIT",
        category="PRE_DAY_1",
        offset_days=-5,
        owner_type=OwnerType.HR_OPS,
        source_system="HRIS",
        applies_to_hire_types=["EMPLOYEE", "CONTRACTOR"],
    )
    defaults.update(overrides)
    return TaskType(**defaults)


def make_orchestrator():
    hris = MagicMock()
    it = MagicMock()
    lms = MagicMock()
    cal = MagicMock()
    ful = MagicMock()
    email = EmailClient()
    audit = AuditLogger()
    orch = CoordinationOrchestrator(hris, it, lms, cal, ful, email, audit)
    return orch, email


# ── Activity 2: Deadline Calculation ─────────────────────────────────────────

class TestDeadlineCalculation:
    def test_calculates_correctly(self):
        orch, _ = make_orchestrator()
        hire = make_hire()
        tt = make_task_type(task_type="WELCOME_KIT", offset_days=-5)
        result = orch.calculate_deadlines(hire, [tt])
        expected = datetime(2025, 2, 12, tzinfo=timezone.utc)  # Feb 17 - 5
        assert result["WELCOME_KIT"] == expected

    def test_skips_null_offset_and_escalates(self):
        orch, _ = make_orchestrator()
        hire = make_hire()
        tt = make_task_type(task_type="AMBIGUOUS", offset_days=None)
        result = orch.calculate_deadlines(hire, [tt])
        assert "AMBIGUOUS" not in result
        assert any(
            e.escalation_type == EscalationType.DEADLINE_CALC_ERROR
            for e in orch._escalations
        )

    def test_skips_inapplicable_hire_type(self):
        orch, _ = make_orchestrator()
        hire = make_hire(hire_type="CONTRACTOR")
        tt = make_task_type(
            task_type="I9_VERIFICATION", offset_days=3,
            applies_to_hire_types=["EMPLOYEE"],
        )
        result = orch.calculate_deadlines(hire, [tt])
        assert "I9_VERIFICATION" not in result


# ── Activity 3: Overdue Detection ────────────────────────────────────────────

class TestOverdueDetection:
    def test_flags_after_24h_grace(self):
        orch, _ = make_orchestrator()
        task = make_task(
            deadline=datetime(2025, 2, 10, tzinfo=timezone.utc),
            status=TaskStatus.PENDING,
        )
        now = datetime(2025, 2, 11, 12, tzinfo=timezone.utc)  # 36h late
        overdue = orch.detect_overdue([task], now)
        assert len(overdue) == 1
        assert overdue[0].overdue_hours == pytest.approx(36.0)

    def test_no_flag_within_24h_grace(self):
        orch, _ = make_orchestrator()
        task = make_task(
            deadline=datetime(2025, 2, 10, tzinfo=timezone.utc),
            status=TaskStatus.PENDING,
        )
        now = datetime(2025, 2, 10, 23, tzinfo=timezone.utc)  # 23h — inside grace
        assert orch.detect_overdue([task], now) == []

    def test_skips_complete_tasks(self):
        orch, _ = make_orchestrator()
        task = make_task(
            deadline=datetime(2025, 2, 10, tzinfo=timezone.utc),
            status=TaskStatus.COMPLETE,
        )
        now = datetime(2025, 2, 20, tzinfo=timezone.utc)
        assert orch.detect_overdue([task], now) == []

    def test_skips_skipped_tasks(self):
        orch, _ = make_orchestrator()
        task = make_task(
            deadline=datetime(2025, 2, 10, tzinfo=timezone.utc),
            status=TaskStatus.SKIPPED,
        )
        now = datetime(2025, 2, 20, tzinfo=timezone.utc)
        assert orch.detect_overdue([task], now) == []


# ── Activity 4: Reminders ─────────────────────────────────────────────────────

class TestReminders:
    def test_sends_first_reminder(self):
        orch, _ = make_orchestrator()
        hire = make_hire()
        task = make_task(overdue_hours=30, last_reminder_sent_at=None)
        now = datetime(2025, 2, 11, 12, tzinfo=timezone.utc)
        orch.send_reminders([task], hire, now)
        assert task.last_reminder_sent_at == now

    def test_suppresses_within_24h(self):
        orch, _ = make_orchestrator()
        hire = make_hire()
        sent_at = datetime(2025, 2, 11, 9, tzinfo=timezone.utc)
        task = make_task(overdue_hours=36, last_reminder_sent_at=sent_at)
        now = datetime(2025, 2, 11, 12, tzinfo=timezone.utc)  # only 3h later
        orch.send_reminders([task], hire, now)
        assert task.last_reminder_sent_at == sent_at  # unchanged

    def test_sends_after_24h(self):
        orch, _ = make_orchestrator()
        hire = make_hire()
        sent_at = datetime(2025, 2, 10, 9, tzinfo=timezone.utc)
        task = make_task(overdue_hours=60, last_reminder_sent_at=sent_at)
        now = datetime(2025, 2, 11, 12, tzinfo=timezone.utc)  # 27h later
        orch.send_reminders([task], hire, now)
        assert task.last_reminder_sent_at == now

    def test_skips_system_owned_tasks(self):
        orch, _ = make_orchestrator()
        hire = make_hire()
        task = make_task(owner_type=OwnerType.SYSTEM, overdue_hours=50)
        now = datetime(2025, 2, 15, tzinfo=timezone.utc)
        orch.send_reminders([task], hire, now)
        assert task.last_reminder_sent_at is None

    def test_uses_manager_email_for_manager_tasks(self):
        orch, email = make_orchestrator()
        hire = make_hire()
        task = make_task(
            owner_type=OwnerType.MANAGER,
            overdue_hours=30,
            last_reminder_sent_at=None,
        )
        now = datetime(2025, 2, 15, tzinfo=timezone.utc)
        orch.send_reminders([task], hire, now)
        sent_key = f"reminder:{task.task_id}:{hire.hire_id}:{now.date().isoformat()}"
        assert sent_key in email._sent_keys

    def test_idempotency_key_prevents_duplicate_in_same_day(self):
        orch, email = make_orchestrator()
        hire = make_hire()
        task = make_task(overdue_hours=30, last_reminder_sent_at=None)
        now = datetime(2025, 2, 15, tzinfo=timezone.utc)
        orch.send_reminders([task], hire, now)
        # reset last_reminder_sent_at to simulate re-entry (e.g. bug)
        task.last_reminder_sent_at = None
        orch.send_reminders([task], hire, now)
        # EmailClient idempotency prevents second send
        assert len(email._sent_keys) == 1


# ── Activity 5: I-9 Compliance ────────────────────────────────────────────────

class TestI9Compliance:
    def _run(self, days_offset: int, i9_status: TaskStatus):
        orch, _ = make_orchestrator()
        hire = make_hire(start_date=date(2025, 2, 17))
        now = datetime(2025, 2, 17, tzinfo=timezone.utc) + timedelta(days=days_offset)
        i9 = make_task(task_type="I9_VERIFICATION", status=i9_status)
        orch.monitor_i9_compliance(hire, [i9], now)
        return orch._escalations

    def test_no_escalation_on_day1(self):
        assert self._run(1, TaskStatus.PENDING) == []

    def test_at_risk_on_day2(self):
        escs = self._run(2, TaskStatus.PENDING)
        assert len(escs) == 1
        assert escs[0].escalation_type == EscalationType.I9_AT_RISK

    def test_violation_on_day3(self):
        escs = self._run(3, TaskStatus.PENDING)
        types = {e.escalation_type for e in escs}
        assert EscalationType.I9_VIOLATION in types

    def test_violation_on_day5(self):
        escs = self._run(5, TaskStatus.PENDING)
        types = {e.escalation_type for e in escs}
        assert EscalationType.I9_VIOLATION in types

    def test_no_escalation_when_complete(self):
        assert self._run(3, TaskStatus.COMPLETE) == []

    def test_idempotent_no_duplicate_at_risk(self):
        orch, _ = make_orchestrator()
        hire = make_hire(start_date=date(2025, 2, 17))
        now = datetime(2025, 2, 19, tzinfo=timezone.utc)  # Day 2
        i9 = make_task(task_type="I9_VERIFICATION", status=TaskStatus.PENDING)
        orch.monitor_i9_compliance(hire, [i9], now)
        orch.monitor_i9_compliance(hire, [i9], now)  # second poll cycle
        at_risk = [
            e for e in orch._escalations
            if e.escalation_type == EscalationType.I9_AT_RISK
        ]
        assert len(at_risk) == 1

    def test_skips_non_onboarding_hire(self):
        orch, _ = make_orchestrator()
        hire = make_hire(status=HireStatus.ON_HOLD, start_date=date(2025, 2, 17))
        now = datetime(2025, 2, 19, tzinfo=timezone.utc)
        i9 = make_task(task_type="I9_VERIFICATION", status=TaskStatus.PENDING)
        orch.monitor_i9_compliance(hire, [i9], now)
        assert orch._escalations == []


# ── Activity 6: IT Provisioning ──────────────────────────────────────────────

class TestITProvisioning:
    def test_submits_known_role(self):
        orch, _ = make_orchestrator()
        hire = make_hire(role="Senior Consultant")
        tasks = [
            make_task(
                task_type="IT_PROVISIONING_REQUESTED",
                status=TaskStatus.PENDING,
            )
        ]
        orch._it.submit_request.return_value = "EXT-123"
        orch.auto_submit_it_provisioning(hire, tasks, datetime.now(timezone.utc))
        assert hire.hire_id in orch._it_requests
        assert orch._it_requests[hire.hire_id].external_request_id == "EXT-123"

    def test_escalates_unknown_role(self):
        orch, _ = make_orchestrator()
        hire = make_hire(role="Quantum Strategist")
        tasks = [
            make_task(
                task_type="IT_PROVISIONING_REQUESTED",
                status=TaskStatus.PENDING,
            )
        ]
        orch.auto_submit_it_provisioning(hire, tasks, datetime.now(timezone.utc))
        assert any(
            e.escalation_type == EscalationType.ROLE_NOT_MAPPED
            for e in orch._escalations
        )

    def test_role_lookup_is_case_insensitive(self):
        orch, _ = make_orchestrator()
        hire = make_hire(role="SENIOR CONSULTANT")  # uppercase
        tasks = [
            make_task(
                task_type="IT_PROVISIONING_REQUESTED",
                status=TaskStatus.PENDING,
            )
        ]
        orch._it.submit_request.return_value = "EXT-456"
        orch.auto_submit_it_provisioning(hire, tasks, datetime.now(timezone.utc))
        assert hire.hire_id in orch._it_requests

    def test_idempotent_no_double_submit(self):
        orch, _ = make_orchestrator()
        hire = make_hire(role="Consultant")
        tasks = [
            make_task(
                task_type="IT_PROVISIONING_REQUESTED",
                status=TaskStatus.PENDING,
            )
        ]
        orch._it.submit_request.return_value = "EXT-789"
        now = datetime.now(timezone.utc)
        orch.auto_submit_it_provisioning(hire, tasks, now)
        orch.auto_submit_it_provisioning(hire, tasks, now)  # second call
        assert orch._it.submit_request.call_count == 1

    def test_escalates_on_api_4xx(self):
        orch, _ = make_orchestrator()
        hire = make_hire(role="Analyst")
        tasks = [
            make_task(
                task_type="IT_PROVISIONING_REQUESTED",
                status=TaskStatus.PENDING,
            )
        ]
        orch._it.submit_request.side_effect = APIError("IT_PROVISIONING", 400, "Bad request")
        orch.auto_submit_it_provisioning(hire, tasks, datetime.now(timezone.utc))
        assert any(
            e.escalation_type == EscalationType.ROLE_NOT_MAPPED
            for e in orch._escalations
        )


# ── Activity 7: Manager Handoff ──────────────────────────────────────────────

class TestManagerHandoff:
    def test_sends_when_all_complete(self):
        orch, _ = make_orchestrator()
        hire = make_hire(start_date=date(2025, 3, 10))
        tasks = [
            make_task(task_id=f"T{i}", category="PRE_DAY_1", status=TaskStatus.COMPLETE)
            for i in range(3)
        ]
        now = datetime(2025, 3, 5, tzinfo=timezone.utc)  # 5 days before start
        orch.check_manager_handoff(hire, tasks, now)
        assert hire.hire_id in orch._handoffs_sent

    def test_sends_at_day_minus_2_with_incomplete_tasks(self):
        orch, _ = make_orchestrator()
        hire = make_hire(start_date=date(2025, 3, 10))
        tasks = [
            make_task(task_id="T1", category="PRE_DAY_1", status=TaskStatus.COMPLETE),
            make_task(task_id="T2", category="PRE_DAY_1", status=TaskStatus.PENDING),
        ]
        now = datetime(2025, 3, 8, tzinfo=timezone.utc)  # Day -2
        orch.check_manager_handoff(hire, tasks, now)
        assert hire.hire_id in orch._handoffs_sent

    def test_skipped_counts_as_complete(self):
        orch, _ = make_orchestrator()
        hire = make_hire(start_date=date(2025, 3, 10))
        tasks = [
            make_task(task_id="T1", category="PRE_DAY_1", status=TaskStatus.COMPLETE),
            make_task(task_id="T2", category="PRE_DAY_1", status=TaskStatus.SKIPPED),
        ]
        now = datetime(2025, 3, 5, tzinfo=timezone.utc)
        orch.check_manager_handoff(hire, tasks, now)
        assert hire.hire_id in orch._handoffs_sent

    def test_does_not_send_before_day_minus_2_with_incomplete(self):
        orch, _ = make_orchestrator()
        hire = make_hire(start_date=date(2025, 3, 10))
        tasks = [
            make_task(task_id="T1", category="PRE_DAY_1", status=TaskStatus.PENDING),
        ]
        now = datetime(2025, 3, 6, tzinfo=timezone.utc)  # Day -4
        orch.check_manager_handoff(hire, tasks, now)
        assert hire.hire_id not in orch._handoffs_sent

    def test_idempotent_no_duplicate_handoff(self):
        orch, email = make_orchestrator()
        hire = make_hire(start_date=date(2025, 3, 10))
        tasks = [make_task(task_id="T1", category="PRE_DAY_1", status=TaskStatus.COMPLETE)]
        now = datetime(2025, 3, 8, tzinfo=timezone.utc)
        orch.check_manager_handoff(hire, tasks, now)
        orch.check_manager_handoff(hire, tasks, now)  # second call
        assert len(email._sent_keys) == 1


# ── Activity 8: Escalation Routing ───────────────────────────────────────────

class TestEscalationRouting:
    def test_escalation_stored_and_dispatched(self):
        orch, email = make_orchestrator()
        orch._create_escalation(
            hire_id="HI-001",
            esc_type=EscalationType.ROLE_NOT_MAPPED,
            message="Role not found",
        )
        assert len(orch._escalations) == 1
        # Email was dispatched
        assert any("ESC-HI-001" in k for k in email._sent_keys)

    def test_idempotency_no_duplicate_escalation(self):
        orch, _ = make_orchestrator()
        for _ in range(3):
            if not orch._escalation_exists("HI-001", EscalationType.ROLE_NOT_MAPPED):
                orch._create_escalation(
                    hire_id="HI-001",
                    esc_type=EscalationType.ROLE_NOT_MAPPED,
                    message="Role not found",
                )
        assert len(orch._escalations) == 1

    def test_i9_violation_uses_critical_severity(self):
        orch, _ = make_orchestrator()
        esc = orch._create_escalation(
            hire_id="HI-001",
            esc_type=EscalationType.I9_VIOLATION,
            message="Violation",
        )
        from models import EscalationSeverity
        assert esc.severity == EscalationSeverity.CRITICAL


# ── Activity 1: Poll Task Status (system failure path) ───────────────────────

class TestPollTaskStatus:
    def test_escalates_on_hris_failure(self):
        orch, _ = make_orchestrator()
        hire = make_hire()
        orch._hris.get_tasks_for_hire.side_effect = APIError("HRIS", 503, "Down")
        result = orch.poll_task_status(hire)
        assert result == []
        assert any(
            e.escalation_type == EscalationType.SYSTEM_UNAVAILABLE
            for e in orch._escalations
        )

    def test_returns_tasks_on_success(self):
        orch, _ = make_orchestrator()
        hire = make_hire()
        task = make_task()
        orch._hris.get_tasks_for_hire.return_value = [task]
        # Sub-system clients return None (no specialist poll needed for HRIS tasks)
        result = orch.poll_task_status(hire)
        assert len(result) == 1


# ── Full cycle smoke test ─────────────────────────────────────────────────────

class TestRunCycle:
    def test_cycle_skips_on_hire_fetch_failure(self):
        orch, _ = make_orchestrator()
        orch._hris.get_active_hires.side_effect = Exception("Network error")
        # Should not raise; just log and return
        orch.run_cycle()

    def test_cycle_processes_onboarding_hires(self):
        orch, _ = make_orchestrator()
        hire = make_hire()
        task = make_task(status=TaskStatus.COMPLETE)
        orch._hris.get_active_hires.return_value = [hire]
        orch._hris.get_tasks_for_hire.return_value = [task]
        orch.run_cycle(now=datetime(2025, 2, 17, tzinfo=timezone.utc))
        orch._hris.get_tasks_for_hire.assert_called_once_with(hire.hire_id)
