from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

from app.models.face import FaceParameters
from app.services.face_code_service import face_code_service


router = APIRouter()


@router.websocket("/face-updates")
async def websocket_face_updates(websocket: WebSocket):
    """WebSocket endpoint for real-time face parameter updates for individual user session."""
    await websocket.accept()
    
    try:
        while True:
            # Receive face update from client
            data = await websocket.receive_text()
            update = json.loads(data)
            
            if update.get("type") == "face_update":
                # Validate parameters
                try:
                    params = FaceParameters(**update["parameters"])
                    face_code = face_code_service.encode_face_code(params)
                    
                    # Send response back to the same client
                    await websocket.send_text(json.dumps({
                        "type": "face_update_response",
                        "parameters": params.dict(),
                        "face_code": face_code
                    }))
                except ValueError as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": str(e)
                    }))
            
            elif update.get("type") == "ping":
                # Simple ping/pong for connection health check
                await websocket.send_text(json.dumps({
                    "type": "pong"
                }))
            
    except WebSocketDisconnect:
        pass  # Client disconnected, nothing to clean up