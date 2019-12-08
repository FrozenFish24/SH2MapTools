import struct

DEBUG = False

# TODO: look into less verbose ways to print objects
# TODO: work out how to gracefully skip corrupt sections

class OffsetValuePair:
    def __init__(self, offset, value):
        self.offset = offset
        self.value = value

    def to_string(self, value_as_hex=False):
        if value_as_hex:
            return '(0x{:X}, 0x{:X})'.format(self.offset, self.value)
        else:
            return '(0x{:X}, {})'.format(self.offset, self.value)

class Sh2Material:
    def __init__(self, f):
        self.texture = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.unk0 = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.specularity = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.unk1 = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])

        if DEBUG:
            self.pretty_print()

    def get_offset(self):
        return self.texture.offset

    def pretty_print(self):
        try:
            print('Sh2Material() =\n{')
            print(f'\ttexture = {self.texture.to_string(True)}')
            print(f'\tunk0 = {self.unk0.to_string(True)}')
            print(f'\tspecularity = {self.specularity.to_string(True)}')
            print(f'\tunk1 = {self.unk1.to_string(True)}')
            print('}')
        except:
            print('{} broken'.format(self.__class__))

    def recursive_print(self):
        self.pretty_print()

class Sh2SubPrimInfo:
    def __init__(self, f):
        self.num_prims = OffsetValuePair(f.tell(), struct.unpack('<H', f.read(2))[0])
        self.unk = OffsetValuePair(f.tell(), struct.unpack('<B', f.read(1))[0])
        self.prim_len = OffsetValuePair(f.tell(), struct.unpack('<B', f.read(1))[0])
        self.vert_start = OffsetValuePair(f.tell(), struct.unpack('<H', f.read(2))[0])
        self.vert_end = OffsetValuePair(f.tell(), struct.unpack('<H', f.read(2))[0])

        if DEBUG:
            self.pretty_print()

    def get_offset(self):
        return self.num_prims.offset

    def pretty_print(self):
        try:
            print('Sh2SubPrimInfo() =\n{')
            print(f'\tnum_prims = {self.num_prims.to_string()}')
            print(f'\tunk = {self.unk.to_string()}')
            print(f'\tprim_len = {self.prim_len.to_string(True)}')
            print(f'\tvert_start = {self.vert_start.to_string()}')
            print(f'\tvert_end = {self.vert_end.to_string()}')
            print('}')
        except:
            print('{} broken'.format(self.__class__))

    def recursive_print(self):
        self.pretty_print()

class Sh2PrimitiveInfo:
    def __init__(self, f):
        self.material_index = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.vertex_buffer_index = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.num_sub_prims = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])

        if DEBUG:
            self.pretty_print()

        self.sub_prims = []
        for _i in range(0, self.num_sub_prims.value):
            self.sub_prims.append(OffsetValuePair(0, Sh2SubPrimInfo(f)))

    def get_offset(self):
        return self.material_index.offset

    def pretty_print(self):
        try:
            print('Sh2PrimitiveInfo() =\n{')
            print(f'\tmaterial_index = {self.material_index.to_string()}')
            print(f'\tvertex_buffer_index = {self.vertex_buffer_index.to_string()}')
            print(f'\tnum_sub_prims = {self.num_sub_prims.to_string()}')
            print(f'\tsub_prims = {self.sub_prims}')
            print('}')
        except:
            print('{} broken'.format(self.__class__))

    def recursive_print(self):
        self.pretty_print()
        for sp in self.sub_prims:
            sp.value.recursive_print()

class Sh2PrimitiveList:
    def __init__(self, f):
        self.len_primitive_list = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.ofs_index_buffer = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.len_index_buffer = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.len_unk = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.num_prims = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])

        if DEBUG:
            self.pretty_print()

        self.prim_info = []
        for _i in range(0, self.num_prims.value):
            self.prim_info.append(OffsetValuePair(0, Sh2PrimitiveInfo(f)))

    def get_offset(self):
        return self.len_primitive_list.offset

    def pretty_print(self):
        try:
            print('Sh2PrimitiveList() =\n{')
            print(f'\tlen_primitive_list = {self.len_primitive_list.to_string(True)}')
            print(f'\tofs_index_buffer = {self.ofs_index_buffer.to_string(True)}')
            print(f'\tlen_index_buffer = {self.len_index_buffer.to_string(True)}')
            print(f'\tlen_unk = {self.len_unk.to_string(True)}')
            print(f'\tnum_prims = {self.num_prims.to_string()}')
            print(f'\tprim_info = {self.prim_info}')
            print('}')
        except:
            print('{} broken'.format(self.__class__))

    def recursive_print(self):
        self.pretty_print()
        for pi in self.prim_info:
            pi.value.recursive_print()

