from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.health import DatabaseHealthResponse, HealthResponse
from app.services.health_service import HealthService

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse, summary="Get application health")
async def get_health() -> HealthResponse:
    """Returns general application status and version."""
    return HealthService.get_app_health()


@router.get("/db", response_model=DatabaseHealthResponse, summary="Get database connectivity health")
async def get_db_health(db: AsyncSession = Depends(get_db)) -> DatabaseHealthResponse:
    """Executes SELECT 1 query against PostgreSQL database to verify connection health."""
    health_service = HealthService(db)
    return await health_service.check_db_health()


@router.get("/live", response_model=HealthResponse, summary="Get liveness probe status")
async def get_liveness() -> HealthResponse:
    """Liveness probe: verifies process is alive."""
    return HealthService.get_app_health()


@router.get("/ready", response_model=HealthResponse, summary="Get readiness probe status")
async def get_readiness(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Readiness probe: verifies database connectivity."""
    health_service = HealthService(db)
    db_res = await health_service.check_db_health()
    if db_res.status != "healthy":
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not ready")
    return HealthService.get_app_health()
