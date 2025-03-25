
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from src.db.models import Project
from src.schemas.project import ProjectCreate, ProjectUpdate

class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_project(self, project_data: ProjectCreate) -> Project:
        """Create a new project"""
        db_project = Project(**project_data.model_dump())
        self.db.add(db_project)
        await self.db.commit()
        await self.db.refresh(db_project)
        return db_project
    
    async def get_project(self, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalars().first()
    
    async def get_projects(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get all projects with pagination"""
        result = await self.db.execute(
            select(Project).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def update_project(self, project_id: int, project_data: ProjectUpdate) -> Optional[Project]:
        """Update a project"""
        db_project = await self.get_project(project_id)
        if not db_project:
            return None
        
        update_data = project_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_project, key, value)
        
        await self.db.commit()
        await self.db.refresh(db_project)
        return db_project
    
    async def delete_project(self, project_id: int) -> bool:
        """Delete a project"""
        db_project = await self.get_project(project_id)
        if not db_project:
            return False
        
        await self.db.delete(db_project)
        await self.db.commit()
        return True
