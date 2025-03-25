
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.base import async_session
from src.services.project_service import ProjectService
from src.services.agent_service import AgentService
from src.services.analysis_service import AnalysisService
from src.services.analysis_tools import AnalysisToolsService

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    """Dependency for getting ProjectService"""
    return ProjectService(db)

async def get_agent_service(db: AsyncSession = Depends(get_db)) -> AgentService:
    """Dependency for getting AgentService"""
    return AgentService(db)

async def get_analysis_service(db: AsyncSession = Depends(get_db)) -> AnalysisService:
    """Dependency for getting AnalysisService"""
    return AnalysisService(db)

async def get_analysis_tools_service(db: AsyncSession = Depends(get_db)) -> AnalysisToolsService:
    """Dependency for getting AnalysisToolsService"""
    return AnalysisToolsService(db)
