import struct

class OffsetValuePair:
    def __init__(self, offset, value):
        self.offset = offset
        self.value = value

class Sh2SubPrimInfo:
    def __init__(self):
        self.num_prims = OffsetValuePair(0, 0)
        self.unk = OffsetValuePair(0, 0)
        self.prim_size = OffsetValuePair(0, 0)
        self.vert_start = OffsetValuePair(0, 0)
        self.vert_end = OffsetValuePair(0, 0)

    def get_offset(self):
        return self.num_prims.offset

class Sh2PrimitiveInfo:
    def __init__(self):
        self.material_index = OffsetValuePair(0, 0)
        self.vertex_buffer_index = OffsetValuePair(0, 0)
        self.num_sub_prims = OffsetValuePair(0, 0)
        self.sub_prims = OffsetValuePair(0, Sh2SubPrimInfo())

    def get_offset(self):
        return self.material_index.offset

class Sh2PrimitiveList:
    def __init__(self):
        self.len_primitive_list = OffsetValuePair(0, 0)
        self.ofs_index_buffer = OffsetValuePair(0, 0)
        self.len_index_buffer = OffsetValuePair(0, 0)
        self.len_unk = OffsetValuePair(0, 0)
        self.num_prims = OffsetValuePair(0, 0)
        self.prim_info = OffsetValuePair(0, Sh2PrimitiveInfo())

    def get_offset(self):
        return self.len_primitive_list.offset

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
    def __init__(self):
        self.len_object = OffsetValuePair(0, 0)
        self.num_bounding_volumes = OffsetValuePair(0, 0)
        self.bounding_volumes = OffsetValuePair(0, Sh2BoundingVolume())
        self.prim_list = OffsetValuePair(0, Sh2PrimitiveList())
        self.vertex_buffers = OffsetValuePair(0, Sh2VertexBuffer())
        self.index_buffer = OffsetValuePair(0, [])

    def get_offset(self):
        return self.len_object.offset

class Sh2ObjectGroup:
    def __init__(self):
        self.unk = OffsetValuePair(0, 0)
        self.len_object_group = OffsetValuePair(0, 0)
        self.prim_count = OffsetValuePair(0, 0)
        self.len_unk = OffsetValuePair(0, 0)
        self.object = OffsetValuePair(0, Sh2Object())

    def get_offset(self):
        return self.unk.offset

    def pretty_print(self):
        print('Sh2ObjectGroup() =\n{')
        print('\tunk = (0x{:X}, {})'.format(self.unk.offset, self.unk.value))
        print('\tlen_object_group = (0x{:X}, 0x{:X})'.format(self.len_object_group.offset, self.len_object_group.value))
        print('\tprim_count = (0x{:X}, {})'.format(self.prim_count.offset, self.prim_count.value))
        print('\tlen_unk = (0x{:X}, 0x{:X})'.format(self.len_unk.offset, self.len_unk.value))
        print('\tobject = (0x{:X}, {})'.format(self.object.offset, self.object.value))
        print('}')

class Sh2GeometrySubSection:
    def __init__(self):
        self.time_stamp = OffsetValuePair(0, 0)
        self.object_group_count = OffsetValuePair(0, 0)
        self.len_geometry_sub_section = OffsetValuePair(0, 0)
        self.unk0 = OffsetValuePair(0, 0)
        self.object_group = OffsetValuePair(0, Sh2ObjectGroup())

    def get_offset(self):
        return self.time_stamp.offset

    def pretty_print(self):
        print('Sh2GeometrySubSection() =\n{')
        print('\ttime_stamp = (0x{:X}, {})'.format(self.time_stamp.offset, self.time_stamp.value))
        print('\tobject_group_count = (0x{:X}, {})'.format(self.object_group_count.offset, self.object_group_count.value))
        print('\tlen_geometry_sub_section = (0x{:X}, 0x{:X})'.format(self.len_geometry_sub_section.offset, self.len_geometry_sub_section.value))
        print('\tunk0 = (0x{:X}, {})'.format(self.unk0.offset, self.unk0.value))
        print('\tobject_group = (0x{:X}, {})'.format(self.object_group.offset, self.object_group.value))
        print('}')

