from models import EscalationType, EscalationSeverity, OwnerType

# ── Polling & thresholds ──────────────────────────────────────────────────────
POLL_INTERVAL_HOURS = 2
OVERDUE_GRACE_HOURS = 24          # Remind after 24h past deadline
OVERDUE_ESCALATION_HOURS = 72    # Escalate to manager after 72h
REMINDER_RATE_LIMIT_HOURS = 24   # Max 1 reminder per task per day
SYSTEM_UNAVAILABLE_RETRY_COUNT = 3
SYSTEM_UNAVAILABLE_RETRY_WAIT_SECONDS = 300  # 5 min, exponential

# ── Escalation routing ────────────────────────────────────────────────────────
# Maps EscalationType → routing config.
# Emails tagged [] are resolved dynamically per-hire at runtime.
ESCALATION_ROUTING: dict[EscalationType, dict] = {
    EscalationType.I9_AT_RISK: {
        "severity": EscalationSeverity.HIGH,
        "route_to": ["HR_OPS_ONCALL", "HR_MANAGER"],
        "emails": ["oncall@aldridge.com", "hr-manager@aldridge.com"],
        "channels": ["email", "sms"],
        "sla_minutes": 15,
    },
    EscalationType.I9_VIOLATION: {
        "severity": EscalationSeverity.CRITICAL,
        "route_to": ["LEGAL", "CEO", "HR_MANAGER"],
        "emails": ["legal@aldridge.com", "ceo@aldridge.com", "hr-manager@aldridge.com"],
        "channels": ["email", "sms", "phone"],
        "sla_minutes": 5,
    },
    EscalationType.TASK_OVERDUE_72H: {
        "severity": EscalationSeverity.MEDIUM,
        "route_to": ["TASK_OWNER", "HR_OPS"],
        "emails": ["hr-ops@aldridge.com"],  # task-owner email appended dynamically
        "channels": ["email"],
        "sla_minutes": 120,
    },
    EscalationType.TASK_BLOCKED_UNRESOLVED: {
        "severity": EscalationSeverity.MEDIUM,
        "route_to": ["TASK_OWNER", "HR_OPS"],
        "emails": ["hr-ops@aldridge.com"],
        "channels": ["email"],
        "sla_minutes": 240,
    },
    EscalationType.ROLE_NOT_MAPPED: {
        "severity": EscalationSeverity.HIGH,
        "route_to": ["IT_MANAGER"],
        "emails": ["it-manager@aldridge.com"],
        "channels": ["email"],
        "sla_minutes": 60,
    },
    EscalationType.SYSTEM_UNAVAILABLE: {
        "severity": EscalationSeverity.MEDIUM,
        "route_to": ["IT_SUPPORT", "HR_OPS"],
        "emails": ["it-support@aldridge.com", "hr-ops@aldridge.com"],
        "channels": ["email"],
        "sla_minutes": 120,
    },
    EscalationType.NO_ELIGIBLE_BUDDY: {
        "severity": EscalationSeverity.MEDIUM,
        "route_to": ["HR_OPS", "MANAGER"],
        "emails": ["hr-ops@aldridge.com"],  # manager email appended dynamically
        "channels": ["email"],
        "sla_minutes": 240,
    },
    EscalationType.SENIORITY_GAP: {
        "severity": EscalationSeverity.LOW,
        "route_to": ["HR_OPS"],
        "emails": ["hr-ops@aldridge.com"],
        "channels": ["email"],
        "sla_minutes": 480,
    },
    EscalationType.COMPLIANCE_TRACK_UNCLEAR: {
        "severity": EscalationSeverity.MEDIUM,
        "route_to": ["HR_OPS", "COMPLIANCE"],
        "emails": ["hr-ops@aldridge.com", "compliance@aldridge.com"],
        "channels": ["email"],
        "sla_minutes": 240,
    },
    EscalationType.DEADLINE_CALC_ERROR: {
        "severity": EscalationSeverity.MEDIUM,
        "route_to": ["HR_OPS"],
        "emails": ["hr-ops@aldridge.com"],
        "channels": ["email"],
        "sla_minutes": 120,
    },
    EscalationType.DATA_INTEGRITY_ERROR: {
        "severity": EscalationSeverity.MEDIUM,
        "route_to": ["IT_SUPPORT"],
        "emails": ["it-support@aldridge.com"],
        "channels": ["email"],
        "sla_minutes": 120,
    },
}

# ── Owner type → fallback email resolution (Gap 3 fix) ───────────────────────
# Used when task.owner_id is NULL and no individual can be looked up.
# MANAGER is resolved at runtime from hire.manager_email.
# SYSTEM-owned tasks never receive reminders.
OWNER_TYPE_FALLBACK_EMAILS: dict[OwnerType, str | None] = {
    OwnerType.HR_OPS: "hr-ops@aldridge.com",
    OwnerType.IT: "it-team@aldridge.com",
    OwnerType.COMPLIANCE: "compliance@aldridge.com",
    OwnerType.SYSTEM: None,
    OwnerType.MANAGER: None,  # Always resolved from hire.manager_email
}

# ── Deep-link URL templates per source system (Gap 6 fix) ────────────────────
# {task_id} is substituted at runtime. None = no direct link available.
SOURCE_SYSTEM_DEEPLINKS: dict[str, str | None] = {
    "HRIS": "https://hris.aldridge.com/tasks/{task_id}",
    "IT_PROVISIONING": "https://it.aldridge.com/requests/{task_id}",
    "LMS": "https://lms.aldridge.com/enrollments/{task_id}",
    "CALENDAR": "https://calendar.aldridge.com/events/{task_id}",
    "EMAIL": None,
    "FULFILLMENT": "https://fulfillment.aldridge.com/orders/{task_id}",
}

# ── IT role-access matrix (Gap 5 fix) ────────────────────────────────────────
# In production this is fetched from:
#   GET https://it.aldridge.com/api/v1/roles/{role_normalized}/access-package
#   Auth: API key (header X-API-Key)
#   Rate limit: 500 req/hr
#   Refresh: IT team updates on role changes; agent re-fetches every 24h
#
# role_normalized = role.strip().lower()  (handles "Senior Consultant" == "senior consultant")
IT_ACCESS_MATRIX: dict[str, dict] = {
    "senior consultant": {
        "access_package_id": "PKG-CONSULT-SR",
        "package_name": "Senior Consultant Standard Access",
    },
    "consultant": {
        "access_package_id": "PKG-CONSULT",
        "package_name": "Consultant Standard Access",
    },
    "junior consultant": {
        "access_package_id": "PKG-CONSULT-JR",
        "package_name": "Junior Consultant Access",
    },
    "manager": {
        "access_package_id": "PKG-MANAGER",
        "package_name": "Manager Access",
    },
    "director": {
        "access_package_id": "PKG-DIRECTOR",
        "package_name": "Director Access",
    },
    "analyst": {
        "access_package_id": "PKG-ANALYST",
        "package_name": "Analyst Access",
    },
    "hr specialist": {
        "access_package_id": "PKG-HR",
        "package_name": "HR Specialist Access",
    },
    "it engineer": {
        "access_package_id": "PKG-IT-ENG",
        "package_name": "IT Engineer Access",
    },
    "contractor": {
        "access_package_id": "PKG-CONTRACTOR",
        "package_name": "Contractor Limited Access",
    },
}
