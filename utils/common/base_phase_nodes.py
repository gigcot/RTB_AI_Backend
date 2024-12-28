from utils.common.state_manager import PhaseStateManager
from utils.common.logging import Logger

class BasePhaseNodes:
    def __init__(self, llm_engine, env_manager):
        self.env_manager = env_manager  
        self.phase_manager = PhaseStateManager()  
        self.llm_engine = llm_engine
        self.logger = Logger(f"{self.__class__.__name__.replace('PhaseNodes','')}").get_logger()
        self.si_follow_prompt = "당신은 SI-Follow의 AI 조직원입니다. SI-Follow는 고객의 요구에 맞춘 신뢰성 있는 맞춤형 소프트웨어 솔루션을 제공하는 AI IT파트너입니다.조직원 모두 명확한 역할을 맡아 협력하고 있으며, 프로젝트의 성공을 목표로 합니다."
    def phase_prompt_update():
        raise NotImplementedError(" must be implemented in subclasses.")

    def phase_update(self):
        self.phase_manager.state = self.env_manager.get_full_state()
        
    def generate_messages(self):
        user_prompt = self.phase_prompt.format(**self.phase_manager.state)
        assistant_prompt = self.assistant_role_prompt.format(**self.phase_manager.state)
        return [
                {"role": "system", "content": self.si_follow_prompt},
                {"role": "user", "name": "coworker", "content": user_prompt},
                {"role": "assistant", "name": self.assistant_role_name, "content": assistant_prompt},
                ]

    def call_llm(self, messages):
        response = self.llm_engine.call_openai_api(messages)
        return response

    def chatting(self):
        messages = self.generate_messages()
        self.logger.info(f"\n\nassistant:\n {messages[0]['content']}\n\nuser:\n{messages[1]['content']}\n\n")

        response = self.call_llm(messages)
        self.logger.info(f"\n\nresponse:\n{response}\n\n")
        return response

    def execute(self, state):
        self.phase_update()
        self.chatting()
        self.env_update()

    def env_update(self):
        self.env_manager.state = self.phase_manager.get_full_state()
        raise NotImplementedError(" must be implemented in subclasses.")
