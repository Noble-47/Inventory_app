from datetime import datetime, timedelta
from pprint import pprint
import pytest

from inventory.domain.models import Stock, Batch, MeasurementMetric

def test_increase_stock_level_for_sold_out_batches():
    batches = [
        Batch(
            sku="sku", ref ="ref11", stock_in_units=11, price=155.0,
            stock_time = datetime.now() - timedelta(days=7), quantity=0
        ),
        Batch(
            sku ="sku", ref ="ref6", stock_in_units=6, price=99.0,
            stock_time = datetime.now() - timedelta(days=5), quantity=0,
        ),
        Batch(
            sku="sku", ref="ref10", stock_in_units=11, price=150.0,
            stock_time = datetime.now() - timedelta(days=3), quantity=10
        ),
        Batch(
            sku="sku", ref="ref5", stock_in_units=5, price=150.0,
            stock_time = datetime.now() - timedelta(hours=3), quantity=5
        )
    ]

    stock = Stock(
        sku="sku",
        name="buenovida",
        metric=MeasurementMetric.medium,
        batches=batches,
        control_strategy="fifo"
    )
    stock.events = []

    assert stock.level == 15
    assert stock.inventory_value == 2250.0

    batch_11 = stock['ref11']
    stock.update_batch('ref11', quantity=15)
    print("\nINCREASE SOLD OUT FIFO BATCH TEST")
    pprint(batches)
    print()
    assert stock.level == 19
    assert stock.inventory_value == 2697.0

def test_increase_stock_level_for_sold_out_batches_lifo():
    batches = [
        Batch(
            sku="sku", ref ="ref11", stock_in_units=11, price=155.0,
            stock_time = datetime.now() - timedelta(days=7)
        ),
        Batch(
            sku ="sku", ref ="ref6", stock_in_units=6, price=99.0,
            stock_time = datetime.now() - timedelta(days=5)
        ),
        Batch(
            sku="sku", ref="ref10", stock_in_units=11, price=150.0,
            stock_time = datetime.now() - timedelta(days=3), quantity=11
        ),
        Batch(
            sku="sku", ref="ref5", stock_in_units=5, price=150.0,
            stock_time = datetime.now() - timedelta(hours=3), quantity=3
        )
    ]

    stock = Stock(
        sku="sku",
        name="buenovida",
        metric=MeasurementMetric.medium,
        batches=batches,
        control_strategy="lifo"
    )
    stock.events = []

    assert stock.level == 31
    assert stock.inventory_value == 4399

    batch_11 = stock['ref11']
    stock.update_batch('ref11', quantity=15)

    print("INCREASE SOLD OUT LIFO BATCH TEST")
    pprint(batches)
    print()
    assert stock.level == 35
    assert stock.inventory_value == 5019

def test_increase_stock_level_for_dispatchable_batch():
    batches = [
        Batch(
            sku="sku", ref ="ref11", stock_in_units=11, price=155.0,
            stock_time = datetime.now() - timedelta(days=7), quantity=1
        ),
        Batch(
            sku ="sku", ref ="ref6", stock_in_units=6, price=99.0,
            stock_time = datetime.now() - timedelta(days=5)
        ),
        Batch(
            sku="sku", ref="ref10", stock_in_units=11, price=150.0,
            stock_time = datetime.now() - timedelta(days=3)
        ),
        Batch(
            sku="sku", ref="ref5", stock_in_units=5, price=150.0,
            stock_time = datetime.now() - timedelta(hours=3)
        )
    ]

    stock = Stock(
        sku="sku",
        name="buenovida",
        metric=MeasurementMetric.medium,
        batches=batches,
        control_strategy="fifo"
    )
    stock.events = []

    assert stock.level == 23
    assert stock.inventory_value == 3149

    batch_11 = stock['ref11']
    stock.update_batch('ref11', quantity=15)

    print("INCREASE DISPATCHABLE BATCH TEST")
    pprint(batches)
    assert stock.level == 27
    assert stock.inventory_value == 3769.0

