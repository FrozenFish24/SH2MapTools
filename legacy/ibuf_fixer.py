import struct

INSERT_INDEX = 15239
VERTS_ADDED = 455
ORIGINAL_BUFFER = 'original_ib.bin'
STRIPPED_BUFFER = 'INDEX BUFFER.txt'

def main():

    with open(ORIGINAL_BUFFER, 'rb') as f:
        ibuf = f.read()

    indexBuffer = []
    for i in range(0, len(ibuf), 2):
        indexBuffer.append(struct.unpack('<H', ibuf[i:i+2])[0])
    
    with open(STRIPPED_BUFFER, 'r') as f:
        lines = f.readlines()

    primType = lines[0]
    primCount = lines[1]
    indexCount = lines[2]
    indices = lines[3]

    indices = indices.split(' ')
    if(indices[-1] == '\n'):
        indices = indices[:-1] # Remove newline

    ibBefore = indexBuffer[:INSERT_INDEX]
    ibAfter = indexBuffer[INSERT_INDEX:]

    indexMod = 0
    for i in ibBefore:
        if(int(i) > indexMod):
            indexMod = int(i)
    print(indexMod)

    indexMod += 1

    out = B''
    for i in ibBefore:
        out += struct.pack('<H', int(i))

    out += struct.pack('<H', int(ibBefore[-1]))
    out += struct.pack('<H', int(indices[0]) + indexMod)

    for i in indices:
        out += struct.pack('<H', int(i) + indexMod)

    #out += struct.pack('<H', int(indices[-1]) + INSERT_INDEX)
    #out += struct.pack('<H', int(ibAfter[0]) + len(indices))
        
    for i in ibAfter:
        out += struct.pack('<H', int(i) + VERTS_ADDED)

    with open('IndexBuffer.bin', 'wb') as f:
        f.write(out)

if __name__ == '__main__':
    main()
