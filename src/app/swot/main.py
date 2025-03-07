from typing import Dict, List
import httpx
import os
import dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.prompts import PromptTemplate
from typing import Optional
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel
import asyncio

dotenv.load_dotenv()

class SwotAnalysisSchema(BaseModel):
    heading: str
    description: str


class SwotAnalysisConsolidated(BaseModel):
    analysis: Dict[str, List[SwotAnalysisSchema]]

class Swot:
    def __init__(self, asin: str,competitors: List[str]):
        self.asin = asin
        self.competitors = competitors
        self.llm = ChatGroq(temperature=0.7, model="llama-3.3-70b-versatile")
        self.parser_consolidated = PydanticOutputParser(pydantic_object=SwotAnalysisConsolidated)

    async def load_asin_info(self,asin:str):

        client = httpx.AsyncClient()
        response = await client.get(f"{os.getenv('BACKEND_URL')}/amazon/{asin}")
        product = response.json()
        product_info = {
            "description": product["description"],
            "specifications": product["specifications"]
        }

        response = await client.get(f"{os.getenv('BACKEND_URL')}/amazon/product-sage/{asin}")
        product_sage = response.json()
        product_info["sentiments"] = product_sage["sentiments"]
        product_info["improvements"] = product_sage["improvements"]

        response = await client.get(f"{os.getenv('BACKEND_URL')}/amazon/product-sage/web-reviewer/{asin}")
        product_web_reviewer = response.json()
        product_info["web_reviewer"] = product_web_reviewer

        return product_info
    
    def process_swot_components(self, data: Dict) -> Dict:
        """Extract SWOT components from structured data"""
        components = {
            'strengths': [],
            'weaknesses': [],
            'opportunities': [],
            'threats': []
        }

        # Process strengths
        components['strengths'].extend(data['description']['highlights'])
        components['strengths'].extend([
            rev['review']['positive_points'] for rev in data['web_reviewer']
        ])
        components['strengths'].extend([
            f"{s['features']} ({s['sentiment']})" 
            for s in data['sentiments'] 
            if s['sentiment'] == 'positive'
        ])

        # Process weaknesses
        components['weaknesses'].extend([
            rev['review']['negative_points'] for rev in data['web_reviewer']
        ])
        components['weaknesses'].extend([
            imp['improvement'] for imp in data['improvements']
        ])

        # Process opportunities
        components['opportunities'].extend([
            imp['improvement'] for imp in data['improvements']
        ])

        return components



    def generate_comparison_prompt(self, 
                                main: Dict,
                                competitors: List[Dict]) -> str:
        """Generate optimized prompt for consolidated SWOT analysis"""
        # Aggregate competitor data
        comp_strengths = set()
        comp_weaknesses = set()
        
        for comp in competitors:
            comp_strengths.update(
                [item for sublist in comp['strengths'] for item in (sublist if isinstance(sublist, list) else [sublist])]
            )
            comp_weaknesses.update(
                [item for sublist in comp['weaknesses'] for item in (sublist if isinstance(sublist, list) else [sublist])]
            )

        template = f"""Generate a consolidated SWOT analysis comparing our product against all competitors. 
        Focus on technical specifications and market positioning.

        Product Data:
        - Strengths: {main['strengths']}
        - Weaknesses: {main['weaknesses']}
        - Opportunities: {main['opportunities']}
        - Threats: {main['threats']}

        Competitor Landscape:
        - Common Strengths Across Competitors: {', '.join(comp_strengths)}
        - Common Weaknesses Across Competitors: {', '.join(comp_weaknesses)}

        {self.parser_consolidated.get_format_instructions()}

        Analysis Guidelines:
        - Prioritize technical specifications from product data
        - Highlight market differentiators
        - Include 3-5 items per category
        - Use comparative language ("X% faster than competitors")
        - Reference specific competitor capabilities
        - Maintain strict JSON validity (no comments, proper escaping)

        Example Structure:
        "strengths": [
            {{
                "heading": "Superior Read Performance",
                "description": "15% faster read speeds compared to average competitor SSDs in same price tier"
            }}
        ]
        """

        return template

    
    async def analyze(self)->SwotAnalysisConsolidated:
        main_data = await self.load_asin_info(self.asin)
        main_components = self.process_swot_components(main_data)
        
        # Process competitors in parallel using asyncio.gather
        competitor_tasks = [self.load_asin_info(competitor) for competitor in self.competitors]
        competitor_data = await asyncio.gather(*competitor_tasks)
        competitor_components = [self.process_swot_components(cdata) for cdata in competitor_data]

        prompt = self.generate_comparison_prompt(main_components, 
                                         competitor_components)
        
        response = self.llm.invoke(prompt)
        output = self.parser_consolidated.parse(response.content)
        return output