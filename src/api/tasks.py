from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from src.core.database import get_async_session
from src.models.task import Task, TaskCreate, TaskUpdate
from src.schemas.task import TaskResponse, TaskListResponse
from src.middleware.auth import get_current_user
from src.models.user import User
from sqlmodel import select, and_
from datetime import datetime


router = APIRouter()


@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    status_filter: Optional[str] = Query("all", description="Filter by completion status: all, pending, completed")
):
    """List all tasks for the authenticated user."""

    # Build query based on status filter
    query = select(Task).where(Task.user_id == current_user.id)

    if status_filter == "pending":
        query = query.where(Task.completed == False)
    elif status_filter == "completed":
        query = query.where(Task.completed == True)

    # Execute query
    result = await session.execute(query)
    tasks = result.scalars().all()

    # Calculate counts
    total = len(tasks)
    pending = len([task for task in tasks if not task.completed])
    completed = len([task for task in tasks if task.completed])

    # Format response
    task_responses = [TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        user_id=task.user_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at
    ) for task in tasks]

    return TaskListResponse(
        tasks=task_responses,
        total=total,
        pending=pending,
        completed=completed
    )


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Create a new task for the authenticated user."""

    # Create task instance
    task = Task(
        title=task_data.title,
        description=task_data.description,
        completed=False,  # New tasks are pending by default
        user_id=current_user.id
    )

    # Add to session and commit
    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Return response
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        user_id=task.user_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get details of a specific task."""

    # Query for the task belonging to the current user
    result = await session.execute(
        select(Task).where(and_(Task.id == task_id, Task.user_id == current_user.id))
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to access it"
        )

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        user_id=task.user_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at
    )


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Update task details."""

    # Query for the task belonging to the current user
    result = await session.execute(
        select(Task).where(and_(Task.id == task_id, Task.user_id == current_user.id))
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to access it"
        )

    # Update fields that were provided
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.completed is not None:
        task.completed = task_data.completed
        # Update completed_at timestamp if task is being marked as completed
        if task_data.completed and not task.completed:
            task.completed_at = datetime.utcnow()
        elif not task_data.completed:
            task.completed_at = None

    # Update the updated_at timestamp
    task.updated_at = datetime.utcnow()

    # Commit changes
    await session.commit()
    await session.refresh(task)

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        user_id=task.user_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at
    )


@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    task_id: int,
    completed_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Toggle task completion status."""

    # Query for the task belonging to the current user
    result = await session.execute(
        select(Task).where(and_(Task.id == task_id, Task.user_id == current_user.id))
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to access it"
        )

    # Update completion status
    if completed_data.completed is not None:
        task.completed = completed_data.completed
        # Update completed_at timestamp if task is being marked as completed
        if completed_data.completed:
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None

    # Update the updated_at timestamp
    task.updated_at = datetime.utcnow()

    # Commit changes
    await session.commit()
    await session.refresh(task)

    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        user_id=task.user_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at
    )


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Delete a task permanently."""

    # Query for the task belonging to the current user
    result = await session.execute(
        select(Task).where(and_(Task.id == task_id, Task.user_id == current_user.id))
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or you don't have permission to access it"
        )

    # Delete the task
    await session.delete(task)
    await session.commit()

    return {"message": "Task deleted successfully"}