from app.api.routes.health import router as health_router
from app.api.routes.datasets import router as datasets_router
from app.api.routes.profiles import router as profiles_router
from app.api.routes.preprocessing import router as preprocessing_router

__all__ = ["health_router", "datasets_router", "profiles_router", "preprocessing_router"]

