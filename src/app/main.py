

from .product_sage.improvement import ProductImprovement, ProductImprovementSchema, ProductImprovements
from .schemas.product_sage import Specifications
from .product_sage.translation import Translation, TranslationSchema
from .product_sage.sentiment import SentimentAnalysis
from .image.main import get_review
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dibkb_scraper import AmazonScraper,AmazonProductResponse
from .product_sage.main import ReActOrchestrator
from concurrent.futures import ThreadPoolExecutor
from functools import partial

app = FastAPI(
    title="Excel Backend",
    description="Excel Backend",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "Healthy and running 🚀 💪"}

@app.get("/amazon/{asin}",response_model=AmazonProductResponse)
async def get_amazon_product(asin: str):
    scraper = AmazonScraper(asin)
    product = scraper.get_all_details()
    return product

@app.get("/amazon/review/{image_id}")
async def get_amazon_review(image_id: str):
    review = get_review(image_id)
    return review

@app.get("/amazon/product-sage/{asin}",response_model=ProductImprovements)
async def get_amazon_product_sage(asin: str)->ProductImprovements:

    scraper = AmazonScraper(asin)
    translator = Translation()
    product_detials = scraper.get_all_details()
    product_info: Specifications = product_detials.product.specifications
    reviews = product_detials.product.reviews
    

    with ThreadPoolExecutor() as executor:
        translated_reviews = list(executor.map(translator.translate, reviews))

    sentiment_analysis = SentimentAnalysis()
    with ThreadPoolExecutor() as executor:
        sentiment_analysis_results = list(
            executor.map(
                sentiment_analysis.analyze,
                [review.translation for review in translated_reviews]
            )
        )

    product_improvement = ProductImprovement()
    improvements = product_improvement.generate_improvements(product_info, sentiment_analysis_results)
    
    
    return improvements
