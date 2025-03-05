from datetime import datetime

from ...product_sage.web_reviewer import ReviewSchema
from ..init_db import get_db
from sqlalchemy.dialects.postgresql import insert
from ..models import Product, ProductEnhancements, ProductSage, ProductWebReviewer
from ..main import engine, SessionLocal
from ...schemas.product import Product as ProductSchema
import json
from pydantic import BaseModel
from typing import List
from ...product_sage.improvement import ProductImprovementSchema
from ...product_sage.sentiment import SentimentSchema

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

def create_product_enhancements(json_data, asin: str):
    db = SessionLocal()
    try:
        # Ensure product_data is a dictionary or a Pydantic model

        # Create the values dictionary for the insert
        values = {
            "asin": asin,
            "enhancements": json_data,
            "created_at": datetime.now()
        }
        
        query = insert(ProductEnhancements).values(**values)
        db.execute(query)
        db.commit()
        return values
    
    except Exception as e:
        db.rollback()
        print(f"Error creating product: {e}")
        raise
    finally:
        db.close()


def create_product_sage(improvements:List[ProductImprovementSchema],sentiments:List[SentimentSchema], asin: str):
    db = SessionLocal()
    try:
        improvements_list = [improvement.model_dump() for improvement in improvements]
        sentiments_list = [sentiment.model_dump() for sentiment in sentiments]

        query = insert(ProductSage).values(asin=asin,improvements=improvements_list,sentiments=sentiments_list)
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


def create_product_web_reviewer(reviews:List[ReviewSchema], asin: str):
    db = SessionLocal()
    try:
        reviews_list = [review.model_dump() for review in reviews]
        query = insert(ProductWebReviewer).values(asin=asin,reviews=reviews_list)
        db.execute(query)
        db.commit()
        return reviews  
    except Exception as e:
        db.rollback()
        print(f"Error creating product: {e}")
        raise
    finally:
        db.close()