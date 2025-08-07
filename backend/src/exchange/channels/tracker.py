from datetime import datetime
from shared import TIMEZONE

from debt_tracker.domain import commands
from debt_tracker.handlers import handle
from shared import get_rotating_logger
from debt_tracker import utils

logger = get_rotating_logger("exchange-tracker", "exchange.log")


def create_record(**kwargs):
    logger.info("[TRA] Creating new inventory")
    command = commands.CreateRecord(shop_id=kwargs["shop_id"])
    handle(command)


def delete_record(**kwargs):
    logger.info("[TRA] Removing inventory record")
    shop_id = kwargs["shop_id"]
    command = commands.DeleteRecord(shop_id=shop_id)
    handle(command)


def check_payment_for_deficit(**kwargs):
    logger.info("[TRA] Checking sale record for payment deficit")
    command = commands.RecordDebt(
        shop_id=kwargs["shop_id"],
        sale_ref=kwargs["sale_ref"],
        selling_price=kwargs["selling_price"],
        amount_paid=kwargs["amount_paid"],
        firstname=kwargs["firstname"],
        lastname=kwargs["lastname"],
        phone=kwargs["customer_phone"],
    )
    handle(command)


def update_debtor_info(firstname, lastname, phone, shop_id, new_phone):
    command = commands.UpdateDebtorInfo(
        firstname=firstname,
        lastname=lastname,
        phone=phone,
        shop_id=shop_id,
        new_phone=new_phone,
    )
    handle(command)

    handle(cmd)


def update_handler(**kwargs):
    logger.info("[TRA] Processing update")
    shop_id = kwargs["shop_id"]
    sale_ref = kwargs["sale_ref"]
    selling_price = kwargs["selling_price"]
    amount_paid = kwargs["amount_paid"]
    if selling_price or amount_paid:
        logger.info("processing debt info")
        if utils.debt_exists(shop_id=shop_id, sale_ref=sale_ref):
            cmd = commands.UpdateDebtInfo(
                sale_ref=sale_ref,
                shop_id=shop_id,
                selling_price=selling_price,
                amount_paid=amount_paid,
            )
        else:
            cmd = commands.RecordDebt(
                shop_id=shop_id,
                sale_ref=sale_ref,
                firstname=kwargs["firstname"],
                lastname=kwargs["lastname"],
                phone=kwargs["customer_phone"],
                selling_price=kwargs["selling_price"],
                amount_paid=kwargs["amount_paid"],
            )
        handle(cmd)


def initialize_hub(hub):
    logger.info("[x] Initializing tracker exchange")
    exchange = hub.create_exchange("tracker")

    exchange.establish_channel(
        channel="tracker_notifications",
        subjects=[
            "attention",
            "new_debt",
            "debtor_info_update",
            "debt_cleared",
            "payment_received",
        ],
    )

    exchange.listen_on(subject="new_shop_added", handler=create_record)

    exchange.listen_on(subject="shop_removed", handler=delete_record)

    exchange.listen_on(subject="new_sale", handler=check_payment_for_deficit)

    exchange.listen_on(subject="sale_update", handler=update_handler)

    # exchange.listen_on(
    #    subject="tracker_setting_update", handler=update_inventory_setting
    # )
    logger.info("...Done.")
