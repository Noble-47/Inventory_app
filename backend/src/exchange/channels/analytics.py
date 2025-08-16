from uuid import UUID
import json

from shared import get_rotating_logger
from analytics.analytics import (
    update_shop_report,
    create_shop_report,
    delete_shop_report,
)

logger = get_rotating_logger("exchange-sales", "exchange.log")


def update_handler(**kwargs):
    logger.info("[ANLYX] Updating shop analytic report")
    shop_id = UUID(kwargs["shop_id"])
    update_shop_report(shop_id)


def create_record(**kwargs):
    logger.info("[ANLYX] Creating inventory record.")
    shop_id = kwargs["shop_id"]
    create_shop_report(shop_id)


def delete_record(**kwargs):
    logger.info("[ANLYX] Deleting inventory record.")
    shop_id = kwargs["shop_id"]
    delete_shop_report(shop_id)


def initialize_hub(hub):
    logger.info("[x] Initializing analytics exchange...")
    exchange = hub.create_exchange("analytics")

    exchange.establish_channel(channel="analytics", subjects=["update_request"])

    exchange.listen_on(subject="new_shop_added", handler=create_record)

    exchange.listen_on(subject="shop_removed", handler=delete_record)

    exchange.listen_on(subject="update_request", handler=update_handler)

    logger.info("Done...")
