import struct

#DEBUG VARS
map_name = 'ca20.map.auto'

OBJECT_IND = 0
PRIM_IND = 1
VB_INDEX = 0

VERTS_ADDED = 6
VERT_SIZE = 0xC0

ORIG_IB_SIZE = 0x159C8
NEW_IB_SIZE = 0x159DA
IB_DIF = NEW_IB_SIZE - ORIG_IB_SIZE

INDEXES_ADDED = IB_DIF // 2

def main():
    with open('%s' % map_name, 'rb+') as f:
        objOffsetList = getObjectOffsets(f)
        UpdateObject(f, objOffsetList[OBJECT_IND])

def getObjectOffsets(f):
        objOffsetList = []

        f.read(4)
        mapSize = f.read(0x4)
        mapSize = struct.unpack('<I', mapSize)[0]
        print('MAP SIZE:\t\t0x%X' % mapSize)
        mapSize += VERT_SIZE + IB_DIF
        f.seek(-4,1)
        f.write(struct.pack('<I', mapSize))
        #UPDATE VALUE HERE
        
        f.read(0xC) #ignore irrelevant data for now
        texSectionLen = f.read(4)
        texSectionLen = struct.unpack('<I', texSectionLen)[0]
        f.read(8)
        f.seek(texSectionLen, 1)

        f.read(4)
        sectionSize = f.read(4)
        sectionSize = struct.unpack('<I', sectionSize)[0]
        print('SECTION SIZE:\t\t0x%X' % sectionSize)
        sectionSize += VERT_SIZE + IB_DIF
        f.seek(-4,1)
        f.write(struct.pack('<I', sectionSize))
        #UPDATE VALUE HERE
        
        f.read(0xC) # discad geom section header and creation date
        objCount = f.read(4)
        objCount = struct.unpack('<I', objCount)[0]

        subSectionSize = f.read(4)
        subSectionSize = struct.unpack('<I', subSectionSize)[0]
        print('SUBSECTION SIZE:\t0x%X' % subSectionSize)
        subSectionSize += VERT_SIZE + IB_DIF
        f.seek(-4,1)
        f.write(struct.pack('<I', subSectionSize))
        #UPDATE VALUE HERE
        
        f.read(4)

        while(objCount > 0):

            objStart = f.tell()
            f.read(4)
            objSize = f.read(4)
            objSize = struct.unpack('<I', objSize)[0]

            objOffsetList.append(objStart)
            
            f.seek(objStart + objSize)
            objCount -= 1

        return objOffsetList

