from langgraph.graph import StateGraph, START, END
from .implementation_sequencing_nodes import ImplementationSequencingPhaseNodes

class ImplementationSequencingGraph():
    def __init__(self,llm_engine, env_manager):
        self.builder = StateGraph(dict)
        implementation_sequencing = ImplementationSequencingPhaseNodes(llm_engine, env_manager)

        self.builder.add_node("execute", implementation_sequencing.execute)
        self.builder.add_edge(START, "execute")


    
    def compile(self):
        return self.builder.compile()
    
    