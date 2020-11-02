import struct

class FieldType:
    u8 = 0
    u16 = 1
    u32 = 2
    f32 = 3
    raw = 4

class Field:
    def __init__(self, name, f, type, size = 0):
        if type not in [FieldType.u8, FieldType.u16, FieldType.u32, FieldType.f32, FieldType.raw]:
            raise ValueError('Field type not u8, 16, u32, f32 or raw')

        if type == FieldType.raw and size < 0:
            raise ValueError('Size cannot be negative')
        if type == FieldType.raw and size == 0:
            raise ValueError("Size cannot be zero when Field type is 'raw'")

        self.name = name
        self.offset = f.tell()
        self.type = type

        if type == FieldType.u8:
            self.size = 1
            self._value = struct.unpack('<B', f.read(1))[0]
        elif type == FieldType.u16:
            self.size = 2
            self._value = struct.unpack('<H', f.read(2))[0]
        elif type == FieldType.u32:
            self.size = 4
            self._value = struct.unpack('<I', f.read(4))[0]
        elif type == FieldType.f32:
            self.size = 4
            self._value = struct.unpack('<f', f.read(4))[0]
        elif type == FieldType.raw:
            self.size = size
            self._value = f.read(size)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self.type in {FieldType.u8, FieldType.u16, FieldType.u32}:
            try:
                value = int(value)
            except:
                print(value)
                raise ValueError('Value not convertible to int')
        elif self.type == FieldType.f32:
            try:
                value = float(value)
            except:
                raise ValueError('Value not convertible to float')
        else:
            raise ValueError('Setting not supported')

        self._value = value
