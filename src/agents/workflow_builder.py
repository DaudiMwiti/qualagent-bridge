
"""Module for building LangGraph workflows for analysis"""
from typing import Callable, Dict, Any
from langgraph.graph import StateGraph, END

def build_workflow(preprocess_fn: Callable, 
                  analyze_fn: Callable, 
                  execute_tools_fn: Callable,
                  postprocess_fn: Callable) -> StateGraph:
    """Build the LangGraph workflow based on agent configuration"""
    # Define the state schema
    class State(dict):
        """The state of the analysis workflow"""
        input_data: Dict[str, Any]
        intermediate_results: Dict[str, Any]
        final_results: Dict[str, Any]
    
    # Create the workflow graph
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("preprocess", preprocess_fn)
    workflow.add_node("analyze", analyze_fn)
    workflow.add_node("tool_execution", execute_tools_fn)
    workflow.add_node("postprocess", postprocess_fn)
    
    # Add edges
    workflow.add_edge("preprocess", "analyze")
    workflow.add_edge("analyze", "tool_execution")
    workflow.add_edge("tool_execution", "analyze")  # Loop back for multi-turn reasoning
    workflow.add_edge("analyze", "postprocess")  # When analysis is complete
    workflow.add_edge("postprocess", END)
    
    # Set the entry point
    workflow.set_entry_point("preprocess")
    
    # Compile the workflow
    return workflow.compile()
