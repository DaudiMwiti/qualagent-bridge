
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from src.schemas.agent import AgentCreate, AgentResponse, AgentUpdate
from src.services.agent_service import AgentService
from src.db.dependencies import get_agent_service

router = APIRouter()

@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(
    agent_data: AgentCreate,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Create a new AI agent"""
    return await agent_service.create_agent(agent_data)

@router.get("", response_model=List[AgentResponse])
async def get_agents(
    skip: int = 0, 
    limit: int = 100,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Get list of AI agents"""
    return await agent_service.get_agents(skip=skip, limit=limit)

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Get details of a specific agent"""
    agent = await agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Update an agent"""
    agent = await agent_service.update_agent(agent_id, agent_data)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.delete("/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: int,
    agent_service: AgentService = Depends(get_agent_service)
):
    """Delete an agent"""
    success = await agent_service.delete_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
