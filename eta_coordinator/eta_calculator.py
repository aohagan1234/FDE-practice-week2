"""ETA calculation from driver location data.

This module handles the GPS branch of the driver contact flow (Section 2.2).
The core calculation formula:
    ETA = now + travel_time(driver_location → delivery_address) + (stops_remaining × avg_stop_duration)

STUB Q4: Three constants in config.py must be confirmed with Apex Distribution
before this module can be fully implemented:
  - AVG_STOP_DURATION_MINUTES
  - ROUTING_API_PROVIDER
  - STOPS_REMAINING_UNIT

The calculate_eta() function returns a datetime if it can produce one, or None
if the input data is insufficient (caller falls back to fallback window).
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from config import AVG_STOP_DURATION_MINUTES, ROUTING_API_PROVIDER
from models import ConsignmentRecord, DriverLocation

logger = logging.getLogger(__name__)


def calculate_eta(
    driver: DriverLocation,
    record: ConsignmentRecord,
    now: Optional[datetime] = None,
) -> Optional[datetime]:
    """Calculate estimated arrival time from driver location data.

    Returns the estimated arrival datetime, or None if calculation is not possible
    (e.g. missing GPS coordinates, routing API unavailable).

    STUB Q4: travel_time_minutes is a stub. Replace _get_travel_time_minutes()
    with a real routing API call (Google Maps Directions, HERE, or internal).

    STUB Q4: stops_remaining interpretation (consignment count vs route waypoint)
    affects accuracy. Confirm STOPS_REMAINING_UNIT before deploying.
    """
    now = now or datetime.now(timezone.utc)

    if driver.latitude is None or driver.longitude is None:
        # GPS branch — coordinates missing, cannot calculate
        logger.warning(
            "calculate_eta: driver %s has no GPS coordinates; returning None",
            driver.driver_id,
        )
        return None

    stops = driver.stops_remaining or 0

    travel_minutes = _get_travel_time_minutes(
        origin_lat=driver.latitude,
        origin_lng=driver.longitude,
        delivery_address=record.delivery_address,
    )
    if travel_minutes is None:
        logger.warning(
            "calculate_eta: routing API returned None for driver %s; returning None",
            driver.driver_id,
        )
        return None

    stop_buffer_minutes = stops * AVG_STOP_DURATION_MINUTES
    total_minutes = travel_minutes + stop_buffer_minutes

    eta = now + timedelta(minutes=total_minutes)
    logger.debug(
        "calculate_eta: driver=%s travel=%dm stops=%d×%dm total=%dm eta=%s",
        driver.driver_id,
        travel_minutes,
        stops,
        AVG_STOP_DURATION_MINUTES,
        total_minutes,
        eta.isoformat(),
    )
    return eta


def _get_travel_time_minutes(
    origin_lat: float,
    origin_lng: float,
    delivery_address: str,
) -> Optional[int]:
    """Return estimated driving time in minutes from origin to delivery address.

    STUB Q4: Replace with real routing API call.
    Provider options (set ROUTING_API_PROVIDER in config.py):
      'google_maps' → Google Maps Directions API
          GET https://maps.googleapis.com/maps/api/directions/json
          ?origin={lat},{lng}&destination={address}&mode=driving&key={API_KEY}
          Parse: routes[0].legs[0].duration.value (seconds) / 60
      'here'        → HERE Routing v8 API
      'internal'    → Apex internal routing service (endpoint unknown — confirm with IT)

    Returns None if the routing call fails (caller falls back to fallback window).
    """
    if ROUTING_API_PROVIDER == "STUB":
        logger.warning(
            "_get_travel_time_minutes: ROUTING_API_PROVIDER is STUB (Q4 not resolved). "
            "Returning None — caller will use fallback window."
        )
        return None

    raise NotImplementedError(
        f"STUB Q4: Implement routing API call for provider '{ROUTING_API_PROVIDER}'. "
        "See docstring for endpoint details."
    )
