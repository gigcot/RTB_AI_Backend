from langgraph.graph import StateGraph, START, END
from .writing_skeleton_code_nodes import WritingSkeletonCodePhaseNodes

class WritingSkeletonCodeGraph():
    def __init__(self,llm_engine, env_manager):
        self.builder = StateGraph(dict)
        writing_skeleton_code = WritingSkeletonCodePhaseNodes(llm_engine, env_manager)

        self.builder.add_node("execute", writing_skeleton_code.execute)
        self.builder.add_edge(START, "execute")


    
    def compile(self):
        return self.builder.compile()
    
    