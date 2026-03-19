from fastapi import APIRouter

from app.api.routes.alerts import router as alerts_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.health import router as health_router
from app.api.routes.improvements import router as improvements_router
from app.api.routes.recommendations import router as recommendations_router
from app.api.routes.suggestions import router as suggestions_router
from app.api.routes.zones import router as zones_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(zones_router, prefix="/api")
api_router.include_router(suggestions_router, prefix="/api")
api_router.include_router(improvements_router, prefix="/api")
api_router.include_router(alerts_router, prefix="/api")
api_router.include_router(recommendations_router, prefix="/api")
api_router.include_router(analytics_router, prefix="/api")