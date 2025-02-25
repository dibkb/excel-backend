from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from typing import List, Dict
import re



class ProductImprovementAgent:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.3, model="gpt-4o-mini")
        self.system_message = SystemMessage(content="""
            You are a product development expert. Suggest technical improvements based on:
            1. Actual product specifications
            2. Analyzed customer feedback
            
            Focus on:
            - Core functionality enhancements
            - Technical specifications improvements
            - Manufacturing feasible changes
            - Cost-effective upgrades
            
            Format:
            Improvement [X]: [Technical Description]
            Affected Component: [Specific product part]
            Expected Impact: [Performance improvement estimate]
        """)
    
    def generate_improvements(self, product_info: str, analysis: str) -> str:
        response = self.llm([
            self.system_message,
            HumanMessage(content=f"Product Specifications:\n{product_info}\n\nReview Analysis:\n{analysis}")
        ])
        return response.content
    


class ProductImprovementValidator:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.0, model="gpt-4")
        self.system_message = SystemMessage(content="""
            You are a manufacturing validation system. Strictly evaluate improvements against:
            1. Current product specifications
            2. Technical feasibility
            3. Review evidence base
            4. Core value impact
            
            Validation Criteria:
            [✓] Direct technical relevance to existing components
            [✓] Minimum 3 review mentions for proposed changes
            [✓] Physically compatible with current design
            [✓] Cost-effective manufacturing
            
            Output Format per Improvement:
            [Improvement X]
            Status: [Approved/Rejected]
            Core Impact: High/Medium/Low
            Feasibility: Simple/Moderate/Complex
            Priority: Critical/Important/Nice-to-have
            Evidence:
            - Spec Reference: [exact spec text]
            - Review Support: [review numbers]
            - Technical Assessment: [engineering analysis]
            
            Final Priority Ranking:
            1. [Most critical improvement]
            Implementation Cost Estimate: [$ - $$$$]
            Expected Impact: [1-5 stars]
            """)

    def validate(self, product_info: str, analysis: str, improvements: str) -> Dict:
        response = self.llm.invoke([
            self.system_message,
            HumanMessage(content=f"PRODUCT SPECS:\n{product_info}\n\n"
                                f"ANALYZED REVIEWS:\n{analysis}\n\n"
                                f"SUGGESTED IMPROVEMENTS:\n{improvements}")
        ])
        return self._structure_output(response.content)
    
    def _structure_output(self, text: str) -> Dict:
        return {
            "detailed_validation": text,
            "priority_list": self._extract_priority(text),
            "rejected_suggestions": self._extract_rejected(text),
            "cost_estimates": self._extract_costs(text)
        }
    
    def _extract_priority(self, text: str) -> List:
        return re.findall(r"\d+\.\s(.+?)\nImplementation", text, re.DOTALL)
    
    def _extract_rejected(self, text: str) -> List:
        return re.findall(r"\[Rejected\]\n(.+?)(?=\n\[)", text, re.DOTALL)
    
    def _extract_costs(self, text: str) -> Dict:
        return dict(re.findall(r"([a-zA-Z ]+)\nImplementation Cost Estimate: (\$+\+?)", text))
    


class ReActOrchestrator:
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalysisAgent()
        self.improvement_generator = ProductImprovementAgent()
        self.validator = ProductImprovementValidator()
    
    def process(self, product_info: str, reviews: List[str]) -> Dict:
        analysis = self.sentiment_analyzer.analyze_reviews(reviews)
        # improvements = self.improvement_generator.generate_improvements(product_info, analysis)
        # validation = self.validator.validate(product_info, analysis, improvements)
    
        return analysis

