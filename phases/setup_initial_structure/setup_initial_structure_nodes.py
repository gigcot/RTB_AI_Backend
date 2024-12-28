from utils.common.base_phase_nodes import BasePhaseNodes
from .setup_initial_structure_prompts import *
from utils.phase_utils.setup_initial_structure_phase_utils import check_answer_in_init_structure
class SetupInitialStructurePhaseNodes(BasePhaseNodes):
    def __init__(self, llm_engine, env_manager):
        super().__init__(llm_engine, env_manager)
        self.phase_prompt_update()
    def phase_prompt_update(self):
        self.phase_prompt = phase_prompt
        self.assistant_role_prompt = assistant_role_prompt
        self.assistant_role_name = assistant_role_name

    def phase_update(self, state):# execute에서 루프문ㄷ만들고 그거 돌아가도록 업데이트 작업
        self.phase_manager.state['task'] = state.get('task')
        self.phase_manager.state['demand_analysis_result'] = self.env_manager.state['demand_analysis_result']
        self.phase_manager.state['return_type_violation_in_inital_structure'] = self.env_manager.state['return_type_violation_in_inital_structure']

    def env_update(self):
        self.env_manager.state["initial_structure"] = self.phase_manager.state['initial_structure']
    def execute(self, state):
        self.phase_update(state)
        while True:
            error_message,is_correct,code_block_content = check_answer_in_init_structure(self.chatting())
            self.logger.info(f"\nmessage: {error_message}, is_correct: {is_correct}\n")
            if is_correct:
                self.phase_manager.state['initial_structure'] = code_block_content
                self.env_update()
                self.logger.info(f"\nstructure:\n{code_block_content}\n")
                break
            if is_correct is not True:
                self.phase_manager.state['return_type_violation_in_inital_structure'] = error_message
                continue
            return