from datetime import datetime, timedelta
import pytest

from inventory.domain.models import Stock, Batch, MeasurementMetric
from inventory.adapters.repository import SQLStockRepository

@pytest.fixture
def populated_session(sqlite_session_factory):
    session = sqlite_session_factory()
    batches = [
        Batch(
            sku="sku1", ref ="ref11", stock_in_units=11, price=155.0,
            stock_time = datetime.now() - timedelta(days=7), quantity=11
        ),
        Batch(
            sku ="sku1", ref ="ref6", stock_in_units=6, price=99.0,
            stock_time = datetime.now() - timedelta(days=5), quantity=0
        ),
        Batch(
            sku="sku2", ref="ref10", stock_in_units=11, price=150.0,
            stock_time = datetime.now() - timedelta(days=3)
        ),
        Batch(
            sku="sku3", ref="ref5", stock_in_units=5, price=150.0,
            stock_time = datetime.now() - timedelta(hours=3)
        )
    ]
    stocks = [
        Stock(
            sku=f"sku1",
            name=f"buenovida_1",
            metric=MeasurementMetric.medium,
            control_strategy="fifo"
        ),
        Stock(
            sku=f"sku2",
            name=f"buenovida_2",
            metric=MeasurementMetric.medium,
            control_strategy="fifo"
        ),
        Stock(
            sku=f"sku3",
            name=f"buenovida_3",
            metric=MeasurementMetric.medium,
            control_strategy="fifo"
        ),
    ]
    for stock in stocks:
        session.add(stock)
    for batch in batches:
        session.add(batch)
    session.commit()
    return session


@pytest.mark.usefixtures('mappers')
def test_get_stock_by_sku(populated_session):
    session = populated_session
    repo = SQLStockRepository(session)
    stock = repo.get("sku1")
    print(stock)
    assert len(stock.batches) == 2

@pytest.mark.usefixtures('mappers')
def test_stock_count(populated_session):
    session = populated_session
    repo = SQLStockRepository(session)
    assert len(repo) == 3

@pytest.mark.usefixtures('mappers')
def test_get_only_dispatchable_batches(populated_session):
    session = populated_session
    repo = SQLStockRepository(session)
    stock = repo.get_only_dispatchable_batches("sku1")
    assert len(stock.batches) == 1
    assert stock.batches[0].ref == "ref11"
