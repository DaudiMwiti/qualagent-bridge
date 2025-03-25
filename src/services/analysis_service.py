
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.db.models import Analysis, Project, Agent
from src.schemas.analysis import AnalysisCreate, AnalysisUpdate
from src.agents.orchestrator import AnalysisOrchestrator

class AnalysisService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_analysis(self, analysis_data: AnalysisCreate) -> Analysis:
        """Create a new analysis"""
        db_analysis = Analysis(**analysis_data.model_dump())
        self.db.add(db_analysis)
        await self.db.commit()
        await self.db.refresh(db_analysis)
        return db_analysis
    
    async def get_analysis(self, analysis_id: int) -> Optional[Analysis]:
        """Get analysis by ID"""
        result = await self.db.execute(
            select(Analysis)
            .options(selectinload(Analysis.project), selectinload(Analysis.agent))
            .where(Analysis.id == analysis_id)
        )
        return result.scalars().first()
    
    async def get_analyses_by_project(
        self, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[Analysis]:
        """Get analyses for a specific project"""
        result = await self.db.execute(
            select(Analysis)
            .where(Analysis.project_id == project_id)
            .order_by(Analysis.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def update_analysis_status(
        self, analysis_id: int, status: str, results: Optional[Dict[str, Any]] = None, error: Optional[str] = None
    ) -> bool:
        """Update the status of an analysis"""
        update_data = {"status": status, "updated_at": datetime.now()}
        
        if status == "completed":
            update_data["completed_at"] = datetime.now()
            if results:
                update_data["results"] = results
        
        if status == "failed" and error:
            update_data["error"] = error
        
        query = (
            update(Analysis)
            .where(Analysis.id == analysis_id)
            .values(**update_data)
        )
        
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_analysis_results(self, analysis_id: int) -> Dict[str, Any]:
        """Get the structured results of a completed analysis"""
        analysis = await self.get_analysis(analysis_id)
        if not analysis:
            return {"error": "Analysis not found"}
        
        if analysis.status != "completed":
            return {"error": "Analysis not completed", "status": analysis.status}
        
        return analysis.results if analysis.results else {}
    
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
            
            # Create and run the orchestrator
            orchestrator = AnalysisOrchestrator(
                agent_config=agent.configuration,
                model=agent.model
            )
            
            results = await orchestrator.run_analysis(data)
            
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
