# Step-by-Step Implementation Guide: Mount & Blade Warband Web Character Editor

## 1. Extracting Character Models, Textures, and Animations from Game Files

### File Locations and Structure
```
Mount & Blade Warband/
├── Modules/
│   └── Native/
│       ├── Resource/       # BRF files (models, textures, animations)
│       ├── Textures/       # DDS texture files
│       └── module.ini
└── Textures/              # Common textures
```

### Using OpenBRF for Asset Extraction

**Download OpenBRF** (version 0.0.80e) from Nexus Mods or TaleWorlds forums.

**Command-line extraction:**
```bash
# Dump module contents for scripting
OpenBRF.exe --dump "C:\...\Modules\Native" module_assets.txt

# Linux compilation
qmake -makefile openBrf.pro
make
env LC_NUMERIC=C ./openBrf
```

**Python batch extraction script:**
```python
import subprocess
import os
from pathlib import Path

class WarbandAssetExtractor:
    def __init__(self, game_path, output_path):
        self.game_path = Path(game_path)
        self.output_path = Path(output_path)
        self.openbrf_path = "OpenBRF.exe"
    
    def extract_module_assets(self, module_name):
        module_path = self.game_path / "Modules" / module_name
        resource_path = module_path / "Resource"
        
        output_dir = self.output_path / module_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process each BRF file
        for brf_file in resource_path.glob("*.brf"):
            self.extract_brf(brf_file, output_dir)
    
    def extract_brf(self, brf_path, output_dir):
        print(f"Processing {brf_path.name}")
        # Manual extraction via OpenBRF GUI
        # Export as: OBJ (static), SMD (rigged/animated)

# Usage
extractor = WarbandAssetExtractor(
    game_path="C:/Program Files (x86)/Steam/steamapps/common/MountBlade Warband",
    output_path="./extracted_assets"
)
extractor.extract_module_assets("Native")
```

## 2. Converting BRF Files to Web-Friendly Formats (GLTF/GLB)

### Conversion Pipeline: BRF → OBJ/SMD → GLTF

**Blender automation script (convert_to_gltf.py):**
```python
import bpy
import sys
import os

# Clear default scene
bpy.ops.object.delete()

# Get file paths from command line
obj_path = sys.argv[sys.argv.index('--') + 1]
output_path = sys.argv[sys.argv.index('--') + 2]

# Import OBJ
bpy.ops.import_scene.obj(filepath=obj_path)

# Export as GLTF/GLB
bpy.ops.export_scene.gltf(
    filepath=output_path,
    export_format='GLB',
    export_materials='EXPORT',
    export_colors=True,
    export_animations=True
)
```

**Batch conversion script:**
```python
import subprocess
from pathlib import Path

def convert_obj_to_gltf(obj_path, output_path):
    """Convert OBJ to GLTF using Blender command-line"""
    cmd = [
        "blender", "-b", "-P", "convert_to_gltf.py", "--",
        str(obj_path), str(output_path)
    ]
    subprocess.run(cmd, check=True)

def batch_convert_to_gltf(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for obj_file in input_path.glob("**/*.obj"):
        gltf_file = output_path / f"{obj_file.stem}.glb"
        try:
            convert_obj_to_gltf(obj_file, gltf_file)
            print(f"Converted {obj_file} → {gltf_file}")
        except Exception as e:
            print(f"Error converting {obj_file}: {e}")

# Run conversion
batch_convert_to_gltf("./extracted_assets", "./web_assets")
```

**GLTF optimization using gltf-transform:**
```bash
# Install gltf-transform
npm install -g @gltf-transform/cli

# Optimize with Draco compression and texture optimization
gltf-transform optimize input.glb output.glb \
    --draco.quantization-position 12 \
    --draco.quantization-normal 8 \
    --draco.quantization-texcoord 10 \
    --texture-compress ktx2
```

## 3. Setting up Python Backend (FastAPI)

### Project Structure
```
warband_editor/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── characters.py
│   │   ├── files.py
│   │   └── profiles.py
│   ├── models/
│   │   ├── character.py
│   │   └── profile.py
│   ├── services/
│   │   ├── profile_parser.py
│   │   ├── character_editor.py
│   │   └── file_manager.py
│   └── utils/
│       ├── binary_utils.py
│       └── validation.py
├── uploads/
├── backups/
└── requirements.txt
```

