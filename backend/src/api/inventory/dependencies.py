from typing import Annotated, Any
import uuid

from fastapi import Depends

from api.shopify.dependencies import get_user_shop_association


def get_shop_id_from_association_record(shop_location:str, record: Annotated[dict[str, Any], Depends(get_user_shop_association)]):
    if record['shop_location'] == shop_location:
        return record['shop_id']
    raise HTTPException(status=404, detail="Shop Not Found")


ShopIDDep = Annotated[uuid.UUID, Depends(get_shop_id_from_association_record)]
