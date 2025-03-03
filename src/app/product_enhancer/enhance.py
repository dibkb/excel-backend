import json
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from .web_search import TopWebsiteSearch

class ProductEnhancer:
    def __init__(self,product_data: Dict[str, Any]):
        self.llm = ChatGroq(temperature=0.7, model="llama-3.3-70b-versatile")
        self.web_search = TopWebsiteSearch(product_data['title'])
        self.title = product_data['title']
        self.highlights = product_data['description']['highlights']
        self.technical = product_data['specifications']['technical']
        self.additional = product_data['specifications']['additional']

    def generate_enhanced_listing(self) -> Dict[str, Any]:
        # Get additional info from web search
        web_info = self.web_search.get_top_website_content()
        
        prompt = f"""
        You are a professional Amazon listing optimizer. Your task is to enhance an existing product listing by integrating original product data with relevant web research insights. Your objective is to improve clarity, detail, and keyword optimization while ensuring technical accuracy. Please follow these guidelines:

        1. **Technical Information:** Enhance the content by incorporating essential keywords, ensuring the total text remains under 200 characters.
        2. **Highlights:** Generate a detailed yet concise list of selling points formatted as an array of strings.
        3. **Additional Information:** Present comprehensive and concise key-value pairs. You may use existing details, add new key-value pairs, or remove those that do not enhance the listing.
        4. **Technical Specifications:** Refine clarity using key-value pairs. Similarly, you can retain, add, or remove key-value pairs as you deem fit to improve the section.

        **Input Data:**

        - **Original Product Data:**
        - Title: `{self.title}`
        - Highlights: `{self.highlights}`
        - Technical: `{self.technical}`
        - Additional: `{self.additional}`

        - **Web Research Information:**
        - `{web_info}`

        **Output Requirements:**

        Return ONLY valid JSON that strictly adheres to the structure below, with all fields enhanced accordingly:

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
        """

        messages = [
            SystemMessage(content="You are a expert e-commerce product listing optimizer."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Clean and parse the response
        try:
            content = response.content
            # Remove markdown code block markers if present
            if content.startswith('```json'):
                content = content.replace('```json\n', '', 1)
                content = content.replace('\n```', '', 1)
            elif content.startswith('```'):
                content = content.replace('```\n', '', 1)
                content = content.replace('\n```', '', 1)
                
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