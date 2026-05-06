"""Structured audit logger for the Coordinator ETA agent.

Every inquiry resolution — success or failure — is written here.
In production, replace _write() with an INSERT into your audit DB table or
a POST to your observability platform (e.g. Datadog, Splunk).

Fields written per the spec (Section 7): resolution type, timing, driver response.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from models import AuditEntry

logger = logging.getLogger(__name__)


class ETAAuditLogger:

    def log_resolution(
        self,
        inquiry_id: str,
        consignment_id: str,
        customer_id: str,
        channel: str,
        resolution_type: str,
        is_escalated: bool,
        duration_seconds: float,
        driver_responded: Optional[bool] = None,
        crm_status_at_query: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        """Write one audit record for a completed inquiry handling cycle."""
        entry = AuditEntry(
            inquiry_id=inquiry_id,
            consignment_id=consignment_id,
            customer_id=customer_id,
            channel=channel,
            resolution_type=resolution_type,
            is_escalated=is_escalated,
            driver_responded=driver_responded,
            crm_status_at_query=crm_status_at_query,
            duration_seconds=duration_seconds,
            timestamp=datetime.now(timezone.utc),
            error=error,
        )
        self._write(entry)

    def _write(self, entry: AuditEntry) -> None:
        record = {
            "inquiry_id": entry.inquiry_id,
            "consignment_id": entry.consignment_id,
            "customer_id": entry.customer_id,
            "channel": entry.channel,
            "resolution_type": entry.resolution_type,
            "is_escalated": entry.is_escalated,
            "driver_responded": entry.driver_responded,
            "crm_status_at_query": entry.crm_status_at_query,
            "duration_seconds": round(entry.duration_seconds, 3),
            "timestamp": entry.timestamp.isoformat(),
            "error": entry.error,
        }
        logger.info("ETA_AUDIT %s", json.dumps(record))
        # Production: INSERT INTO eta_inquiry_audit (...) VALUES (...)
        # or: requests.post(OBSERVABILITY_ENDPOINT, json=record)
