from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from ..config.main import settings

class AIModels:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIModels, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        self.chatgpt_4o_model = ChatOpenAI(model="gpt-4o", temperature=0.7, api_key=settings.OPENAI_API_KEY)
        self.llama_4_mavrick_model = ChatGroq(temperature=0.7, model="meta-llama/llama-4-maverick-17b-128e-instruct", api_key=settings.GROQ_API_KEY)
        self.llama_3_8b_model = ChatGroq(temperature=0.7, model="llama-3.3-70b-versatile", api_key=settings.GROQ_API_KEY)

    def chatgpt_4o(self):
        return self.chatgpt_4o_model
    
    def llama_4_mavrick(self):
        return self.llama_4_mavrick_model
    