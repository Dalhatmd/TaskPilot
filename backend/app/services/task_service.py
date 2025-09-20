"""
Task service for business logic.
Handles task CRUD operations and business rules.
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime

from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskBulkUpdate


class TaskService:
    """Service for handling task operations."""
    
    def __init__(self):
        pass
    
    def create_task(self, task_data: TaskCreate, user_id: int, db: Session) -> Task:
        """Create a new task for a user."""
        db_task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            due_date=task_data.due_date,
            priority=task_data.priority,
            user_id=user_id
        )
        
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
    def get_task(self, task_id: int, user_id: int, db: Session) -> Optional[Task]:
        """Get a specific task by ID for a user."""
        return db.query(Task).filter(
            and_(Task.id == task_id, Task.user_id == user_id)
        ).first()
    
    def get_tasks(
        self, 
        user_id: int, 
        db: Session,
        status: Optional[TaskStatus] = None,
        priority: Optional[str] = None,
        is_archived: bool = False,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Task], int]:
        """Get paginated list of tasks for a user with filters."""
        
        # Base query
        query = db.query(Task).filter(Task.user_id == user_id)
        
        # Apply filters
        if status is not None:
            query = query.filter(Task.status == status)
        
        if priority is not None:
            query = query.filter(Task.priority == priority)
        
        if is_archived is not None:
            query = query.filter(Task.is_archived == is_archived)
        
        if search:
            search_filter = or_(
                Task.title.ilike(f"%{search}%"),
                Task.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        if hasattr(Task, sort_by):
            sort_column = getattr(Task, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        
        # Apply pagination
        offset = (page - 1) * size
        tasks = query.offset(offset).limit(size).all()
        
        return tasks, total
    
    def update_task(
        self, 
        task_id: int, 
        user_id: int, 
        task_data: TaskUpdate, 
        db: Session
    ) -> Optional[Task]:
        """Update an existing task."""
        db_task = self.get_task(task_id, user_id, db)
        if not db_task:
            return None
        
        # Update only provided fields
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    
    def delete_task(self, task_id: int, user_id: int, db: Session) -> bool:
        """Delete a task."""
        db_task = self.get_task(task_id, user_id, db)
        if not db_task:
            return False
        
        db.delete(db_task)
        db.commit()
        return True
    
    def bulk_update_tasks(
        self, 
        bulk_data: TaskBulkUpdate, 
        user_id: int, 
        db: Session
    ) -> int:
        """Bulk update multiple tasks."""
        update_data = bulk_data.model_dump(exclude_unset=True, exclude={"task_ids"})
        if not update_data:
            return 0
        
        # Update tasks that belong to the user
        updated_count = db.query(Task).filter(
            and_(
                Task.id.in_(bulk_data.task_ids),
                Task.user_id == user_id
            )
        ).update(update_data, synchronize_session=False)
        
        db.commit()
        return updated_count
    
    def get_tasks_by_status(
        self, 
        user_id: int, 
        status: TaskStatus, 
        db: Session
    ) -> List[Task]:
        """Get all tasks with a specific status for a user."""
        return db.query(Task).filter(
            and_(Task.user_id == user_id, Task.status == status)
        ).all()
    
    def get_overdue_tasks(self, user_id: int, db: Session) -> List[Task]:
        """Get all overdue tasks for a user."""
        now = datetime.utcnow()
        return db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.due_date < now,
                Task.status != TaskStatus.COMPLETED,
                Task.is_archived == False
            )
        ).all()
    
    def get_tasks_due_today(self, user_id: int, db: Session) -> List[Task]:
        """Get all tasks due today for a user."""
        today = datetime.utcnow().date()
        return db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.due_date.cast(db.Date) == today,
                Task.status != TaskStatus.COMPLETED,
                Task.is_archived == False
            )
        ).all()


# Global task service instance
task_service = TaskService()