### requirements.txt
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
python-magic==0.4.27
aiofiles==23.2.1
structlog==23.2.0
redis==5.0.1
```

### main.py - FastAPI Application
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import structlog

from app.api import characters, files, profiles
from app.core.config import settings

app = FastAPI(
    title="Mount & Blade Warband Character Editor API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(characters.router, prefix="/api/v1/characters", tags=["characters"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(profiles.router, prefix="/api/v1/profiles", tags=["profiles"])

# Static file serving
app.mount("/assets", StaticFiles(directory="web_assets"), name="assets")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

### Profile Parser Service Integration
```python
# services/profile_parser.py
import struct
import asyncio
from typing import List, Dict
import aiofiles
from pathlib import Path

class ProfileParserService:
    """Integration with existing profiles.dat manipulation script"""
    
    def __init__(self):
        self.profiles_dir = Path("uploads/profiles")
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
    
    async def parse_profiles_data(self, data: bytes) -> List[Dict]:
        """Parse binary profiles.dat - integrate your existing script here"""
        # Your existing profiles.dat parsing logic
        characters = []
        offset = 0
        
        # Read header
        magic_number = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        
        # Parse characters
        char_count = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        
        for i in range(char_count):
            # Parse character data using your existing logic
            character = self.parse_character(data, offset)
            characters.append(character)
            offset = character['next_offset']
        
        return characters
    
    def parse_character(self, data: bytes, offset: int) -> Dict:
        """Parse individual character from profiles.dat"""
        # Implement based on your reverse-engineered format
        pass
```

### Character API Endpoints
```python
# api/characters.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.character import Character, CharacterUpdate
from app.services.character_editor import CharacterEditorService

router = APIRouter()

@router.get("/{character_id}")
async def get_character(character_id: str, profile_id: str):
    editor = CharacterEditorService()
    character = await editor.get_character(profile_id, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character

@router.put("/{character_id}")
async def update_character(
    character_id: str,
    profile_id: str,
    character_data: CharacterUpdate,
    background_tasks: BackgroundTasks
):
    editor = CharacterEditorService()
    background_tasks.add_task(editor.create_backup, profile_id)
    
    updated_character = await editor.update_character(
        profile_id, character_id, character_data
    )
    return updated_character

@router.post("/{character_id}/appearance")
async def update_character_appearance(
    character_id: str,
    profile_id: str,
    face_code: str
):
    """Update character appearance using Mount & Blade face code"""
    editor = CharacterEditorService()
    
    # Validate face code format (64-character hex)
    if not face_code.startswith('0x') or len(face_code) != 66:
        raise HTTPException(status_code=400, detail="Invalid face code")
    
    updated_character = await editor.update_appearance(
        profile_id, character_id, face_code
    )
    return updated_character
```

## 4. Building Three.js Frontend with Character Rendering

### Three.js Scene Setup
```javascript
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js';

class CharacterViewer {
    constructor(container) {
        this.container = container;
        this.setupScene();
        this.setupLoaders();
        this.setupLights();
        this.setupControls();
    }

    setupScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x2a2a2a);
        
        this.camera = new THREE.PerspectiveCamera(
            75, 
            window.innerWidth / window.innerHeight,
            0.1, 
            1000
        );
        this.camera.position.set(0, 1.5, 3);
        
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);
    }

    setupLoaders() {
        // Setup Draco loader for compressed models
        this.dracoLoader = new DRACOLoader();
        this.dracoLoader.setDecoderPath('/libs/draco/');
        
        this.gltfLoader = new GLTFLoader();
        this.gltfLoader.setDRACOLoader(this.dracoLoader);
    }

    async loadCharacterModel(modelPath) {
        try {
            const gltf = await this.gltfLoader.loadAsync(modelPath);
            this.characterModel = gltf.scene;
            
            // Setup animations if available
            if (gltf.animations && gltf.animations.length > 0) {
                this.mixer = new THREE.AnimationMixer(this.characterModel);
                this.animations = {};
                
                gltf.animations.forEach((clip) => {
                    this.animations[clip.name] = this.mixer.clipAction(clip);
                });
                
                // Play idle animation
                if (this.animations['idle']) {
                    this.animations['idle'].play();
                }
            }
            
            this.scene.add(this.characterModel);
            this.setupMorphTargets();
            
        } catch (error) {
            console.error('Error loading character model:', error);
        }
    }
}
```

### Mount & Blade Face Code Implementation
```javascript
class MountBladeFaceCustomizer {
    constructor(characterModel) {
        this.characterModel = characterModel;
        this.morphTargets = new Map();
        this.initializeMorphTargets();
    }

