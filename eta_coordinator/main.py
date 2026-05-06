"""Entry point for the Coordinator ETA agent.

In production this process is event-driven (each incoming inquiry triggers
handle_inquiry() via a message queue or webhook), not poll-based.

For development/testing: a minimal HTTP shim or CLI loop can be added here.

Before deploying:
  1. Replace all NotImplementedError stubs in api_clients.py with real
     HTTP calls for CRMClient, ReplyGatewayClient, and DriverAppClient.
  2. Set DRIVER_APP_CAPABILITY in config.py (resolve STUB Q1).
  3. Set REPLY_GATEWAY in config.py (resolve STUB Q2).
  4. Confirm VIP_CRM_FIELD_NAME in config.py (resolve STUB Q3).
  5. Confirm AVG_STOP_DURATION_MINUTES and ROUTING_API_PROVIDER in config.py
     (resolve STUB Q4) if GPS capability is available.
  6. Replace InquiryCache with Redis (or equivalent) for multi-instance safety.
  7. Replace ETAAuditLogger._write() with DB insert or observability platform call.
"""
import logging

from api_clients import CRMClient, DriverAppClient, ReplyGatewayClient
from audit import ETAAuditLogger
from cache import InquiryCache
from orchestrator import ETACoordinator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def build_coordinator() -> ETACoordinator:
    return ETACoordinator(
        crm=CRMClient(),
        driver_app=DriverAppClient(),
        reply_gateway=ReplyGatewayClient(),
        audit=ETAAuditLogger(),
        cache=InquiryCache(),
    )


def main() -> None:
    coordinator = build_coordinator()
    logger.info("Coordinator ETA agent started — awaiting inquiries")
    # Production: subscribe to message queue / webhook here
    # e.g.: consumer.subscribe(topic="eta_inquiries", callback=coordinator.handle_inquiry)


if __name__ == "__main__":
    main()
