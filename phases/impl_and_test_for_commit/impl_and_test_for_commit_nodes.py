from utils.common.base_phase_nodes import BasePhaseNodes
from .impl_and_test_for_commit_prompts import *
from utils.phase_utils.writing_skeleton_codes_utils import parse_text, rewrite_codes
from utils.phase_utils.common_phase_utils import load_codes_from_hardware
from utils.phase_utils.impl_and_test_for_commit_phase_utils import build_docker_image, count_steps, extract_test_file, remove_pycache_dirs, verify_functionality,validate_response_format
from utils.docker.docker_manager import DockerManager

class ImplAndTestForCommitPhaseNodes(BasePhaseNodes):
    def __init__(self, llm_engine, env_manager):
        super().__init__(llm_engine, env_manager)
        self.phase_prompt_update()
        self.output_dir = "output"
    def phase_prompt_update(self):
        self.phase_prompt = phase_prompt
        self.assistant_role_name = assistant_role_name
        self.assistant_role_prompt = assistant_role_prompt

    def phase_update(self, state):
        self.phase_manager.state['task'] = state.get('task')
        self.phase_manager.state['initial_structure'] = self.env_manager.state['initial_structure']
        self.phase_manager.state['current_step'] = self.env_manager.state['current_step']
        self.phase_manager.state['error_code'] = self.env_manager.state['error_code']
        self.phase_manager.state['impl_step'] = self.env_manager.state['impl_step']
        self.phase_manager.state['skeleton_code'] = load_codes_from_hardware(self.output_dir)

    def env_update(self):
        self.env_manager.state["skeleton_code"] = load_codes_from_hardware(self.output_dir)

    def execute(self,state):
        import os

        abs_path = os.path.abspath("utils/docker")# dockerfile path
        if build_docker_image(path=abs_path, tag="using_xvfb:v1"):
            print("이미지 빌드 성공. 다음 작업을 진행합니다.")
        else:
            print("이미지 빌드에 실패했습니다.")

        container = DockerManager.get_container(
                                                            "si_foIIow_test",
                                                            volume=self.output_dir,
                                                            image_name="using_xvfb:v1",
                                                            )
        self.phase_update(state)
        self.logger.info(f"{self.phase_manager.state['impl_step']}\n==> 입력된 impl_step입니다.")
        self.phase_manager.state["total_step_num"] = count_steps(self.phase_manager.state["impl_step"])
        self.logger.info(f"{self.phase_manager.state['total_step_num']}\n==> 계산된 step 수 입니다")
        is_error_in_conclusion = False
        for step in range(1, self.phase_manager.state['total_step_num']+1): 
            self.logger.info(f"[ {step} ] 단계 작업입니다.")
            code_error_resolve_attempts = 1
            while True:
                self.phase_update(state)
                
                if is_error_in_conclusion :
                    self.phase_manager.state["error_code"] = error_message_in_validate
                
                self.phase_manager.state["code_error_resolve_attempts"] = code_error_resolve_attempts
                seminar_conclusion = self.chatting()

                if not (result := validate_response_format(seminar_conclusion))[1]:
                    error_message_in_validate = result[0]
                    self.logger.info(f"반환형식위반: {error_message_in_validate}")
                    self.phase_manager.state["error_code"] = error_message_in_validate
                    is_error_in_conclusion = True
                    continue
                clean_modified_codes=parse_text(seminar_conclusion)
                rewrite_codes(clean_modified_codes, base_path=self.output_dir) # 하드웨어에 직접 덮어씀
                file_path, file_name = extract_test_file(seminar_conclusion)
                error_code, is_step_complete = verify_functionality(file_path, file_name, container, self.output_dir)
                self.logger.info(f"error code: {error_code},\nis_step_complete: {is_step_complete}")
                remove_pycache_dirs(self.output_dir)
                if is_step_complete != True:
                    code_error_resolve_attempts += 1
                    if code_error_resolve_attempts == 4:
                        self.logger.info(f"{step}단계 오류수정 시도 {code_error_resolve_attempts-1}회로 제한 횟수 초과하여 다음 구현 단계로 넘어갑니다.")
                        self.env_update()
                        self.env_manager.state["current_step"] += 1
                        self.env_manager.state["error_code"] = ""
                        is_error_in_conclusion = False
                        break 
                    self.env_update()
                    self.env_manager.state["error_code"] = error_code
                    self.logger.info(f"**[{step}]Step 실패.**\n**[ERROR CODE]**: {error_code}")
                    is_error_in_conclusion = False
                    continue

                if is_step_complete == True:
                    self.env_update()
                    self.env_manager.state["error_code"] = ""
                    self.env_manager.state["current_step"] += 1
                    is_error_in_conclusion = False
                    code_error_resolve_attempts = 1
                    #TODO: git commit
                    break
            self.logger.info(f"{step}step completed")
        self.logger.info("all staeps completed.")

        return

    