
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from typing import List, Dict, Any, Optional
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
import logging

from src.schemas.analysis import AnalysisCreate, AnalysisResponse, AnalysisUpdate
from src.services.analysis_service import AnalysisService
from src.services.analysis_tools import AnalysisToolsService
from src.db.dependencies import get_analysis_service, get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
logger = logging.getLogger(__name__)

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

@router.post("/tool/{tool_name}")
async def execute_tool(
    tool_name: str,
    params: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Execute a specific analysis tool with parameters"""
    logger.info(f"Tool execution request: {tool_name}")
    tools_service = AnalysisToolsService(db)
    
    result = await tools_service.execute_tool(tool_name, params)
    return result

@router.post("/analyze")
async def analyze_data(
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Analyze data using the appropriate tool based on content"""
    logger.info("Received analyze request")
    tools_service = AnalysisToolsService(db)
    
    # Extract the input query or text
    query = ""
    if "messages" in data and data["messages"]:
        for msg in data["messages"]:
            if msg.get("role") == "user" and "content" in msg:
                query = msg["content"]
                break
    elif "query" in data:
        query = data["query"]
    elif "text" in data:
        query = data["text"]
    
    if not query:
        raise HTTPException(status_code=400, detail="No input query or text provided")
    
    # Route to appropriate tool and execute
    result = await tools_service.route_and_execute(query)
    return result

@router.get("/stream/{analysis_id}")
async def stream_analysis_results(
    request: Request,
    analysis_id: int,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """Stream analysis results as they become available"""
    
    async def event_generator():
        # Initial check if analysis exists
        analysis = await analysis_service.get_analysis(analysis_id)
        if not analysis:
            yield {
                "event": "error",
                "data": json.dumps({"error": "Analysis not found"})
            }
            return
        
        # Stream initial state
        yield {
            "event": "status",
            "data": json.dumps({"status": analysis.status, "id": analysis.id})
        }
        
        # Poll for updates until completed or failed
        poll_interval = 2  # seconds
        timeout = 600  # 10 minutes maximum
        elapsed = 0
        
        while elapsed < timeout:
            # Check for client disconnect
            if await request.is_disconnected():
                logger.info(f"Client disconnected from stream for analysis {analysis_id}")
                break
            
            # Get latest analysis state
            analysis = await analysis_service.get_analysis(analysis_id)
            
            # Check for completion or failure
            if analysis.status in ["completed", "failed"]:
                result = {}
                if analysis.status == "completed":
                    result = await analysis_service.get_analysis_results(analysis_id)
                else:
                    result = {"error": analysis.error}
                
                # Send final status and results
                yield {
                    "event": "status",
                    "data": json.dumps({"status": analysis.status, "id": analysis.id})
                }
                
                yield {
                    "event": "result",
                    "data": json.dumps(result)
                }
                
                yield {
                    "event": "done",
                    "data": ""
                }
                
                break
            
            # Send progress update
            yield {
                "event": "status",
                "data": json.dumps({"status": analysis.status, "id": analysis.id})
            }
            
            # Wait before polling again
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        # Handle timeout
        if elapsed >= timeout:
            yield {
                "event": "error",
                "data": json.dumps({"error": "Analysis stream timeout"})
            }
    
    return EventSourceResponse(event_generator())

@router.get("/tools")
async def list_available_tools(
    db: AsyncSession = Depends(get_db)
):
    """List all available analysis tools with descriptions"""
    tools_service = AnalysisToolsService(db)
    return {"tools": tools_service.get_available_tools()}
