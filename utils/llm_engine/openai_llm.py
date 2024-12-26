from langchain_openai import ChatOpenAI
from .base_llm_engine import BaseLLMEngine

class OpenAIEngine(BaseLLMEngine):
    def __init__(self, api_key, model_name, max_tokens=16000, temperature=0.7, top_p=0.8):
        self.model = model_name
        # self.api_key = api_key
        # self.max_tokens = max_tokens
        # self.temperature = temperature
        # self.top_p = top_p
        llm_config = ChatOpenAI(
            api_key=api_key,
            model=model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )
        super().__init__(llm_config)