def UpdateObject(f, off):
    vertBufOffsets = []

    f.seek(off)

    f.read(4)
    objectSize = f.read(4)
    objectSize = struct.unpack('<I', objectSize)[0]
    print('OBJECT SIZE:\t\t0x%X' % objectSize)
    objectSize += VERT_SIZE + IB_DIF
    f.seek(-4,1)
    f.write(struct.pack('<I', objectSize))
    # UPDATE VALUE HERE
    
    f.read(4)

    unkSizeNEG1 = f.read(4)
    unkSizeNEG1 = struct.unpack('<I', unkSizeNEG1)[0]
    print('UNK-1 SIZE:\t\t0x%X' % unkSizeNEG1)
    if(unkSizeNEG1 != 0): # Only non-zero in streamed maps
        unkSizeNEG1 += VERT_SIZE + IB_DIF
    f.seek(-4,1)
    f.write(struct.pack('<I', unkSizeNEG1))
    # UPDATE VALUE HERE (ALSO NEEDS PROPER VAR NAME)

    unkSize0 = f.read(4)
    unkSize0 = struct.unpack('<I', unkSize0)[0]
    print('UNK0 SIZE:\t\t0x%X' % unkSize0)
    unkSize0 += VERT_SIZE + IB_DIF
    f.seek(-4,1)
    f.write(struct.pack('<I', unkSize0))
    # UPDATE VALUE HERE

    f.read(4)
    
    cullVolumeSz = f.read(4)
    cullVolumeSz = struct.unpack('<I', cullVolumeSz)[0]

    f.read(cullVolumeSz * 4) # ignore occlusion culling volume

    f.read(4) # ignore whatever this is

    index_buf_ptr = f.read(4)
    index_buf_ptr = struct.unpack('<I', index_buf_ptr)[0]
    print('INDEX BUF POINTER:\t0x%X' % index_buf_ptr)
    index_buf_ptr += VERT_SIZE
    f.seek(-4,1)
    f.write(struct.pack('<I', index_buf_ptr))
    # UPDATE VALUE HERE
    
    index_buf_sz = f.read(4)
    index_buf_sz = struct.unpack('<I', index_buf_sz)[0]
    print('INDEX BUF SIZE:\t\t0x%X' % index_buf_sz)
    index_buf_sz += IB_DIF
    f.seek(-4,1)
    f.write(struct.pack('<I', index_buf_sz))
    # UPDATE VALUE HERE

    unkSize1 = f.read(4)
    unkSize1 = struct.unpack('<I', unkSize1)[0]
    print('UNK1 SIZE:\t\t0x%X' % unkSize1)
    unkSize1 += VERT_SIZE + IB_DIF
    f.seek(-4,1)
    f.write(struct.pack('<I', unkSize1))
    #UPDATE VALUE HERE

    primList = getPrimitives(f)

    unkSize2 = f.read(4)
    unkSize2 = struct.unpack('<I', unkSize2)[0]
    print('UNK2 SIZE:\t\t0x%X' % unkSize2)
    unkSize2 += VERT_SIZE
    f.seek(-4,1)
    f.write(struct.pack('<I', unkSize2))
    #UPDATE VALUE HERE

    vb_count = f.read(4)
    vb_count = struct.unpack('<I', vb_count)[0]

    vbInfoList = []
    for vb in range(0, vb_count):
        if(vb >= VB_INDEX): # SHOULD REALLY GET THE VB INDEX PROGRAMATICALLY
            vbStart = f.read(4)
            vbStart = struct.unpack('<I', vbStart)[0]
            print('VERTBUF START:\t\t0x%X' % vbStart)
            if(vb > VB_INDEX):
                vbStart += VERT_SIZE
            f.seek(-4,1)
            f.write(struct.pack('<I', vbStart))
            #UPDATE VALUE HERE (NOT NECESSARY FOR HP190)

            f.read(4) #discard stride

            vbSize = f.read(4)
            vbSize = struct.unpack('<I', vbSize)[0]
            print('VERTBUF SIZE:\t\t0x%X' % vbSize)
            vbSize += VERT_SIZE
            f.seek(-4,1)
            f.write(struct.pack('<I', vbSize))
            #UPDATE VALUE HERE
        else:
            f.read(12) # skip vertex buffer

def getPrimitives(f):
    print()
    obj_count = f.read(4)
    obj_count = struct.unpack('<I', obj_count)[0]
    
    primList = []
    for o in range(0, obj_count):
        if(o >= PRIM_IND):
            f.read(0xC)

            primCount = f.read(2)
            primCount = struct.unpack('<H', primCount)[0]
            print('P%d PRIM COUNT:\t\t0x%X' % (o, primCount))
            if(o == PRIM_IND):
                primCount += INDEXES_ADDED
                f.seek(-2,1)
                f.write(struct.pack('<H', primCount))
                #UPDATE VALUE HERE

            f.read(2)

            vertStart = f.read(2)
            vertStart = struct.unpack('<H', vertStart)[0]
            print('P%d VERT START:\t\t0x%X' % (o, vertStart))
            if(o > PRIM_IND):
                vertStart += VERTS_ADDED
                f.seek(-2,1)
                f.write(struct.pack('<H', vertStart))
                #UPDATE VALUE HERE

            vertEnd = f.read(2)
            vertEnd = struct.unpack('<H', vertEnd)[0]
            print('P%d VERT END:\t\t0x%X' % (o, vertEnd))
            vertEnd += VERTS_ADDED
            f.seek(-2,1)
            f.write(struct.pack('<H', vertEnd))
            #UPDATE VALUE HERE
        else:
            f.read(0x14) # Not interested, skip
        
    return primList

if __name__ == '__main__':
    main()
