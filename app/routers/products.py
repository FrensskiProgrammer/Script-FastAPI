from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from sqlalchemy import select
from app.models import *
from sqlalchemy import insert
from app.schemas import CreateProduct
from sqlalchemy import update
from slugify import slugify

router = APIRouter(prefix="/products", tags=["Products"])


@router.post('/create')
async def create_product(db: Annotated[Session, Depends(get_db)], create_product: CreateProduct):
    db.execute(insert(Product).values(name=create_product.name,
                                      description=create_product.description,
                                      price=create_product.price,
                                      image_url=create_product.image_url,
                                      stock=create_product.stock,
                                      category_id=create_product.category,
                                      rating=0.0,
                                      slug=slugify(create_product.name)))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }

@router.get("/", status_code=status.HTTP_200_OK)
def all_products(db: Annotated[Session, Depends(get_db)]):
    products = db.scalars(select(Product).where(Product.is_active == True, Product.stock > 0)).all()
    if products is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no product'
        )
    return products


@router.get('/{category_slug}')
async def product_by_category(db: Annotated[Session, Depends(get_db)], category_slug: str):
    category = db.scalar(select(Category).where(Category.slug == category_slug))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found'
        )
    subcategories = db.scalars(select(Category).where(Category.parent_id == category.id)).all()
    categories_and_subcategories = [category.id] + [i.id for i in subcategories]
    products_category = db.scalar(
        select(Product).where(Product.category_id.in_(categories_and_subcategories), Product.is_active == True,
                              Product.stock > 0)).all()
    return products_category
@router.get("/{product_slug}", status_code=status.HTTP_200_OK)
def product_detail(product_slug: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.slug == product_slug).first()
    if not product:
        raise HTTPException(status_code=404, detail="There are no product")
    return product


@router.put("/update/{product_slug}", status_code=status.HTTP_200_OK)
def update_product(product_slug: str, updated_product: CreateProduct, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.slug == product_slug).first()
    if not product:
        raise HTTPException(status_code=404, detail="There is no product found")

    product.name = updated_product.name
    product.description = updated_product.description
    product.price = updated_product.price
    product.stock = updated_product.stock
    product.category_id = updated_product.category_id

    db.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "Product update is successful"}


@router.delete("/delete/{product_slug}", status_code=status.HTTP_200_OK)
def delete_product(product_slug: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.slug == product_slug).first()
    if not product:
        raise HTTPException(status_code=404, detail="There is no product found")

    product.is_active = False
    db.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": "Product delete is successful"}
