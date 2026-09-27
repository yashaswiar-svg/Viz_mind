from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.exceptions import DatabaseConnectionException
from app.schemas.health import DatabaseHealthResponse, HealthResponse


class HealthService:
    """Service providing application and database health validation."""

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def get_app_health() -> HealthResponse:
        return HealthResponse(
            status="healthy",
            service=settings.APP_NAME,
            version=settings.APP_VERSION,
        )

    async def check_db_health(self) -> DatabaseHealthResponse:
        try:
            result = await self.session.execute(text("SELECT 1"))
            val = result.scalar()
            if val == 1:
                return DatabaseHealthResponse(status="healthy", database="connected")
            else:
                raise DatabaseConnectionException(message="Unexpected response from database check.")
        except Exception as exc:
            raise DatabaseConnectionException(message=f"Database connectivity check failed: {str(exc)}")
