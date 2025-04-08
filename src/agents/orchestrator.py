
"""Main orchestrator module for running AI agents to analyze qualitative data"""
from typing import Dict, Any, List
import logging
import asyncio
from datetime import datetime
from langchain_openai import ChatOpenAI

from src.core.config import settings
from src.services.cache import CacheService
from src.db.base import async_session
from src.agents.workflow_builder import build_workflow
from src.agents.tool_manager import setup_tools
from src.agents.data_processor import extract_text_data, preprocess_data, postprocess_results
from src.agents.state_handler import analyze_data, execute_tools

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
        self.tools = setup_tools(self.agent_config)
        self.workflow = build_workflow(self._preprocess_data, self._analyze_data, 
                                      self._execute_tools, self._postprocess_results)
        self._cache = None  # Lazy-initialized cache
    
    async def _get_cache(self) -> CacheService:
        """Lazy initialization of cache service"""
        if self._cache is None:
            # Create a new session for the cache
            session = async_session()
            self._cache = CacheService(session)
        return self._cache
    
    async def _preprocess_data(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess the input data"""
        logger.info("Preprocessing data")
        return await preprocess_data(state, self._get_cache, extract_text_data)
    
    async def _analyze_data(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Core analysis using LLM and tools with smart parameter extraction"""
        logger.info("Running core analysis with smart parameter extraction")
        return await analyze_data(state, self.agent_config, self.llm, self._get_cache)
    
    async def _execute_tools(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the selected tools based on the analysis"""
        logger.info("Executing tools")
        return await execute_tools(state)
    
    async def _postprocess_results(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Postprocess the results into a structured format"""
        logger.info("Postprocessing results")
        return await postprocess_results(state, self.llm)
    
    async def run_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the full analysis workflow"""
        logger.info("Starting analysis workflow with smart parameter extraction")
        
        try:
            # Initialize the state
            initial_state = {"input_data": data}
            
            # Run the workflow
            result = await self.workflow.ainvoke(initial_state)
            
            # Return the final results
            return result["final_results"]
            
        finally:
            # Clean up resources
            if self._cache is not None:
                # We don't close the session here because it might be used by other code
                # The session will be closed when the app shuts down
                pass
