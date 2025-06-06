# Warband Face Editor Backend

FastAPI backend for Mount & Blade Warband face editor web application.

## Features

- Face code encoding/decoding
- Profile.dat file parsing and character extraction
- Real-time face updates via WebSocket
- 3D asset serving
- RESTful API for face manipulation

## Quick Start

### Using Docker (Recommended)

```bash
# Build and start services
make build
make up

# View logs
make logs

# Stop services
make down
```

### Manual Setup

```bash
# Run the application
./run.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API will be available at: http://localhost:8000
Documentation: http://localhost:8000/docs

## Docker Commands

```bash
make build   # Build Docker images
make up      # Start services (development)
make down    # Stop services
make logs    # View logs
make shell   # Enter backend container
make clean   # Remove containers and volumes
make test    # Run tests
```

## API Endpoints

### Face Operations
- `POST /api/v1/face/decode` - Decode hex face code to parameters
- `POST /api/v1/face/encode` - Encode parameters to hex face code
- `GET /api/v1/face/validate/{face_code}` - Validate face code

### Profile Management
- `POST /api/v1/profiles/upload` - Upload profiles.dat
- `GET /api/v1/profiles/{upload_id}/characters` - Get characters
- `PUT /api/v1/profiles/{upload_id}/characters/{index}/face` - Update face

### Assets
- `GET /api/v1/assets/manifest` - Get asset URLs
- `GET /api/v1/assets/models/{filename}` - Get 3D models
- `GET /api/v1/assets/textures/{filename}` - Get textures

### WebSocket
- `WS /api/v1/ws/face-updates` - Real-time face updates

## Project Structure

```
warband-face-editor-backend/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Core configuration
│   ├── models/       # Pydantic models
│   ├── services/     # Business logic
│   └── main.py       # FastAPI app
├── assets/           # 3D models and textures
├── tests/            # Unit tests
└── scripts/          # Utility scripts
```