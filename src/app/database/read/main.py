from ..init_db import get_db
from ..models import Product,ProductSage
from fastapi.encoders import jsonable_encoder
from sqlalchemy import exists


def asin_exists(asin: str) -> bool:
    with get_db() as db:
        return db.query(exists().where(Product.asin == asin)).scalar()

def asin_exists_sage(asin: str) -> bool:
    with get_db() as db:
        return db.query(exists().where(ProductSage.asin == asin)).scalar()

def fetch_product_by_asin(asin: str = None) -> dict:
    with get_db() as db:
        query = db.query(Product)
        if asin:
            query = query.filter(Product.asin == asin).first()
        return jsonable_encoder(query)
    
def fetch_product_sage_by_asin(asin: str = None) -> dict:
    with get_db() as db:
        query = db.query(ProductSage)
        if asin:
            query = query.filter(ProductSage.asin == asin).first()
        return jsonable_encoder(query)