class Sh2GeometrySection:
    def __init__(self):
        self.section_index = OffsetValuePair(0, 0)
        self.len_data = OffsetValuePair(0, 0)
        self.unk0 = OffsetValuePair(0, 0)
        self.geometry_sub_section = OffsetValuePair(0, Sh2GeometrySubSection())
        self.materials = OffsetValuePair(0, 0)

    def get_offset(self):
        return self.section_index.offset

    def pretty_print(self):
        print('Sh2GeometrySection() =\n{')
        print('\tsection_index = (0x{:X}, {})'.format(self.section_index.offset, self.section_index.value))
        print('\tlen_data = (0x{:X}, 0x{:X})'.format(self.len_data.offset, self.len_data.value))
        print('\tunk0 = (0x{:X}, {})'.format(self.unk0.offset, self.unk0.value))
        print('\tgeometry_sub_section = (0x{:X}, {})'.format(self.geometry_sub_section.offset, self.geometry_sub_section.value))
        print('\tmaterials = (0x{:X}, {})'.format(self.materials.offset, self.materials.value))
        print('}')

def get_objects(f):

        objects = []

        # TODO: Make this an Sh2Map object
        f.read(0x14) # ignore irrelevant data for now
        tex_section_len = f.read(4)
        tex_section_len = struct.unpack('<I', tex_section_len)[0]
        f.read(8)
        f.seek(tex_section_len, 1)

        sh2gs = Sh2GeometrySection()
        sh2gs.section_index = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        sh2gs.len_data = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        sh2gs.unk0 = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        sh2gs.unk1 = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])

        sh2gs.pretty_print()

        sub_section = sh2gs.geometry_sub_section.value
        sub_section.time_stamp = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        sub_section.object_group_count = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        sub_section.len_geometry_sub_section = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
        sub_section.unk0 = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])

        sub_section.pretty_print()

        object_count = sub_section.object_group_count.value
        while(object_count > 0):
            og = Sh2ObjectGroup()
            og.unk = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
            og.len_object_group = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
            og.prim_count = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])
            og.len_unk = OffsetValuePair(f.tell(), struct.unpack('<I', f.read(4))[0])

            objects.append(og)

            f.seek(og.get_offset() + og.len_object_group.value)
            object_count -= 1

        return objects

def get_object_offsets(f):

        #return [0x1c06e0, 0x1CA5F0, 0x1d4dd0]

        object_offsets = []

        f.read(0x14) # ignore irrelevant data for now
        tex_section_len = f.read(4)
        tex_section_len = struct.unpack('<I', tex_section_len)[0]
        f.read(8)
        f.seek(tex_section_len, 1)

        f.read(0x14) # discard geom section header and creation date
        object_count = f.read(4)
        object_count = struct.unpack('<I', object_count)[0]
        f.read(8)

        while(object_count > 0):

            print(f'START = 0x{f.tell():x}')

            object_start = f.tell()
            f.read(4)
            object_size = f.read(4)
            object_size = struct.unpack('<I', object_size)[0]

            object_offsets.append(object_start)

            f.seek(object_start + object_size)
            object_count -= 1

        return object_offsets

def get_primitives(f):
    obj_count = f.read(4)
    obj_count = struct.unpack('<I', obj_count)[0]

    primitive_list = []
    for _o in range(0, obj_count):
        info = f.read(20)
        info = struct.unpack('<IIIHBBHH', info)

        if(info[2] == 2):
            extra_fields = f.read(8)
            extra_fields = struct.unpack('<HBBHH', extra_fields)
            info = info + extra_fields

        primitive_list.append(info)

    return primitive_list