from pydantic import BaseModel
from typing import List
from ..product_sage.improvement import ProductImprovementSchema
from ..product_sage.sentiment import SentimentSchema

class ProductSageResponse(BaseModel):
    improvements: List[ProductImprovementSchema]
    sentiments: List[SentimentSchema]
