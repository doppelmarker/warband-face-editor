# Mount & Blade Warband Face Editor: Step-by-Step Implementation Plan

## Code Style
- Use modern Python type hints: `dict`, `list`, `tuple` instead of `Dict`, `List`, `Tuple`
- Use `str | None` instead of `Optional[str]`
- WebSocket: Each user has individual connection for their character editing session (no broadcasting)

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT (Browser)                               │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────────────┐  │
│  │   UI Controls   │  │  3D Viewport     │  │   Face Code Display   │  │
│  │  ┌───────────┐  │  │  ┌────────────┐  │  │  ┌─────────────────┐  │  │
│  │  │ Sliders x8│  │  │  │   Three.js │  │  │  │ Hex: 0x1234... │  │  │
│  │  └───────────┘  │  │  │   Scene    │  │  │  └─────────────────┘  │  │
│  │  ┌───────────┐  │  │  └────────────┘  │  │  ┌─────────────────┐  │  │
│  │  │  Presets  │  │  └──────────────────┘  │  │ Import/Export   │  │  │
│  │  └───────────┘  │                        │  └─────────────────┘  │  │
│  └─────────────────┘                        └───────────────────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                      Core Components                              │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │  │
│  │  │ FaceManager  │  │ MorphEngine  │  │  FaceCodeConverter   │  │  │
│  │  └──────────────┘  └──────────────┘  └───────────────────────┘  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐  │  │
│  │  │AssetLoader   │  │ Performance  │  │   ProfileManager     │  │  │
│  │  └──────────────┘  │   Monitor    │  └───────────────────────┘  │  │
│  │                    └──────────────┘                              │  │
│  └─────────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────┤
│                           SERVER (Python/FastAPI)                        │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │  Profile Parser  │  │   Face Code      │  │   Static Asset    │     │
│  │  (Your Script)   │  │   Validator      │  │     Server        │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘
```

[Version: 1.0]
{F: Mount&Blade Warband web face editor project. User has reverse-engineered profiles.dat, created Python manipulation script. Need 3D visualization matching in-game face morphing system.}
{R: Initial: Full character editor with equipment→Corrected: Face-only editor with sliders. Approach: Extract BRF assets→Convert to web formats→Three.js morph targets→Real-time preview.}
{G: User clarified: No armor/equipment, just facial features. Visual feedback essential. WSE2 not suitable. Focus on morph targets matching game's 8 parameters. Continuous slider updates preferred.}
{T: Extract meshes_face_gen.brf, implement 8 morph sliders (3-bit values), decode/encode face codes, web deployment with Python backend + React/Three.js frontend.}

## Phase 1: Asset Preparation Pipeline (Week 1)

### Step 1.1: Extract Face Assets
**Components:**
- OpenBRF tool
- Python extraction script

**Actions:**
```python
# extract_face_assets.py
import os
from pathlib import Path

REQUIRED_BRF_FILES = [
    'meshes_face_gen.brf',      # Base head meshes
    'materials_face_gen.brf',    # Face materials
    'char_hair_mesh.brf',        # Hair meshes
    'char_beard_mesh.brf'        # Beard meshes
]

def extract_assets(warband_path, output_path):
    # Extract base mesh + 8 morph targets
    # Export as OBJ files maintaining vertex order
    pass
```

**Output:** 
- `base_head.obj`
- `morph_chin_size.obj`
- `morph_mouth_nose_distance.obj`
- ... (6 more morph targets)

### Step 1.2: Convert to Web Format
**Components:**
- Blender Python API
- obj2gltf converter

**Pipeline:**
```
OBJ → Blender → Merge Morphs → Export GLTF → Compress with Draco
```

**Script:**
```python
# convert_to_gltf.py
import bpy

def create_morph_targets():
    base = bpy.data.objects['base_head']
    
    # Add shape keys for each morph
    for morph_file in morph_files:
        # Import morph OBJ
        # Add as shape key
        # Set influence range 0-1
```

**Output:** `warband_head.glb` (with embedded morphs)

### Step 1.3: Optimize Textures
**Components:**
- Image processing tools
- Texture atlas generator

**Actions:**
- Convert DDS → PNG/WebP
- Create texture atlas for skin tones
- Generate mipmaps

## Phase 2: Backend Setup (Week 2)

### Step 2.1: Core API Structure
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Endpoints
POST   /api/profiles/upload      # Upload profiles.dat
GET    /api/profiles/{id}/characters
PUT    /api/characters/{id}/face
GET    /api/assets/manifest      # Asset URLs
```

### Step 2.2: Face Code Service
```python
# services/face_code_service.py
class FaceCodeService:
    def decode_face_code(self, hex_code: str) -> dict:
        """
        Returns: {
            'morphs': [7, 3, 5, 2, 6, 1, 4, 3],  # 0-7 values
            'hair_index': 12,
            'beard_index': 0,
            'age': 35,
            'skin_tone': 2
        }
        """
    
    def encode_face_code(self, params: dict) -> str:
        """Generate hex face code from parameters"""
```

### Step 2.3: WebSocket Support
```python
# websocket_handler.py
@app.websocket("/ws/face-updates")
async def face_updates(websocket: WebSocket):
    # Real-time face parameter updates
    # Broadcast to multiple viewers
```

## Phase 3: Frontend Core Components (Week 3)

