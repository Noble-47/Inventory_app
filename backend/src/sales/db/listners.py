from exchange.hub import publish
from sales.domain import events

def publish_new_sale(event:events.NewSaleAdded):
    publish("sales_notifications", "new_sale", event.model_dump())

def publish_sale_update(event:events.SaleRecordUpdated):
    publish("sales_notifications", "sale_update", event.model_dump())


event_handlers = {
    events.NewSaleAdded : [publish_new_sale],
    events.SaleRecordUpdated : [publish_sale_update]
}

def handle(event):
    for handler in handlers.get(event, []):
        handler(event)
