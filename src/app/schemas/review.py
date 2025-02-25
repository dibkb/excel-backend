from pydantic import BaseModel

class ReviewImage(BaseModel):
    image_id: str
    review: str
    rating: int