### Step 3.1: Asset Loading System
```javascript
// AssetLoader.js
class AssetLoader {
    constructor() {
        this.cache = new Map();
        this.loadingQueue = [];
    }
    
    async loadFaceModel() {
        // 1. Load low-poly preview first
        const preview = await this.loadGLTF('head_preview.glb');
        this.onPreviewLoaded(preview);
        
        // 2. Load full quality in background
        const full = await this.loadGLTF('head_full.glb');
        this.upgradeToFull(full);
    }
    
    async loadTextureSet(skinTone) {
        // Lazy load texture variants
    }
}
```

### Step 3.2: Morph Engine
```javascript
// MorphEngine.js
class MorphEngine {
    constructor(mesh) {
        this.mesh = mesh;
        this.morphTargets = [
            'chin_size',
            'mouth_nose_distance',
            'nose_height',
            'face_width',
            'temple_width',
            'eye_to_eye_dist',
            'mouth_width',
            'cheeks'
        ];
        this.pendingUpdates = new Map();
    }
    
    updateMorph(index, value) {
        // Immediate visual update
        this.mesh.morphTargetInfluences[index] = value / 7;
        
        // Debounced face code generation
        this.scheduleFaceCodeUpdate();
    }
    
    scheduleFaceCodeUpdate() {
        clearTimeout(this.updateTimer);
        this.updateTimer = setTimeout(() => {
            this.generateFaceCode();
        }, 100);
    }
}
```

### Step 3.3: UI Controls
```javascript
// UIControls.js
class FaceEditorUI {
    constructor(morphEngine) {
        this.morphEngine = morphEngine;
        this.createSliders();
    }
    
    createSliders() {
        const sliderConfig = [
            { name: 'Chin Size', min: 0, max: 7, default: 3 },
            { name: 'Mouth-Nose Distance', min: 0, max: 7, default: 3 },
            // ... 6 more
        ];
        
        sliderConfig.forEach((config, index) => {
            const slider = this.createSlider(config);
            slider.addEventListener('input', (e) => {
                this.morphEngine.updateMorph(index, e.target.value);
            });
        });
    }
}
```

## Phase 4: Integration & Polish (Week 4)

### Step 4.1: Performance Monitoring
```javascript
// PerformanceMonitor.js
class PerformanceMonitor {
    constructor() {
        this.stats = new Stats();
        this.frameTimings = [];
    }
    
    checkPerformance() {
        const fps = this.stats.getFPS();
        if (fps < 30 && !this.degraded) {
            this.enableDegradedMode();
        }
    }
    
    enableDegradedMode() {
        // Switch to on-release updates
        // Reduce texture quality
        // Disable shadows
    }
}
```

### Step 4.2: Import/Export System
```javascript
// ProfileManager.js
class ProfileManager {
    async importProfile(file) {
        const formData = new FormData();
        formData.append('profile', file);
        
        const response = await fetch('/api/profiles/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        this.loadCharacters(data.characters);
    }
    
    exportFaceCode() {
        const code = this.morphEngine.getCurrentFaceCode();
        navigator.clipboard.writeText(code);
    }
}
```

### Step 4.3: Preset System
```javascript
// PresetManager.js
const FACE_PRESETS = {
    'young_warrior': {
        morphs: [3, 2, 4, 5, 3, 4, 3, 2],
        age: 20
    },
    'old_noble': {
        morphs: [5, 6, 3, 2, 4, 3, 5, 6],
        age: 60
    }
};
```

## Data Flow Sequence

```
User Moves Slider
       ↓
Update Morph Value (Immediate)
       ↓
GPU Updates Mesh (Per Frame)
       ↓
Debounce Timer Starts
       ↓
[100ms pause]
       ↓
Generate Face Code
       ↓
Update UI Display
       ↓
[Optional] Send to Server
```

## Critical Implementation Details

### 1. Morph Target Vertex Order
- **CRITICAL**: Vertex order must match exactly between base and morphs
- Use same export settings in OpenBRF for all meshes
- Validate vertex count matches

### 2. Face Code Bit Layout
```
Bits 0-23:   8 morphs × 3 bits each
Bits 24-29:  Hair index (6 bits)
Bits 30-35:  Beard index (6 bits)
Bits 36-41:  Age (6 bits)
Bits 42-47:  Skin tone (6 bits)
Bits 48-63:  Reserved/Additional data
```

### 3. Texture Switching
```javascript
// Efficient texture swapping
const textureCache = new Map();

function switchSkinTone(toneIndex) {
    const key = `skin_${toneIndex}`;
    
    if (!textureCache.has(key)) {
        textureCache.set(key, loadTexture(`skin_${toneIndex}.webp`));
    }
    
    material.map = textureCache.get(key);
    material.needsUpdate = true;
}
```

### 4. Memory Management
```javascript
// Dispose unused resources
function cleanup() {
    // Dispose old textures
    oldTexture.dispose();
    
    // Remove from GPU
    renderer.renderLists.dispose();
}
```

## Deployment Architecture

```
CDN (CloudFront)
    ├── Static Assets
    │   ├── head_model.glb (2MB)
    │   ├── textures/ (10MB total)
    │   └── app.js (200KB)
    │
API Server (EC2/Lambda)
    ├── Profile Parser
    ├── Face Code Validator
    └── Character Storage
    │
Database (DynamoDB/PostgreSQL)
    └── User Profiles
```

## Testing Checklist

- [ ] Face morphs match in-game appearance
- [ ] Face codes are compatible with game
- [ ] 60fps on desktop, 30fps on mobile
- [ ] All 8 sliders function correctly
- [ ] Texture switching is seamless
- [ ] Import/export preserves data
- [ ] Memory usage stays under 100MB
- [ ] Works on Chrome, Firefox, Safari
- [ ] Touch controls work on mobile
- [ ] Graceful degradation on slow devices