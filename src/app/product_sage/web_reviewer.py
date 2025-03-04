import os
from typing import Dict
from langchain_community.utilities import SerpAPIWrapper
import httpx
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from typing import List
class TitleSchema(BaseModel):
    title: str

class WebsiteReviewSchema(BaseModel):
    positive_points: List[str]
    negative_points: List[str]
    suggested_improvements: List[str]
    overall_rating: float


class ReviewSchema(BaseModel):
    source: str
    review: WebsiteReviewSchema
    favicon: str

class WebReviewer:
    def __init__(self, title: str):
        self.title = title
        self.llm = ChatGroq(temperature=0.7, model="gemma2-9b-it")
        self.search = SerpAPIWrapper(serpapi_api_key=os.getenv("SERP_API_KEY"))
        self.refined_title = None
        self.website_reviewer = WebsiteReviewer()
        self.websites_to_skip = ['https://www.amazon','https://www.reddit','https://www.youtube','https://www.instagram','https://www.tiktok','https://www.twitter','https://www.facebook','https://www.linkedin',]

        self.reviews:List[ReviewSchema] = []


    def refine_title(self):
        parser = PydanticOutputParser(pydantic_object=TitleSchema)
        prompt = PromptTemplate(
            template="""
            Input: [Full Product Description]
            Rules for Extracting Main Product Title:
            1. Remove parenthetical details (color, specifications, variants)
            2. Remove additional descriptive phrases
            3. Keep the core product name and primary category
            4. Prioritize the most specific and meaningful product identifier

            Desired Output: [Clean Product Title]

            For Example: Samsung Galaxy S25 Ultra 5G AI Smartphone (Titanium Whitesilver, 12GB RAM, 512GB Storage), 200MP Camera, S Pen Included, Long Battery Life

            -> Samsung Galaxy S25 Ultra 5G AI Smartphone

            Text to refine: {title}
            {format_instructions}""",
            input_variables=["title"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        formatted_prompt = prompt.format(title=self.title)
        messages = [
            SystemMessage(content="You are a helpful assistant that extracts clean product titles."),
            HumanMessage(content=formatted_prompt)
        ]
        response = self.llm.invoke(messages)
        self.refined_title = parser.parse(response.content).model_dump().get("title")
        return self.refined_title
    
    def get_top_website_content(self) -> Dict:
        """Returns content from the top search result website"""
        if not self.refined_title:
            self.refine_title()

        results = self.search.results(self.refined_title + "review")
        if not results.get("organic_results"):
            return {"error": "No results found"}
        count = 0
        for x in results["organic_results"]:
        # discard amazon links as we  have products data 
            if(x["link"].startswith(tuple(self.websites_to_skip))):
                continue
            else:
                url = x.get("link")
                review = self.website_reviewer.analyze_website(url)
                self.reviews.append(ReviewSchema(source=url,review=review,favicon=x.get("favicon")))
                count += 1
                if count == 2:
                    break


        return self.reviews



class WebsiteReviewer:
    def __init__(self):
        self.url = None
        self.llm = ChatGroq(temperature=0.7, model="deepseek-r1-distill-qwen-32b")
        self.parser = PydanticOutputParser(pydantic_object=WebsiteReviewSchema)

    def analyze_website(self, url: str) -> WebsiteReviewSchema:
        response = httpx.get(f"https://r.jina.ai/{url}", timeout=10)
        content = response.text[:10000]
        
        prompt = PromptTemplate(
        template="""
        Analyze the following product or service based on the given evaluation criteria:

        **Product/Service Description:**  
        {content}

        **Evaluation Criteria:**  
        1. **Positive Aspects:** Identify key strengths such as quality, usability, uniqueness, value for money, and customer satisfaction.  
        2. **Negative Aspects:** Highlight potential drawbacks, including usability issues, pricing concerns, durability, or missing features.  
        3. **Suggested Improvements:** Provide actionable recommendations to enhance the product/service based on identified weaknesses.  
        4. **Overall Assessment:** Give a concise summary, including a rating (out of 10) based on quality, user experience, and overall value.  

        **Output Format:**  
        {format_instructions}
        """,
        input_variables=["content"],
        partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

        formatted_prompt = prompt.format(content=content)
        messages = [
            SystemMessage(content="You are a helpful assistant that analyzes websites."),
            HumanMessage(content=formatted_prompt)
        ]
        response = self.llm.invoke(messages)
        return self.parser.parse(response.content)


    def get_website_content(self) -> Dict:
        pass