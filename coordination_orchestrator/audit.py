"""Structured audit logger.

Every agent action is written here. In production, replace _write
with an INSERT into your audit DB table. The schema matches Section 7
of the Agent Purpose Document.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


class AuditLogger:
    def log(
        self,
        action_type: str,
        status: str,
        hire_id: Optional[str] = None,
        task_id: Optional[str] = None,
        input_data: Optional[dict] = None,
        output_data: Optional[dict] = None,
        error: Optional[str] = None,
    ) -> None:
        entry = {
            "action_type": action_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "hire_id": hire_id,
            "task_id": task_id,
            "input_data": input_data or {},
            "output_data": output_data or {},
            "error": error,
        }
        self._write(entry)

    def _write(self, entry: dict) -> None:
        logger.info("AUDIT %s", json.dumps(entry))
        # Production: INSERT INTO audit_log (action_type, timestamp, ...) VALUES (...)
