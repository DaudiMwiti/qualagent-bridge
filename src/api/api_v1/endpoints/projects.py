
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from src.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from src.services.project_service import ProjectService
from src.db.dependencies import get_project_service

router = APIRouter()

@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    project_service: ProjectService = Depends(get_project_service)
):
    """Create a new analysis project"""
    return await project_service.create_project(project_data)

@router.get("", response_model=List[ProjectResponse])
async def get_projects(
    skip: int = 0, 
    limit: int = 100,
    project_service: ProjectService = Depends(get_project_service)
):
    """Get list of analysis projects"""
    return await project_service.get_projects(skip=skip, limit=limit)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service)
):
    """Get details of a specific project"""
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    project_service: ProjectService = Depends(get_project_service)
):
    """Update a project"""
    project = await project_service.update_project(project_id, project_data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service)
):
    """Delete a project"""
    success = await project_service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
