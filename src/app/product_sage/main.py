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
        self._reviews_translated = False
        self._sentiment_analyzed = False


    def translate_reviews(self) -> List[str]:
        if not self._reviews_translated:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_review = {
                    executor.submit(self.translation.translate, review): review 
                    for review in self.reviews
                }
                self.translated_reviews = [
                    future.result() 
                    for future in as_completed(future_to_review)
                ]
            self._reviews_translated = True
        return self.translated_reviews

    def analyze_sentiment(self) -> List[SentimentSchema]:
        self.translate_reviews()  # Ensure reviews are translated first
    
        if not self._sentiment_analyzed:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_review = {
                    executor.submit(self.sentiment_analysis.analyze, review): review 
                    for review in self.translated_reviews
                }
                self.sentiment_analysis_results = [
                    future.result() 
                    for future in as_completed(future_to_review)
                ]
            self._sentiment_analyzed = True
        return self.sentiment_analysis_results
    
    def get_analysis(self) -> List[SentimentSchema]:
        return self.analyze_sentiment()
    
    def get_product_improvement(self) -> List[ProductImprovementSchema]:
        self.analyze_sentiment() 
        return self.product_improvement.generate_improvements(
            self.product_info, 
            self.sentiment_analysis_results
        )


