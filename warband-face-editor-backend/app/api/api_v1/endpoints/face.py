from fastapi import APIRouter, HTTPException
from app.models.face import FaceParameters, FaceCode, DecodedFace
from app.services.face_code_service import face_code_service


router = APIRouter()


@router.post("/decode", response_model=DecodedFace)
async def decode_face_code(face_code: FaceCode):
    """Decode a hex face code into individual parameters."""
    try:
        params_dict = face_code_service.decode_face_code(face_code.hex_code)
        params = FaceParameters(**params_dict)
        
        return DecodedFace(
            parameters=params,
            face_code=face_code.hex_code
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/encode")
async def encode_face_parameters(params: FaceParameters):
    """Encode face parameters into a hex face code."""
    try:
        face_code = face_code_service.encode_face_code(params)
        return {"face_code": face_code}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/validate/{face_code}")
async def validate_face_code(face_code: str):
    """Validate if a face code is properly formatted and within valid ranges."""
    try:
        # Try to decode it
        params_dict = face_code_service.decode_face_code(face_code)
        FaceParameters(**params_dict)
        
        return {
            "valid": True,
            "face_code": face_code,
            "message": "Face code is valid"
        }
    except Exception as e:
        return {
            "valid": False,
            "face_code": face_code,
            "message": str(e)
        }