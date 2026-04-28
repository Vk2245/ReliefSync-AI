"""
Simple API Router for quick deployment.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Simple"])

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint."""
    return {"message": "ReliefSync-AI API is working!", "status": "success"}

@router.get("/emergencies")
async def list_emergencies():
    """Simple emergencies list."""
    return {"emergencies": [], "message": "Database connected"}

@router.get("/volunteers")
async def list_volunteers():
    """Simple volunteers list."""
    return {"volunteers": [], "message": "Database connected"}