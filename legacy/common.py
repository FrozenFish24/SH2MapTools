import struct
from Sh2Map import Sh2Map

def get_objects(f):

    objects = []

    sh2map = Sh2Map(f)
    sh2map.recursive_print()

    for ob in sh2map.geometry_section.value.geometry_sub_section.value.object_groups:
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
