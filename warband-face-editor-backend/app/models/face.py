from pydantic import BaseModel, Field, validator


class FaceParameters(BaseModel):
    morphs: list[int] = Field(..., min_length=8, max_length=8)
    hair_index: int = Field(ge=0, le=63)
    beard_index: int = Field(ge=0, le=63)
    age: int = Field(ge=0, le=63)
    skin_tone: int = Field(ge=0, le=4)
    
    @validator('morphs')
    def validate_morph_values(cls, v):
        for morph in v:
            if not 0 <= morph <= 7:
                raise ValueError(f"Morph value must be between 0 and 7, got {morph}")
        return v
    
    @validator('skin_tone')
    def validate_skin_tone(cls, v):
        valid_tones = [0, 1, 2, 3, 4]  # White, Light, Tan, Dark, Black
        if v not in valid_tones:
            raise ValueError(f"Invalid skin tone: {v}")
        return v


class FaceCode(BaseModel):
    hex_code: str = Field(..., regex=r'^0x[0-9a-fA-F]+$')
    
    @property
    def as_int(self) -> int:
        return int(self.hex_code, 16)


class DecodedFace(BaseModel):
    parameters: FaceParameters
    face_code: str
    
    
class Character(BaseModel):
    name: str
    face_code: str
    sex: int = Field(ge=0, le=1)  # 0=Male, 1=Female
    skin: int