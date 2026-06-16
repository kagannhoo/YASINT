from fastapi import APIRouter

from .analysis import router as analysis_router
from .upload import router as upload_router
from .websocket import router as websocket_router
from .system import router as system_router

api_router = APIRouter()
api_router.include_router(analysis_router)
api_router.include_router(upload_router)
api_router.include_router(websocket_router)
api_router.include_router(system_router)
