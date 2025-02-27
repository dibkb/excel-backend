from ..init_db import get_db
from sqlalchemy.dialects.postgresql import insert
from ..models import Product, ProductSage
from ..main import engine, SessionLocal
from ...schemas.product import Product as ProductSchema
import json
from pydantic import BaseModel


def create_product(product_data, asin: str):
    db = SessionLocal()
    try:
        # Ensure product_data is a dictionary or a Pydantic model
        if isinstance(product_data, BaseModel):
            # Convert Pydantic model to dictionary
            product_data = product_data.dict()
        elif isinstance(product_data, str):
            # If product_data is a string, you might need to parse it (if it's JSON)
            product_data = json.loads(product_data)

        # Create the values dictionary for the insert
        values = {
            "asin": asin,
            "title": product_data["title"],
            "image": product_data["image"],
            "price": product_data["price"],
            "categories": product_data["categories"],
            "description": product_data["description"],
            "specifications": product_data["specifications"],
            "ratings": product_data["ratings"],
            "reviews": product_data["reviews"],
            "related_products": product_data["related_products"]
        }
        
        query = insert(Product).values(**values)
        db.execute(query)
        db.commit()
        return values
    except Exception as e:
        db.rollback()
        print(f"Error creating product: {e}")
        raise
    finally:
        db.close()


def create_product_sage(improvements,sentiments, asin: str):
    db = SessionLocal()
    try:
        if isinstance(improvements, BaseModel):
            improvements = improvements.model_dump_json()
        elif isinstance(improvements, str):
            improvements = json.loads(improvements)

        if isinstance(sentiments, BaseModel):
            sentiments = sentiments.model_dump_json()
        elif isinstance(sentiments, str):
            sentiments = json.loads(sentiments)
        query = insert(ProductSage).values(asin=asin,improvements=improvements,sentiments=sentiments)
        db.execute(query)
        db.commit()
        return {
            "improvements":improvements,
            "sentiments":sentiments
        }
    except Exception as e:
        db.rollback()
        print(f"Error creating product: {e}")
        raise
    finally:
        db.close()