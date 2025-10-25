from typing import Annotated

from fastapi import Depends

from api.shared_dependencies import get_shop_id_from_association_record


def get_shop_id_as_string(
    shop_id: Annotated[str, Depends(get_shop_id_from_association_record)]
):
    return str(shop_id)


ShopIDDep = Annotated[str, Depends(get_shop_id_as_string)]
