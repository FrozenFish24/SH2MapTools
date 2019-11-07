import os
import struct
import pdb

SCALE_VAL = 0.0060
X_TRANS = 0.0
Y_TRANS = 0.0
Z_TRANS = 0.0
CENTERED = False

#DEBUG VARS
map_name = 'ps85'

def main():
    with open('%s.map' % map_name, 'rb') as f:
        objOffsetList = getObjectOffsets(f)

        print('Object Count: %d' % len(objOffsetList))
        for i in range(0, len(objOffsetList)):
            vbRawList, vbInfoList, primList, ibRaw, vertBufOffsets = ripObj(f, objOffsetList[i])

            total_index = 0
            for j in range(0, len(primList)):
                total_index_backup = total_index
                wavefrontObj = ''
                currentPrimInfo = primList[j]

                primTotal = 0
                vertStarts = []
                vertEnds = []
                index = 3
                for sub in range(0, currentPrimInfo[2]):
                    primTotal += currentPrimInfo[index]
                    vertStarts.append(currentPrimInfo[index+3])
                    vertEnds.append(currentPrimInfo[index+4])
                    index += 5
                
                vertList = extractVerts(vbRawList[currentPrimInfo[1]], vbInfoList[currentPrimInfo[1]][1], vertStarts, vertEnds)
                faceList = extractFaces(ibRaw, total_index, primTotal, currentPrimInfo[5], currentPrimInfo[6])

                print(currentPrimInfo)

                wavefrontObj += 'o Object_%02d_%02d\n' % (i, j)
                wavefrontObj += buildObj(vertList, faceList)
                total_index += primTotal * currentPrimInfo[5]

                #DEBUGGERY
                startOfVB = vertBufOffsets[currentPrimInfo[1]]
                startOfObject = currentPrimInfo[6] * vbInfoList[currentPrimInfo[1]][1]
                print('Object %02d, Primitve %02d = 0x%X (Stride = %d) (IB = %d)' % (i,j, startOfVB + startOfObject, vbInfoList[currentPrimInfo[1]][1], total_index_backup))
                #END DEBUG

                writeObj('%s-dump\\%s_%02d_%02d.obj' % (map_name,map_name,i,j), wavefrontObj)    

def getObjectOffsets(f):

        #return [0x1c06e0, 0x1CA5F0, 0x1d4dd0]

        objOffsetList = []

        f.read(0x14) #ignore irrelevant data for now
        texSectionLen = f.read(4)
        texSectionLen = struct.unpack('<I', texSectionLen)[0]
        f.read(8)
        f.seek(texSectionLen, 1)

        f.read(0x14) # discard geom section header and creation date
        objCount = f.read(4)
        objCount = struct.unpack('<I', objCount)[0]
        f.read(8)

        while(objCount > 0):

            print("START = 0x%x" % f.tell())

            objStart = f.tell()
            f.read(4)
            objSize = f.read(4)
            objSize = struct.unpack('<I', objSize)[0]

            objOffsetList.append(objStart)
            
            f.seek(objStart + objSize)
            objCount -= 1

        return objOffsetList

def ripObj(f, off):
    
    vertBufOffsets = []

    f.seek(off)

    f.read(0x18) # discard for now
    boundingVolumeSz = f.read(4)
    boundingVolumeSz = struct.unpack('<I', boundingVolumeSz)[0]

    boundingVolume = f.read(boundingVolumeSz * 4) # ignore occlusion culling volume
    boundingVolume = struct.unpack('<8f', boundingVolume)

    global CENTERED
    if CENTERED is False:
        centerObj(boundingVolume)
        CENTERED = True

    f.read(4) # ignore whatever this is

    index_buf_ptr = f.read(4)
    index_buf_ptr = struct.unpack('<I', index_buf_ptr)[0]
    
    index_buf_sz = f.read(4)
    index_buf_sz = struct.unpack('<I', index_buf_sz)[0]

    f.read(4) #discard irrelevant size field

    primList = getPrimitives(f)

    f.read(4) # discard a size field

    vb_count = f.read(4)
    vb_count = struct.unpack('<I', vb_count)[0]

    vbInfoList = []
    for vb in range(0, vb_count):
        vb_info = f.read(12)
        vb_info = struct.unpack('<III', vb_info)
        vbInfoList.append(vb_info)

    vbRawList = []
    for vb in vbInfoList:
        vertBufOffsets.append(f.tell())
        vert_buf_raw = f.read(vb[2])
        vbRawList.append(vert_buf_raw)
        
    ibRaw = f.read(index_buf_sz)

    return vbRawList, vbInfoList, primList, ibRaw, vertBufOffsets

