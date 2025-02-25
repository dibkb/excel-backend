from io import BytesIO
from PIL import Image
import base64
from io import BytesIO
import requests
from ..schemas.review import ReviewImage
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()



def constructImageUrl(imageId: str, size = 900) -> str:
  return f"https://m.media-amazon.com/images/I/{imageId}._SL{size}_.jpg"

def encode_image(image_id: str) -> str:
    """
    Fetches an image from a URL and encodes it in base64 format for API processing.
    """
    image_url = constructImageUrl(image_id)
    response = requests.get(image_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch image: {response.status_code}")
    
    image = Image.open(BytesIO(response.content))
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

def get_review(image_id: str)->ReviewImage:
    llm = ChatOpenAI(model_name="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
    image_base64 = encode_image(image_id)
    prompt = f"""
        You are an AI trained in image evaluation for e-commerce listings. 
        Evaluate the following image based on Amazon’s product image guidelines.
        
        Criteria:
        - White background
        - No watermarks, text, or branding overlays
        - Clear and high-resolution
        - Focused on the product without unnecessary distractions
        
        Provide a rating from 1 to 10 and a brief review.
        Image (base64 encoded):
        {image_base64}
        """
    review = llm.invoke(prompt).content
    print(review)
    return ReviewImage(image_id=image_id, review="x", rating=5)