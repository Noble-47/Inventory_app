from sqlmodel import Session, select

from debt_tracker import utils as tracker_utils
from inventory import utils as inventory_utils
from stock_port import views as order_view
from sales import views as sales_view

from exchange import hub
from analytics import config
from analytics.db import engine
from analytics.models import Analytics
from shared import datetime_now_func, TIMEZONE


class ReportNotFound(Exception):
    pass


def get_shop_analytics(shop_id):
    with Session(engine) as session:
        analytics = session.exec(
            select(Analytics).where(Analytics.shop_id == shop_id)
        ).first()
        if analytics is None:
            raise ReportNotFound
        if analytics.last_updated is None:
            update_shop_report(shop_id)
        else:
            last_update_period = datetime_now_func() - TIMEZONE.localize(
                analytics.last_updated
            )
            if (
                last_update_period.total_seconds() / 3600
                > config.update_period_in_hours
            ):
                trigger_update(shop_id)
        report = analytics.model_dump()
        print(report)
    return report


def trigger_update(shop_id):
    hub.publish("analytics", "update_request", {"shop_id": str(shop_id)})


def update_shop_report(shop_id):
    inventory_report = inventory_utils.get_report(shop_id)
    sales_report = sales_view.get_report(shop_id)
    debt_report = tracker_utils.get_report(shop_id)
    orders_report = order_view.get_report(shop_id)
    with Session(engine) as session:
        analytics = session.exec(
            select(Analytics).where(Analytics.shop_id == shop_id)
        ).first()
        analytics.update(
            debt=debt_report,
            orders=orders_report,
            inventory=inventory_report,
            sales=sales_report,
        )
        session.commit()


def create_shop_report(shop_id):
    analytics = Analytics(shop_id=shop_id)
    with Session(engine) as session:
        session.add(analytics)
        session.commit()


def delete_shop_report(shop_id):
    with Session(engine) as session:
        analytics = session.exec(
            select(Analytics).where(Analytics.shop_id == shop_id)
        ).first()
        if analytics:
            session.delete(analytics)
            session.commit()


def initialize_record(shop_id):
    analytics = Analytics.new(shop_id=shop_id)
    with Session(engine) as session:
        session.add(analytics)
        session.commit()