    parseFaceCode(faceCodeHex) {
        // Convert Mount & Blade face code to morph target values
        const hexWithoutPrefix = faceCodeHex.replace('0x', '');
        const parts = [];
        
        // Split hex into 16-digit chunks
        for (let i = hexWithoutPrefix.length; i > 0; i -= 16) {
            const start = Math.max(0, i - 16);
            const part = hexWithoutPrefix.substring(start, i);
            parts.unshift(parseInt(part, 16));
        }
        
        // Map to facial features
        return this.mapToFacialFeatures(parts);
    }

    mapToFacialFeatures(parts) {
        // Based on Mount & Blade face code structure
        return {
            age: (parts[0] & 0xFF) / 255,
            weight: ((parts[0] >> 8) & 0xFF) / 255,
            build: ((parts[0] >> 16) & 0xFF) / 255,
            // ... map other features
        };
    }

    applyFaceCode(faceCode) {
        const features = this.parseFaceCode(faceCode);
        
        // Apply to morph targets
        Object.entries(features).forEach(([feature, value]) => {
            this.setMorphTarget(feature, value);
        });
    }

    setMorphTarget(targetName, value) {
        this.characterModel.traverse((child) => {
            if (child.isMesh && child.morphTargetInfluences) {
                const index = child.morphTargetDictionary?.[targetName];
                if (index !== undefined) {
                    child.morphTargetInfluences[index] = value;
                }
            }
        });
    }
}
```

### Equipment System
```javascript
class EquipmentManager {
    constructor(scene, loader) {
        this.scene = scene;
        this.loader = loader;
        this.equipmentSlots = {
            helmet: null,
            armor: null,
            gloves: null,
            boots: null,
            weapon: null,
            shield: null
        };
    }

    async equipItem(slot, itemId) {
        // Remove existing item
        if (this.equipmentSlots[slot]) {
            this.scene.remove(this.equipmentSlots[slot]);
        }

        // Load new item
        const itemPath = `/assets/models/equipment/${itemId}.glb`;
        const gltf = await this.loader.loadAsync(itemPath);
        const item = gltf.scene;

        // Attach to character
        const attachPoint = this.getAttachPoint(slot);
        if (attachPoint) {
            attachPoint.add(item);
            this.equipmentSlots[slot] = item;
        }
    }

    getAttachPoint(slot) {
        // Find bone/attachment point on character model
        const attachPoints = {
            helmet: 'head_bone',
            weapon: 'weapon_bone_r',
            shield: 'weapon_bone_l'
        };
        
        let attachBone = null;
        this.scene.traverse((child) => {
            if (child.name === attachPoints[slot]) {
                attachBone = child;
            }
        });
        
        return attachBone;
    }
}
```

## 5. Connecting Frontend and Backend - API Design

### API Client Service
```javascript
class CharacterAPIClient {
    constructor(baseURL = 'http://localhost:8000/api/v1') {
        this.baseURL = baseURL;
    }

    async getCharacter(profileId, characterId) {
        const response = await fetch(
            `${this.baseURL}/characters/${characterId}?profile_id=${profileId}`
        );
        return response.json();
    }

    async updateCharacter(profileId, characterId, characterData) {
        const response = await fetch(
            `${this.baseURL}/characters/${characterId}?profile_id=${profileId}`,
            {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(characterData)
            }
        );
        return response.json();
    }

    async uploadProfile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${this.baseURL}/files/upload-profile`, {
            method: 'POST',
            body: formData
        });
        return response.json();
    }

    async downloadProfile(profileId) {
        const response = await fetch(
            `${this.baseURL}/files/download-profile/${profileId}`
        );
        const blob = await response.blob();
        
        // Trigger download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `profiles_${profileId}.dat`;
        a.click();
    }
}
```

### WebSocket Integration for Real-time Updates
```javascript
class CharacterWebSocket {
    constructor(characterId) {
        this.characterId = characterId;
        this.ws = null;
        this.reconnectInterval = 5000;
        this.connect();
    }

    connect() {
        this.ws = new WebSocket(
            `ws://localhost:8000/ws/character/${this.characterId}`
        );

        this.ws.onopen = () => {
            console.log('WebSocket connected');
        };

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            setTimeout(() => this.connect(), this.reconnectInterval);
        };
    }

    handleMessage(message) {
        switch (message.type) {
            case 'character_update':
                this.onCharacterUpdate(message.data);
                break;
            case 'equipment_change':
                this.onEquipmentChange(message.data);
                break;
        }
    }

    sendUpdate(updateType, data) {
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: updateType,
                data: data
            }));
        }
    }
}
```

## 6. Asset Pipeline Automation

### Automated Asset Processing Script
```python
#!/usr/bin/env python3
import os
import subprocess
import json
from pathlib import Path
import concurrent.futures

