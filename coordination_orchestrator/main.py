"""Entry point for the Coordination Orchestrator.

Run with:
    python main.py

The process polls all active ONBOARDING hires every POLL_INTERVAL_HOURS (2h),
running all 9 activities per cycle. Replace the NotImplementedError stubs in
api_clients.py with real HTTP calls before deploying.
"""
import logging
import time

from api_clients import (
    CalendarClient,
    EmailClient,
    FulfillmentClient,
    HRISClient,
    ITProvisioningClient,
    LMSClient,
)
from audit import AuditLogger
from config import POLL_INTERVAL_HOURS
from orchestrator import CoordinationOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def build_orchestrator() -> CoordinationOrchestrator:
    return CoordinationOrchestrator(
        hris=HRISClient(),
        it_provisioning=ITProvisioningClient(),
        lms=LMSClient(),
        calendar=CalendarClient(),
        fulfillment=FulfillmentClient(),
        email=EmailClient(),
        audit=AuditLogger(),
    )


def main() -> None:
    orchestrator = build_orchestrator()
    interval_seconds = POLL_INTERVAL_HOURS * 3600

    logger.info(
        "Coordination Orchestrator started — polling every %dh", POLL_INTERVAL_HOURS
    )
    while True:
        logger.info("─── Poll cycle starting ───")
        orchestrator.run_cycle()
        logger.info("─── Poll cycle complete; sleeping %dh ───", POLL_INTERVAL_HOURS)
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
