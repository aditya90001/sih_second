from fastapi import APIRouter
from app.api.endpoints import (
    health, wells, map, documents, search, chat, risks, alerts
)
from app.websocket.connection_manager import router as websocket_router

api_router = APIRouter()

# Register all routes specified in prompt
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(wells.router, prefix="/wells", tags=["Wells"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(chat.router, prefix="/chat", tags=["RAG Chat"])
api_router.include_router(risks.router, prefix="/risk", tags=["ML Risks"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alert Engine"])
api_router.include_router(websocket_router, tags=["eRTMAC WebSocket Simulator"])