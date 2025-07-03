from datetime import datetime

from inventory.domain.strategies import Strategy, FIFO, LIFO, WeightedAverage

strategies = {
    "fifo" : FIFO,
    "lifo" : LIFO,
    "weighted_average" : WeightedAverage
}

def get_controller(stock, strategy: str):
    strategy_class = strategies.get(strategy)
    return Controller(stock, strategy_class)


def is_between(time, start_date: datetime, end_date: datetime):
    return (time >= start_date) and (time <= end_date)


class Controller:

    def __init__(self, stock, strategy: Strategy):
        self.stock = stock
        self.strategy = strategy()

    def adjust_stock_level(self, starting_batch, offset: int, adjustment: str, record:list):
        stock = [
            batch
            for batch in self.dispatch_generator()
            if batch.ref != starting_batch.ref
        ]
        # reverse list so that it begins from the batch after starting batch to "next-to-be-sold" batch
        if adjustment.lower() == "lower":
            starting_batch.quantity = 0
            self.strategy.lower_stock_level(offset, stock, record)
        elif adjustment.lower() == "raise":
            stock = stock[::-1]
            stock.append(starting_batch)
            self.strategy.raise_stock_level(offset, stock, record)
        else:
            raise ValueError(
                "Adjustment must either be 'raise' or 'lower'. Got {adjustment}"
            )

    def dispatch_generator(self):
        return self.strategy.get_batch_gen(self.stock.batches)

    def compute_cogs(self, start_date: datetime, end_date: datetime):

        return sum(
            (batch.stock_in_units - batch.quantity) * batch.price
            for batch in stock
            if is_between(batch.stock_time, start_date, end_date)
        )

    def compute_inventory_value(self):
        batches = [batch for batch in self.stock]
        return self.strategy.calculate_inventory_value(batches, self.stock.level)
