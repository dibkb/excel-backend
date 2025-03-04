from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel

class TranslationSchema(BaseModel):
    language: str 
    translation: str

class Translation():
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.3, model="gpt-4o-mini")
        self.parser = PydanticOutputParser(pydantic_object=TranslationSchema)
        self.prompt = PromptTemplate(
            template="""You are a language detection and translation expert. Analyze the following text:
            1. Detect the language of the input text
            2. If the text is not in English:
               - Translate it to English naturally and accurately
               - Preserve the original meaning and sentiment
            3. If the text is already in English, return it unchanged
            
            For the output:
            - 'language' should be the ISO language code (e.g., 'en', 'es', 'fr')
            - 'translation' should be the English translation (or original text if already English)
            
            Text to analyze: {text}
            {format_instructions}""",
            input_variables=["text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

    def translate(self, text: str) -> TranslationSchema:
        formatted_prompt = self.prompt.format(text=text)

        response = self.llm.invoke(formatted_prompt)
        
        return self.parser.parse(response.content)

