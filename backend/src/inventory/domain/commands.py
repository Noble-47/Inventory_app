from dataclasses import dataclass

class Command:
    pass


@dataclass
class DispatchGoodsFromStock:
    sku:str
    quantity:int
    sale_time:float


@dataclass
class AddBatchToStock:
    sku:str
    batch_ref:str
    quantity:int
    price:float


@dataclass
class UpdateBatchPrice:
    sku:str
    batch_ref:str
    price:float


@dataclass
class UpdateBatchQuantity:
    sku:str
    batch_ref:str
    quantity:int