def getPrimitives(f):
    obj_count = f.read(4)
    obj_count = struct.unpack('<I', obj_count)[0]
    
    primList = []
    for o in range(0, obj_count):
        info = f.read(20)
        info = struct.unpack('<IIIHBBHH', info)

        if(info[2] == 2):
            extra_fields = f.read(8)
            extra_fields = struct.unpack('<HBBHH', extra_fields)
            info = info + extra_fields

        primList.append(info)
        
    return primList

def extractVerts(vertBuf, stride, vertStarts, vertEnds):
    #pdb.set_trace()
    vertices = []
    for i in range(0, len(vertStarts)):
        for j in range(vertStarts[i] * stride, (vertEnds[i] + 1) * stride, stride):
            formatString = '<' + 'f' * (stride // 4)
            vertices.append(struct.unpack(formatString, vertBuf[j:j+stride]))

    return vertices

def extractFaces(indexBuf, baseVertexIndex, primCount, skip, startIndex):

    primCount *= skip

    # Unpack the index buffer
    indexList = []
    for i in range(baseVertexIndex * 2, (baseVertexIndex * 2) + (primCount * 2), 2):
        indexList.append(struct.unpack('<H', indexBuf[i:i+2])[0])
    
    faceList = []
    even = True
    for i in range(0, len(indexList) - 2, skip):
        face = (indexList[i] - startIndex, indexList[i+1] - startIndex, indexList[i+2] - startIndex)
        if(even or skip == 3):
            faceList.append(face)
        else:
            faceList.append((face[2], face[1], face[0]))
        even = not even

    return faceList

def buildObj(vertList, faceList):
    objString = ''
    for vert in vertList:
        #objString += 'v %f %f %f\n' % (vert[0], vert[1], vert[2])
        #objString += 'v %f %f %f\n' % ((vert[0] * SCALE_VAL) + X_TRANS, (vert[1] * SCALE_VAL) + Y_TRANS, (vert[2] * SCALE_VAL) + Z_TRANS)
        objString += 'v %f %f %f\n' % ((vert[0] - X_TRANS) * SCALE_VAL, (vert[1] - Y_TRANS) * SCALE_VAL, (vert[2] - Z_TRANS) * SCALE_VAL)
    for uv in vertList:
        if(len(uv) == 5):
            objString += 'vt %f %f\n' % (uv[3], 1.0 - uv[4])
        if(len(uv) == 8):
            objString += 'vt %f %f\n' % (uv[6], 1.0 - uv[7])
        elif(len(uv) == 9):
            objString += 'vt %f %f\n' % (uv[7], 1.0 - uv[8])
    for norm in vertList:
        if(len(norm) == 8):
            objString += 'vn %f %f %f\n' % (norm[3], norm[4], norm[5])
        elif(len(norm) == 9):
            objString += 'vn %f %f %f\n' % (norm[3], norm[4], norm[5])
    
    for face in faceList:
        if(face[0] != face[1] and face[0] != face[2] and face[1] != face[2]):
            objString += 'f {0}/{0}/{0} {1}/{1}/{1} {2}/{2}/{2}\n'.format(face[0] + 1, face[1] + 1, face[2] + 1)
        else:
            objString += '#f {0}/{0}/{0} {1}/{1}/{1} {2}/{2}/{2} # degenerate\n'.format(face[0] + 1, face[1] + 1, face[2] + 1)

    return objString

def centerObj(boundingVolume):

    global X_TRANS
    global Y_TRANS
    global Z_TRANS

    minX = boundingVolume[0]
    maxX = boundingVolume[4]
    minY = boundingVolume[1]
    maxY = boundingVolume[5]
    minZ = boundingVolume[2]
    maxZ = boundingVolume[6]

    centerX = (maxX + minX) / 2
    centerY = (maxY + minY) / 2
    centerZ = (maxZ + minZ) / 2

    X_TRANS = centerX
    #Y_TRANS = centerY
    Z_TRANS = centerZ

def writeObj(filename, objString):

    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    
    with open(filename, 'w') as f:
        f.write(objString)

if __name__ == '__main__':
    main()
