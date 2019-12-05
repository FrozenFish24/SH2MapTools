import os
import struct
import pdb
import errno
import collada
import numpy

import common

# TODO: OOP-ify parsing code
# TODO: Collada directly supports tri-strips, may remove some complexity

SCALE_X = 0.0060
SCALE_Y = -0.0060
SCALE_Z = -0.0060

x_trans = 0.0
y_trans = 0.0
z_trans = 0.0
centered = False

# DEBUG VARS
map_name = 'ps85'

def main():
    with open('%s.map' % map_name, 'rb') as f:
        objects = common.get_objects(f)
        for ob in objects:
            ob.pretty_print()
        print()

        # Hack: Remove Object 03 to avoid crash
        objects.remove(objects[2])

        for i in range(0, len(objects)):
            vb_raw_list, vb_info_list, primitive_list, ib_raw, vb_offsets = rip_object(f, objects[i].get_offset())

            total_index = 0
            for j in range(0, len(primitive_list)):
                total_index_backup = total_index
                current_prim_info = primitive_list[j]

                prim_total = 0
                vert_starts = []
                vert_ends = []
                index = 3
                for _sub in range(0, current_prim_info[2]):
                    prim_total += current_prim_info[index]
                    vert_starts.append(current_prim_info[index+3])
                    vert_ends.append(current_prim_info[index+4])
                    index += 5
                
                vert_list = extract_verts(vb_raw_list[current_prim_info[1]], vb_info_list[current_prim_info[1]][1], vert_starts, vert_ends)
                face_list = extract_faces(ib_raw, total_index, prim_total, current_prim_info[5], current_prim_info[6])

                print(current_prim_info)

                collada_mesh = build_collada(i, j, vert_list, face_list)
                total_index += prim_total * current_prim_info[5]

                # DEBUGGERY
                start_of_vb = vb_offsets[current_prim_info[1]]
                start_of_object = current_prim_info[6] * vb_info_list[current_prim_info[1]][1]
                print('Object {:02d}, Primitve {:02d} = 0x{:X} (Stride = {}) (IB = {})'.format(i,j, start_of_vb + start_of_object, vb_info_list[current_prim_info[1]][1], total_index_backup))
                # END DEBUG

                write_collada(f'{map_name}-dump\\{map_name}_{i:02d}_{j:02d}.dae', collada_mesh)

def rip_object(f, off):
    
    vb_offsets = []

    f.seek(off)

    f.read(0x18) # discard for now
    bounding_volume_len = f.read(4)
    bounding_volume_len = struct.unpack('<I', bounding_volume_len)[0]

    bounding_volume = f.read(bounding_volume_len * 4) # ignore occlusion culling volume
    bounding_volume = struct.unpack('<8f', bounding_volume)

    global centered
    if centered is False:
        find_scene_center(bounding_volume)
        centered = True

    f.read(4) # ignore whatever this is

    index_buf_ptr = f.read(4)
    index_buf_ptr = struct.unpack('<I', index_buf_ptr)[0]
    
    index_buf_len = f.read(4)
    index_buf_len = struct.unpack('<I', index_buf_len)[0]

    f.read(4) # discard irrelevant size field

    primitive_list = common.get_primitives(f)

    f.read(4) # discard a size field

    vb_count = f.read(4)
    vb_count = struct.unpack('<I', vb_count)[0]

    vb_info_list = []
    for vb in range(0, vb_count):
        vb_info = f.read(12)
        vb_info = struct.unpack('<III', vb_info)
        vb_info_list.append(vb_info)

    vb_raw_list = []
    for vb in vb_info_list:
        vb_offsets.append(f.tell())
        vert_buf_raw = f.read(vb[2])
        vb_raw_list.append(vert_buf_raw)

    ib_offset = f.tell()
    ib_raw = f.read(index_buf_len)
    #ib_raw = f.tell()
    #f.read(index_buf_len)

    print(f'Index Buffer Offset = 0x{ib_offset:02X}, index Buffer Size = 0x{index_buf_len:02X}')

    return vb_raw_list, vb_info_list, primitive_list, ib_raw, vb_offsets

