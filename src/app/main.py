from typing import Any, Dict, List

from .product_sage.web_reviewer import WebReviewer

from .product_sage.sentiment import SentimentSchema
from .product_sage.improvement import ProductImprovementSchema
import httpx
from .database.read.main import asin_exists, asin_exists_sage, fetch_product_by_asin, fetch_product_enhancements_by_asin, fetch_product_sage_by_asin, product_enhancements_exists
from .database.create.main import create_product, create_product_enhancements, create_product_sage
from .database.init_db import init_db

from .schemas.api import ProductSageResponse
from .schemas.product_sage import Specifications
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dibkb_scraper import AmazonScraper,AmazonProductResponse
from .product_sage.main import ProductSage
import socketio
from .product_enhancer.enhance import ProductEnhancer

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["http://localhost:3001", "http://localhost:3000", "http://localhost:5173"],
    logger=True,
    engineio_logger=True
)

app = FastAPI(
    title="Excel Backend",
    description="Excel Backend",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio_app = socketio.ASGIApp(sio, app)


@app.on_event("startup")
async def startup_db_client():
    try:
        init_db()
    except Exception as e:
        print(f"Failed to initialize database: {e}")

# socket io events
@sio.event
async def connect(sid, environ):
    print("Client connected:", sid)
    await sio.emit("welcome", {"message": "Welcome to the FastAPI Socket.IO server!"}, room=sid)

@sio.event
async def disconnect(sid):
    print("Client disconnected:", sid)
        
@app.get("/health")
async def health_check():
    return {"status": "Healthy and running 🚀 💪"}

@app.get("/amazon/{asin}",response_model=Dict[str,Any])
async def get_amazon_product(asin: str)->Dict[str,Any]:
    if not asin_exists(asin):
        scraper = AmazonScraper(asin)
        product = scraper.get_all_details()
        response = create_product(product.product,asin)
        return response
    else:
        product = fetch_product_by_asin(asin)
        return product

@app.get("/amazon/product-sage/{asin}",response_model=Any)
async def get_amazon_product_sage(asin: str)->Any:
    if not asin_exists_sage(asin):
        scraper = AmazonScraper(asin)
        product_detials = scraper.get_all_details()

        # product_info: Specifications = product_detials.product.specifications
        # reviews: List[str] = product_detials.product.reviews
    

        # product_sage = ProductSage(product_info, reviews)
        # sentiments = product_sage.get_analysis()
        # improvements = product_sage.get_product_improvement()

        # response = create_product_sage(improvements,sentiments,asin)

        # return response
        title_refiner = WebReviewer(product_detials.product.title)
        refined_title = title_refiner.get_top_website_content()
        return refined_title
    else:
        product = fetch_product_sage_by_asin(asin)
        return product


@app.get("/amazon/competitors/{asin}")
async def get_amazon_competitors(asin: str):
    scraper = AmazonScraper(asin)
    competitors = scraper.get_competitors()
    return competitors

@app.get("/amazon/product-enhancements/{asin}")
async def get_amazon_competitors(asin: str):
    if not product_enhancements_exists(asin):
        try:
            client = httpx.AsyncClient()
            response = await client.get(f"http://localhost:8000/amazon/{asin}")
            product = response.json()
            product_enhancer = ProductEnhancer(product)
            content = product_enhancer.generate_enhanced_listing()
            response = create_product_enhancements(content,asin)

            return {
                "asin": asin,
                "enhancements": content
            }
        
        except Exception as e:
            print(f"Error generating product enhancements: {e}")
            return {"error": "Failed to generate product enhancements"}
        finally:
            await client.aclose()

    else:
        product = fetch_product_enhancements_by_asin(asin)
        return product
