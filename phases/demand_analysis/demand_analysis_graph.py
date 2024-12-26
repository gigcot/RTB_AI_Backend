from langgraph.graph import StateGraph, START, END
from .demand_analysis_nodes import DemandAnalysisPhaseNodes

class DemandAnalysisGraph():
    def __init__(self,llm_engine, env_manager):
        self.builder = StateGraph(dict)
        demand_analysis_phase_nodes = DemandAnalysisPhaseNodes(llm_engine, env_manager)

        self.builder.add_node("execute", demand_analysis_phase_nodes.execute)
        self.builder.add_edge(START, "execute")


    
    def compile(self):
        return self.builder.compile()
    
    