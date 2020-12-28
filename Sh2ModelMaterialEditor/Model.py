import struct
from Field import Field, FieldType
from Node import Node


class Sh2Model(Node):
    def __init__(self, f):
        super().__init__('Sh2Model')

        self.add_field('unk0', f, FieldType.u32)
        self.add_field('model_id', f, FieldType.u32)
        self.add_field('num_textures', f, FieldType.u32)
        self.add_field('texture_section_offset', f, FieldType.u32)
        self.add_field('unk2', f, FieldType.u32)
        self.add_field('offset_table_offset', f, FieldType.u32)
        self.add_field('unk3', f, FieldType.raw, 0x28)

        f.seek(self.offset + self.get('offset_table_offset').value)

        self.add_child(Sh2ModelOffsetTable(f))


class Sh2ModelOffsetTable(Node):
    def __init__(self, f):
        super().__init__('Sh2ModelOffsetTable')

        self.add_field('unk0', f, FieldType.u32)
        self.add_field('unk1', f, FieldType.u32)
        self.add_field('skeleton_points_offset', f, FieldType.u32)
        self.add_field('skeleton_point_count', f, FieldType.u32)
        self.add_field('skeleton_index_buffer_part_1_offset', f, FieldType.u32)
        self.add_field('unk2', f, FieldType.u32)
        self.add_field('skeleton_index_buffer_part_2_offset', f, FieldType.u32)
        self.add_field('unk0_offset', f, FieldType.u32)
        self.add_field('material_count', f, FieldType.u32)
        self.add_field('materials_offset', f, FieldType.u32)
        self.add_field('unk3', f, FieldType.u32)
        self.add_field('unk1_offset', f, FieldType.u32)
        self.add_field('unk4', f, FieldType.u32)
        self.add_field('unk2_offset', f, FieldType.u32)
        self.add_field('unk5', f, FieldType.u32)
        self.add_field('unk3_offset', f, FieldType.u32)
        self.add_field('unk6', f, FieldType.raw, 0x70)

        f.seek(self.offset + self.get('materials_offset').value)

        for _ in range(self.get('material_count').value):
            self.add_child(Sh2ModelMaterial(f))


class Sh2ModelMaterial(Node):
    def __init__(self, f):
        super().__init__('Sh2ModelMaterial')

        # Length of this material in bytes
        self.add_field('material_length', f, FieldType.u32)
        # Reserved, zero in all .mdl files
        self.add_field('reserved_0', f, FieldType.u32)

        # Number of elements in first u16 array, array purpose unknown
        self.add_field('unk_u16_count_0', f, FieldType.u32)
        # Offset of first array of u16s, always 128 (Relative start of this material)
        self.add_field('unk_u16_array_0_offset', f, FieldType.u32)
        # Number of elements in second u16 array
        self.add_field('unk_u16_count_1', f, FieldType.u32)
        # Offset of second array of u16s (Relative start of this material)
        self.add_field('unk_u16_array_1_offset', f, FieldType.u32)
        # Number of elements in third u16 array, always 1
        self.add_field('unk_u16_count_2', f, FieldType.u32)
        # Offset of third array of u16s (Relative start of this material)
        self.add_field('unk_u16_array_2_offset', f, FieldType.u32)
        #Offset of array of 4 u8s containing values for ADDRESSU, ADDRESSV, MAGFILTER and MINFILTER sampler states
        self.add_field('sampler_states_offset', f, FieldType.u32)

        # Determines which of the diffuse/ambient/specular color arrays are passed to vertex/pixel shaders
        # 1 = No lighting (fullbright), ignores diffuse, ambient and specular color
        # 2 = Matte, respects diffuse and ambient color, no specular highlight
        # 3 = Seems the same as 2, but always paired with non-zero specular color, unk_diffuse_float and unk_ambient_float
        # 4 = Glossy, respects diffuse, ambient and specular colors
        # Any other value = Defaults to type 2/3 behavior
        self.add_field('material_type', f, FieldType.u8)

        # Probably a boolean, binds an extra texture and configures some texture states in stage 1 and 2
        self.add_field('unk_material_subtype', f, FieldType.u8)

        # Used to identify pieces of the model so their visibility can be toggled
        # e.g. Swapping James's hand pose when using different weapons
        # 0 = Always visible
        self.add_field('pose_id', f, FieldType.u8)

        # Purpose unknown
        self.add_field('unk_byte_0x27', f, FieldType.u8)

        # 0 = CULLMODE set to D3DCULL_NONE, TEXTUREFACTOR Alpha set to 33
        # 1 = CULLMODE set to D3DCULL_CW, TEXTUREFACTOR Alpha set to 25
        self.add_field('cull_backfaces', f, FieldType.u32)

        # Purpose unknown, affects diffuse color somehow, always 0 or positive (vs float register 43[3])
        self.add_field('unk_diffuse_float', f, FieldType.f32)
        # Purpose unknown, affects ambient color somehow, always 0 or negative (vs float register 44[3])
        self.add_field('unk_ambient_float', f, FieldType.f32)

        # Controls the size of the specular highlight, larger value = smaller highlight (Distance from light source?)
        # Only used when material_type = 4
        self.add_field('specular_highlight_scale', f, FieldType.f32)

        # Reserved, zero in all .mdl files, generated value placed here at run-time
        self.add_field('reserved_1', f, FieldType.u32)
        # Reserved, zero in all .mdl files
        self.add_field('reserved_2', f, FieldType.u32)

        # Controls diffuse color (X,R,G,B)
        # Range = [0.0 - 1.0]
        self.add_field('diffuse_color_x', f, FieldType.f32)
        self.add_field('diffuse_color_r', f, FieldType.f32)
        self.add_field('diffuse_color_g', f, FieldType.f32)
        self.add_field('diffuse_color_b', f, FieldType.f32)

        # Controls ambient color (X,R,G,B)
        # Range = [0.0 - 1.0]
        self.add_field('ambient_color_x', f, FieldType.f32)
        self.add_field('ambient_color_r', f, FieldType.f32)
        self.add_field('ambient_color_g', f, FieldType.f32)
        self.add_field('ambient_color_b', f, FieldType.f32)

        # Controls color of specular highlights (X,R,G,B)
        # Range = [0.0 - 128.0]
        self.add_field('specular_color_x', f, FieldType.f32)
        self.add_field('specular_color_r', f, FieldType.f32)
        self.add_field('specular_color_g', f, FieldType.f32)
        self.add_field('specular_color_b', f, FieldType.f32)

        # Reserved, zero in all .mdl files
        self.add_field('reserved_3', f, FieldType.u32)
        # Index into some array of u16s (An index buffer?)
        self.add_field('unk_index', f, FieldType.u32)
        # Passed to DrawIndexedPrimitive -2 (A buffer with length this*2 is malloc'd at runtime)
        self.add_field('prim_count', f, FieldType.u32)
        # Reserved, zero in all .mdl files
        self.add_field('reserved_4', f, FieldType.u32)

        # First array of u16s, purpose unknown
        f.seek(self.offset + self.get('unk_u16_array_0_offset').value)
        self.add_child(Sh2UnkU16Array0(f, self.get('unk_u16_count_0').value))

        # Second array of u16s, purpose unknown
        f.seek(self.offset + self.get('unk_u16_array_1_offset').value)
        self.add_child(Sh2UnkU16Array1(f, self.get('unk_u16_count_1').value))

        # Third array of u16s, always length 1 in retail .mdls, purpose unknown
        f.seek(self.offset + self.get('unk_u16_array_2_offset').value)
        self.add_child(Sh2UnkU16Array2(f, self.get('unk_u16_count_2').value))

        f.seek(self.offset + self.get('sampler_states_offset').value)
        self.add_child(Sh2SamplerStateArray(f))

        f.seek(self.offset + self.get('material_length').value)


