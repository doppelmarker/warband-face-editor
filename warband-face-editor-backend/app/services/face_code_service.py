from app.models.face import FaceParameters, FaceCode


class FaceCodeService:
    """Service for encoding and decoding Mount & Blade face codes."""
    
    # Bit layout for face code
    MORPH_BITS = 3  # Each morph uses 3 bits (0-7)
    INDEX_BITS = 6  # Hair/beard/age/skin use 6 bits each
    
    def decode_face_code(self, hex_code: str) -> dict:
        """
        Decode a hex face code into individual parameters.
        
        Face code bit layout:
        - Bits 0-23:   8 morphs × 3 bits each
        - Bits 24-29:  Hair index (6 bits)
        - Bits 30-35:  Beard index (6 bits)
        - Bits 36-41:  Age (6 bits)
        - Bits 42-47:  Skin tone (6 bits)
        """
        # Convert hex to integer
        if hex_code.startswith('0x'):
            hex_code = hex_code[2:]
        
        face_int = int(hex_code, 16)
        
        # Extract morphs (8 values, 3 bits each)
        morphs = []
        for i in range(8):
            shift = i * self.MORPH_BITS
            morph_value = (face_int >> shift) & 0b111
            morphs.append(morph_value)
        
        # Extract other parameters (6 bits each)
        hair_index = (face_int >> 24) & 0b111111
        beard_index = (face_int >> 30) & 0b111111
        age = (face_int >> 36) & 0b111111
        skin_tone = (face_int >> 42) & 0b111111
        
        # Map skin tone from game values to 0-4 range
        skin_map = {0: 0, 16: 1, 32: 2, 48: 3, 64: 4}
        skin_tone = skin_map.get(skin_tone, 0)
        
        return {
            'morphs': morphs,
            'hair_index': hair_index,
            'beard_index': beard_index,
            'age': age,
            'skin_tone': skin_tone
        }
    
    def encode_face_code(self, params: FaceParameters) -> str:
        """
        Encode face parameters into a hex face code.
        """
        face_int = 0
        
        # Encode morphs
        for i, morph in enumerate(params.morphs):
            shift = i * self.MORPH_BITS
            face_int |= (morph & 0b111) << shift
        
        # Encode other parameters
        face_int |= (params.hair_index & 0b111111) << 24
        face_int |= (params.beard_index & 0b111111) << 30
        face_int |= (params.age & 0b111111) << 36
        
        # Map skin tone to game values
        skin_values = [0, 16, 32, 48, 64]
        skin_value = skin_values[params.skin_tone]
        face_int |= (skin_value & 0b111111) << 42
        
        # Convert to hex string
        return f"0x{face_int:016x}"


face_code_service = FaceCodeService()