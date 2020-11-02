from Field import Field, FieldType

class Node:
    def __init__(self, type):
        self.type = type

        # Keep track of fields in both a list and dict for fast access via index or field name
        self._fields_list = []
        self._fields_dict = {}

        self._children = []

    def __iter__(self):
        for field in self._fields_list:
            yield field

    @property
    def offset(self):
        return self._fields_list[0].offset

    def add_field(self, name, f, type, size = 0):
        if name in self._fields_dict:
            raise ValueError(f'Field with name {name} already exists in structure {self.type}')

        field = Field(name, f, type, size)
        self._fields_dict[name] = field
        self._fields_list.append(field)

    def field_count(self):
        return len(self._fields_list)

    def add_child(self, child):
        self._children.append(child)

    def child_count(self):
        return len(self._children)

    def child_at(self, index):
        return self._children[index]

    def get_children(self):
        return self._children

    def at(self, index):
        return self._fields_list[index]

    def get(self, name):
        return self._fields_dict.get(name)

    def get_fields(self, recurse=False):
        fields = []
        fields += self._fields_list

        if not recurse:
            return fields

        for child in self._children:
            child_fields = child.get_fields(True)
            fields += child_fields

        return fields
