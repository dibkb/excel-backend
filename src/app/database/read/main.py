from ..init_db import get_db
from ..models import Product, ProductEnhancements,ProductSage, ProductWebReviewer
from fastapi.encoders import jsonable_encoder
from sqlalchemy import exists
from sqlalchemy.exc import OperationalError
from time import sleep


def asin_exists(asin: str, max_retries: int = 3) -> bool:
    for attempt in range(max_retries):
        try:
            with get_db() as db:
                return db.query(exists().where(Product.asin == asin)).scalar()
        except OperationalError as e:
            if "SSL SYSCALL error: EOF detected" in str(e):
                if attempt == max_retries - 1:
                    raise
                sleep(1 * (attempt + 1))  # Exponential backoff
                continue
            raise

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
    
def product_enhancements_exists(asin: str) -> bool:
    
    with get_db() as db:
        return db.query(exists().where(ProductEnhancements.asin == asin)).scalar()

def fetch_product_enhancements_by_asin(asin: str = None) -> dict:
    with get_db() as db:
        query = db.query(ProductEnhancements)
        if asin:
            query = query.filter(ProductEnhancements.asin == asin).first()
        return jsonable_encoder(query)
    

def product_web_reviewer_exists(asin: str) -> bool:
    with get_db() as db:
        return db.query(exists().where(ProductWebReviewer.asin == asin)).scalar()

def fetch_product_web_reviewer_by_asin(asin: str = None) -> dict:
    with get_db() as db:
        query = db.query(ProductWebReviewer)
        if asin:
            query = query.filter(ProductWebReviewer.asin == asin).first()
        return jsonable_encoder(query)

