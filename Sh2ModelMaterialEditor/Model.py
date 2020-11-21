import struct
from Field import Field, FieldType
from Node import Node


class Sh2Model(Node):
    def __init__(self, f):
        super().__init__('Sh2Model')

        self.add_field('unk0', f, FieldType.u32)
        self.add_field('unk1', f, FieldType.u32)
        self.add_field('num_textures', f, FieldType.u32)
        self.add_field('ptr_texture_section', f, FieldType.u32)
        self.add_field('unk2', f, FieldType.u32)
        self.add_field('ptr_ptr_table', f, FieldType.u32)
        self.add_field('unk3', f, FieldType.raw, 0x28)

        f.seek(self.offset + self.at(5).value)

        self.add_child(Sh2PtrTable(f))


class Sh2PtrTable(Node):
    def __init__(self, f):
        super().__init__('Sh2PtrTable')

        self.add_field('unk0', f, FieldType.u32)
        self.add_field('unk1', f, FieldType.u32)
        self.add_field('ptr_skeleton_points', f, FieldType.u32)
        self.add_field('skeleton_point_count', f, FieldType.u32)
        self.add_field('ptr_skeleton_index_buffer_part_1', f, FieldType.u32)
        self.add_field('unk2', f, FieldType.u32)
        self.add_field('ptr_skeleton_index_buffer_part_2', f, FieldType.u32)
        self.add_field('ptr_unk0', f, FieldType.u32)
        self.add_field('material_count', f, FieldType.u32)
        self.add_field('ptr_material_table', f, FieldType.u32)
        self.add_field('unk3', f, FieldType.u32)
        self.add_field('ptr_unk1', f, FieldType.u32)
        self.add_field('unk4', f, FieldType.u32)
        self.add_field('ptr_unk2', f, FieldType.u32)
        self.add_field('unk5', f, FieldType.u32)
        self.add_field('ptr_unk3', f, FieldType.u32)
        self.add_field('unk6', f, FieldType.raw, 0x70)

        f.seek(self.offset + self.at(9).value)

        for _i in range(self.at(8).value):
            self.add_child(Sh2ModelMaterial(f))


class Sh2ModelMaterial(Node):
    def __init__(self, f):
        super().__init__('Sh2ModelMaterial')

        self.add_field('ptr_next', f, FieldType.u32)
        self.add_field('reserved_0', f, FieldType.u32)

        self.add_field('unk_u16_count_0', f, FieldType.u32)
        self.add_field('ptr_unk_u16_array_0', f, FieldType.u32)
        self.add_field('unk_u16_count_1', f, FieldType.u32)
        self.add_field('ptr_unk_u16_array_1', f, FieldType.u32)
        self.add_field('unk_u16_count_2', f, FieldType.u32)
        self.add_field('ptr_unk_u16_array_2', f, FieldType.u32)
        self.add_field('ptr_sampler_state_array', f, FieldType.u32)

        self.add_field('material_type', f, FieldType.u8)
        self.add_field('unk_material_subtype', f, FieldType.u8)
        self.add_field('pose_id', f, FieldType.u16)

        self.add_field('cull_backfaces', f, FieldType.u32)

        self.add_field('unk_diffuse_float', f, FieldType.f32)
        self.add_field('unk_ambient_float', f, FieldType.f32)
        self.add_field('specular_highlight_scale', f, FieldType.f32)

        self.add_field('reserved_1', f, FieldType.u32)
        self.add_field('reserved_2', f, FieldType.u32)

        self.add_field('diffuse_color_x', f, FieldType.f32)
        self.add_field('diffuse_color_r', f, FieldType.f32)
        self.add_field('diffuse_color_g', f, FieldType.f32)
        self.add_field('diffuse_color_b', f, FieldType.f32)

        self.add_field('ambient_color_x', f, FieldType.f32)
        self.add_field('ambient_color_r', f, FieldType.f32)
        self.add_field('ambient_color_g', f, FieldType.f32)
        self.add_field('ambient_color_b', f, FieldType.f32)

        self.add_field('specular_color_x', f, FieldType.f32)
        self.add_field('specular_color_r', f, FieldType.f32)
        self.add_field('specular_color_g', f, FieldType.f32)
        self.add_field('specular_color_b', f, FieldType.f32)

        self.add_field('reserved_3', f, FieldType.u32)
        self.add_field('unk_index', f, FieldType.u32)
        self.add_field('prim_count', f, FieldType.u32)
        self.add_field('reserved_4', f, FieldType.u32)

        f.seek(self.offset + self.at(3).value)
        self.add_child(Sh2UnkU16Array0(f, self.get('unk_u16_count_0').value))

        f.seek(self.offset + self.at(5).value)
        self.add_child(Sh2UnkU16Array1(f, self.get('unk_u16_count_1').value))

        f.seek(self.offset + self.at(7).value)
        self.add_child(Sh2UnkU16Array2(f, self.get('unk_u16_count_2').value))

        f.seek(self.offset + self.at(8).value)
        self.add_child(Sh2SamplerStateArray(f))

        f.seek(self.offset + self.at(0).value)


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

        self.add_field('addressu', f, FieldType.u8)
        self.add_field('addressv', f, FieldType.u8)
        self.add_field('magfilter', f, FieldType.u8)
        self.add_field('minfilter', f, FieldType.u8)
