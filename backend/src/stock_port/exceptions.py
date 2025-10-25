class UnprocessableDelivery(Exception):
    pass


class DuplicateOrderDelivery(Exception):
    pass


class CancelledOrder(Exception):
    pass


class OrderNotFound(Exception):
    pass
