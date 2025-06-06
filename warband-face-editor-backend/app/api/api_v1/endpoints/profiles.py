from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
from uuid import uuid4

from app.core.config import settings
from app.models.face import Character
from app.services.profile_parser import ProfileParser


router = APIRouter()
profile_parser = ProfileParser()


@router.post("/upload")
async def upload_profile(file: UploadFile = File(...)):
    """Upload a profiles.dat file and parse characters."""
    # Validate file extension
    if not file.filename.endswith('.dat'):
        raise HTTPException(status_code=400, detail="Only .dat files are allowed")
    
    # Validate file size
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE} bytes")
    
    # Save uploaded file
    upload_id = str(uuid4())
    upload_path = settings.UPLOADS_DIR / f"{upload_id}.dat"
    
    try:
        with upload_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse characters
        characters = profile_parser.parse_profile(upload_path)
        
        return {
            "upload_id": upload_id,
            "filename": file.filename,
            "character_count": len(characters),
            "characters": characters
        }
    
    except Exception as e:
        # Clean up on error
        if upload_path.exists():
            upload_path.unlink()
        raise HTTPException(status_code=400, detail=f"Failed to parse profile: {str(e)}")
    finally:
        file.file.close()


@router.get("/{upload_id}/characters")
async def get_characters(upload_id: str):
    """Get parsed characters from a previously uploaded profile."""
    upload_path = settings.UPLOADS_DIR / f"{upload_id}.dat"
    
    if not upload_path.exists():
        raise HTTPException(status_code=404, detail="Upload not found")
    
    try:
        characters = profile_parser.parse_profile(upload_path)
        return {"characters": characters}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse profile: {str(e)}")


@router.put("/{upload_id}/characters/{character_index}/face")
async def update_character_face(upload_id: str, character_index: int, face_code: str):
    """Update a character's face code in the uploaded profile."""
    upload_path = settings.UPLOADS_DIR / f"{upload_id}.dat"
    
    if not upload_path.exists():
        raise HTTPException(status_code=404, detail="Upload not found")
    
    try:
        success = profile_parser.update_character_face(upload_path, character_index, face_code)
        if success:
            return {"message": "Face updated successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to update face")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))