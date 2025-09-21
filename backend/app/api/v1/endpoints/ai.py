from fastapi import APIRouter
from pydantic import BaseModel
from app.services.ai_service import summarize_tasks

router = APIRouter(tags=["AI"])

class TaskInput(BaseModel):
    title: str
    description: str
    due_date: str | None = None

@router.post("/summarize-tasks")
def summarize_tasks_endpoint(tasks: list[TaskInput]):
    """
    Summarize a list of tasks using AI.
    
    This endpoint takes a list of tasks and returns a summarized version
    using an AI model.
    """
    try:
        # Add IDs to tasks since AI service expects them
        tasks_with_ids = []
        for i, task in enumerate(tasks, 1):
            task_dict = task.model_dump()
            task_dict['id'] = i
            tasks_with_ids.append(task_dict)
        
        summary = summarize_tasks(tasks_with_ids)
        return {"summary": summary}
    except Exception as e:
        return {"error": str(e)}