import concurrent.futures
import os
from typing import Dict, List
import httpx
from langchain_community.utilities import SerpAPIWrapper
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from ...config.llm import AIModels
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
        self.llm = AIModels().llama_4_mavrick()
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
            {format_instructions}
            Respond only with valid JSON. Do not write an introduction or summary.
            """,
            
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
    
    def get_top_website_content(self) -> List[ReviewSchema]:
        if not self.refined_title:
            self.refine_title()

        results = self.search.results(self.refined_title + " review")
        if not results.get("organic_results"):
            return {"error": "No results found"}

        # Filter valid URLs first
        valid_entries = []
        for entry in results["organic_results"]:
            if any(entry.get("link", "").startswith(site) for site in self.websites_to_skip):
                continue
            valid_entries.append(entry)
            if len(valid_entries) == 2:
                break

        # Process valid entries in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self._process_single_website, entry)
                for entry in valid_entries
            }
            for future in concurrent.futures.as_completed(futures):
                try:
                    review = future.result()
                    self.reviews.append(review)
                except Exception as e:
                    # Handle or log exceptions as needed
                    pass

        return self.reviews
    
    def _process_single_website(self, entry: dict) -> ReviewSchema:
        """Process a single website entry and return ReviewSchema"""
        url = entry.get("link")
        favicon = entry.get("favicon", "")
        review = self.website_reviewer.analyze_website(url)
        return ReviewSchema(
            source=url,
            review=review,
            favicon=favicon
        )



class WebsiteReviewer:
    def __init__(self):
        self.url = None
        self.llm = AIModels().llama_4_mavrick()
        self.parser = PydanticOutputParser(pydantic_object=WebsiteReviewSchema)

    def analyze_website(self, url: str) -> WebsiteReviewSchema:
        response = httpx.get(f"https://r.jina.ai/{url}", timeout=10)
        content = response.text[:30000]
        
        prompt = PromptTemplate(
            template="""
            You are tasked with reviewing the following product or service based on its **core features and real-world performance**.
            Your analysis should focus exclusively on the product itself, evaluating its quality, functionality, and overall value.

            **Product/Service Description:**  
            {content}

            **Evaluation Criteria:**  
            1. **Build Quality & Design:** Assess the durability, material quality, aesthetics, and ergonomics.
            2. **Performance & Usability:** Evaluate efficiency, ease of use, reliability, and effectiveness in real-world scenarios.
            3. **Features & Functionality:** Analyze the key features, unique selling points, and compare them with similar products.
            4. **Value for Money:** Determine if the product justifies its price based on its features, longevity, and user experience.
            5. **Pros & Cons:** Clearly outline the advantages and disadvantages based on the factors above.
            6. **Final Verdict:** Provide a concise summary with a rating (out of 10) reflecting the overall performance and value.

            **Output Format:**  
            {format_instructions}

            *Note: Ensure that your review strictly addresses the product or service itself, with no references to website design or online presentation.*

            Respond only with valid JSON. Do not write an introduction or summary.
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