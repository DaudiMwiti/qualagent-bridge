
from fastapi import APIRouter

from src.api.api_v1.endpoints import projects, agents, analysis

api_router = APIRouter()

api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
