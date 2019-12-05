import struct

#DEBUG VARS
map_name = 'ca20.map.auto'

OBJECT_IND = 0
PRIM_IND = 1
VB_INDEX = 0

VERTS_ADDED = 6
VERT_LEN = 0xC0

ORIG_IB_LEN = 0x159C8
NEW_IB_LEN = 0x159DA
IB_DIF = NEW_IB_LEN - ORIG_IB_LEN

INDEXES_ADDED = IB_DIF // 2

def main():
    with open('%s' % map_name, 'rb+') as f:
        object_offsets = get_object_offsets(f)
        update_object(f, object_offsets[OBJECT_IND])

def get_object_offsets(f):
        object_offsets = []

        f.read(4)
        map_len = f.read(0x4)
        map_len = struct.unpack('<I', map_len)[0]
        print(f'MAP LEN:\t\t0x{map_len:X}')
        map_len += VERT_LEN + IB_DIF
        f.seek(-4, 1)
        f.write(struct.pack('<I', map_len))
        #UPDATE VALUE HERE
        
        f.read(0xC) #ignore irrelevant data for now
        tex_section_len = f.read(4)
        tex_section_len = struct.unpack('<I', tex_section_len)[0]
        f.read(8)
        f.seek(tex_section_len, 1)

        f.read(4)
        section_len = f.read(4)
        section_len = struct.unpack('<I', section_len)[0]
        print(f'SECTION LEN:\t\t0x{section_len:X}')
        section_len += VERT_LEN + IB_DIF
        f.seek(-4, 1)
        f.write(struct.pack('<I', section_len))
        #UPDATE VALUE HERE
        
        f.read(0xC) # discad geom section header and creation date
        object_count = f.read(4)
        object_count = struct.unpack('<I', object_count)[0]

        sub_section_len = f.read(4)
        sub_section_len = struct.unpack('<I', sub_section_len)[0]
        print(f'SUBSECTION LEN:\t0x{sub_section_len:X}')
        sub_section_len += VERT_LEN + IB_DIF
        f.seek(-4, 1)
        f.write(struct.pack('<I', sub_section_len))
        #UPDATE VALUE HERE
        
        f.read(4)

        while(object_count > 0):

            object_start = f.tell()
            f.read(4)
            object_len = f.read(4)
            object_len = struct.unpack('<I', object_len)[0]

            object_offsets.append(object_start)
            
            f.seek(object_start + object_len)
            object_count -= 1

        #return objOffsetList
        return [object_offsets[0], object_offsets[1], object_offsets[3]]

