from langgraph.graph import StateGraph, START, END
from .impl_and_test_for_commit_nodes import ImplAndTestForCommitPhaseNodes

class ImplAndTestForCommitGraph():
    def __init__(self,llm_engine, env_manager):
        self.builder = StateGraph(dict)
        impl_and_test_for_commit = ImplAndTestForCommitPhaseNodes(llm_engine, env_manager)

        self.builder.add_node("execute", impl_and_test_for_commit.execute)
        self.builder.add_edge(START, "execute")


    
    def compile(self):
        return self.builder.compile()
    
    