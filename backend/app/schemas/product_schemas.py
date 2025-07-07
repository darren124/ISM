from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


#PRODUCT_BATCH
class ProductBatchBase(BaseModel):
    product_id: int
    quantity: int
    expiry_date: date
    received_date: date

class ProductBatchCreate(ProductBatchBase):
    pass

class ProductBatchUpdate(BaseModel):
    quantity: Optional[int] = None
    expiry_date: Optional[date] = None
    received_date: Optional[date] = None

class ProductBatchRead(ProductBatchBase):
    batch_id: int

    class Config:
        from_attributes = True


#INVENTORY
class TransactionTypeEnum(str, Enum):
    sale = "sale"
    restock = "restock"
    manual_add = "manual_add"
    adjustment = "adjustment"


class InventoryBase(BaseModel):
    product_id: int
    change_amount: int
    transaction_type: TransactionTypeEnum
    batch_id: Optional[int] = None

class InventoryCreate(InventoryBase):
    pass

class InventoryRead(InventoryBase):
    id: int
    created_at: datetime
    batch: Optional[ProductBatchRead] = None

    class Config:
        from_attributes = True


#PRODUCT
class ProductBase(BaseModel):
    name: str
    category: str
    code: str
    cost: float
    retail_price: float
    stock_threshold: int

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    category: Optional[str] = None
    code: Optional[str] = None
    cost: Optional[float] = None
    retail_price: Optional[float] = None
    stock_threshold: Optional[int] = None

class ProductRead(ProductBase):
    id: int
    batches: Optional[List[ProductBatchRead]] = []
    inventory: Optional[List[InventoryRead]] = []

    class Config:
        from_attributes = True
