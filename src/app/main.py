from typing import Any, Dict, List

from src.app.swot.main import Swot, SwotAnalysisConsolidated

from .product_sage.web_reviewer import ReviewSchema, WebReviewer
from bs4 import BeautifulSoup
import httpx
from .database.read.main import asin_exists, asin_exists_sage, fetch_product_by_asin, fetch_product_enhancements_by_asin, fetch_product_sage_by_asin, fetch_product_web_reviewer_by_asin, product_enhancements_exists, product_web_reviewer_exists, fetch_all_products
from .database.create.main import create_product, create_product_enhancements, create_product_sage, create_product_web_reviewer
from .database.init_db import init_db
from fastapi.responses import JSONResponse
from .schemas.api import ProductSageResponse
from .schemas.product_sage import Specifications
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dibkb_scraper import AmazonScraper
from dibkb_scraper.playwright import PlaywrightScraper

from .product_sage.main import ProductSage
import socketio
from .product_enhancer.enhance import ProductEnhancer
import os
import dotenv
from ..config.main import settings
dotenv.load_dotenv()

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["http://localhost:3001", "http://localhost:3000", "http://localhost:5173","https://excel.borborah.xyz"],
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
    allow_origins=["http://localhost:3001", "http://localhost:3000", "http://localhost:5173","https://excel.borborah.xyz"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio_app = socketio.ASGIApp(sio, app)


@app.on_event("startup")
async def startup_db_client():
    try:
        init_db()
        global chrome_scraper
        chrome_scraper = PlaywrightScraper()
        await chrome_scraper.initialize()
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
    return {"status": "Healthy running 🚀"}

@app.get("/products")
async def get_products():
    try:
        products = fetch_all_products()
        return products
    except Exception as e:
        print(f"Error getting products: {e}")
        return []

@app.get("/latest-update")
async def latest_update():
    return {"status": "Scraper updated to version 0.2.9 (fake headers added)"}

@app.get("/amazon/{asin}",response_model=Dict[str,Any])
async def get_amazon_product(asin: str)->Dict[str,Any]:
    if not asin_exists(asin):
        try:
            html = await chrome_scraper.get_html_content(f"https://www.amazon.in/dp/{asin}")
            soup = BeautifulSoup(html, "html.parser")
            scraper = AmazonScraper(asin,soup)
            product = scraper.get_all_details()
            if product['product'] is None:
                raise Exception("Product not found")
            
            result = product['product']
            if result['title'] == None or result['title'] == "":
                raise Exception("Product title not found")
            if result['price'] == None or result['price'] == "":
                raise Exception("Product price not found")
            response = create_product(result,asin)
            return response
        except Exception as e:
            print(f"Error getting product: {e}")
            return JSONResponse(status_code=404, content={"message": str(e)})
    else:
        product = fetch_product_by_asin(asin)
        return product

@app.get("/amazon/product-sage/{asin}",response_model=Any)
async def get_amazon_product_sage(asin: str)->Any:
    if not asin_exists_sage(asin):
        try:
            client = httpx.AsyncClient()
            response = await client.get(f"{settings.BACKEND_URL}/amazon/{asin}")
            product_detials = response.json()

            product_info = product_detials['specifications']
            reviews: List[str] = product_detials['reviews']
    

            product_sage = ProductSage(product_info, reviews)
            sentiments = product_sage.get_analysis()
            improvements = product_sage.get_product_improvement()

            response = create_product_sage(improvements,sentiments,asin)

            return response

        except Exception as e:
            print(f"Error getting product sage: {e}")
            return []

    else:
        product = fetch_product_sage_by_asin(asin)
        return product

@app.get("/amazon/product-sage/web-reviewer/{asin}", response_model=List[ReviewSchema])
async def get_amazon_product_sage_web_reviewer(asin: str) -> List[ReviewSchema]:
    if not product_web_reviewer_exists(asin):
        try:
            client = httpx.AsyncClient()
            response = await client.get(f"{settings.BACKEND_URL}/amazon/{asin}")
            product = response.json()
            title = product['title']
            reviewer = WebReviewer(title)
            reviews = reviewer.get_top_website_content()
            response = create_product_web_reviewer(reviews, asin)
            return response
        except Exception as e:
            print(f"Error getting product sage web reviewer: {e}")
            return []
    else:
        reviews = fetch_product_web_reviewer_by_asin(asin)
        return [ReviewSchema(**review) for review in reviews['reviews']]


@app.get("/amazon/product-enhancements/{asin}")
async def get_amazon_competitors(asin: str):
    if not product_enhancements_exists(asin):
        try:
            client = httpx.AsyncClient()
            response = await client.get(f"{settings.BACKEND_URL}/amazon/{asin}")
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

@app.get("/amazon/swot-consolidated/{asin}",response_model=SwotAnalysisConsolidated)
async def get_amazon_swot(asin: str,competitors: str):
    competitors = [competitor.strip() for competitor in competitors.split(",")]
    swot = Swot(asin,competitors)
    return await swot.analyze()

