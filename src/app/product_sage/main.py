from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

from .translation import Translation
from ..schemas.product_sage import Specifications
from .improvement import ProductImprovement, ProductImprovementSchema
from .sentiment import SentimentAnalysis, SentimentSchema


class ProductSage:
    def __init__(self, product_info: Specifications, reviews: List[str]):
        self.product_improvement = ProductImprovement()
        self.translation = Translation()
        self.sentiment_analysis = SentimentAnalysis()
        self.product_info = product_info
        self.reviews = reviews
        self.translated_reviews = []
        self.sentiment_analysis_results = []
        self.max_workers = min(32, len(reviews))


    def translate_reviews(self) -> List[str]:
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_review = {
                executor.submit(self.translation.translate, review): review 
                for review in self.reviews
            }
            self.translated_reviews = [
                future.result() 
                for future in as_completed(future_to_review)
            ]
        return self.translated_reviews

    def analyze_sentiment(self) -> List[SentimentSchema]:
        if len(self.translated_reviews) == 0:
            self.translate_reviews()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_review = {
                executor.submit(self.sentiment_analysis.analyze, review): review 
                for review in self.translated_reviews
            }
            self.sentiment_analysis_results = [
                future.result() 
                for future in as_completed(future_to_review)
            ]
        return self.sentiment_analysis_results

    def get_product_improvement(self) -> List[ProductImprovementSchema]:
        self.translate_reviews()
        self.analyze_sentiment()
        return self.product_improvement.generate_improvements(
            self.product_info, 
            self.sentiment_analysis_results
        )


