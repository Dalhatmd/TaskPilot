"""
Task endpoints.
Handles task CRUD operations and task management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, 
    TaskStatusUpdate, TaskBulkUpdate
)
from app.schemas.auth import UserResponse
from app.services.task_service import task_service
from app.models.task import TaskStatus
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new task.
    
    Creates a new task for the currently authenticated user.
    """
    try:
        task = task_service.create_task(task_data, current_user.id, db)
        return TaskResponse.model_validate(task)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get("/", response_model=TaskListResponse)
def get_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    is_archived: bool = Query(False, description="Filter by archive status"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)")
):
    """
    Get paginated list of tasks.
    
    Retrieves tasks for the currently authenticated user with optional filtering,
    searching, and pagination.
    """
    try:
        tasks, total = task_service.get_tasks(
            user_id=current_user.id,
            db=db,
            status=status,
            priority=priority,
            is_archived=is_archived,
            search=search,
            page=page,
            size=size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        pages = (total + size - 1) // size  # Calculate total pages
        
        return TaskListResponse(
            tasks=[TaskResponse.model_validate(task) for task in tasks],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tasks: {str(e)}"
        )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific task by ID.
    
    Retrieves a single task by its ID for the currently authenticated user.
    """
    task = task_service.get_task(task_id, current_user.id, db)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing task.
    
    Updates a task by its ID for the currently authenticated user.
    """
    task = task_service.update_task(task_id, current_user.id, task_data, db)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(
    task_id: int,
    status_data: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update task status only.
    
    Updates only the status of a task by its ID.
    """
    task_data = TaskUpdate(status=status_data.status)
    task = task_service.update_task(task_id, current_user.id, task_data, db)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a task.
    
    Deletes a task by its ID for the currently authenticated user.
    """
    success = task_service.delete_task(task_id, current_user.id, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )


@router.post("/bulk-update", status_code=status.HTTP_200_OK)
def bulk_update_tasks(
    bulk_data: TaskBulkUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk update multiple tasks.
    
    Updates multiple tasks at once for the currently authenticated user.
    """
    try:
        updated_count = task_service.bulk_update_tasks(bulk_data, current_user.id, db)
        return {"message": f"Successfully updated {updated_count} tasks"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk update tasks: {str(e)}"
        )


@router.get("/status/{status}", response_model=List[TaskResponse])
def get_tasks_by_status(
    status: TaskStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get tasks by status.
    
    Retrieves all tasks with a specific status for the currently authenticated user.
    """
    try:
        tasks = task_service.get_tasks_by_status(current_user.id, status, db)
        return [TaskResponse.model_validate(task) for task in tasks]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tasks by status: {str(e)}"
        )


@router.get("/overdue", response_model=List[TaskResponse])
def get_overdue_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get overdue tasks.
    
    Retrieves all overdue tasks for the currently authenticated user.
    """
    try:
        tasks = task_service.get_overdue_tasks(current_user.id, db)
        return [TaskResponse.model_validate(task) for task in tasks]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve overdue tasks: {str(e)}"
        )


@router.get("/due-today", response_model=List[TaskResponse])
def get_tasks_due_today(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get tasks due today.
    
    Retrieves all tasks due today for the currently authenticated user.
    """
    try:
        tasks = task_service.get_tasks_due_today(current_user.id, db)
        return [TaskResponse.model_validate(task) for task in tasks]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve tasks due today: {str(e)}"
        )
