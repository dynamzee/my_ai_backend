from fastapi import APIRouter, HTTPException
from loguru import logger

from schemas.task import ExtractedTask, TaskExtractionRequest, TaskPipelineResponse
from services.prompt_engineering import extract_task, run_task_pipeline

router = APIRouter(prefix="/ai_tasks", tags=["AI TASK - STRUCTURED OUTPUT & CHAINING."])

@router.post("/extract", response_model=ExtractedTask)
async def extract_task_endpoint(request: TaskExtractionRequest):
    """
    POST /ai_task/extract

    Send free-form text. Get back a validated, parsed object every single time --
    not a paragraph, not markdown, not "Sure, Here's your json:".
    Data is shaped exactly as ExtractedTask and it's guaranteed.
    """
    try:
        return extract_task(request.text)
    except ValueError as error:
        logger.error(f"TASK EXTRACTION ERROR: {error}")
        raise HTTPException(status_code=502, detail=str(error))
    except Exception as error:
        logger.error(f"TASK EXTRACTION FAILED: {error}")
        raise HTTPException(status_code=502, detail="Task extraction failed. Please try again.")

@router.post("/pipeline", response_model=TaskPipelineResponse)
async def task_pipeline_endpoint(request: TaskExtractionRequest):
    """
    POST /ai_task/pipeline

    The full chain in one call:
    1. Extract a structured task from raw text (AI CALL NO.1).
    2. Generate a notification message FROM that structured extracted task (AI CALL NO.2).

    Two AI calls, one endpoint, each call doing one job.
    """
    try:
        result = run_task_pipeline(request.text)
    except ValueError as error:
        logger.error(f"COULDN'T RUN TASK PIPELINE: {error}")
        raise HTTPException(status_code=502, detail=str(error))
    except Exception as error:
        logger.error(f"TASK PIPELINE ERROR: {error}")
        raise HTTPException(status_code=502, detail="Task pipeline failed. Please try again.")

    return TaskPipelineResponse(**result)


