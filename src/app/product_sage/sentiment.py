from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel

class SentimentSchema(BaseModel):
    sentiment: str 
    features: str
    key_aspects: str


class SentimentAnalysis():
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.1, model="gpt-4o-mini")
        self.parser = PydanticOutputParser(pydantic_object=SentimentSchema)
        self.prompt = PromptTemplate(
            template="""You are an expert sentiment analyzer. Analyze the following customer review:
            {text}

            Provide a single analysis in the following format:
            - sentiment: [Positive/Negative/Neutral]
            - features: [comma-separated list of product features mentioned]
            - key_aspects: [comma-separated list of main positive and negative points]

            {format_instructions}""",
                input_variables=["text"],
                partial_variables={"format_instructions": self.parser.get_format_instructions()}
            )

    def analyze(self, text: str) -> SentimentSchema:
        formatted_prompt = self.prompt.format(text=text)
        response = self.llm.invoke(formatted_prompt)
        return self.parser.parse(response.content)


