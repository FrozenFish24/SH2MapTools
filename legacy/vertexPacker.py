import struct

def main():

    vertList = []
    uvList = []
    normList = []
    with open('model.obj', 'r') as f:
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

    with open('model.bin', 'wb') as f:
        for i in range(0, len(vertList)):
            f.write(struct.pack('<8f', vertList[i][0], vertList[i][1], vertList[i][2], normList[i][0], normList[i][1], normList[i][2], uvList[i][0], uvList[i][1]))


if __name__ == '__main__':
    main()