class AssetPipeline:
    def __init__(self, source_dir, output_dir):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.manifest = {"models": {}, "textures": {}}
    
    def process_all_assets(self):
        """Process all game assets in parallel"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Process models
            model_futures = []
            for brf_file in self.source_dir.glob("**/*.brf"):
                future = executor.submit(self.process_brf_file, brf_file)
                model_futures.append(future)
            
            # Process textures
            texture_futures = []
            for dds_file in self.source_dir.glob("**/*.dds"):
                future = executor.submit(self.process_texture, dds_file)
                texture_futures.append(future)
            
            # Wait for completion
            concurrent.futures.wait(model_futures + texture_futures)
        
        self.save_manifest()
    
    def process_brf_file(self, brf_path):
        """Extract and convert BRF to GLTF"""
        # Step 1: Extract using OpenBRF
        temp_obj = self.output_dir / "temp" / f"{brf_path.stem}.obj"
        self.extract_from_brf(brf_path, temp_obj)
        
        # Step 2: Convert to GLTF
        output_glb = self.output_dir / "models" / f"{brf_path.stem}.glb"
        self.convert_to_gltf(temp_obj, output_glb)
        
        # Step 3: Optimize
        self.optimize_gltf(output_glb)
        
        # Add to manifest
        self.manifest["models"][brf_path.stem] = {
            "path": str(output_glb.relative_to(self.output_dir)),
            "size": output_glb.stat().st_size,
            "format": "glb"
        }
    
    def process_texture(self, dds_path):
        """Convert DDS textures to web formats"""
        # Convert to WebP for better compression
        output_webp = self.output_dir / "textures" / f"{dds_path.stem}.webp"
        
        subprocess.run([
            "convert", str(dds_path), 
            "-quality", "85",
            str(output_webp)
        ], check=True)
        
        # Generate mipmaps
        self.generate_mipmaps(output_webp)
        
        # Add to manifest
        self.manifest["textures"][dds_path.stem] = {
            "path": str(output_webp.relative_to(self.output_dir)),
            "format": "webp",
            "sizes": ["1024", "512", "256", "128"]
        }
    
    def optimize_gltf(self, gltf_path):
        """Optimize GLTF with compression"""
        subprocess.run([
            "gltf-transform", "optimize", str(gltf_path), str(gltf_path),
            "--draco.quantization-position", "12",
            "--draco.quantization-normal", "8",
            "--texture-compress", "ktx2"
        ], check=True)
    
    def save_manifest(self):
        """Save asset manifest for frontend"""
        manifest_path = self.output_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)

# Run pipeline
pipeline = AssetPipeline("./warband_assets", "./web_assets")
pipeline.process_all_assets()
```

### Batch Processing Configuration
```yaml
# asset_pipeline_config.yaml
processing:
  models:
    formats: [brf]
    output_format: glb
    compression:
      draco:
        enabled: true
        quantization_position: 12
        quantization_normal: 8
    lod_generation:
      enabled: true
      levels: [100%, 50%, 25%]
  
  textures:
    formats: [dds, tga]
    output_formats:
      primary: webp
      fallback: jpg
    sizes: [2048, 1024, 512, 256]
    compression_quality: 85

optimization:
  parallel_workers: 4
  cache_processed: true
  skip_existing: true
```

## 7. Deployment Architecture

### Docker Deployment Configuration

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/warband
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./uploads:/app/uploads
      - ./web_assets:/app/web_assets
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=warband
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./web_assets:/usr/share/nginx/html/assets
    depends_on:
      - api
      - frontend

volumes:
  postgres_data:
  redis_data:
```

### Nginx Configuration for Asset Serving
```nginx
# nginx.conf
server {
    listen 80;
    server_name your-domain.com;

    # API proxy
    location /api/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket proxy
    location /ws/ {
        proxy_pass http://api:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static assets with caching
    location /assets/ {
        alias /usr/share/nginx/html/assets/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # CORS headers for 3D assets
        add_header Access-Control-Allow-Origin "*";
        
        # Compression
        gzip on;
        gzip_types model/gltf+json model/gltf-binary image/webp;
    }

    # Frontend
    location / {
        proxy_pass http://frontend:80;
    }
}
```

### AWS Deployment with CDN
```yaml
# AWS CloudFormation template snippet
Resources:
  S3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: warband-assets
      CorsConfiguration:
        CorsRules:
          - AllowedMethods: [GET, HEAD]
            AllowedOrigins: ['*']
            AllowedHeaders: ['*']
            MaxAge: 86400

  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - DomainName: !GetAtt S3Bucket.BucketRegionalDomainName
            Id: S3Origin
            S3OriginConfig:
              OriginAccessIdentity: !Sub origin-access-identity/cloudfront/${CloudFrontOAI}
        DefaultCacheBehavior:
          TargetOriginId: S3Origin
          ViewerProtocolPolicy: redirect-to-https
          Compress: true
          CachePolicyId: 658327ea-f89d-4fab-a63d-7e88639e58f6  # Managed-CachingOptimized
```

## 8. Performance Optimization

### Three.js Optimization Implementation
```javascript
class PerformanceOptimizer {
    constructor(renderer, scene, camera) {
        this.renderer = renderer;
        this.scene = scene;
        this.camera = camera;
        this.stats = new Stats();
        document.body.appendChild(this.stats.dom);
        
        this.setupLOD();
        this.setupFrustumCulling();
        this.setupTextureOptimization();
    }

    setupLOD() {
        // Character LOD system
        this.characterLOD = new THREE.LOD();
        
        // High detail (close)
        const highDetail = this.loadModel('character_high.glb');
        this.characterLOD.addLevel(highDetail, 0);
        
        // Medium detail
        const mediumDetail = this.loadModel('character_medium.glb');
        this.characterLOD.addLevel(mediumDetail, 50);
        
        // Low detail (far)
        const lowDetail = this.loadModel('character_low.glb');
        this.characterLOD.addLevel(lowDetail, 200);
    }

    setupFrustumCulling() {
        // Manual frustum culling
        this.frustum = new THREE.Frustum();
        this.frustumMatrix = new THREE.Matrix4();
    }

    update() {
        this.stats.begin();
        
        // Update LODs
        this.scene.traverse((object) => {
            if (object.isLOD) {
                object.update(this.camera);
            }
        });
        
        // Frustum culling
        this.frustumMatrix.multiplyMatrices(
            this.camera.projectionMatrix,
            this.camera.matrixWorldInverse
        );
        this.frustum.setFromProjectionMatrix(this.frustumMatrix);
        
        this.scene.traverse((object) => {
            if (object.isMesh) {
                object.visible = this.frustum.intersectsObject(object);
            }
        });
        
        this.stats.end();
    }
}

// Material optimization
class MaterialOptimizer {
    constructor() {
        this.materialCache = new Map();
    }

    getMaterial(config) {
        const key = this.generateKey(config);
        
        if (!this.materialCache.has(key)) {
            const material = new THREE.MeshStandardMaterial(config);
            this.materialCache.set(key, material);
        }
        
        return this.materialCache.get(key);
    }

    generateKey(config) {
        return JSON.stringify({
            color: config.color?.getHex(),
            map: config.map?.uuid,
            normalMap: config.normalMap?.uuid,
            roughness: config.roughness,
            metalness: config.metalness
        });
    }
}
```

### Asset Loading Performance
```javascript
class ProgressiveAssetLoader {
    constructor() {
        this.loadQueue = [];
        this.loading = false;
        this.ktx2Loader = new KTX2Loader();
        this.ktx2Loader.setTranscoderPath('/libs/basis/');
    }

    async loadCharacterProgressive(characterData) {
        // Load low-res version first
        const lowRes = await this.loadAsset(characterData.lowRes);
        this.displayCharacter(lowRes);
        
        // Queue high-res assets
        this.queueAsset(characterData.highRes, () => {
            this.upgradeCharacter(characterData.highRes);
        });
        
        // Start processing queue
        this.processQueue();
    }

    async loadCompressedTexture(path) {
        // Load KTX2 compressed texture
        const texture = await this.ktx2Loader.loadAsync(path);
        texture.anisotropy = 4;
        return texture;
    }

    processQueue() {
        if (this.loading || this.loadQueue.length === 0) return;
        
        this.loading = true;
        const task = this.loadQueue.shift();
        
        this.loadAsset(task.asset).then(() => {
            task.callback();
            this.loading = false;
            this.processQueue();
        });
    }
}
```

## 9. Complete Implementation Example

### Full Character Editor Component
```javascript
// CharacterEditor.js
import * as THREE from 'three';
import { GUI } from 'dat.gui';
import { CharacterAPIClient } from './api/CharacterAPIClient';
import { CharacterViewer } from './viewer/CharacterViewer';
import { EquipmentManager } from './equipment/EquipmentManager';
import { MountBladeFaceCustomizer } from './customization/FaceCustomizer';

class CharacterEditor {
    constructor(container) {
        this.container = container;
        this.api = new CharacterAPIClient();
        this.viewer = new CharacterViewer(container);
        this.setupUI();
        this.loadCharacter();
    }

    async loadCharacter() {
        // Load character data from API
        const characterData = await this.api.getCharacter(
            this.profileId, 
            this.characterId
        );
        
        // Load 3D model
        await this.viewer.loadCharacterModel(
            `/assets/models/character_base.glb`
        );
        
        // Setup customization
        this.faceCustomizer = new MountBladeFaceCustomizer(
            this.viewer.characterModel
        );
        this.faceCustomizer.applyFaceCode(characterData.appearance.face_code);
        
        // Setup equipment
        this.equipmentManager = new EquipmentManager(
            this.viewer.scene,
            this.viewer.gltfLoader
        );
        
        // Load character equipment
        for (const [slot, itemId] of Object.entries(characterData.equipment)) {
            await this.equipmentManager.equipItem(slot, itemId);
        }
    }

    setupUI() {
        this.gui = new GUI();
        
        // Character stats
        const statsFolder = this.gui.addFolder('Stats');
        statsFolder.add(this.characterData.stats, 'strength', 1, 30)
            .onChange(value => this.updateStat('strength', value));
        statsFolder.add(this.characterData.stats, 'agility', 1, 30)
            .onChange(value => this.updateStat('agility', value));
        
        // Appearance
        const appearanceFolder = this.gui.addFolder('Appearance');
        appearanceFolder.add(this, 'faceCode')
            .onChange(code => this.updateFaceCode(code));
        
        // Equipment
        const equipmentFolder = this.gui.addFolder('Equipment');
        this.setupEquipmentUI(equipmentFolder);
        
        // Save/Load
        this.gui.add(this, 'saveCharacter');
        this.gui.add(this, 'exportProfile');
    }

    async saveCharacter() {
        const updatedData = {
            stats: this.characterData.stats,
            appearance: {
                face_code: this.faceCode
            },
            equipment: this.equipmentManager.getEquipment()
        };
        
        await this.api.updateCharacter(
            this.profileId,
            this.characterId,
            updatedData
        );
        
        alert('Character saved!');
    }

    async exportProfile() {
        await this.api.downloadProfile(this.profileId);
    }

    render() {
        requestAnimationFrame(() => this.render());
        
        // Update animations
        if (this.viewer.mixer) {
            this.viewer.mixer.update(this.clock.getDelta());
        }
        
        // Update performance optimizer
        if (this.optimizer) {
            this.optimizer.update();
        }
        
        this.viewer.controls.update();
        this.viewer.renderer.render(
            this.viewer.scene, 
            this.viewer.camera
        );
    }
}

// Initialize
const container = document.getElementById('character-viewer');
const editor = new CharacterEditor(container);
editor.render();
```

### Deployment Script
```bash
#!/bin/bash
# deploy.sh

# Build frontend
cd frontend
npm run build

# Build backend Docker image
cd ../backend
docker build -t warband-editor-api .

# Process assets
cd ../assets
python process_assets.py

# Upload to S3
aws s3 sync ./web_assets s3://warband-assets --delete

# Deploy to server
docker-compose up -d

# Run database migrations
docker-compose exec api python manage.py migrate

echo "Deployment complete!"
```

This comprehensive guide provides all the necessary components and code examples to build a fully functional Mount & Blade Warband web character editor, from asset extraction through deployment.