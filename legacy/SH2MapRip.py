import os
import struct
import pdb
import errno

import collada
import numpy

# TODO: Collada directly supports tri-strips, may remove some steps

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

        print(f'Object Count: {len(objOffsetList)}\n')
        for i in range(0, len(objOffsetList)):
            vbRawList, vbInfoList, primList, ibRaw, vertBufOffsets = ripObj(f, objOffsetList[i])

            total_index = 0
            for j in range(0, len(primList)):
                total_index_backup = total_index
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

                colladaMesh = buildCollada(i, j, vertList, faceList)
                total_index += primTotal * currentPrimInfo[5]

                #DEBUGGERY
                startOfVB = vertBufOffsets[currentPrimInfo[1]]
                startOfObject = currentPrimInfo[6] * vbInfoList[currentPrimInfo[1]][1]
                print('Object %02d, Primitve %02d = 0x%X (Stride = %d) (IB = %d)' % (i,j, startOfVB + startOfObject, vbInfoList[currentPrimInfo[1]][1], total_index_backup))
                #END DEBUG

                writeCollada('%s-dump\\%s_%02d_%02d.dae' % (map_name,map_name,i,j), colladaMesh)

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

    ibOffset = f.tell()
    ibRaw = f.read(index_buf_sz)
    #ibRaw = f.tell()
    #f.read(index_buf_sz)

    print(f'Index Buffer Offset = 0x{ibOffset:02X}, index Buffer Size = 0x{index_buf_sz:02X}')

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
            if(stride // 4 == 9):
                # special case for vertices containing vertex color
                vertices.append(struct.unpack('<ffffffIff', vertBuf[j:j+stride]))
            else:
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

def buildCollada(objInd, primInd, vertList, faceList):

    vert_floats = []
    normal_floats = []
    texcoord_floats = []
    color_floats = []

    indices = []

    for vert in vertList:
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

    for face in faceList:
        if(face[0] != face[1] and face[0] != face[2] and face[1] != face[2]):
            indices.extend([face[0], face[1], face[2]])
        #else:
        #    pass
        #    objString += '#f {0}/{0}/{0} {1}/{1}/{1} {2}/{2}/{2} # degenerate\n'.format(face[0] + 1, face[1] + 1, face[2] + 1)

    mesh = collada.Collada()

    #effect = collada.material.Effect('effect0', [], 'phong', diffuse=(1,0,0), specular=(0,1,0))
    #mat = collada.material.Material('material0', 'mymaterial', effect)
    #mesh.effects.append(effect)
    #mesh.materials.append(mat)

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

    translate_transform = collada.scene.TranslateTransform(-X_TRANS * SCALE_VAL, -Y_TRANS * SCALE_VAL, -Z_TRANS * SCALE_VAL)
    scale_transform = collada.scene.ScaleTransform(SCALE_VAL, SCALE_VAL, SCALE_VAL)

    #matnode = collada.scene.MaterialNode('materialref', mat, inputs=[])
    geomnode = collada.scene.GeometryNode(geom, [])
    node = collada.scene.Node('mesh', children=[geomnode], transforms=[translate_transform, scale_transform])

    myscene = collada.scene.Scene('scene', [node])
    mesh.scenes.append(myscene)
    mesh.scene = myscene

    return mesh

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

    X_TRANS = (maxX + minX) / 2
    Y_TRANS = 0.0 #(maxY + minY) / 2
    Z_TRANS = (maxZ + minZ) / 2

def writeCollada(filename, colladaMesh):

    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    
    #with open(filename, 'w') as f:
    #    f.write(objString)
    colladaMesh.write(filename)

if __name__ == '__main__':
    main()
