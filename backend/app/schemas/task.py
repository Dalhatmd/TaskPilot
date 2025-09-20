"""
Task schemas for request/response validation.
Defines Pydantic models for task CRUD operations.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.task import TaskStatus


class TaskBase(BaseModel):
    """Base schema for task data."""
    
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: TaskStatus = Field(TaskStatus.TODO, description="Task status")
    due_date: Optional[datetime] = Field(None, description="Due date and time")
    priority: str = Field("medium", description="Task priority (low, medium, high)")


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: Optional[TaskStatus] = Field(None, description="Task status")
    due_date: Optional[datetime] = Field(None, description="Due date and time")
    priority: Optional[str] = Field(None, description="Task priority (low, medium, high)")
    is_archived: Optional[bool] = Field(None, description="Whether task is archived")


class TaskResponse(TaskBase):
    """Schema for task data in responses."""
    
    id: int
    user_id: int
    is_archived: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for paginated task list response."""
    
    tasks: list[TaskResponse]
    total: int
    page: int
    size: int
    pages: int


class TaskStatusUpdate(BaseModel):
    """Schema for updating only task status."""
    
    status: TaskStatus = Field(..., description="New task status")


class TaskBulkUpdate(BaseModel):
    """Schema for bulk updating multiple tasks."""
    
    task_ids: list[int] = Field(..., min_items=1, description="List of task IDs to update")
    status: Optional[TaskStatus] = Field(None, description="New status for all tasks")
    is_archived: Optional[bool] = Field(None, description="Archive status for all tasks")
