from Model import Node
from Field import Field

class SimpleMaterial(Node):
    def __init__(self, modelMaterial):
        if modelMaterial.type != 'Sh2ModelMaterial':
            raise ValueError('SimpleMaterial can only adapt an Sh2ModelMaterial')

        super().__init__('SimpleMaterial')

        self._fields_list = modelMaterial._fields_list.copy()
        self._fields_dict = modelMaterial._fields_dict.copy()

        sampler_states = modelMaterial.child_at(3)
        for field in sampler_states._fields_list:
            self._fields_list.append(field)
            self._fields_dict[field.name] = field
