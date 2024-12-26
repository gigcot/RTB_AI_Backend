from langgraph.graph import StateGraph, START, END
from phases.demand_analysis.demand_analysis_graph import DemandAnalysisGraph
from utils.common.state_manager import EnvStateManager
from utils.llm_engine.openai_llm import OpenAIEngine

class MainGraph:
    def __init__(self, api_key, model_name, max_tokens):
        self.env_manager = EnvStateManager()
        self.llm_engine = OpenAIEngine(
                                        api_key=api_key,
                                        model_name=model_name,
                                        max_tokens=max_tokens
                                        )
        self.builder = StateGraph(dict)
        # self.builder.add_node("task_update",lambda task_update: self.env_manager.update("task", task))
        # print(f"envmanager.state ==> \n\n{self.env_manager.state}\n\n")
        def compile_and_setup_run(graph):
            return lambda state: graph.compile().invoke(state)
        demand_analysis_graph = DemandAnalysisGraph(self.llm_engine, self.env_manager)
        self.builder.add_node("demand_analysis", compile_and_setup_run(demand_analysis_graph))
        
        # 노드 연결
        self.builder.add_edge(START, "demand_analysis")
        # self.builder.add_edge("task_update", "")
        # self.builder.add_edge("demand_analysis.env_update", END)

    def run(self, initial_state):
        # 그래프 실행
        graph = self.builder.compile()
        graph.invoke(initial_state)