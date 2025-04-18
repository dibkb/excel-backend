import json
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from .web_search import TopWebsiteSearch
from ...config.llm import AIModels
class ProductEnhancer:
    def __init__(self,product_data: Dict[str, Any]):
        self.llm = AIModels().llama_4_mavrick()
        self.web_search = TopWebsiteSearch(product_data['title'])
        self.title = product_data['title']
        self.highlights = product_data['description']['highlights']
        self.technical = product_data['specifications']['technical']
        self.additional = product_data['specifications']['additional']

    def generate_enhanced_listing(self) -> Dict[str, Any]:
        # Get additional info from web search
        web_info = self.web_search.get_top_website_content()
        
        prompt = f"""
        You are a professional Amazon listing optimizer tasked with enhancing product listings.

        IMPORTANT: Your response MUST be ONLY valid JSON with NO explanations, thoughts, or markdown.

        Enhance the following product listing by incorporating original product data with web research:

        **Original Product Data:**
        - Title: `{self.title}`
        - Highlights: `{self.highlights}`
        - Technical: `{self.technical}`
        - Additional: `{self.additional}`

        **Web Research Information:**
        - `{web_info}`

        Guidelines:
        1. Enhance the title with essential keywords (under 200 characters)
        2. Generate detailed highlights as an array of strings
        3. Improve additional information as key-value pairs
        4. Refine technical specifications as key-value pairs

        {{
            "title": "Enhanced Product Title",
            "highlights": [
                "Enhanced Highlight 1",
                "Enhanced Highlight 2",
                "Enhanced Highlight 3"
            ],
            "additional": {{
                "Enhanced Additional Key 1": "Enhanced Value 1",
                "Enhanced Additional Key 2": "Enhanced Value 2"
            }},
            "technical": {{
                "Enhanced Technical Key 1": "Enhanced Value 1",
                "Enhanced Technical Key 2": "Enhanced Value 2"
            }},
            "source": "{web_info['source'] if isinstance(web_info, dict) and 'source' in web_info else ''}"
        }}
        Respond only with valid JSON. Do not write an introduction or summary.
        """

        messages = [
            SystemMessage(content="You are an e-commerce product listing optimizer. Return ONLY valid JSON with no explanations."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Clean and parse the response
        try:
            content = response.content
            
            # Remove any markdown code block markers
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
                
            # Find and extract just the JSON part if there's explanation text
            if '{' in content and '}' in content:
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                content = content[start_idx:end_idx]
                
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            # Return a basic structure if parsing fails
            return {
                "title": self.title,
                "highlights": self.highlights,
                "additional": self.additional,
                "technical": self.technical
            }