def update_object(f, off):
    vb_offsets = []

    f.seek(off)

    f.read(4)
    object_len = f.read(4)
    object_len = struct.unpack('<I', object_len)[0]
    print(f'OBJECT LEN:\t\t0x{object_len:X}')
    object_len += VERT_LEN + IB_DIF
    f.seek(-4, 1)
    f.write(struct.pack('<I', object_len))
    # UPDATE VALUE HERE
    
    f.read(4)

    unk_len_0 = f.read(4)
    unk_len_0 = struct.unpack('<I', unk_len_0)[0]
    print(f'UNK0 LEN:\t\t0x{unk_len_0:X}')
    if(unk_len_0 != 0): # Only non-zero in streamed maps
        unk_len_0 += VERT_LEN + IB_DIF
    f.seek(-4, 1)
    f.write(struct.pack('<I', unk_len_0))
    # UPDATE VALUE HERE

    unk_len_1 = f.read(4)
    unk_len_1 = struct.unpack('<I', unk_len_1)[0]
    print(f'UNK1 len:\t\t0x{unk_len_1:X}')
    unk_len_1 += VERT_LEN + IB_DIF
    f.seek(-4, 1)
    f.write(struct.pack('<I', unk_len_1))
    # UPDATE VALUE HERE

    f.read(4)
    
    bounding_volume_len = f.read(4)
    bounding_volume_len = struct.unpack('<I', bounding_volume_len)[0]

    f.read(bounding_volume_len * 4) # ignore occlusion culling volume

    f.read(4) # ignore whatever this is

    index_buf_ptr = f.read(4)
    index_buf_ptr = struct.unpack('<I', index_buf_ptr)[0]
    print(f'INDEX BUF POINTER:\t0x{index_buf_ptr:X}')
    index_buf_ptr += VERT_LEN
    f.seek(-4, 1)
    f.write(struct.pack('<I', index_buf_ptr))
    # UPDATE VALUE HERE
    
    index_buf_len = f.read(4)
    index_buf_len = struct.unpack('<I', index_buf_len)[0]
    print(f'INDEX BUF LEN:\t\t0x{index_buf_len:X}')
    index_buf_len += IB_DIF
    f.seek(-4, 1)
    f.write(struct.pack('<I', index_buf_len))
    # UPDATE VALUE HERE

    unk_len_2 = f.read(4)
    unk_len_2 = struct.unpack('<I', unk_len_2)[0]
    print(f'UNK2 LEN:\t\t0x{unk_len_2:X}')
    unk_len_2 += VERT_LEN + IB_DIF
    f.seek(-4, 1)
    f.write(struct.pack('<I', unk_len_2))
    #UPDATE VALUE HERE

    primitive_list = get_primitives(f)

    unk_len_3 = f.read(4)
    unk_len_3 = struct.unpack('<I', unk_len_3)[0]
    print(f'UNK3 LEN:\t\t0x{unk_len_3:X}')
    unk_len_3 += VERT_LEN
    f.seek(-4, 1)
    f.write(struct.pack('<I', unk_len_3))
    #UPDATE VALUE HERE

    vb_count = f.read(4)
    vb_count = struct.unpack('<I', vb_count)[0]

    vb_info_list = []
    for vb in range(0, vb_count):
        if(vb >= VB_INDEX): # SHOULD REALLY GET THE VB INDEX PROGRAMATICALLY
            vb_start = f.read(4)
            vb_start = struct.unpack('<I', vb_start)[0]
            print(f'VERTBUF START:\t\t0x{vb_start:X}')
            if(vb > VB_INDEX):
                vb_start += VERT_LEN
            f.seek(-4,1)
            f.write(struct.pack('<I', vb_start))
            #UPDATE VALUE HERE (NOT NECESSARY FOR HP190)

            f.read(4) #discard stride

            vb_len = f.read(4)
            vb_len = struct.unpack('<I', vb_len)[0]
            print(f'VERTBUF LEN:\t\t0x{vb_len:X}')
            vb_len += VERT_LEN
            f.seek(-4,1)
            f.write(struct.pack('<I', vb_len))
            #UPDATE VALUE HERE
        else:
            f.read(12) # skip vertex buffer

def get_primitives(f):
    print()
    object_count = f.read(4)
    object_count = struct.unpack('<I', object_count)[0]
    
    primitives = []
    for o in range(0, object_count):
        if(o >= PRIM_IND):
            f.read(0xC)

            primitive_count = f.read(2)
            primitive_count = struct.unpack('<H', primitive_count)[0]
            print(f'P{o} PRIM COUNT:\t\t0x{primitive_count:X}')
            if(o == PRIM_IND):
                primitive_count += INDEXES_ADDED
                f.seek(-2,1)
                f.write(struct.pack('<H', primitive_count))
                #UPDATE VALUE HERE

            f.read(2)

            vert_start = f.read(2)
            vert_start = struct.unpack('<H', vert_start)[0]
            print(f'P{o} VERT START:\t\t0x{vert_start:X}')
            if(o > PRIM_IND):
                vert_start += VERTS_ADDED
                f.seek(-2,1)
                f.write(struct.pack('<H', vert_start))
                #UPDATE VALUE HERE

            vert_end = f.read(2)
            vert_end = struct.unpack('<H', vert_end)[0]
            print(f'P{o} VERT END:\t\t0x{vert_end:X}')
            vert_end += VERTS_ADDED
            f.seek(-2,1)
            f.write(struct.pack('<H', vert_end))
            #UPDATE VALUE HERE
        else:
            f.read(0x14) # Not interested, skip
        
    return primitives

if __name__ == '__main__':
    main()
