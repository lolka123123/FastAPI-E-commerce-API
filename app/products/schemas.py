from pydantic import  BaseModel, ConfigDict, Field
from decimal import Decimal


class ProductBase(BaseModel):
    id: int
    name: str
    price: Decimal

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    price: Decimal = Field(gt=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    price: Decimal | None = Field(default=None, gt=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    price: Decimal

    model_config = ConfigDict(
        from_attributes=True
    )