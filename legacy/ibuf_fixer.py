import struct

INSERT_INDEX = 15239
VERTS_ADDED = 455
ORIGINAL_BUFFER = 'original_ib.bin'
STRIPPED_BUFFER = 'INDEX BUFFER.txt'

def main():

    with open(ORIGINAL_BUFFER, 'rb') as f:
        ibuf = f.read()

    index_buffer = []
    for i in range(0, len(ibuf), 2):
        index_buffer.append(struct.unpack('<H', ibuf[i:i+2])[0])
    
    with open(STRIPPED_BUFFER, 'r') as f:
        lines = f.readlines()

    prim_type = lines[0]
    prim_count = lines[1]
    index_count = lines[2]
    indices = lines[3]

    indices = indices.split(' ')
    if(indices[-1] == '\n'):
        indices = indices[:-1] # Remove newline

    ib_head = index_buffer[:INSERT_INDEX]
    ib_tail = index_buffer[INSERT_INDEX:]

    index_mod = 0
    for i in ib_head:
        if(int(i) > index_mod):
            index_mod = int(i)
    print(index_mod)

    index_mod += 1

    out = B''
    for i in ib_head:
        out += struct.pack('<H', int(i))

    out += struct.pack('<H', int(ib_head[-1]))
    out += struct.pack('<H', int(indices[0]) + index_mod)

    for i in indices:
        out += struct.pack('<H', int(i) + index_mod)

    #out += struct.pack('<H', int(indices[-1]) + INSERT_INDEX)
    #out += struct.pack('<H', int(ibAfter[0]) + len(indices))
        
    for i in ib_tail:
        out += struct.pack('<H', int(i) + VERTS_ADDED)

    with open('IndexBuffer.bin', 'wb') as f:
        f.write(out)

if __name__ == '__main__':
    main()