class Sh2VertexBufferInfo:
    def __init__(self):
        self.ofs_start = OffsetValuePair(0, 0)
        self.stride = OffsetValuePair(0, 0)
        self.ofs_end = OffsetValuePair(0, 0)

    def get_offset(self):
        return self.ofs_start.offset

class Sh2VertexBuffer:
    def __init__(self):
        self.len_all_vertex_buffers = OffsetValuePair(0, 0)
        self.num_vertex_buffers = OffsetValuePair(0, 0)
        self.vertex_buffer_infos = OffsetValuePair(0, Sh2VertexBufferInfo())
        self.vertex_data = OffsetValuePair(0, [])

    def get_offset(self):
        return self.len_all_vertex_buffers.offset

class Sh2BoundingVolume:
    def __init__(self):
        self.len_bounding_volume = OffsetValuePair(0, 0)
        self.data = OffsetValuePair(0, 0)

    def get_offset(self):
        return self.len_bounding_volume.offset

class Sh2Object:
    def __init__(self, f):
        self.unk0 = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.unk1 = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.num_bounding_volumes = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])

        # TODO: Actually parse bounding vols
        self.bounding_volumes = OffsetValuePair(0, 0)
        f.read(self.num_bounding_volumes.value * 4)

        if DEBUG:
            self.pretty_print()

        self.prim_list = OffsetValuePair(f.tell(), Sh2PrimitiveList(f))

        # TODO: Keep parsing
        self.vertex_buffers = OffsetValuePair(0, 0)
        self.index_buffer = OffsetValuePair(0, 0)

    def get_offset(self):
        return self.unk0.offset

    def pretty_print(self):
        try:
            print('Sh2Object() =\n{')
            print(f'\tunk0 = {self.unk0.to_string()}')
            print(f'\tunk1 = {self.unk1.to_string()}')
            print(f'\tnum_bounding_volumes = {self.num_bounding_volumes.to_string()}')
            print(f'\tbounding_volumes = {self.bounding_volumes.to_string()}')
            print(f'\tprim_list = {self.prim_list.to_string()}')
            print(f'\tvertex_buffers = {self.vertex_buffers.to_string()}')
            print(f'\tindex_buffer = {self.index_buffer.to_string()}')
            print('}')
        except:
            print('{} broken'.format(self.__class__))

    def recursive_print(self):
        self.pretty_print()
        self.prim_list.value.recursive_print()

class Sh2ObjectGroup:
    def __init__(self, f):
        self.unk0 = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.len_object_group = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.unk1 = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.len_unk = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.object = None

        if DEBUG:
            self.pretty_print()

        # Hack: Skip broken ObjectGroup in ps85.map
        if(self.get_offset() == 0x1D49C0):
            f.seek(self.get_offset() + self.len_object_group.value)
            return

        self.object = OffsetValuePair(f.tell(), Sh2Object(f))

        f.seek(self.get_offset() + self.len_object_group.value) # Can hopefully go once parsing works

    def get_offset(self):
        return self.unk0.offset

    def pretty_print(self):
        try:
            print('Sh2ObjectGroup() =\n{')
            print(f'\tunk0 = {self.unk0.to_string()}')
            print(f'\tlen_object_group = {self.len_object_group.to_string(True)}')
            print(f'\tunk1 = {self.unk1.to_string()}')
            print(f'\tlen_unk = {self.len_unk.to_string(True)}')
            print(f'\tobject = {self.object.to_string()}')
            print('}')
        except:
            print('{} broken'.format(self.__class__))

    def recursive_print(self):
        self.pretty_print()
        if self.object != None: # Hack
            self.object.value.recursive_print()

