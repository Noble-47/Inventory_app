from shared import get_rotating_logger

logger = get_rotating_logger("exchange-shopify", "exchange.log")


def initialize_hub(hub):
    logger.info("[x] Initializing shopify exchange...")
    exchange = hub.create_exchange("shopify")

    exchange.establish_channel(
        channel="shops_notifications", subjects=["new_shop_added", "shop_removed"]
    )

    exchange.establish_channel(
        channel="settings_notifications",
        subjects=[
            "inventory_setting_update",
            "sales_setting_updates",
            "tracker_setting_updates",
            "order_setting_updates",
        ],
    )
    logger.info("Done")
