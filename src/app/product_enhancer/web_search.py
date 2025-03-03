import os
from langchain_community.utilities import SerpAPIWrapper
from typing import Dict
import httpx
class TopWebsiteSearch:
    def __init__(self,title):
        self.search = SerpAPIWrapper(serpapi_api_key=os.getenv("SERP_API_KEY")) 

        self.title = title
    
    def get_top_website_content(self) -> Dict:
        """Returns content from the top search result website"""
        results = self.search.results(self.title)
        
        if not results.get("organic_results"):
            return {"error": "No results found"}
            
        for x in results["organic_results"]:
            # discard amazon links as we  have products data 
            if(x["link"].startswith("https://www.amazon")):
                continue
            else:
                url = x.get("link")
                break
        
        try:
            response = httpx.get(f"https://r.jina.ai/{url}", timeout=10)
            
            return {
                "source": url,
                "content": response.text[:10000],
            }
            
        except Exception as e:
            return {"error": str(e), "source": url}