class Sh2GeometrySubSection:
    def __init__(self, f):
        self.time_stamp = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.object_group_count = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.len_geometry_sub_section = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.num_materials = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])

        if DEBUG:
            self.pretty_print()

        self.object_groups = []
        for _i in range(0, self.object_group_count.value):
            self.object_groups.append(OffsetValuePair(0, Sh2ObjectGroup(f)))

        self.materials = []
        for _i in range(0, self.num_materials.value):
            self.materials.append(OffsetValuePair(0, Sh2Material(f)))

    def get_offset(self):
        return self.time_stamp.offset

    def pretty_print(self):
        try:
            print('Sh2GeometrySubSection() =\n{')
            print(f'\ttime_stamp = {self.time_stamp.to_string()}')
            print(f'\tobject_group_count = {self.object_group_count.to_string()}')
            print(f'\tlen_geometry_sub_section = {self.len_geometry_sub_section.to_string(True)}')
            print(f'\tnum_materials = {self.num_materials.to_string()}')
            print(f'\tobject_groups = {self.object_groups}')
            print(f'\tmaterials = {self.materials}')
            print('}')
        except:
            print('{} broken'.format(self.__class__))

    def recursive_print(self):
        self.pretty_print()
        for og in self.object_groups:
            og.value.recursive_print()
        for mat in self.materials:
            mat.value.recursive_print()

class Sh2GeometrySection:
    def __init__(self, f):
        self.section_index = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.len_data = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.unk0 = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.unk1 = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])

        if DEBUG:
            self.pretty_print()

        self.geometry_sub_section = OffsetValuePair(f.tell(), Sh2GeometrySubSection(f))

    def get_offset(self):
        return self.section_index.offset

    def pretty_print(self):
        try:
            print('Sh2GeometrySection() =\n{')
            print(f'\tsection_index = {self.section_index.to_string()}')
            print(f'\tlen_data = {self.len_data.to_string(True)}')
            print(f'\tunk0 = {self.unk0.to_string()}')
            print(f'\tunk1 = {self.unk1.to_string()}')
            print(f'\tgeometry_sub_section = {self.geometry_sub_section.to_string()}')
            print('}')
        except:
            print('{} broken'.format(self.__class__))

    def recursive_print(self):
        self.pretty_print()
        self.geometry_sub_section.value.recursive_print()

class Sh2TextureSection:
    def __init__(self, f):
        self.section_index = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.len_data = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.unk0 = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.unk1 = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])

        # TODO: Actually parse this
        self.data = OffsetValuePair(f.tell(), 0)
        f.seek(f.tell() + self.len_data.value)

    def get_offset(self):
        return self.section_index.offset

    def pretty_print(self):
        try:
            print('Sh2TextureSection() =\n{')
            print(f'\tsection_index = {self.section_index.to_string()}')
            print(f'\tlen_data = {self.len_data.to_string(True)}')
            print(f'\tunk0 = {self.unk0.to_string()}')
            print(f'\tunk1 = {self.unk1.to_string()}')
            print(f'\tdata = {self.data.to_string()}')
            print('}')
        except:
            print('{} broken'.format(self.__class__))

    def recursive_print(self):
        self.pretty_print()

class Sh2Map:
    def __init__(self, f):
        self.time_stamp = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.len_map = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.num_sections = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        self.unk = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])

        self.texture_section = OffsetValuePair(f.tell(), Sh2TextureSection(f))

        self.geometry_section = OffsetValuePair(f.tell(), Sh2GeometrySection(f))

    def get_offset(self):
        return self.time_stamp.offset

    def pretty_print(self):
        try:
            print('Sh2Map() =\n{')
            print(f'\ttime_stamp = {self.time_stamp.to_string()}')
            print(f'\tlen_map = {self.len_map.to_string(True)}')
            print(f'\tnum_sections = {self.num_sections.to_string()}')
            print(f'\tunk = {self.unk.to_string()}')
            print(f'\ttexture_section = {self.texture_section.to_string()}')
            print(f'\tgeometry_section = {self.geometry_section.to_string()}')
            print('}')
        except:
            print('{} broken'.format(self.__class__))

    def recursive_print(self):
        self.pretty_print()
        self.texture_section.value.recursive_print()
        self.geometry_section.value.recursive_print()
