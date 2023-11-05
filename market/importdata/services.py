from typing import List, Optional
from decimal import Decimal

from pydantic import BaseModel, Field


class DetailsPydantic(BaseModel):
    name: str = Field(max_length=512)
    value: str = Field(max_length=128)


class CategoryPydantic(BaseModel):
    name: str = Field(max_length=128)
    cat_slug: str = Field(max_length=128)
    parent: Optional[str] = Field(default=None, max_length=128)
    par_slug: Optional[str] = Field(default=None, max_length=128)


class ManufacturerPydantic(BaseModel):
    name: str = Field(max_length=128)
    slug: str = Field(max_length=128)


class ShopPydantic(BaseModel):
    pass


class OfferPydantic(BaseModel):
    price: Decimal = Field(ge=0.01, max_digits=10, decimal_places=2)
    quantity: int = Field(gt=0)


class ProductPydantic(BaseModel):
    name: str = Field(max_length=512)
    manufacturer: ManufacturerPydantic
    about: str = Field(max_length=512)
    description: str = Field(max_length=1024)
    category: CategoryPydantic
    shop: str = Field(max_length=512)
    preview: str
    tags: Optional[List[str]] = Field(max_length=64)
    offer: OfferPydantic
    details: List[DetailsPydantic]
