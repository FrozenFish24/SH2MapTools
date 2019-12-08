import struct
from Sh2Map import Sh2GeometrySection

def get_objects(f):

        objects = []

        # TODO: Make this an Sh2Map object
        f.read(0x14) # ignore irrelevant data for now
        tex_section_len = f.read(4)
        tex_section_len = struct.unpack('<I', tex_section_len)[0]
        f.read(8)
        f.seek(tex_section_len, 1)

        sh2gs = Sh2GeometrySection(f)
        sh2gs.recursive_print()

        for ob in sh2gs.geometry_sub_section.value.object_groups:
            objects.append(ob.value)

        return objects

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
