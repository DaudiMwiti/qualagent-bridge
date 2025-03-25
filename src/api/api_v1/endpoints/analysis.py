
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List

from src.schemas.analysis import AnalysisCreate, AnalysisResponse, AnalysisUpdate
from src.services.analysis_service import AnalysisService
from src.db.dependencies import get_analysis_service

router = APIRouter()

@router.post("", response_model=AnalysisResponse, status_code=202)
async def submit_analysis(
    analysis_data: AnalysisCreate,
    background_tasks: BackgroundTasks,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """Submit a new analysis task"""
    # Create the analysis record
    analysis = await analysis_service.create_analysis(analysis_data)
    
    # Run the analysis in the background
    background_tasks.add_task(
        analysis_service.run_analysis, 
        analysis_id=analysis.id, 
        project_id=analysis_data.project_id,
        agent_id=analysis_data.agent_id,
        data=analysis_data.data
    )
    
    return analysis

@router.get("/project/{project_id}", response_model=List[AnalysisResponse])
async def get_analyses_by_project(
    project_id: int,
    skip: int = 0, 
    limit: int = 100,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """Get analyses for a specific project"""
    return await analysis_service.get_analyses_by_project(
        project_id=project_id, 
        skip=skip, 
        limit=limit
    )

@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """Get a specific analysis by ID"""
    analysis = await analysis_service.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

@router.get("/{analysis_id}/results")
async def get_analysis_results(
    analysis_id: int,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """Get structured results of a completed analysis"""
    analysis = await analysis_service.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis not yet completed")
    
    return await analysis_service.get_analysis_results(analysis_id)
