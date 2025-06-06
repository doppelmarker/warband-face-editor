from fastapi import APIRouter

from app.api.api_v1.endpoints import face, profiles, assets, websocket


api_router = APIRouter()

api_router.include_router(face.router, prefix="/face", tags=["face"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])