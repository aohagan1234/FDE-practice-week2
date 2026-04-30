"""API client stubs for all 6 source systems.

Each client exposes the interface the orchestrator needs. Replace
NotImplementedError bodies with real HTTP calls for the target system.
Retry logic lives in BaseAPIClient._request_with_retry.
"""
from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from typing import Optional

from models import Hire, Task, TaskStatus

logger = logging.getLogger(__name__)


class APIError(Exception):
    def __init__(self, system: str, status_code: int, message: str) -> None:
        self.system = system
        self.status_code = status_code
        super().__init__(f"[{system}] HTTP {status_code}: {message}")


class BaseAPIClient(ABC):
    system_name: str

    def _request_with_retry(self, fn, max_retries: int = 3, base_wait: int = 5):
        """Retry with exponential backoff on 5xx errors."""
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


class HRISClient(BaseAPIClient):
    """Fetch hire records, tasks, and employee details.

    Production endpoints:
      GET /hrh-list-hires?status=onboarding   → list[Hire]
      GET /hrh-get-hire?hire_id={id}           → Hire
      GET /tasks?hire_id={id}                  → list[Task]
      GET /emp-get?emp_id={id}                 → {email: str}

    Auth: OAuth 2.0 client-credentials (Bearer token)
    Rate limit: 1,000 req/hr   SLA: 99.9%
    Fallback: daily batch file export from HRIS
    """
    system_name = "HRIS"

    def get_active_hires(self) -> list[Hire]:
        raise NotImplementedError

    def get_hire(self, hire_id: str) -> Hire:
        raise NotImplementedError

    def get_tasks_for_hire(self, hire_id: str) -> list[Task]:
        raise NotImplementedError

    def get_employee_email(self, employee_id: str) -> Optional[str]:
        raise NotImplementedError


class ITProvisioningClient(BaseAPIClient):
    """Submit and poll IT access provisioning requests.

    Production endpoints:
      POST /provisioning-requests               → {external_request_id: str}
      GET  /provisioning-requests/{id}          → {status: str}
      GET  /roles/{role_normalized}/access-package → {access_package_id, package_name}

    Auth: API key (header X-API-Key)
    Rate limit: 500 req/hr   SLA: 99.5%
    Fallback: manual IT ticket via email to it-support@aldridge.com
    """
    system_name = "IT_PROVISIONING"

    def submit_request(self, request) -> str:
        """Returns external_request_id."""
        raise NotImplementedError

    def get_request_status(self, external_request_id: str) -> str:
        raise NotImplementedError


class LMSClient(BaseAPIClient):
    """Fetch compliance training enrollment status via SOAP (legacy).

    Wraps SOAP response into TaskStatus enum.
    Rate limit: 100 req/hr   SLA: 98%
    Fallback: weekly batch export
    """
    system_name = "LMS"

    def get_task_status(self, task_id: str) -> TaskStatus:
        raise NotImplementedError


class CalendarClient(BaseAPIClient):
    """Check availability and create calendar events via CalDAV.

    Rate limit: 1,000 req/day   SLA: 99%
    Fallback: manual scheduling via HR Ops
    """
    system_name = "CALENDAR"

    def get_task_status(self, task_id: str) -> TaskStatus:
        raise NotImplementedError


class FulfillmentClient(BaseAPIClient):
    """Track welcome-pack and laptop shipment status.

    Rate limit: 500 req/hr   SLA: 95%
    Fallback: manual status check via email to supplier
    """
    system_name = "FULFILLMENT"

    def get_task_status(self, task_id: str) -> TaskStatus:
        raise NotImplementedError


class EmailClient:
    """Send email via SMTP (MS Graph in production) with idempotency.

    Idempotency: caller provides a unique key; duplicate sends are silently
    suppressed.  In production the sent-key store is a DB table, not a set.

    Rate limit: 10,000 msg/day   SLA: 99.95%
    Fallback: exponential retry; SMS backup for CRITICAL escalations
    """

    def __init__(self) -> None:
        self._sent_keys: set[str] = set()

    def send(
        self,
        to: str | list[str],
        subject: str,
        body: str,
        idempotency_key: str,
    ) -> bool:
        if idempotency_key in self._sent_keys:
            logger.info("Email suppressed (duplicate key=%s)", idempotency_key)
            return True

        recipients = [to] if isinstance(to, str) else to
        logger.info("Sending email → %s | %s", recipients, subject)
        # Production: POST /users/{service_account}/messages/send (MS Graph)
        self._sent_keys.add(idempotency_key)
        return True

    def send_sms(self, to_number: str, message: str) -> bool:
        logger.info("Sending SMS → %s | %s", to_number, message[:80])
        # Production: Twilio API call
        return True
