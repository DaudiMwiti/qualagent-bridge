
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class AnalysisBase(BaseModel):
    project_id: int = Field(..., example=1)
    agent_id: int = Field(..., example=1)
    data: Dict[str, Any] = Field(
        ..., 
        example={
            "interviews": [
                {
                    "id": "interview-1",
                    "text": "In this interview, the participant mentioned...",
                    "metadata": {"participant_id": "P001", "date": "2023-04-15"}
                }
            ],
            "parameters": {
                "theme_count": 5,
                "include_quotes": True
            }
        }
    )

class AnalysisCreate(AnalysisBase):
    pass

class AnalysisUpdate(BaseModel):
    status: Optional[str] = Field(None, example="completed")
    results: Optional[Dict[str, Any]] = None

class AnalysisResponse(AnalysisBase):
    id: int
    status: str = Field(..., example="pending")
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MemoryItem(BaseModel):
    id: str = Field(..., example="mem-123")
    text: str = Field(..., example="Users expressed frustration with the signup process.")
    memory_type: str = Field(..., example="long_term")
    tag: Optional[str] = Field(None, example="user_feedback")
    score: Optional[float] = Field(None, example=0.92)
    timestamp: Optional[float] = Field(None, example=1679504400)
    metadata: Optional[Dict[str, Any]] = None

class AnalysisResults(BaseModel):
    summary: Optional[str] = None
    themes: Optional[List[Dict[str, Any]]] = None
    insights: Optional[List[str]] = None
    sentiment: Optional[Dict[str, Any]] = None
    memory_used: Optional[List[MemoryItem]] = None
