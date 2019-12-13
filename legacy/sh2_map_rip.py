import os
import sys
import struct
import errno
import collada
import numpy

from Sh2Map import Sh2Map

# TODO: Collada directly supports tri-strips, may remove some complexity

SCALE_X = 0.0060
SCALE_Y = -0.0060
SCALE_Z = -0.0060

def main():
    if len(sys.argv) < 2:
        print(f'Usage: python {os.path.basename(__file__)} <map file>')
        return

    run(sys.argv[1])

def run(filename, silent=False, test_mode=False):
    with open(f'{filename}', 'rb') as f:
        sh2map = Sh2Map(f)

        if not silent:
            sh2map.recursive_print()

        geometry_section = sh2map.geometry_section.value
        geometry_sub_section = geometry_section.geometry_sub_section.value
        object_groups = geometry_sub_section.object_groups

        transform = None

        for og in range(0, len(object_groups)):
            if(object_groups[og].value.object == None):
                continue

            obj = object_groups[og].value.object.value

            # Find rough scene center from first object's bounding volume
            if transform is None:
                transform = find_scene_center(obj.bounding_volumes)

            primitive_list = obj.prim_list.value

            total_index = 0
            for pi in range(0, len(primitive_list.prim_info)):

                current_prim_info = primitive_list.prim_info[pi].value

                prim_total = 0
                for sp in range(0, current_prim_info.num_sub_prims.value):
                    sub_prim = current_prim_info.sub_prims[sp].value

                    prim_total += sub_prim.num_prims.value

                    vert_buf = obj.vertex_buffers.value.vertex_data.value
                    stride = obj.vertex_buffers.value.vertex_buffer_infos[current_prim_info.vertex_buffer_index.value].value.stride.value
                    vert_start = sub_prim.vert_start.value
                    vert_end = sub_prim.vert_end.value

                    index_buf = obj.index_buffer.value
                    base_vertex_index = total_index
                    primitive_count = prim_total
                    skip = sub_prim.prim_len.value
                    start_index = vert_start

                    vert_list = extract_vertices(vert_buf, stride, vert_start, vert_end)
                    face_list = extract_faces(index_buf, base_vertex_index, primitive_count, skip, start_index)

                    collada_mesh = build_collada(og, pi, vert_list, face_list, transform)
                    total_index += prim_total * sub_prim.prim_len.value

                    if not test_mode:
                        write_collada(f'{filename}-dump\\{filename}_{og:02d}_{pi:02d}.dae', collada_mesh)

                    # DEBUGGERY
                    #start_of_vb = vb_offsets[current_prim_info[1]]
                    #start_of_object = current_prim_info[6] * vb_info_list[current_prim_info[1]][1]
                    #print('Object {:02d}, Primitve {:02d} = 0x{:X} (Stride = {}) (IB = {})'.format(i,j, start_of_vb + start_of_object, vb_info_list[current_prim_info[1]][1], total_index_backup))
                    # END DEBUG

def find_scene_center(bounding_volume):
    min_x = bounding_volume[0]
    max_x = bounding_volume[4]
    min_y = bounding_volume[1]
    max_y = bounding_volume[5]
    min_z = bounding_volume[2]
    max_z = bounding_volume[6]

    x_trans = (max_x + min_x) / 2
    y_trans = (max_y + min_y) / 2
    z_trans = (max_z + min_z) / 2

    return (x_trans, y_trans, z_trans)

def extract_vertices(vert_buf, stride, vert_start, vert_end):
    vertices = []
    for j in range(vert_start * stride, (vert_end + 1) * stride, stride):
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

def build_collada(obj_ind, prim_ind, vert_list, face_list, transform):

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

    translate_transform = collada.scene.TranslateTransform(-transform[0] * SCALE_X, -transform[1] * SCALE_Y, -transform[2] * SCALE_Z)
    scale_transform = collada.scene.ScaleTransform(SCALE_X, SCALE_Y, SCALE_Z)

    geomnode = collada.scene.GeometryNode(geom, [])
    node = collada.scene.Node('mesh', children=[geomnode], transforms=[translate_transform, scale_transform])

    myscene = collada.scene.Scene('scene', [node])
    mesh.scenes.append(myscene)
    mesh.scene = myscene

    return mesh

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
