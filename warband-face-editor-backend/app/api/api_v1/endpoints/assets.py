from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from app.core.config import settings


router = APIRouter()


@router.get("/manifest")
async def get_asset_manifest():
    """Get manifest of available 3D assets and textures."""
    manifest = {
        "models": {
            "head_preview": "/api/v1/assets/models/head_preview.glb",
            "head_full": "/api/v1/assets/models/head_full.glb"
        },
        "textures": {
            "skin_tones": [
                "/api/v1/assets/textures/skin_0.webp",  # White
                "/api/v1/assets/textures/skin_1.webp",  # Light
                "/api/v1/assets/textures/skin_2.webp",  # Tan
                "/api/v1/assets/textures/skin_3.webp",  # Dark
                "/api/v1/assets/textures/skin_4.webp"   # Black
            ]
        },
        "hair": {
            "meshes": "/api/v1/assets/hair/manifest.json",
            "textures": "/api/v1/assets/hair/textures/"
        },
        "beard": {
            "meshes": "/api/v1/assets/beard/manifest.json",
            "textures": "/api/v1/assets/beard/textures/"
        }
    }
    return manifest


@router.get("/models/{filename}")
async def get_model(filename: str):
    """Serve 3D model files."""
    model_path = settings.ASSETS_DIR / "models" / filename
    
    if not model_path.exists() or not model_path.is_file():
        raise HTTPException(status_code=404, detail="Model not found")
    
    return FileResponse(
        path=model_path,
        media_type="model/gltf-binary" if filename.endswith('.glb') else "model/gltf+json"
    )


@router.get("/textures/{filename}")
async def get_texture(filename: str):
    """Serve texture files."""
    texture_path = settings.ASSETS_DIR / "textures" / filename
    
    if not texture_path.exists() or not texture_path.is_file():
        raise HTTPException(status_code=404, detail="Texture not found")
    
    media_type = "image/webp" if filename.endswith('.webp') else "image/png"
    return FileResponse(path=texture_path, media_type=media_type)