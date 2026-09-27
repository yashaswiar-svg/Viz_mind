from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.datasets import router as datasets_router
from app.api.routes.profiles import router as profiles_router
from app.api.routes.preprocessing import router as preprocessing_router
from app.api.routes.visualizations import router as visualizations_router
from app.api.routes.patterns import router as patterns_router
from app.api.routes.anomalies import router as anomalies_router
from app.api.routes.predictions import router as predictions_router
from app.api.routes.insights import router as insights_router
from app.api.routes.analyst import router as analyst_router
from app.core.config import settings
from app.core.exceptions import (
    VizMindException,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
    vizmind_exception_handler,
)
from app.core.logging import logger
from app.core.middleware import RequestIDMiddleware
from app.core.middleware.security_headers import SecurityHeadersMiddleware
from app.core.middleware.rate_limiter import check_rate_limit


from app.db.database import Base, engine
import app.db.models


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.APP_ENV}]")
    settings.validate_production_config()
    if settings.DATABASE_URL.startswith("sqlite"):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Initialized SQLite database schema.")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        docs_url=f"{settings.api_v1_str}/docs",
        redoc_url=f"{settings.api_v1_str}/redoc",
        openapi_url=f"{settings.api_v1_str}/openapi.json",
        lifespan=lifespan,
        dependencies=[Depends(check_rate_limit)],
    )

    # Middleware
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    app.add_exception_handler(VizMindException, vizmind_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # Router Mounting
    app.include_router(health_router, prefix=settings.api_v1_str)
    app.include_router(auth_router, prefix=settings.api_v1_str)
    app.include_router(datasets_router, prefix=settings.api_v1_str)
    app.include_router(profiles_router, prefix=settings.api_v1_str)
    app.include_router(preprocessing_router, prefix=settings.api_v1_str)
    app.include_router(visualizations_router, prefix=settings.api_v1_str)
    app.include_router(patterns_router, prefix=settings.api_v1_str)
    app.include_router(anomalies_router, prefix=settings.api_v1_str)
    app.include_router(predictions_router, prefix=settings.api_v1_str)
    app.include_router(insights_router, prefix=settings.api_v1_str)
    app.include_router(analyst_router, prefix=settings.api_v1_str)

    return app


app = create_application()






app = create_application()
