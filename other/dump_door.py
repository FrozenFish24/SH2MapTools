'''Quick and dirty script to dump/document b_do4.mdl (Hospital front double doors)'''
import struct
from dataclasses import dataclass

INDEX_DATA_START = 0x2F0
INDEX_DATA_SIZE = 0x470
INDEX_COUNT = INDEX_DATA_SIZE // 2

VERT_DATA_START = 0x760
VERT_COUNT = 384

@dataclass
class Vertex:
    x: float
    y: float
    z: float
    w: float

    # normals?
    a: float
    b: float
    c: float
    
    # diffuse color?
    diffuse_a: int
    diffuse_b: int
    diffuse_g: int
    diffuse_r: int

    # specular color?
    specular_a: int
    specular_b: int
    specular_g: int
    specular_r: int

    # texture coords
    u: float
    v: float

    unk0x2C: int # known values 0, 1 (associated bone?)

    def __str__(self) -> str:
        return f'x: {self.x}, y: {self.y}, z: {self.z}, ' \
               f'a: {self.a}, b: {self.b}, c: {self.c}, ' \
               f'diffuse_rgba: ({self.diffuse_r}, {self.diffuse_g}, {self.diffuse_b}, {self.diffuse_a}), ' \
               f'specular_rgba: ({self.specular_r}, {self.specular_g}, {self.specular_b}, {self.specular_a}), ' \
               f'u: {self.u}, v: {self.v}, ' \
               f'unk0x2C: {self.unk0x2C}'

verts = []
with open('b_do4.mdl', 'rb') as f:
    f.seek(INDEX_DATA_START)
    indices = struct.unpack(f'<{INDEX_COUNT}H', f.read(INDEX_DATA_SIZE))
    
    f.seek(VERT_DATA_START)
    for i in range(VERT_COUNT):
        verts.append(Vertex(*struct.unpack('<7f8B2fI', f.read(0x30))))

with open('output.obj', 'w') as f:
    for i, v in enumerate(verts):
        f.write(f'v {v.x} {v.y} {v.z} {v.w} # vert {i}\n')
    
    f.write('\n')

    for v in verts:
        f.write(f'vt {v.u} {v.v}\n')
    
    f.write('\n')

    for v in verts:
        f.write(f'vn {v.a} {v.b} {v.c}\n')
    
    f.write('\n')

    # write out the faces
    for i in range(2, INDEX_COUNT):
    
        v0, v1, v2 = indices[i-2] + 1, indices[i-1] + 1, indices[i] + 1
        
        if i % 2 == 0:
            f.write(f'f {v0}/{v0}/{v0} {v1}/{v1}/{v1} {v2}/{v2}/{v2}\n')
        else:
            f.write(f'f {v1}/{v1}/{v1} {v0}/{v0}/{v0} {v2}/{v2}/{v2}\n')

    f.write('\n')

    for i, v in enumerate(verts):
        f.write(f'# vert {i} [{v}]\n')
