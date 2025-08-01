from sqlmodel import select

from stock_port.domain import events
from stock_port.domain.models import Order, batch_ref_gen


class OrderDB:

    def __init__(self, session, events):
        self.session = session
        self.events = events
        self.seen = set()

    def get(self, shop_id, order_id):
        order = self.session.exec(
            select(Order).where(Order.id == order_id, Order.shop_id == shop_id)
        ).first()
        self.seen.add(order)
        return order

    def create(self, shop_id, batchline, expected_delivery_date, cost, supplier):
        order = Order(
            shop_id=shop_id,
            batchline=batchline,
            expected_delivery_date=expected_delivery_date,
            supplier_id=supplier.id,
            cost=cost,
            supplier_phone=supplier.supplier_phone,
        )
        self.session.add(order)
        self.seen.add(order)
        self.events.append(
            events.OrderCreated(
                order_id=order.id,
                shop_id=order.shop_id,
                status=order.status,
                supplier=repr(supplier.supplier),
                supplier_phone=supplier.supplier_phone,
                order_line=[
                    events.NewOrderLine(
                        sku=b.sku,
                        batch_ref=b.batch_ref,
                        cost=b.cost,
                        expected_quantity=b.expected_quantity,
                    )
                    for b in batchline
                ],
                expected_delivery_date=order.expected_delivery_date,
            )
        )
        return order