def test_decrease_stock_level_for_dispatchable_batch():
    batches = [
        Batch(
            sku="sku", ref ="ref11", stock_in_units=11, price=155.0,
            stock_time = datetime.now() - timedelta(days=7), quantity=1
        ),
        Batch(
            sku ="sku", ref ="ref6", stock_in_units=6, price=99.0,
            stock_time = datetime.now() - timedelta(days=5)
        ),
        Batch(
            sku="sku", ref="ref10", stock_in_units=11, price=150.0,
            stock_time = datetime.now() - timedelta(days=3)
        ),
        Batch(
            sku="sku", ref="ref5", stock_in_units=5, price=150.0,
            stock_time = datetime.now() - timedelta(hours=3)
        )
    ]

    stock = Stock(
        sku="sku",
        name="buenovida",
        metric=MeasurementMetric.medium,
        batches=batches,
        control_strategy="fifo"
    )
    stock.events = []

    assert stock.level == 23
    assert stock.inventory_value == 3149

    batch_11 = stock['ref11']
    stock.update_batch('ref11', quantity=1)

    print("Decrease DISPATCHABLE BATCH TEST")
    pprint(batches)
    assert stock.level == 13
    assert stock.inventory_value == 1950.0

def test_decrease_stock_level_for_sold_less_than_decrement_quantity():
    batches = [
        Batch(
            sku="sku", ref ="ref11", stock_in_units=11, price=155.0,
            stock_time = datetime.now() - timedelta(days=7), quantity=11
        ),
        Batch(
            sku ="sku", ref ="ref6", stock_in_units=6, price=99.0,
            stock_time = datetime.now() - timedelta(days=5)
        ),
        Batch(
            sku="sku", ref="ref10", stock_in_units=11, price=150.0,
            stock_time = datetime.now() - timedelta(days=3)
        ),
        Batch(
            sku="sku", ref="ref5", stock_in_units=5, price=150.0,
            stock_time = datetime.now() - timedelta(hours=3)
        )
    ]

    stock = Stock(
        sku="sku",
        name="buenovida",
        metric=MeasurementMetric.medium,
        batches=batches,
        control_strategy="fifo"
    )
    stock.events = []

    assert stock.level == 33
    assert stock.inventory_value == 4699

    batch_11 = stock['ref11']
    stock.update_batch('ref11', quantity=1)

    print("Decrease SOLD OUT LESS THAN DECREMENT BATCH TEST")
    pprint(batches)
    assert stock.level == 23
    assert stock.inventory_value == 3149.0


def test_batch_update_is_idempotent():
    batches = [
        Batch(
            sku="sku", ref ="ref11", stock_in_units=11, price=155.0,
            stock_time = datetime.now() - timedelta(days=7), quantity=1
        ),
        Batch(
            sku ="sku", ref ="ref6", stock_in_units=6, price=99.0,
            stock_time = datetime.now() - timedelta(days=5)
        ),
        Batch(
            sku="sku", ref="ref10", stock_in_units=11, price=150.0,
            stock_time = datetime.now() - timedelta(days=3)
        ),
        Batch(
            sku="sku", ref="ref5", stock_in_units=5, price=150.0,
            stock_time = datetime.now() - timedelta(hours=3)
        )
    ]

    stock = Stock(
        sku="sku",
        name="buenovida",
        metric=MeasurementMetric.medium,
        batches=batches,
        control_strategy="fifo"
    )
    stock.events = []

    assert stock.level == 23
    assert stock.inventory_value == 3149

    batch_11 = stock['ref11']
    stock.update_batch('ref11', quantity=1) # take batch to 1

    assert stock.level == 13
    assert stock.inventory_value == 1950.0

    stock.update_batch('ref11', quantity=11) # take it back to 11

    print("UPDATE IS IDEMPOTENT")
    pprint(batches)
    assert stock.level == 23
    assert stock.inventory_value == 3149
