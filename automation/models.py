from pydantic import BaseModel
from typing import List, Optional

class ProductIntent(BaseModel):
    product: str
    max_price:Optional[float]=None
    min_price:Optional[float]=None
    min_rating:Optional[float]=None
    max_rating:Optional[float]=None
    sort_by:Optional[str]=None
    color:Optional[str]=None
    brand:Optional[str]=None

class ProductItem(BaseModel):
    name:str
    price:Optional[float]=None
    rating:Optional[float]=None
    url:str

class CartResult(BaseModel):
    items:List[ProductItem]