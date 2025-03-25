
from typing import Dict, Any, List
import asyncio
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from src.core.config import settings

class AnalysisOrchestrator:
    """Orchestrator for running AI agents to analyze qualitative data"""
    
    def __init__(self, agent_config: Dict[str, Any], model: str = None):
        self.agent_config = agent_config
        self.model_name = model or settings.DEFAULT_MODEL
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=self.model_name,
            temperature=self.agent_config.get("temperature", 0.7)
        )
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow based on agent configuration"""
        # This is a simplified example - in a real implementation, you would
        # create more sophisticated workflows with multiple nodes and edges
        
        # Define the state schema
        class State(dict):
            """The state of the analysis workflow"""
            input_data: Dict[str, Any]
            intermediate_results: Dict[str, Any]
            final_results: Dict[str, Any]
        
        # Create the workflow graph
        workflow = StateGraph(State)
        
        # Add nodes
        workflow.add_node("preprocess", self._preprocess_data)
        workflow.add_node("analyze", self._analyze_data)
        workflow.add_node("postprocess", self._postprocess_results)
        
        # Add edges
        workflow.add_edge("preprocess", "analyze")
        workflow.add_edge("analyze", "postprocess")
        workflow.add_edge("postprocess", END)
        
        # Set the entry point
        workflow.set_entry_point("preprocess")
        
        # Compile the workflow
        return workflow.compile()
    
    async def _preprocess_data(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess the input data"""
        # Implement data preprocessing logic
        return {
            **state,
            "intermediate_results": {
                "preprocessed_data": state["input_data"]
            }
        }
    
    async def _analyze_data(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Core analysis using LLM"""
        preprocessed_data = state["intermediate_results"]["preprocessed_data"]
        
        # Extract text data for analysis
        texts = []
        if "interviews" in preprocessed_data:
            texts = [item["text"] for item in preprocessed_data["interviews"]]
        elif "texts" in preprocessed_data:
            texts = preprocessed_data["texts"]
        
        # Join texts for analysis
        combined_text = "\n\n".join(texts)
        
        # Get parameters
        params = preprocessed_data.get("parameters", {})
        theme_count = params.get("theme_count", 5)
        include_quotes = params.get("include_quotes", True)
        
        # Create the prompt
        system_prompt = self.agent_config.get("system_prompt", 
            "You are a qualitative research expert. Analyze the provided data and identify key themes.")
        
        user_prompt = f"""
        Analyze the following qualitative data and identify {theme_count} main themes.
        
        {combined_text}
        
        Provide a structured analysis with:
        1. A list of the main themes
        2. A brief description of each theme
        {f'3. Representative quotes for each theme' if include_quotes else ''}
        
        Return the results in a structured format.
        """
        
        # Call the LLM
        response = await self.llm.ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        # Process the response
        return {
            **state,
            "intermediate_results": {
                **state["intermediate_results"],
                "raw_analysis": response.content
            }
        }
    
    async def _postprocess_results(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Postprocess the results into a structured format"""
        raw_analysis = state["intermediate_results"]["raw_analysis"]
        
        # In a real implementation, you would parse the raw LLM output
        # into a structured format here
        
        # Simplified example - structure would be more sophisticated in practice
        structured_results = {
            "themes": [
                {
                    "name": "Example Theme 1",
                    "description": "This is just a placeholder example theme",
                    "quotes": ["Example quote 1", "Example quote 2"]
                }
            ],
            "summary": raw_analysis
        }
        
        return {
            **state,
            "final_results": structured_results
        }
    
    async def run_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the full analysis workflow"""
        # Initialize the state
        initial_state = {"input_data": data}
        
        # Run the workflow
        result = await self.workflow.ainvoke(initial_state)
        
        # Return the final results
        return result["final_results"]
