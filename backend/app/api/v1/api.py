"""
Main API router for v1 endpoints.
Combines all endpoint routers into a single API router.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, tasks, ai

api_router = APIRouter()

# Include authentication routes
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

# Include task routes
api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["tasks"]
)

# Include AI routes
api_router.include_router(
    ai.router,
    prefix="/ai",
    tags=["ai"]
)
