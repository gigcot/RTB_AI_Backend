from langgraph.graph import StateGraph, START, END
from .setup_initial_structure_nodes import SetupInitialStructurePhaseNodes

class SetupInitialStructureGraph():
    def __init__(self,llm_engine, env_manager):
        self.builder = StateGraph(dict)
        setup_initial_structure_phase_nodes = SetupInitialStructurePhaseNodes(llm_engine, env_manager)

        self.builder.add_node("execute", setup_initial_structure_phase_nodes.execute)
        self.builder.add_edge(START, "execute")


    
    def compile(self):
        return self.builder.compile()
    
    