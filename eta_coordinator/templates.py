"""Reply message templates for all closed-path resolution types.

All templates are derived from Section 2.1 and Section 3.2 of the spec.
Each render_*() function returns a plain-text string suitable for SMS, app,
or email (caller applies channel-specific formatting if needed).

No template contains personalisation beyond what is in the consignment record —
customer name lookup is not specified in the spec and is not added here.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from config import FALLBACK_WINDOW_LABEL
from models import ConsignmentRecord


def render_delivered(record: ConsignmentRecord) -> str:
    """Status = delivered. Returns delivery time + signature name.

    Spec Section 2.1: 'Delivered at [time], signed by [name]'
    """
    delivered_at = (
        record.delivered_at.strftime("%H:%M on %d %b %Y")
        if record.delivered_at
        else "earlier today"
    )
    signature = record.signature_name or "recipient"
    return (
        f"Your consignment {record.consignment_id} was delivered at {delivered_at}, "
        f"signed by {signature}. "
        f"If you have any concerns please contact our support team."
    )


def render_pre_dispatch(record: ConsignmentRecord) -> str:
    """Status = pre-dispatch. Returns next-day departure + window.

    Spec Section 2.1: 'Departing tomorrow 08:00. Will arrive by [next-day window]'
    Window is taken from the scheduled fields on the record if available,
    otherwise the generic next-day message is used.
    """
    if record.scheduled_window_start and record.scheduled_window_end:
        window = (
            f"{record.scheduled_window_start.strftime('%H:%M')}–"
            f"{record.scheduled_window_end.strftime('%H:%M')}"
        )
        return (
            f"Your consignment {record.consignment_id} has not yet left our warehouse. "
            f"It is scheduled to depart tomorrow at 08:00 and arrive between {window}."
        )
    return (
        f"Your consignment {record.consignment_id} has not yet left our warehouse. "
        f"It is scheduled to depart tomorrow at 08:00. "
        f"You will receive an update once it is out for delivery."
    )


def render_exception(record: ConsignmentRecord) -> str:
    """Status = exception. Returns exception reason + next steps.

    Spec Section 2.1: 'Reply with exception reason; route to dispatcher queue'
    """
    reason = record.exception_reason or "an issue requiring attention"
    return (
        f"We were unable to complete delivery of consignment {record.consignment_id} "
        f"due to {reason}. "
        f"A member of our team will contact you shortly to arrange a resolution. "
        f"We apologise for the inconvenience."
    )


def render_eta_driver_response(
    record: ConsignmentRecord,
    eta_datetime: datetime,
) -> str:
    """Driver responded in time; tight ETA window available.

    Spec Section 2.2: 'Calculate ETA from driver location + stops remaining + travel time'
    The eta_datetime is the calculated arrival time passed in from the orchestrator.
    """
    eta_str = eta_datetime.strftime("%H:%M")
    return (
        f"Your consignment {record.consignment_id} is currently out for delivery. "
        f"Based on your driver's current location, estimated arrival is around {eta_str}. "
        f"Your driver will call approximately 30 minutes before arrival."
    )


def render_eta_fallback(
    record: ConsignmentRecord,
    driver_confirmed: bool = False,
) -> str:
    """Driver did not respond in time, or MSG mode: fallback window used.

    Spec Section 2.2:
    - driver_confirmed=False: driver non-responsive; standard fallback.
    - driver_confirmed=True: MSG mode — driver replied but no GPS; treat as
      confirmation delivery is proceeding. Adds "Driver has confirmed your
      delivery is on track." per Section 2.2 MSG mode rule.
    Uses FALLBACK_WINDOW_LABEL from config (13:00–17:00).
    """
    on_track_note = (
        "Your driver has confirmed your delivery is on track. "
        if driver_confirmed
        else ""
    )
    return (
        f"Your consignment {record.consignment_id} is currently out for delivery. "
        f"{on_track_note}"
        f"Best estimate: delivery this {FALLBACK_WINDOW_LABEL}. "
        f"Your driver will call approximately 30 minutes before arrival. "
        f"Note: delivery status may be a few minutes behind actual progress."
    )


def render_not_found(raw_consignment_id: str) -> str:
    """Consignment not found in CRM.

    Spec Section 2.3: 'may not be scanned yet; checking manually'
    """
    return (
        f"We could not locate consignment {raw_consignment_id} in our system. "
        f"This may mean it has not yet been scanned into our network. "
        f"We are checking manually and will update you shortly."
    )


def render_null_status(consignment_id: str) -> str:
    """CRM status is null/missing — data error path.

    Spec Section 2.3: agent flags for human investigation.
    """
    return (
        f"We are currently unable to retrieve the status of consignment {consignment_id}. "
        f"Our team has been notified and will investigate immediately. "
        f"We apologise for the inconvenience and will update you as soon as possible."
    )


def render_invalid_id(raw_id: str) -> str:
    """Consignment ID failed format validation — escalated path."""
    return (
        f"We were unable to find a consignment matching the reference '{raw_id}'. "
        f"Please double-check the reference number on your delivery notification "
        f"and try again, or contact our support team for assistance."
    )


def render_crm_unavailable(raw_consignment_id: str) -> str:
    """CRM API is down — failover path.

    Spec Section 3.1: 'Route to manual inquiry queue'
    """
    return (
        f"We are experiencing a temporary system issue and cannot retrieve the status "
        f"of consignment {raw_consignment_id} right now. "
        f"A member of our team will look into this and contact you as soon as possible. "
        f"We apologise for the inconvenience."
    )
