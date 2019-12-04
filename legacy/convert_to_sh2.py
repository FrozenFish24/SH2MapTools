import sys
import os
import struct

import collada
import numpy

SCALE_VAL = 0.0060
X_TRANS = 0.0
Y_TRANS = 0.0
Z_TRANS = 0.0

name = 'bars-cleaned-up'
vert_mode = 36

def main():
    mesh = collada.Collada(f'{name}.dae')

    geom = mesh.geometries[0]
    triset = geom.primitives[0]

    # TODO: Read pycollada docs, this is probably tremendously inefficient
    pos_set = triset.sources['VERTEX'][0][4]
    normal_set = triset.sources['NORMAL'][0][4]
    tex_set = triset.sources['TEXCOORD'][0][4]
    color_set = triset.sources['COLOR'][0][4]

    vert_dict = {}
    for t in triset.indices:
        for v in t:
            vert_dict[v[0]] = (v[1], v[2], v[3])
    
    print(f'Pos: {pos_set[0]}')
    print(f'Normal: {normal_set[vert_dict[0][0]]}')
    print(f'Tex: {tex_set[vert_dict[0][1]]}')
    print(f'Color: {color_set[vert_dict[0][2]]}')

    # Write out vertices
    with open('bars-in-place-out.bin', 'wb') as f:
        for i in range(0, len(pos_set)):
            f.write(struct.pack('<6f', pos_set[i][0], pos_set[i][1], pos_set[i][2], normal_set[vert_dict[i][0]][0], normal_set[vert_dict[i][0]][1], normal_set[vert_dict[i][0]][2]))

            if vert_mode == 36:
                r = int(color_set[vert_dict[0][2]][0] * 255)
                g = int(color_set[vert_dict[0][2]][1] * 255)
                b = int(color_set[vert_dict[0][2]][2] * 255)
                f.write(struct.pack('<BBBB', r, g, b, 255))

            f.write(struct.pack('<2f', tex_set[vert_dict[i][1]][0], tex_set[vert_dict[i][1]][1]))

    # Write out index buffer for stripification
    with open(f'{name}-ibuf.txt', 'w') as f:
        for face in triset.indices:
            #INVERTED WINDING ORDER
            f.write(f'{face[2][0] + 1} ')
            f.write(f'{face[1][0] + 1} ')
            f.write(f'{face[0][0] + 1} ')

        f.write('-1')

    #debug_write_obj(pos_set, normal_set, tex_set, color_set, vert_dict, triset)


def debug_write_obj(pos_set, normal_set, tex_set, color_set, vert_dict, triset):
    obj_string = ''

    for p in range(0, len(pos_set)):
        obj_string += f'v {pos_set[p][0]} {pos_set[p][1]} {pos_set[p][2]}\n'

    for p in range(0, len(pos_set)):
        obj_string += f'vt {tex_set[vert_dict[p][1]][0]} {tex_set[vert_dict[p][1]][1]}\n'

    for p in range(0, len(pos_set)):
        obj_string += f'vn {normal_set[vert_dict[p][0]][0]} {normal_set[vert_dict[p][0]][1]} {normal_set[vert_dict[p][0]][2]}\n'

    for face in triset.indices:
        v1 = face[0][0] + 1
        v2 = face[1][0] + 1
        v3 = face[2][0] + 1
        obj_string += f'f {v1}/{v1}/{v1} {v2}/{v2}/{v2} {v3}/{v3}/{v3}\n'

    with open('debug-obj.obj', 'w') as f:
        f.write(obj_string)


if __name__ == '__main__':
    main()
