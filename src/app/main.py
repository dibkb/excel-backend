from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dibkb_scraper import AmazonScraper,AmazonProductResponse
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