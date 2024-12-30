from langgraph.graph import StateGraph, START, END
from phases.demand_analysis.demand_analysis_graph import DemandAnalysisGraph
from phases.setup_initial_structure.setup_initial_structure_graph import SetupInitialStructureGraph
from phases.writing_skeleton_code.writing_skeleton_code_graph import WritingSkeletonCodeGraph
from phases.implementation_sequencing.implementation_sequencing_graph import ImplementationSequencingGraph
from phases.impl_and_test_for_commit.impl_and_test_for_commit_graph import ImplAndTestForCommitGraph
from utils.common.state_manager import EnvStateManager
from utils.llm_engine.openai_llm import OpenAIEngine
from .env_states import states
class MainGraph:
    def __init__(self, api_key, model_name, max_tokens):
        all_states = states
        self.env_manager = EnvStateManager(all_states)
        self.env_manager.state["current_step"] = 1 # TODO: dataclass사용해서 변경
        self.llm_engine = OpenAIEngine(
                                        api_key=api_key,
                                        model_name=model_name,
                                        max_tokens=max_tokens
                                        )
        self.builder = StateGraph(dict)
        
        def compile_and_setup_run(graph):
            return lambda state: graph.compile().invoke(state)
        demand_analysis_graph = DemandAnalysisGraph(self.llm_engine, self.env_manager)
        setup_initial_structure = SetupInitialStructureGraph(self.llm_engine, self.env_manager)
        writing_skeleton_code = WritingSkeletonCodeGraph(self.llm_engine, self.env_manager)
        implementaion_sequencing = ImplementationSequencingGraph(self.llm_engine, self.env_manager)
        impl_and_test_for_commit = ImplAndTestForCommitGraph(self.llm_engine, self.env_manager)
        self.builder.add_node("demand_analysis", compile_and_setup_run(demand_analysis_graph))
        self.builder.add_node("setup_initial_structure", compile_and_setup_run(setup_initial_structure))
        self.builder.add_node("writing_skeleton_code", compile_and_setup_run(writing_skeleton_code))
        self.builder.add_node("implementaion_sequencing", compile_and_setup_run(implementaion_sequencing))
        self.builder.add_node("impl_and_test_for_commit", compile_and_setup_run(impl_and_test_for_commit))
        # 노드 연결
        self.builder.add_edge(START, "demand_analysis")
        self.builder.add_edge("demand_analysis", "setup_initial_structure")
        self.builder.add_edge("setup_initial_structure", "writing_skeleton_code")
        self.builder.add_edge("writing_skeleton_code", "implementaion_sequencing")
        self.builder.add_edge("implementaion_sequencing", "impl_and_test_for_commit")
    
    def run(self, initial_state):
        # 그래프 실행
        graph = self.builder.compile()
        graph.invoke(initial_state)