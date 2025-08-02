from datetime import datetime
from shared import TIMEZONE

from debt_tracker.domain import commands
from debt_tracker.handlers import handle
from shared import get_rotating_logger

logger = get_rotating_logger("exchange-tracker", "exchange.log")

def create_record(**kwargs):
    logger.info(" [TRA] Creating new inventory")
    command = commands.CreateRecord(shop_id=kwargs["shop_id"])
    handle(command)


def delete_record(**kwargs):
    logger.info("     [TRA] Removing inventory record")
    shop_id = kwargs['shop_id']
    command = commands.DeleteRecord(shop_id=shop_id)
    handle(command)


def check_payment_for_deficit(**kwargs):
    logger.info("     [TRA] Checking sale record for payment deficit")
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


def update_debtor_info(firstname, lastname, phone):
    command = commands.UpdateDebtorInfo(
        firstname=firstname, lastname=lastname, phone=phone, shop_id=kwargs["shop_id"]
    )
    handle(command)


def update_debt_info(selling_price, amount_paid, sale_ref, shop_id):
    cmd = commands.UpdateDebtInfo(
        sale_ref=sale_ref,
        shop_id=shop_id,
        selling_price=selling_price,
        amount_paid=amount_paid,
    )
    handle(cmd)


def update_handler(**kwargs):
    logger.info("     [TRA] Check if update is required.")
    firstname = kwargs.get("firstname")
    lastname = kwargs.get("lastname")
    if firstname or lastname:
        phone = kwargs.get("phone")
        if phone is None:
            raise KeyError("Missing `phone` field.")
        update_debtor_info(
            firstname=firstname, lastname=lastname, phone=kwargs["phone"]
        )

    sale_ref = kwargs["sale_ref"]
    shop_id = kwargs["shop_id"]
    selling_price = kwargs.get("selling_price")
    amount_paid = kwargs.get("amount_paid")

    if selling_price or amount_paid:
        update_debtor_info(
            selling_price=selling_price,
            amount_paid=amount_paid,
            sale_ref=sale_ref,
            shop_id=shop_id,
        )


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
