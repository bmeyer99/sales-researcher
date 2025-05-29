from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from celery.result import AsyncResult
from backend.celery_app import celery_app

from backend.core.config import settings
from backend.db.user_store import get_user_credentials as get_user
from backend.services.google_drive_service import find_or_create_folder
from backend.tasks.orchestrator import research_orchestrator_task
from backend.api.v1.auth import get_current_user

router = APIRouter()

class ResearchStartRequest(BaseModel):
    company_name: str
    gdrive_folder_name: str

class ResearchStartResponse(BaseModel):
    job_id: str
    message: str

class ResearchStatusResponse(BaseModel):
    job_id: str
    status: str
    progress_message: Optional[str] = None
    current_phase: Optional[str] = None
    result_link: Optional[str] = None
    error: Optional[str] = None

@router.post("/start", response_model=ResearchStartResponse)
async def start_research(
    request: ResearchStartRequest,
    current_user: dict = Depends(get_current_user) # This will be implemented in auth.py
):
    user_id = current_user["user_id"]
    company_name = request.company_name
    gdrive_folder_name = request.gdrive_folder_name

    if not company_name or not gdrive_folder_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company name and Google Drive folder name are required."
        )
    
    @router.get("/status/{job_id}", response_model=ResearchStatusResponse)
    async def get_research_status(
        job_id: str,
        current_user: dict = Depends(get_current_user)
    ):
        user_id = current_user["user_id"]
    
        # TODO: Implement authorization check: Verify that job_id belongs to user_id
        # This requires storing job_id to user_id mapping when the task is initiated.
        # For now, we proceed without this check, but it's crucial for security.
    
        task = AsyncResult(job_id, app=celery_app)
    
        if not task.ready():
            # Task is still pending or in progress
            response_data = {
                "job_id": job_id,
                "status": task.state,
                "progress_message": task.info.get("message", "Task is in progress."),
                "current_phase": task.info.get("current_phase", "Initializing")
            }
        else:
            # Task is completed, failed, or unknown
            if task.state == 'SUCCESS':
                response_data = {
                    "job_id": job_id,
                    "status": task.state,
                    "progress_message": "Task completed successfully.",
                    "result_link": task.info.get("result_link"),
                    "current_phase": "Completed"
                }
            elif task.state == 'FAILURE':
                response_data = {
                    "job_id": job_id,
                    "status": task.state,
                    "progress_message": "Task failed.",
                    "error": str(task.info), # task.info contains the exception/traceback
                    "current_phase": "Failed"
                }
            else:
                # PENDING for unknown IDs, or other states
                response_data = {
                    "job_id": job_id,
                    "status": task.state,
                    "progress_message": "Task status unknown or not found.",
                    "error": "Task with this ID might not exist or has an unexpected state."
                }
        return ResearchStatusResponse(**response_data)

    # Synchronously find or create the Google Drive folder
    try:
        gdrive_folder_id = find_or_create_folder(user_id, gdrive_folder_name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set up Google Drive folder: {str(e)}"
        )

    # Asynchronously initiate the research orchestrator task
    task = research_orchestrator_task.delay(
        user_id,
        company_name,
        gdrive_folder_id
    )

    return ResearchStartResponse(
        job_id=task.id,
        message="Research task initiated successfully."
    )