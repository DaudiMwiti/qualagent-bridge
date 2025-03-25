
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from src.db.models import Agent
from src.schemas.agent import AgentCreate, AgentUpdate

class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_agent(self, agent_data: AgentCreate) -> Agent:
        """Create a new agent"""
        db_agent = Agent(**agent_data.model_dump())
        self.db.add(db_agent)
        await self.db.commit()
        await self.db.refresh(db_agent)
        return db_agent
    
    async def get_agent(self, agent_id: int) -> Optional[Agent]:
        """Get agent by ID"""
        result = await self.db.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        return result.scalars().first()
    
    async def get_agents(self, skip: int = 0, limit: int = 100) -> List[Agent]:
        """Get all agents with pagination"""
        result = await self.db.execute(
            select(Agent).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def update_agent(self, agent_id: int, agent_data: AgentUpdate) -> Optional[Agent]:
        """Update an agent"""
        db_agent = await self.get_agent(agent_id)
        if not db_agent:
            return None
        
        update_data = agent_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_agent, key, value)
        
        await self.db.commit()
        await self.db.refresh(db_agent)
        return db_agent
    
    async def delete_agent(self, agent_id: int) -> bool:
        """Delete an agent"""
        db_agent = await self.get_agent(agent_id)
        if not db_agent:
            return False
        
        await self.db.delete(db_agent)
        await self.db.commit()
        return True
