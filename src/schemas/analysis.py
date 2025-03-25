
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