class Sh2UnkU16Array0(Node):
    def __init__(self, f, count):
        super().__init__('Sh2UnkU16Array0')

        for i in range(count):
            self.add_field(f'unk_u16_array_0_{i}', f, FieldType.u16)

        # Pad to 16 byte bounds if necessary
        #pad_bytes = 16 - ((count * 2) % 16)
        #if pad_bytes > 0:
        #    self.add_field('padding', f, FieldType.raw, pad_bytes)


class Sh2UnkU16Array1(Node):
    def __init__(self, f, count):
        super().__init__('Sh2UnkU16Array1')

        for i in range(count):
            self.add_field(f'unk_u16_array_1_{i}', f, FieldType.u16)

        # Pad to 16 byte bounds if necessary
        #pad_bytes = 16 - ((count * 2) % 16)
        #if pad_bytes > 0:
        #    self.add_field('padding', f, FieldType.raw, pad_bytes)


class Sh2UnkU16Array2(Node):
    def __init__(self, f, count):
        super().__init__('Sh2UnkU16Array2')

        for i in range(count):
            self.add_field(f'unk_u16_array_2_{i}', f, FieldType.u16)

        # Pad to 16 byte bounds if necessary
        #pad_bytes = 16 - ((count * 2) % 16)
        #if pad_bytes > 0:
        #    self.add_field('padding', f, FieldType.raw, pad_bytes)


class Sh2SamplerStateArray(Node):
    def __init__(self, f):
        super().__init__('Sh2SamplerStateArray')

        # Texture-address mode for the u coordinate
        self.add_field('addressu', f, FieldType.u8)
        # Texture-address mode for the v coordinate
        self.add_field('addressv', f, FieldType.u8)

        # 1 = D3DTADDRESS_WRAP
        # 2 = D3DTADDRESS_MIRROR
        # 3 = D3DTADDRESS_CLAMP
        # 4 = D3DTADDRESS_BORDER
        # 5 = D3DTADDRESS_MIRRORONCE

        # Texture filtering mode used for magnification
        self.add_field('magfilter', f, FieldType.u8)
        # Texture filtering mode used for minification
        self.add_field('minfilter', f, FieldType.u8)

        # 0 = D3DTEXF_NONE
        # 1 = D3DTEXF_POINT
        # 2 = D3DTEXF_LINEAR
        # 3 = D3DTEXF_ANISOTROPIC
        # 4 = D3DTEXF_PYRAMIDALQUAD
        # 5 = D3DTEXF_GAUSSIANQUAD
        # 6 = D3DTEXF_CONVOLUTIONMONO
