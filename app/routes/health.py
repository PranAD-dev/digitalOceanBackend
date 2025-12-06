from fastapi import APIRouter

from app.config import settings
from app.models import HealthCheckResponse

router = APIRouter(tags=["Health"])


@router.get("/", response_model=HealthCheckResponse)
async def root():
    """Root endpoint - basic health check"""
    return HealthCheckResponse(
        status="ok",
        version=settings.app_version,
        service=settings.app_name
    )


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    return HealthCheckResponse(
        status="healthy",
        version=settings.app_version,
        service=settings.app_name
    )
