
from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, tools_to_execute_tools
import logging

from src.core.config import settings
from src.agents.tools import (
    document_search,
    generate_insight,
    sentiment_analysis,
    theme_cluster,
    llm_router
)

logger = logging.getLogger(__name__)

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
        self.tools = self._setup_tools()
        self.workflow = self._build_workflow()
    
    def _setup_tools(self) -> List[Any]:
        """Set up the tools available to the agent"""
        available_tools = {
            "document_search": document_search,
            "generate_insight": generate_insight,
            "sentiment_analysis": sentiment_analysis,
            "theme_cluster": theme_cluster,
            "llm_router": llm_router
        }
        
        # Filter tools based on agent configuration
        if "tools" in self.agent_config:
            enabled_tools = self.agent_config["tools"]
            return [tool for name, tool in available_tools.items() if name in enabled_tools]
        
        # By default, return all tools
        return list(available_tools.values())
    
    def _build_workflow(self) -> StateGraph:
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
        workflow.add_node("preprocess", self._preprocess_data)
        workflow.add_node("analyze", self._analyze_data)
        workflow.add_node("tool_execution", self._execute_tools)
        workflow.add_node("postprocess", self._postprocess_results)
        
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
    
    async def _preprocess_data(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess the input data"""
        logger.info("Preprocessing data")
        
        # Extract parameters and data
        input_data = state.get("input_data", {})
        parameters = input_data.get("parameters", {})
        
        # Structure the input data for processing
        preprocessed_data = {
            "text_data": self._extract_text_data(input_data),
            "parameters": parameters,
            "metadata": {
                "start_time": datetime.now().isoformat(),
                "agent_config": self.agent_config
            }
        }
        
        logger.info(f"Preprocessed data with {len(preprocessed_data['text_data'])} text items")
        
        return {
            **state,
            "intermediate_results": {
                "preprocessed_data": preprocessed_data,
                "analysis_steps": [],
                "tool_results": []
            }
        }
    
    def _extract_text_data(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract text data from various input formats"""
        text_data = []
        
        # Handle different input formats
        if "interviews" in input_data:
            text_data.extend(input_data["interviews"])
        elif "texts" in input_data:
            text_data.extend([{"text": t, "metadata": {}} for t in input_data["texts"]])
        elif "documents" in input_data:
            text_data.extend(input_data["documents"])
        elif "text" in input_data:
            text_data.append({"text": input_data["text"], "metadata": {}})
        
        return text_data
    
    async def _analyze_data(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Core analysis using LLM and tools"""
        logger.info("Running core analysis")
        
        # Extract preprocessed data
        preprocessed_data = state["intermediate_results"]["preprocessed_data"]
        text_data = preprocessed_data["text_data"]
        parameters = preprocessed_data["parameters"]
        
        # Check if we need to continue analysis or finish
        analysis_steps = state["intermediate_results"].get("analysis_steps", [])
        
        if analysis_steps and analysis_steps[-1].get("is_final", False):
            # Analysis is complete, move to postprocessing
            logger.info("Analysis complete, moving to postprocessing")
            return {
                **state,
                "intermediate_results": {
                    **state["intermediate_results"],
                    "analysis_complete": True
                }
            }
        
        # Combine text data for analysis
        combined_text = "\n\n".join([item["text"] for item in text_data])
        
        # Create the prompt based on agent configuration
        system_prompt = self.agent_config.get("system_prompt", 
            "You are a qualitative research expert. Analyze the provided data and identify key themes.")
        
        # Get the research question or objective
        research_objective = parameters.get("research_objective", "Identify key themes and insights")
        
        user_prompt = f"""
        Research Objective: {research_objective}
        
        Data to analyze:
        {combined_text[:4000]}  # Limit text size for initial analysis
        
        Please analyze this data and determine what analysis steps would be most helpful.
        You have access to the following tools:
        - document_search: Search through documents for relevant information
        - generate_insight: Extract structured insights from text
        - sentiment_analysis: Analyze emotional tone of text
        - theme_cluster: Cluster related concepts from statements
        
        Explain your proposed analysis approach and which tool to use first.
        """
        
        # Call the LLM
        response = await self.llm.ainvoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        # Add the analysis step
        analysis_steps.append({
            "timestamp": datetime.now().isoformat(),
            "analysis": response.content,
            "is_final": False  # This will be set to True in a later step
        })
        
        # Determine which tool to use based on LLM response
        tool_to_use = self._extract_tool_from_response(response.content)
        
        return {
            **state,
            "intermediate_results": {
                **state["intermediate_results"],
                "analysis_steps": analysis_steps,
                "next_tool": tool_to_use,
                "tool_params": self._extract_tool_params(response.content, combined_text)
            }
        }
    
    def _extract_tool_from_response(self, response_text: str) -> str:
        """Extract which tool to use from the LLM response"""
        response_lower = response_text.lower()
        
        # Check for explicit tool mentions
        if "document_search" in response_lower or "search" in response_lower:
            return "document_search"
        elif "generate_insight" in response_lower or "insight" in response_lower:
            return "generate_insight"
        elif "sentiment_analysis" in response_lower or "sentiment" in response_lower:
            return "sentiment_analysis"
        elif "theme_cluster" in response_lower or "cluster" in response_lower:
            return "theme_cluster"
        elif "router" in response_lower:
            return "llm_router"
        
        # Default to generate_insight if no clear tool is mentioned
        return "generate_insight"
    
    def _extract_tool_params(self, response_text: str, default_text: str) -> Dict[str, Any]:
        """Extract parameters for the selected tool from the LLM response"""
        # This is a simplified implementation
        # In a real system, we would use more sophisticated parameter extraction
        
        # Default parameters by tool type
        tool_params = {
            "document_search": {"query": response_text.split("\n")[0]},
            "generate_insight": {"text": default_text, "approach": "thematic"},
            "sentiment_analysis": {"text": default_text},
            "theme_cluster": {"excerpts": default_text.split("\n\n")},
            "llm_router": {"query": response_text.split("\n")[0]}
        }
        
        return tool_params
    
    async def _execute_tools(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the selected tools based on the analysis"""
        logger.info("Executing tools")
        
        # Get the tool to execute and its parameters
        next_tool = state["intermediate_results"].get("next_tool")
        tool_params = state["intermediate_results"].get("tool_params", {})
        
        if not next_tool:
            logger.warning("No tool specified for execution")
            return {
                **state,
                "intermediate_results": {
                    **state["intermediate_results"],
                    "analysis_complete": True  # Force completion in case of error
                }
            }
        
        logger.info(f"Executing tool: {next_tool}")
        
        try:
            # Get the appropriate tool function
            tool_map = {
                "document_search": document_search,
                "generate_insight": generate_insight,
                "sentiment_analysis": sentiment_analysis,
                "theme_cluster": theme_cluster,
                "llm_router": llm_router
            }
            
            tool_fn = tool_map.get(next_tool)
            if not tool_fn:
                raise ValueError(f"Unknown tool: {next_tool}")
            
            # Execute the tool
            result = await tool_fn.ainvoke(tool_params.get(next_tool, {}))
            
            # Add the result to the tool results
            tool_results = state["intermediate_results"].get("tool_results", [])
            tool_results.append({
                "timestamp": datetime.now().isoformat(),
                "tool": next_tool,
                "params": tool_params.get(next_tool, {}),
                "result": result
            })
            
            # Check if we've executed enough tools based on agent config
            max_tool_calls = self.agent_config.get("max_tool_calls", 3)
            
            if len(tool_results) >= max_tool_calls:
                # If we've reached the max tool calls, mark analysis as complete
                analysis_steps = state["intermediate_results"].get("analysis_steps", [])
                if analysis_steps:
                    analysis_steps[-1]["is_final"] = True
            
            return {
                **state,
                "intermediate_results": {
                    **state["intermediate_results"],
                    "tool_results": tool_results
                }
            }
            
        except Exception as e:
            logger.error(f"Error executing tool {next_tool}: {str(e)}")
            return {
                **state,
                "intermediate_results": {
                    **state["intermediate_results"],
                    "tool_error": str(e),
                    "analysis_complete": True  # Force completion in case of error
                }
            }
    
    async def _postprocess_results(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Postprocess the results into a structured format"""
        logger.info("Postprocessing results")
        
        # Extract all data
        preprocessed_data = state["intermediate_results"]["preprocessed_data"]
        analysis_steps = state["intermediate_results"].get("analysis_steps", [])
        tool_results = state["intermediate_results"].get("tool_results", [])
        
        # Create a summary prompt based on the collected data
        summary_prompt = f"""
        You are a qualitative research expert. Synthesize the following analysis steps and tool results into a coherent summary.
        
        Research Objective: {preprocessed_data["parameters"].get("research_objective", "Identify key themes and insights")}
        
        Analysis Steps:
        {self._format_analysis_steps(analysis_steps)}
        
        Tool Results:
        {self._format_tool_results(tool_results)}
        
        Create a structured summary with:
        1. Key Themes: The main themes identified in the data
        2. Notable Insights: Specific insights derived from the data
        3. Evidence: Supporting quotes or data points
        4. Recommendations: Suggested actions or further research
        
        Format your response as clear sections with headings.
        """
        
        # Call the LLM for the summary
        response = await self.llm.ainvoke([
            {"role": "system", "content": "You are a qualitative research expert specializing in synthesizing findings."},
            {"role": "user", "content": summary_prompt}
        ])
        
        # Extract themes from tool results (if available)
        themes = self._extract_themes_from_results(tool_results)
        
        # Structure the final results
        structured_results = {
            "summary": response.content,
            "themes": themes,
            "analysis_steps": analysis_steps,
            "tool_results": tool_results,
            "metadata": {
                "completed_at": datetime.now().isoformat(),
                "model": self.model_name,
                "agent_config": self.agent_config
            }
        }
        
        logger.info(f"Analysis complete with {len(themes)} themes extracted")
        
        return {
            **state,
            "final_results": structured_results
        }
    
    def _format_analysis_steps(self, analysis_steps: List[Dict[str, Any]]) -> str:
        """Format analysis steps for the summary prompt"""
        if not analysis_steps:
            return "No analysis steps recorded."
        
        formatted_steps = []
        for i, step in enumerate(analysis_steps):
            formatted_steps.append(f"Step {i+1}: {step.get('analysis', '')[:500]}...")
        
        return "\n\n".join(formatted_steps)
    
    def _format_tool_results(self, tool_results: List[Dict[str, Any]]) -> str:
        """Format tool results for the summary prompt"""
        if not tool_results:
            return "No tool results recorded."
        
        formatted_results = []
        for i, result in enumerate(tool_results):
            tool = result.get("tool", "unknown")
            result_text = str(result.get("result", {}))[:500]
            formatted_results.append(f"Tool {i+1} ({tool}): {result_text}...")
        
        return "\n\n".join(formatted_results)
    
    def _extract_themes_from_results(self, tool_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract themes from tool results"""
        themes = []
        
        for result in tool_results:
            tool = result.get("tool")
            result_data = result.get("result", {})
            
            # Extract themes from different tool results
            if tool == "generate_insight" and "insights" in result_data:
                for insight in result_data["insights"]:
                    if "theme" in insight:
                        themes.append({
                            "name": insight.get("theme"),
                            "description": insight.get("summary", ""),
                            "quotes": [insight.get("quote", "")]
                        })
            elif tool == "theme_cluster" and "clusters" in result_data:
                for cluster in result_data["clusters"]:
                    if "theme" in cluster:
                        themes.append({
                            "name": cluster.get("theme"),
                            "description": cluster.get("description", ""),
                            "quotes": cluster.get("excerpts", [])
                        })
        
        # Remove duplicates based on theme name
        unique_themes = {}
        for theme in themes:
            name = theme.get("name")
            if name and name not in unique_themes:
                unique_themes[name] = theme
        
        return list(unique_themes.values())
    
    async def run_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the full analysis workflow"""
        logger.info("Starting analysis workflow")
        
        # Initialize the state
        initial_state = {"input_data": data}
        
        # Run the workflow
        result = await self.workflow.ainvoke(initial_state)
        
        # Return the final results
        return result["final_results"]
