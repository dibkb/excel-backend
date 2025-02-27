from .init_db import Base
from sqlalchemy import Column, String, Text, DECIMAL,JSON

class Product(Base):
    __tablename__ = 'products'
    asin = Column(String(20), primary_key=True)
    title = Column(Text, nullable=False)
    price = Column(DECIMAL(10,2), nullable=False)
    image = Column(JSON,nullable=True)
    categories = Column(JSON,nullable=True)
    description = Column(JSON,nullable=True)
    specifications = Column(JSON,nullable=True)
    ratings = Column(JSON,nullable=True)
    reviews = Column(JSON,nullable=True)
    related_products = Column(JSON,nullable=True)

class ProductSage(Base):
    __tablename__ = 'product_sages'
    asin = Column(String(20), primary_key=True)
    improvements = Column(JSON,nullable=True)
    sentiments = Column(JSON,nullable=True)
