from tenacity import retry, stop_after_attempt, wait_exponential

class BaseLLMEngine:
    def __init__(self, llm_config):
        self.llm = llm_config

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def call_openai_api(self, messages):
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            print(f"LLM 호출 중 오류 발생: {e}")
            raise