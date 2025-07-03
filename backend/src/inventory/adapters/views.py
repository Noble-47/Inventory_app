from datetime import datetime
import uuid

from sqlalchemy import select

from inventory.domain.read_models import BatchView, StockView

class View:

    def __init__(self, session):
        self.session = session

    def update_veiw_level(self, shop_id, sku):
        pass

    def update_view_cogs(self, shop_id, sku):
        pass
