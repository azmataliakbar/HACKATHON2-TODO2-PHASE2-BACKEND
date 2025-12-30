from fastapi import APIRouter
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_async_session
from sqlalchemy import text
from fastapi import Depends


router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint to verify the application is running."""
    return {
        "status": "healthy",
        "message": "Todo API is running",
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }