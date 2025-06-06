from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    PROJECT_NAME: str = "Warband Face Editor API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # File upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set[str] = {".dat"}
    
    # Paths - use home directory for resources
    HOME_DIR: Path = Path.home()
    DATA_DIR: Path = HOME_DIR / ".warband-face-editor"
    ASSETS_DIR: Path = DATA_DIR / "assets"
    UPLOADS_DIR: Path = DATA_DIR / "uploads"
    CACHE_DIR: Path = DATA_DIR / "cache"
    
    # Face generation
    MAX_MORPH_VALUE: int = 7
    NUM_MORPHS: int = 8
    
    # WebSocket
    WS_MESSAGE_QUEUE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Create directories
settings.DATA_DIR.mkdir(exist_ok=True)
settings.ASSETS_DIR.mkdir(exist_ok=True)
settings.UPLOADS_DIR.mkdir(exist_ok=True)
settings.CACHE_DIR.mkdir(exist_ok=True)