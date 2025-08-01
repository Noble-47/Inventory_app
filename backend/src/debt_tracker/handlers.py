from uuid import UUID

from exchange import hub
from debt_tracker.db import DB
from debt_tracker.domain import messages
from debt_tracker.domain import events
from debt_tracker.domain import commands

from debt_tracker.domain.models import manual_ref_generator


def record_debt(cmd: commands.RecordDebt, db):
    if cmd.amount_paid >= cmd.selling_price:
        return
    with db:
        debtor = db.debtors.add(
            shop_id=cmd.shop_id,
            phone=cmd.phone,
            firstname=cmd.firstname,
            lastname=cmd.lastname,
        )
        debt = db.debts.add(
            shop_id=cmd.shop_id,
            debtor=debtor,
            phone=debtor.phone,
            amount_paid=cmd.amount_paid,
            selling_price=cmd.selling_price,
            sale_ref=cmd.sale_ref or manual_ref_generator(),
        )
        db.records.record_debt(cmd.shop_id, debt)
        db.commit()


def create_record(cmd: commands.CreateRecord, db):
    with db:
        db.records.create(cmd.shop_id)
        db.commit()


def delete_record(cmd: commands.CreateRecord, db):
    with db:
        db.records.delete(cmd.shop_id)
        db.commit()


def record_payment(cmd: commands.RecordPayment, db):
    with db:
        debt = db.debts.get(shop_id=cmd.shop_id, sale_ref=cmd.sale_ref)
        debt.increment_amount_paid(cmd.amount)
        db.commit()


def update_debtor_info(cmd: commands.UpdateDebtorInfo, db):
    with db:
        debtor = db.debtors.get(shop_id, phone, firstname, lastname, trigger=False)
        if debtor is None:
            return
        if cmd.firstname:
            debtor = cmd.firstname
        if cmd.lastname:
            debtor = cmd.lastname
        db.commit()


def update_debt_info(cmd: commands.UpdateDebtInfo, db):
    with db:
        debt = db.debts.get(shop_id=shop_id, sale_ref=sale_ref)
        if debt is None:
            return
        if cmd.amount_paid and debt.last_paid_date is None:
            debt.amount_paid = amount_paid
        else:
            db.events.append(
                messages.AttentionNeeded(
                    shop_id=shop_id,
                    sale_ref=sale_ref,
                    message="Conflict while updating debt's `amount_paid`",
                )
            )
        if cmd.selling_price:
            debt.selling_price = selling_price
            if debt.amount_paid >= selling_price:
                debt.cleared = True
        db.commit()


def waive_debt(cmd: commands.WaiveDebt, db):
    with db:
        debt = db.debts.get(shop_id=cmd.shop_id, sale_ref=cmd.sale_ref)
        debt.waive()
        db.commit()


def log_event(event: events.Event, db):
    with db:
        db.audit.add(event)
        db.commit()


def publish_payment(event: events.PaymentReceived, db):
    hub.publish("tracker_notifications", "payment_received", event.json())


def publish_debt_cleared(event: events.DebtCleared, db):
    hub.publish("tracker_notifications", "debt_cleared", event.json())


def publish_new_debt(event: events.NewDebt, db):
    hub.publish("tracker_notifications", "new_debt", event.json())


def publish_info_mismatch(message: messages.InfoMismatch, db):
    hub.publish("tracker_notifications", "debtor_info_mismatch", message.json())


def publish_attention_needed(message: messages.AttentionNeeded, db):
    hub.publish("tracker_notifications", "attention", message.json())


command_handlers = {
    commands.CreateRecord: [create_record],
    commands.DeleteRecord: [delete_record],
    commands.WaiveDebt: [waive_debt],
    commands.RecordPayment: [record_payment],
    commands.RecordDebt: [record_debt],
    commands.UpdateDebtInfo: [update_debt_info],
    commands.UpdateDebtorInfo: [update_debtor_info],
}

event_handlers = {
    events.NewDebt: [log_event, publish_new_debt],
    events.PaymentReceived: [log_event, publish_payment],
    events.DebtCleared: [log_event, publish_debt_cleared],
    messages.InfoMismatch: [publish_info_mismatch],
    messages.AttentionNeeded: [publish_attention_needed],
}


def handle(message):
    db = DB()
    for handler in command_handlers.get(type(message), []):
        handler(message, db)
    for event in db.collect_events():
        for handler in event_handlers.get(type(event), []):
            handler(event, db)
