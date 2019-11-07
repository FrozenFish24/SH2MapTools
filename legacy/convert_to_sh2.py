import sys
import os
import struct

SCALE_VAL = 0.0060
X_TRANS = 0.0
Y_TRANS = 0.0
Z_TRANS = 0.0

name = 'ps85_02_08'

def main():
    vertList = []
    uvList = []
    normList = []
    faceList = []
    
    vertToUV = {}
    vertToNorm = {}
    with open('%s.obj' % name, 'r') as f:
        for line in f:
            split = line.split('\n')
            split = split[0].split(' ')

            if(split[0] == 'v'):
                    vert = (float(split[1]), float(split[2]), float(split[3]))
                    vertList.append(vert)
            elif(split[0] == 'vt'):
                    uv = (float(split[1]), float(split[2]))
                    uvList.append(uv)
            elif(split[0] == 'vn'):
                    norm = (float(split[1]), float(split[2]), float(split[3]))
                    normList.append(norm)
            elif(split[0] == 'f'):
                one = split[1].split('/')
                two = split[2].split('/')
                three = split[3].split('/')

                faceList.append((int(one[0]) - 1, int(two[0]) - 1, int(three[0]) - 1))

                # Record Vert to UV correspondence
                vertToUV[int(one[0]) - 1] = int(one[1]) - 1
                vertToUV[int(two[0]) - 1] = int(two[1]) - 1
                vertToUV[int(three[0]) - 1] = int(three[1]) - 1

                # Record Vert to Normal correspondence
                vertToNorm[int(one[0]) - 1] = int(one[2]) - 1
                vertToNorm[int(two[0]) - 1] = int(two[2]) - 1
                vertToNorm[int(three[0]) - 1] = int(three[2]) - 1

    newUVList = []
    for i in sorted(vertToUV):
        newUVList.append(uvList[vertToUV[i]])

    newNormList = []
    for i in sorted(vertToNorm):
        newNormList.append(normList[vertToNorm[i]])

    if(len(vertList) != len(newUVList) or len(vertList) != len(newNormList)):
        print('Error: different list lengths v%d, u%d n%d' % (len(vertList), len(newUVList), len(newNormList)))

    with open('%s-out.obj' % name, 'w') as f:
        for v in vertList:
            f.write('v %f %f %f\n' % ((v[0] / SCALE_VAL) + X_TRANS, (v[1] / SCALE_VAL) + Y_TRANS, (v[2] / SCALE_VAL) + Z_TRANS))
        for uv in newUVList:
            f.write('vt %f %f \n' % (uv[0], 1.0 - uv[1]))
        for norm in newNormList:
            f.write('vn %f %f %f \n' % (norm[0], norm[1], norm[2]))
        for face in faceList:
            f.write('f {0}/{0}/{0} {1}/{1}/{1} {2}/{2}/{2}\n'.format(face[0] + 1, face[1] + 1, face[2] + 1))

    with open('%s-ibuf.txt' % name, 'w') as f:
        for face in faceList:
            #INVERTED WINDING ORDER
            f.write('%d ' % face[2])
            f.write('%d ' % face[1])
            f.write('%d ' % face[0])

        f.write('-1')

if __name__ == '__main__':
    main()
