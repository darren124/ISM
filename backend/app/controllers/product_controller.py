from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.product_models import Product
from app.models.product_batch_models import ProductBatch
from app.models.inventory_models import Inventory, TransactionTypeEnum
from app.models.product_mapping_models import ProductMapping
from app.schemas.product_schemas import ProductCreate, ProductUpdate, ProductRead, ProductBatchCreate, ProductBatchUpdate, ProductBatchRead
from typing import List

product_router = APIRouter()


# Get All Products and batches
@product_router.get("/", response_model=List[ProductRead])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).options(
        joinedload(Product.batches),
        joinedload(Product.inventory).joinedload(Inventory.batch)
        ).all()
    return products


# Add Product
@product_router.post("/", response_model=ProductRead)
def add_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.code == product_data.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product code already exists")

    new_product = Product(**product_data.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


# Edit/Update Product
@product_router.put("/{product_id}", response_model=ProductRead)
def update_product(product_id: int, updated_data: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


# Delete Product
@product_router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete product mappings first
    mappings = db.query(ProductMapping).filter(ProductMapping.product_id == product_id).all()
    for mapping in mappings:
        db.delete(mapping)

    inventories = db.query(Inventory).filter(Inventory.product_id == product_id).all()
    for inventory in inventories:
        db.delete(inventory)

    batches = db.query(ProductBatch).filter(ProductBatch.product_id == product_id).all()
    for batch in batches:
        db.delete(batch)

    db.delete(product)
    db.commit()
    return {"detail": "Product and related data deleted successfully"}


# Add Product Batch
@product_router.post("/{product_id}/batches", response_model=ProductBatchRead)
def add_product_batch(product_id: int, batch_data: ProductBatchCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_batch = ProductBatch(
        product_id=product_id,
        quantity=batch_data.quantity,
        expiry_date=batch_data.expiry_date,
        received_date=batch_data.received_date
    )
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)

    inventory_entry = Inventory(
        product_id=product_id,
        change_amount=new_batch.quantity,
        transaction_type=TransactionTypeEnum.manual_add,
        batch_id=new_batch.batch_id
    )
    db.add(inventory_entry)
    db.commit()

    return new_batch


# Update Product Batch
@product_router.put("/{product_id}/batches/{batch_id}", response_model=ProductBatchRead)
def update_product_batch(product_id: int, batch_id: int, updated_data: ProductBatchUpdate, db: Session = Depends(get_db)):
    # Ensure the batch exists and belongs to the correct product
    batch = db.query(ProductBatch).filter(
        ProductBatch.batch_id == batch_id,
        ProductBatch.product_id == product_id
    ).first()

    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found for the given product")
    
    old_quantity = batch.quantity
    for key, value in updated_data.model_dump(exclude_unset=True).items():
        setattr(batch, key, value)

    db.commit()
    db.refresh(batch)

    if "quantity" in updated_data.model_dump(exclude_unset=True):
        diff = batch.quantity - old_quantity
        if diff != 0:
            inventory_entry = Inventory(
                product_id=product_id,
                change_amount=diff,
                transaction_type=TransactionTypeEnum.manual_add if diff > 0 else TransactionTypeEnum.adjustment,
                batch_id=batch.batch_id
            )
            db.add(inventory_entry)
            db.commit()

    return batch


# Delete Product Batch
@product_router.delete("/{product_id}/batches/{batch_id}")
def delete_product_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(ProductBatch).filter(ProductBatch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    db.delete(batch)
    db.commit()
    return {"detail": "Batch deleted successfully"}