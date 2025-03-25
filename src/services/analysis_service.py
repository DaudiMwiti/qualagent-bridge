
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.db.models import Analysis, Project, Agent
from src.schemas.analysis import AnalysisCreate, AnalysisUpdate
from src.agents.orchestrator import AnalysisOrchestrator
from src.utils.vector_store import VectorStore
from src.agents.tools import summarize_memory

class AnalysisService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ... keep existing code (methods for crud operations)
    
    async def run_analysis(self, analysis_id: int, project_id: int, agent_id: int, data: Dict[str, Any]) -> None:
        """Run the analysis using AI agents"""
        try:
            # Update status to in_progress
            await self.update_analysis_status(analysis_id, "in_progress")
            
            # Get the agent configuration
            agent_result = await self.db.execute(
                select(Agent).where(Agent.id == agent_id)
            )
            agent = agent_result.scalars().first()
            if not agent:
                await self.update_analysis_status(
                    analysis_id, "failed", error="Agent not found"
                )
                return
            
            # Initialize the vector store for memory operations
            vector_store = VectorStore(self.db)
            
            # Get previous analysis context if available
            recent_context = []
            try:
                # Retrieve recent preferences and session memories
                recent_context = await vector_store.get_recent_memories(
                    project_id=project_id,
                    agent_id=agent_id,
                    limit=5
                )
            except Exception as e:
                # Non-critical error, just log it
                print(f"Error retrieving context: {str(e)}")
            
            # Add context to data if available
            if recent_context:
                if "context" not in data:
                    data["context"] = {}
                data["context"]["memories"] = recent_context
            
            # Create and run the orchestrator
            orchestrator = AnalysisOrchestrator(
                agent_config=agent.configuration,
                model=agent.model
            )
            
            results = await orchestrator.run_analysis(data)
            
            # Store important insights as memories
            try:
                if "themes" in results and results["themes"]:
                    # Store the top themes as long-term memories
                    for theme in results["themes"][:3]:  # Store top 3 themes
                        theme_text = f"Theme: {theme.get('name')} - {theme.get('description', '')}"
                        await vector_store.add_memory(
                            text=theme_text,
                            project_id=project_id,
                            memory_type="long_term",
                            agent_id=agent_id,
                            analysis_id=analysis_id,
                            metadata={"theme": theme.get('name')}
                        )
                
                # Store a summary of this analysis
                if "summary" in results and results["summary"]:
                    summary_text = f"Analysis summary: {results['summary'][:500]}..."
                    await vector_store.add_memory(
                        text=summary_text,
                        project_id=project_id,
                        memory_type="session",
                        agent_id=agent_id,
                        analysis_id=analysis_id,
                        metadata={"type": "analysis_summary"}
                    )
            except Exception as e:
                # Non-critical error, just log it
                print(f"Error storing memories: {str(e)}")
            
            # Update with results
            await self.update_analysis_status(
                analysis_id, "completed", results=results
            )
            
        except Exception as e:
            # Handle errors
            error_message = f"Analysis failed: {str(e)}"
            await self.update_analysis_status(
                analysis_id, "failed", error=error_message
            )
