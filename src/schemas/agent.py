
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class AgentBase(BaseModel):
    name: str = Field(..., example="Thematic Analyzer")
    description: Optional[str] = Field(None, example="Agent for thematic analysis of research data")
    model: str = Field(..., example="gpt-4o")
    configuration: Dict[str, Any] = Field(
        ..., 
        example={
            "agent_type": "thematic_analysis",
            "system_prompt": "You are a qualitative research expert...",
            "temperature": 0.7
        }
    )

class AgentCreate(AgentBase):
    pass

class AgentUpdate(AgentBase):
    name: Optional[str] = None
    description: Optional[str] = None
    model: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None

class AgentResponse(AgentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
