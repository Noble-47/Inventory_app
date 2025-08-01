from sqlalchemy import select

from inventory.domain.models import sku_generator
from inventory.domain import models
from inventory import exceptions


class Product:

    def __init__(self, session):
        self.session = session

    def get_or_create(self, name, brand, packet_type, packet_size):
        sku = sku_generator(
            name=name, brand=brand, packet_type=packet_type, packet_size=packet_size
        )
        product = self.session.scalars(
            select(models.Product).where(models.Product.sku == sku)
        ).first()
        if product is None:
            product = models.Product(
                sku=sku,
                name=name,
                brand=brand,
                packet_size=packet_size,
                packet_type=packet_type,
            )
            self.session.add(product)
        return product

    def get(self, sku):
        product = self.session.scalars(
            select(models.Product).where(models.Product.sku == sku)
        ).first()
        if product is None:
            raise exceptions.StockNotFound
        return product
