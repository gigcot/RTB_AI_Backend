from utils.common.state_manager import PhaseStateManager
class BasePhaseNodes:
    def __init__(self, llm_engine, env_manager):
        self.env_manager = env_manager  
        self.phase_manager = PhaseStateManager()  
        self.llm_engine = llm_engine

    def phase_prompt_update():
        raise NotImplementedError(" must be implemented in subclasses.")

    def phase_update(self):
        self.phase_manager.state = self.env_manager.get_full_state()
        
    def generate_messages(self):
        user_prompt = self.phase_prompt
        filled_prompt = user_prompt.format(**self.phase_manager.state)
        assistant_prompt = self.assistant_prompt
        return [
            {"role": "assistant", "content": assistant_prompt},
            {"role": "user", "content": filled_prompt}
        ]

    def call_llm(self, messages):
        response = self.llm_engine.call_openai_api(messages)
        return response

    def chatting(self):
        messages = self.generate_messages()
        response = self.call_llm(messages)
        return response

    def execute(self, state):
        self.phase_update()
        self.chatting()
        self.env_update()

    def env_update(self):
        self.env_manager.state = self.phase_manager.get_full_state()
        raise NotImplementedError(" must be implemented in subclasses.")