def extract_verts(vert_buf, stride, vert_starts, vert_ends):
    vertices = []
    for i in range(0, len(vert_starts)):
        for j in range(vert_starts[i] * stride, (vert_ends[i] + 1) * stride, stride):
            if(stride // 4 == 9):
                # special case for vertices containing vertex color
                vertices.append(struct.unpack('<ffffffIff', vert_buf[j:j+stride]))
            else:
                format_string = '<' + 'f' * (stride // 4)
                vertices.append(struct.unpack(format_string, vert_buf[j:j+stride]))

    return vertices

def extract_faces(index_buf, base_vertex_index, primitive_count, skip, start_index):

    primitive_count *= skip

    # Unpack the index buffer
    index_list = []
    for i in range(base_vertex_index * 2, (base_vertex_index * 2) + (primitive_count * 2), 2):
        index_list.append(struct.unpack('<H', index_buf[i:i+2])[0])
    
    face_list = []
    even = True
    for i in range(0, len(index_list) - 2, skip):
        face = (index_list[i] - start_index, index_list[i+1] - start_index, index_list[i+2] - start_index)
        if(even or skip == 3):
            face_list.append(face)
        else:
            face_list.append((face[2], face[1], face[0]))
        even = not even

    return face_list

def build_collada(obj_ind, prim_ind, vert_list, face_list):

    vert_floats = []
    normal_floats = []
    texcoord_floats = []
    color_floats = []

    indices = []

    for vert in vert_list:
        vert_floats.extend([vert[0], vert[1], vert[2]])

        if(len(vert) == 5):
            texcoord_floats.extend([vert[3], 1.0 - vert[4]])
        if(len(vert) == 8):
            normal_floats.extend([vert[3], vert[4], vert[5]])
            texcoord_floats.extend([vert[6], 1.0 - vert[7]])
        elif(len(vert) == 9):
            normal_floats.extend([vert[3], vert[4], vert[5]])

            # convert vert colors from 0-255 to 0.0-1.0
            r = (vert[6] & 0xFF) / 255.0
            g = ((vert[6] >> 8) & 0xFF) / 255.0
            b = ((vert[6] >> 16) & 0xFF) / 255.0
            a = ((vert[6] >> 24) & 0xFF) / 255.0

            color_floats.extend([r, g, b, a])
            texcoord_floats.extend([vert[7], 1.0 - vert[8]])

    for face in face_list:
        if(face[0] != face[1] and face[0] != face[2] and face[1] != face[2]):
            indices.extend([face[0], face[1], face[2]])

    mesh = collada.Collada()

    vert_src = collada.source.FloatSource('vertices', numpy.array(vert_floats), ('X', 'Y', 'Z'))
    normal_src = collada.source.FloatSource('normals', numpy.array(normal_floats), ('X', 'Y', 'Z'))
    color_src = collada.source.FloatSource('colors', numpy.array(color_floats), ('R', 'G', 'B', 'A'))
    texcoord_src = collada.source.FloatSource('texcoords', numpy.array(texcoord_floats), ('S', 'T'))

    geom = collada.geometry.Geometry(mesh, 'geometry', 'mesh', [vert_src, normal_src, color_src, texcoord_src])

    input_list = collada.source.InputList()
    input_list.addInput(0, 'VERTEX', '#vertices')
    input_list.addInput(0, 'NORMAL', '#normals')
    input_list.addInput(0, 'COLOR', '#colors')
    input_list.addInput(0, 'TEXCOORD', '#texcoords')

    triset = geom.createTriangleSet(numpy.array(indices), input_list, '')
    geom.primitives.append(triset)
    mesh.geometries.append(geom)

    translate_transform = collada.scene.TranslateTransform(-x_trans * SCALE_X, -y_trans * SCALE_Y, -z_trans * SCALE_Z)
    scale_transform = collada.scene.ScaleTransform(SCALE_X, SCALE_Y, SCALE_Z)

    geomnode = collada.scene.GeometryNode(geom, [])
    node = collada.scene.Node('mesh', children=[geomnode], transforms=[translate_transform, scale_transform])

    myscene = collada.scene.Scene('scene', [node])
    mesh.scenes.append(myscene)
    mesh.scene = myscene

    return mesh

def find_scene_center(boundingVolume):

    global x_trans
    global y_trans
    global z_trans

    min_x = boundingVolume[0]
    max_x = boundingVolume[4]
    min_y = boundingVolume[1]
    max_y = boundingVolume[5]
    min_z = boundingVolume[2]
    max_z = boundingVolume[6]

    x_trans = (max_x + min_x) / 2
    y_trans = (max_y + min_y) / 2
    z_trans = (max_z + min_z) / 2

def write_collada(filename, collada_mesh):

    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    
    collada_mesh.write(filename)

if __name__ == '__main__':
    main()
