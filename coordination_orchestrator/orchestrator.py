"""Coordination Orchestrator — all 9 activities + main poll cycle.

Activities implemented:
  1. Poll task status across 6 source systems
  2. Calculate deadlines (once per hire at intake)
  3. Detect overdue tasks
  4. Send reminders (rate-limited, idempotent)
  5. Monitor I-9 compliance (every 2 hours, mandatory escalation)
  6. Auto-submit IT provisioning requests
  7. Generate manager handoff notification
  8. Route escalations to correct owner
  9. Audit log every action (delegated to AuditLogger)
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from api_clients import (
    APIError,
    CalendarClient,
    EmailClient,
    FulfillmentClient,
    HRISClient,
    ITProvisioningClient,
    LMSClient,
)
from audit import AuditLogger
from config import (
    IT_ACCESS_MATRIX,
    ESCALATION_ROUTING,
    OVERDUE_ESCALATION_HOURS,
    OVERDUE_GRACE_HOURS,
    OWNER_TYPE_FALLBACK_EMAILS,
    REMINDER_RATE_LIMIT_HOURS,
    SOURCE_SYSTEM_DEEPLINKS,
    SYSTEM_UNAVAILABLE_RETRY_COUNT,
)
from models import (
    Escalation,
    EscalationStatus,
    EscalationType,
    Hire,
    ITProvisioningRequest,
    OwnerType,
    Task,
    TaskStatus,
    TaskType,
)

logger = logging.getLogger(__name__)


class CoordinationOrchestrator:
    def __init__(
        self,
        hris: HRISClient,
        it_provisioning: ITProvisioningClient,
        lms: LMSClient,
        calendar: CalendarClient,
        fulfillment: FulfillmentClient,
        email: EmailClient,
        audit: AuditLogger,
    ) -> None:
        self._hris = hris
        self._it = it_provisioning
        self._lms = lms
        self._calendar = calendar
        self._fulfillment = fulfillment
        self._email = email
        self._audit = audit

        # In-memory state — replace with DB persistence in production
        self._escalations: list[Escalation] = []
        self._handoffs_sent: set[str] = set()
        self._it_requests: dict[str, ITProvisioningRequest] = {}

    # ── Activity 1: Poll Task Status ──────────────────────────────────────────

    def poll_task_status(self, hire: Hire) -> list[Task]:
        """Fetch current task status for all tasks belonging to a hire.

        Retries each source-system call 3× with exponential backoff.
        Raises SYSTEM_UNAVAILABLE escalation after 3 consecutive failures.
        """
        try:
            tasks = self._hris.get_tasks_for_hire(hire.hire_id)
        except APIError as exc:
            self._handle_system_failure("HRIS", hire.hire_id, str(exc))
            return []

        for task in tasks:
            refreshed = self._poll_one_task(task, hire)
            if refreshed is not None:
                task.status = refreshed
                task.data_freshness = datetime.now(timezone.utc)

        self._audit.log(
            action_type="POLL_TASK_STATUS",
            hire_id=hire.hire_id,
            output_data={"task_count": len(tasks)},
            status="OK",
        )
        return tasks

    def _poll_one_task(self, task: Task, hire: Hire) -> Optional[TaskStatus]:
        client_map = {
            "HRIS": None,            # already fetched in bulk above
            "IT_PROVISIONING": self._it,
            "LMS": self._lms,
            "CALENDAR": self._calendar,
            "FULFILLMENT": self._fulfillment,
            "EMAIL": None,           # EMAIL tasks tracked inside HRIS
        }
        client = client_map.get(task.source_system)
        if client is None:
            return None
        try:
            return client.get_task_status(task.task_id)
        except APIError as exc:
            self._handle_system_failure(task.source_system, hire.hire_id, str(exc))
            return None

    def _handle_system_failure(self, system: str, hire_id: str, error: str) -> None:
        if not self._escalation_exists(hire_id, EscalationType.SYSTEM_UNAVAILABLE):
            self._create_escalation(
                hire_id=hire_id,
                esc_type=EscalationType.SYSTEM_UNAVAILABLE,
                message=(
                    f"Source system '{system}' unavailable after "
                    f"{SYSTEM_UNAVAILABLE_RETRY_COUNT} retries. Error: {error}"
                ),
            )

    # ── Activity 2: Calculate Deadlines ──────────────────────────────────────

    def calculate_deadlines(
        self, hire: Hire, task_types: list[TaskType]
    ) -> dict[str, datetime]:
        """Return {task_type_name: deadline} for all applicable task types.

        Called once per hire at intake. SKIPS task types not applicable to
        the hire's hire_type (e.g. I-9 tasks for certain contractor variants).
        """
        deadlines: dict[str, datetime] = {}
        for tt in task_types:
            if hire.hire_type not in tt.applies_to_hire_types:
                continue
            if tt.offset_days is None:
                self._audit.log(
                    action_type="DEADLINE_CALC_ERROR",
                    hire_id=hire.hire_id,
                    output_data={"task_type": tt.task_type},
                    status="ERROR",
                    error=f"offset_days NULL for {tt.task_type}",
                )
                self._create_escalation(
                    hire_id=hire.hire_id,
                    esc_type=EscalationType.DEADLINE_CALC_ERROR,
                    message=(
                        f"offset_days is NULL for task_type={tt.task_type}. "
                        f"Task registry needs correction."
                    ),
                )
                continue
            start = datetime(
                hire.start_date.year,
                hire.start_date.month,
                hire.start_date.day,
                tzinfo=timezone.utc,
            )
            deadlines[tt.task_type] = start + timedelta(days=tt.offset_days)

        self._audit.log(
            action_type="CALCULATE_DEADLINES",
            hire_id=hire.hire_id,
            output_data={"count": len(deadlines)},
            status="OK",
        )
        return deadlines

    # ── Activity 3: Detect Overdue Tasks ─────────────────────────────────────

    def detect_overdue(self, tasks: list[Task], now: datetime) -> list[Task]:
        """Flag tasks that have exceeded the 24-hour grace period past deadline.

        COMPLETE and SKIPPED tasks are never flagged (both are terminal states).
        """
        overdue: list[Task] = []
        for task in tasks:
            if task.is_terminal:
                continue
            elapsed = (now - task.deadline).total_seconds()
            if elapsed > OVERDUE_GRACE_HOURS * 3600:
                task.overdue_hours = elapsed / 3600
                overdue.append(task)
        return overdue

    # ── Activity 4: Send Reminders ────────────────────────────────────────────

    def send_reminders(
        self, overdue_tasks: list[Task], hire: Hire, now: datetime
    ) -> None:
        """Send one reminder per overdue task per 24-hour window.

        SYSTEM-owned tasks are skipped (no human to notify).
        Idempotency key prevents duplicate sends within the same calendar day.
        """
        for task in overdue_tasks:
            self._maybe_send_reminder(task, hire, now)

    def _maybe_send_reminder(
        self, task: Task, hire: Hire, now: datetime
    ) -> None:
        if task.owner_type == OwnerType.SYSTEM:
            return

        if task.last_reminder_sent_at is not None:
            since_last = (now - task.last_reminder_sent_at).total_seconds()
            if since_last < REMINDER_RATE_LIMIT_HOURS * 3600:
                return

        recipient = self._resolve_owner_email(task, hire)
        if not recipient:
            self._audit.log(
                action_type="REMINDER_SKIPPED_NO_OWNER",
                hire_id=hire.hire_id,
                task_id=task.task_id,
                status="WARN",
                error="owner_id NULL and no fallback email configured for owner_type",
            )
            return

        idempotency_key = (
            f"reminder:{task.task_id}:{hire.hire_id}:{now.date().isoformat()}"
        )
        subject = (
            f"Action Required: {task.task_type.replace('_', ' ').title()} "
            f"overdue for {hire.full_name} "
            f"({task.overdue_hours:.0f}h late)"
        )
        sent = self._email.send(
            to=recipient,
            subject=subject,
            body=self._render_reminder_body(task, hire),
            idempotency_key=idempotency_key,
        )
        if sent:
            task.last_reminder_sent_at = now
            self._audit.log(
                action_type="REMINDER_SENT",
                hire_id=hire.hire_id,
                task_id=task.task_id,
                output_data={"recipient": recipient, "subject": subject},
                status="OK",
            )

    def _resolve_owner_email(self, task: Task, hire: Hire) -> Optional[str]:
        if task.owner_type == OwnerType.MANAGER:
            return hire.manager_email
        if task.owner_id:
            try:
                email = self._hris.get_employee_email(task.owner_id)
                if email:
                    return email
            except APIError:
                pass  # fall through to team alias
        return OWNER_TYPE_FALLBACK_EMAILS.get(task.owner_type)

    def _render_reminder_body(self, task: Task, hire: Hire) -> str:
        template = SOURCE_SYSTEM_DEEPLINKS.get(task.source_system)
        link = (
            template.format(task_id=task.task_id)
            if template
            else "Check your email inbox or contact hr-ops@aldridge.com"
        )
        return (
            f"Hi,\n\n"
            f"Automated reminder from HR Ops.\n\n"
            f"Task    : {task.task_type.replace('_', ' ').title()}\n"
            f"Hire    : {hire.full_name} (start: {hire.start_date})\n"
            f"Deadline: {task.deadline.strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"Status  : {task.status.value} — {task.overdue_hours:.0f}h overdue\n"
            f"View    : {link}\n\n"
            f"Please complete or update this task as soon as possible.\n\n"
            f"Questions? Contact hr-ops@aldridge.com\n\n"
            f"— HR Ops (Automated)"
        )

    # ── Activity 5: Monitor I-9 Compliance ───────────────────────────────────

    def monitor_i9_compliance(
        self, hire: Hire, tasks: list[Task], now: datetime
    ) -> None:
        """Mandatory I-9 escalation on Day 2 (AT_RISK) and Day 3+ (VIOLATION).

        Runs on the 2-hour polling cycle — NOT daily.  A daily cycle risks
        missing the 15-minute SLA if the poll window misses the hire's start hour.

        Idempotent: escalation is only created once per hire per type.
        No discretion: these escalations fire regardless of any other state.
        """
        if hire.status.value != "ONBOARDING":
            return

        i9_task = next(
            (t for t in tasks if t.task_type == "I9_VERIFICATION"), None
        )
        if i9_task is None or i9_task.status == TaskStatus.COMPLETE:
            return

        start = datetime(
            hire.start_date.year,
            hire.start_date.month,
            hire.start_date.day,
            tzinfo=timezone.utc,
        )
        days_since = (now - start).days

        if days_since >= 3:
            if not self._escalation_exists(hire.hire_id, EscalationType.I9_VIOLATION):
                self._create_escalation(
                    hire_id=hire.hire_id,
                    esc_type=EscalationType.I9_VIOLATION,
                    message=(
                        f"I-9 not complete {days_since} days after start date for "
                        f"{hire.full_name}. FEDERAL VIOLATION — immediate legal "
                        f"action required."
                    ),
                )
        elif days_since == 2:
            if not self._escalation_exists(hire.hire_id, EscalationType.I9_AT_RISK):
                self._create_escalation(
                    hire_id=hire.hire_id,
                    esc_type=EscalationType.I9_AT_RISK,
                    message=(
                        f"I-9 not complete on Day 2 for {hire.full_name}. "
                        f"Federal deadline is Day 3. Immediate contact required."
                    ),
                )

    # ── Activity 6: Auto-Submit IT Provisioning ───────────────────────────────

    def auto_submit_it_provisioning(
        self, hire: Hire, tasks: list[Task], now: datetime
    ) -> None:
        """Submit IT provisioning request when role is found in access matrix.

        Role lookup uses role.strip().lower() to handle capitalisation variants.
        If role is not in matrix → escalate ROLE_NOT_MAPPED; never guess.
        If already submitted for this hire → skip (idempotent).
        """
        it_task = next(
            (
                t for t in tasks
                if t.task_type == "IT_PROVISIONING_REQUESTED"
                and t.status == TaskStatus.PENDING
            ),
            None,
        )
        if it_task is None or hire.hire_id in self._it_requests:
            return

        role_key = hire.role.strip().lower()
        package = IT_ACCESS_MATRIX.get(role_key)

        if not package:
            if not self._escalation_exists(hire.hire_id, EscalationType.ROLE_NOT_MAPPED):
                self._create_escalation(
                    hire_id=hire.hire_id,
                    esc_type=EscalationType.ROLE_NOT_MAPPED,
                    message=(
                        f"Role '{hire.role}' not found in IT access matrix for "
                        f"{hire.full_name}. IT Manager must map role or approve "
                        f"manual access package."
                    ),
                )
            return

        req = ITProvisioningRequest(
            request_id=f"ITRQ-{hire.hire_id}-{now.strftime('%Y%m%d')}",
            hire_id=hire.hire_id,
            role=hire.role,
            access_package_id=package["access_package_id"],
            access_package_name=package["package_name"],
            requested_by="ai-agent",
            requested_at=now,
        )
        try:
            external_id = self._it.submit_request(req)
            req.external_request_id = external_id
            self._it_requests[hire.hire_id] = req
            self._audit.log(
                action_type="IT_PROVISIONING_SUBMITTED",
                hire_id=hire.hire_id,
                output_data={
                    "request_id": req.request_id,
                    "package": package["package_name"],
                    "external_id": external_id,
                },
                status="OK",
            )
        except APIError as exc:
            self._audit.log(
                action_type="IT_PROVISIONING_FAILED",
                hire_id=hire.hire_id,
                status="ERROR",
                error=str(exc),
            )
            if exc.status_code >= 400:
                self._create_escalation(
                    hire_id=hire.hire_id,
                    esc_type=EscalationType.ROLE_NOT_MAPPED,
                    message=(
                        f"IT provisioning API rejected request for {hire.full_name}: "
                        f"{exc}"
                    ),
                )

    # ── Activity 7: Manager Handoff Notification ──────────────────────────────

    def check_manager_handoff(
        self, hire: Hire, tasks: list[Task], now: datetime
    ) -> None:
        """Send handoff email when all PRE_DAY_1 tasks are terminal OR Day -2 arrives.

        all_tasks_complete: status IN [COMPLETE, SKIPPED].
        SKIPPED counts as terminal — contractors have legitimately N/A tasks
        (e.g. I-9 not required for some contractor types).

        Idempotent: sends exactly once per hire.
        """
        if hire.hire_id in self._handoffs_sent:
            return

        pre_day1 = [t for t in tasks if t.category == "PRE_DAY_1"]
        if not pre_day1:
            return

        all_done = all(t.is_terminal for t in pre_day1)
        day_minus_2 = datetime(
            hire.start_date.year,
            hire.start_date.month,
            hire.start_date.day,
            tzinfo=timezone.utc,
        ) - timedelta(days=2)

        if not (all_done or now >= day_minus_2):
            return

        incomplete = [t for t in pre_day1 if not t.is_terminal]
        trigger = "ALL_COMPLETE" if all_done else "DAY_MINUS_2"

        sent = self._email.send(
            to=hire.manager_email,
            subject=(
                f"Day 1 Readiness — {hire.full_name} starts "
                f"{hire.start_date.strftime('%d %b %Y')}"
            ),
            body=self._render_handoff_body(hire, pre_day1, incomplete),
            idempotency_key=f"handoff:{hire.hire_id}",
        )
        if sent:
            self._handoffs_sent.add(hire.hire_id)
            self._audit.log(
                action_type="MANAGER_HANDOFF_SENT",
                hire_id=hire.hire_id,
                output_data={
                    "manager_email": hire.manager_email,
                    "incomplete_count": len(incomplete),
                    "triggered_by": trigger,
                },
                status="OK",
            )

    def _render_handoff_body(
        self, hire: Hire, all_tasks: list[Task], incomplete: list[Task]
    ) -> str:
        done_count = len(all_tasks) - len(incomplete)
        lines = [
            f"Hi {hire.manager_id},\n",
            f"Day 1 readiness summary for {hire.full_name} "
            f"(start: {hire.start_date}).\n",
            f"✓ {done_count} of {len(all_tasks)} pre-Day-1 tasks complete.\n",
        ]
        if incomplete:
            lines.append(f"\n⚠  {len(incomplete)} task(s) outstanding:\n")
            for t in incomplete:
                lines.append(
                    f"   • {t.task_type.replace('_', ' ').title()} "
                    f"(due {t.deadline.strftime('%d %b')})"
                )
        else:
            lines.append("\n✓ All tasks complete — your new hire is ready for Day 1.")
        lines.append(
            "\n\nContact hr-ops@aldridge.com if you need support."
            "\n\n— HR Ops (Automated)"
        )
        return "\n".join(lines)

    # ── Activity 8: Escalation Routing ───────────────────────────────────────

    def _create_escalation(
        self,
        hire_id: str,
        esc_type: EscalationType,
        message: str,
    ) -> Escalation:
        routing = ESCALATION_ROUTING[esc_type]
        esc = Escalation(
            escalation_id=f"ESC-{hire_id}-{uuid.uuid4().hex[:8]}",
            hire_id=hire_id,
            escalation_type=esc_type,
            severity=routing["severity"],
            route_to=routing["route_to"],
            route_to_emails=list(routing["emails"]),
            message=message,
            created_at=datetime.now(timezone.utc),
        )
        self._escalations.append(esc)
        self._dispatch_escalation(esc, routing["channels"])
        self._audit.log(
            action_type="ESCALATION_CREATED",
            hire_id=hire_id,
            output_data={
                "type": esc_type.value,
                "severity": esc.severity.value,
                "recipients": esc.route_to,
            },
            status="OK",
        )
        return esc

    def _dispatch_escalation(self, esc: Escalation, channels: list[str]) -> None:
        subject = (
            f"[{esc.severity.value}] {esc.escalation_type.value} — "
            f"Hire {esc.hire_id}"
        )
        if "email" in channels and esc.route_to_emails:
            self._email.send(
                to=esc.route_to_emails,
                subject=subject,
                body=esc.message,
                idempotency_key=f"esc-email:{esc.escalation_id}",
            )
        if "sms" in channels:
            for addr in esc.route_to_emails:
                self._email.send_sms(
                    to_number=addr,
                    message=f"{subject}: {esc.message[:100]}",
                )
        if "phone" in channels:
            logger.critical(
                "CRITICAL escalation — manual phone call required: %s", esc.message
            )

    def _escalation_exists(
        self, hire_id: str, esc_type: EscalationType
    ) -> bool:
        """Idempotency guard: returns True if an open escalation of this type
        already exists for this hire, preventing alert flooding across poll cycles."""
        return any(
            e.hire_id == hire_id
            and e.escalation_type == esc_type
            and e.status == EscalationStatus.OPEN
            for e in self._escalations
        )

    # ── Activity 9: Audit (delegated to AuditLogger injected at __init__) ────

    # ── Main Poll Cycle ───────────────────────────────────────────────────────

    def run_cycle(
        self,
        now: Optional[datetime] = None,
        task_types: Optional[list[TaskType]] = None,
    ) -> None:
        """One full poll cycle across all active hires.

        Runs every POLL_INTERVAL_HOURS (2h). Catches per-hire exceptions so
        one bad hire record doesn't block the rest of the batch.
        """
        now = now or datetime.now(timezone.utc)
        task_types = task_types or []

        try:
            active_hires = self._hris.get_active_hires()
        except Exception as exc:
            logger.error("Failed to fetch active hires: %s", exc)
            return

        for hire in active_hires:
            if hire.status.value != "ONBOARDING":
                continue
            try:
                self._process_hire(hire, now, task_types)
            except Exception as exc:
                logger.error(
                    "Unhandled error processing hire %s: %s",
                    hire.hire_id, exc, exc_info=True,
                )

    def _process_hire(
        self, hire: Hire, now: datetime, task_types: list[TaskType]
    ) -> None:
        tasks = self.poll_task_status(hire)
        if not tasks:
            return

        overdue = self.detect_overdue(tasks, now)
        self.send_reminders(overdue, hire, now)
        self.monitor_i9_compliance(hire, tasks, now)
        self.auto_submit_it_provisioning(hire, tasks, now)
        self.check_manager_handoff(hire, tasks, now)

        # Escalate tasks overdue > 72h
        for task in overdue:
            if task.overdue_hours >= OVERDUE_ESCALATION_HOURS:
                if not self._escalation_exists(hire.hire_id, EscalationType.TASK_OVERDUE_72H):
                    self._create_escalation(
                        hire_id=hire.hire_id,
                        esc_type=EscalationType.TASK_OVERDUE_72H,
                        message=(
                            f"Task {task.task_type} for {hire.full_name} is "
                            f"{task.overdue_hours:.0f}h overdue. Immediate action required."
                        ),
                    )

        # Escalate tasks blocked > 24h
        for task in tasks:
            if (
                task.status == TaskStatus.BLOCKED
                and task.blocked_reason
                and (now - task.data_freshness).total_seconds() > 24 * 3600
            ):
                if not self._escalation_exists(
                    hire.hire_id, EscalationType.TASK_BLOCKED_UNRESOLVED
                ):
                    self._create_escalation(
                        hire_id=hire.hire_id,
                        esc_type=EscalationType.TASK_BLOCKED_UNRESOLVED,
                        message=(
                            f"Task {task.task_type} for {hire.full_name} blocked "
                            f">24h. Reason: {task.blocked_reason}"
                        ),
                    )
