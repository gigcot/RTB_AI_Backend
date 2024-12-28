from utils.common.base_phase_nodes import BasePhaseNodes
from .writing_skeleton_code_prompts import *
from utils.phase_utils.writing_skeleton_codes_utils import validate_response_format, parse_text, rewrite_codes
from utils.phase_utils.common_phase_utils import load_codes_from_hardware
class WritingSkeletonCodePhaseNodes(BasePhaseNodes):
    def __init__(self, llm_engine, env_manager):
        super().__init__(llm_engine, env_manager)
        self.phase_prompt_update()
        self.output_dir = "./output"
    def phase_prompt_update(self):
        self.phase_prompt = phase_prompt
        self.assistant_role_name = assistant_role_name
        self.assistant_role_prompt = assistant_role_prompt

    def phase_update(self, state):
        self.phase_manager.state['task'] = state.get('task')
        self.phase_manager.state['initial_structure'] = self.env_manager.state['initial_structure']
        self.phase_manager.state['return_type_violation_in_writing_skeleton_code'] = self.env_manager.state['return_type_violation_in_writing_skeleton_code']

    def env_update(self):
        self.env_manager.state["skeleton_code"] = load_codes_from_hardware(self.output_dir)
    def execute(self, state):
        self.phase_update(state)
        while True:
            response = self.chatting()
            message, is_valid = validate_response_format(response)
            if not is_valid:
                self.phase_manager.state['return_type_violation_in_writing_skeleton_code'] = message
                continue
            if is_valid:
                path_and_codes = parse_text(response)
                rewrite_codes(path_and_codes, base_path=self.output_dir)
                break
        self.env_update()
    