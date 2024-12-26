from utils.common.base_phase_nodes import BasePhaseNodes
from .demand_analysis_prompts import *
class DemandAnalysisPhaseNodes(BasePhaseNodes):
    def __init__(self, llm_engine, env_manager):
        super().__init__(llm_engine, env_manager)
        self.phase_prompt_update()
    def phase_prompt_update(self):    
        self.phase_prompt = phase_prompt
        self.assistant_prompt = assistant_role_prompt

    def phase_update(self, state):
        print(f"\n\nstate:{state}\n\ntype:{type(state)}\n\n")
        self.phase_manager.state['task'] = state.get('task')
    def env_update(self):
        print(f"\n\nself.env_manager:{self.env_manager.state}\n\n")
        self.env_manager.state["demand_analysis_result"] = self.response
        print(f"\n\nself.env_manager:{self.env_manager.state}\n\n")
    def execute(self, state):
        self.phase_update(state)
        self.response = self.chatting()
        self.env_update()