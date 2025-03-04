from typing import List

from ..schemas.product_sage import Specifications
from .sentiment import SentimentSchema
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel

class ProductImprovementSchema(BaseModel):
    improvement: str 
    affected_component: str
    expected_impact: str
    priority_level: str
    implementation_complexity: str

class ProductImprovements(BaseModel):
    improvements: List[ProductImprovementSchema]

class ProductImprovement:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.1,
            model="gpt-4o-mini",
            model_kwargs={"response_format": {"type": "json_object"}}
        )
        self.parser = PydanticOutputParser(pydantic_object=ProductImprovements)
        self.prompt = PromptTemplate(
            template="""You are a product development expert. Analyze the provided product information and customer feedback to suggest technical improvements.

            Guidelines:
            - Provide 3-5 distinct improvement suggestions
            - Prioritize improvements that address customer pain points
            - Ensure suggestions are technically feasible
            - Consider cost-benefit ratio
            - Focus on measurable impacts
            - customer sentiment analysis if of the format:
                sentiment: [Positive/Negative/Neutral]
                features: [comma-separated list of product features mentioned]
                key_aspects: [comma-separated list of main positive and negative points]
            
            Focus areas:
            - Core functionality enhancements
            - Technical specifications improvements
            - Manufacturing feasible changes
            - Cost-effective upgrades
            
            Product Information:
            {product_info}
            
            Customer Feedback Analysis:

            {analysis}
            
            {format_instructions}""",
            input_variables=["product_info", "analysis"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        
    def generate_improvements(self, product_info: Specifications, analysis: List[SentimentSchema]) -> List[ProductImprovementSchema]:
        try:
            # Format the analysis list into a more readable string format
            formatted_analysis = "\n".join([
                f"Review {i+1}:\n"
                f"- Sentiment: {review.sentiment}\n"
                f"- Features: {', '.join(review.features)}\n"
                f"- Key Aspects: {', '.join(review.key_aspects)}\n"
                for i, review in enumerate(analysis)
            ])
            
            formatted_prompt = self.prompt.format(
                product_info=product_info, 
                analysis=formatted_analysis
            )
            response = self.llm.invoke(formatted_prompt)
            parsed_response: ProductImprovements = self.parser.parse(response.content)
            return parsed_response.improvements
        
        except Exception as e:
            raise ValueError(f"Failed to generate improvements: {str(e)}")