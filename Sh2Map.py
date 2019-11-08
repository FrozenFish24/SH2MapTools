from construct import *

TextureSection = Struct(
    'section_index' / Int32ul,
    'len_data' / Int32ul,
    'unk0' / Int32ul,
    'unk1' / Int32ul,
    'data' / Bytes(this.len_data)
)

# One of these could be a pixel shader to use
Material = Struct(
    'texture' / Int32ul, # Maybe an offset to the actual texture data?
    'unk1' / Int32ul,
    'specularity' / Int32ul, # ???
    'unk2' / Int32ul
)

# If bounding volume is not visible, geometry is culled?
# Haven't seen more complex than two points defining a box
BoundingVolume = Struct(
    'len_bounding_volume' / Int32ul,
    'data' / Bytes(this.len_bounding_volume * 4)
)

SubPrimInfo = Struct(
    'num_prims' / Int16ul,
    'unk' / Int8ul, # usually 0, 1 = garbled polys, >1 = invisible
    'prim_size' / Int8ul,
    'vert_start' / Int16ul,
    'vert_end' / Int16ul
)

PrimitiveInfo = Struct(
    'material_index' / Int32ul, # corresponds to material table at EOF
    'vertex_buffer_index' / Int32ul,
    'num_sub_prims' / Int32ul,
    'sub_prims' / Array(this.num_prims, SubPrimInfo)
)

PrimitiveList = Struct(
    'len_primitive_list' / Int32ul, # This might actually be an offset to the start of vertexbufferdata
    'ofs_index_buffer' / Int32ul,
    'len_index_buffer' / Int32ul,
    'len_unk' / Int32ul, # Seems to be optional? Not present in some transparent geometry
    'num_prims' / Int32ul,
    'prim_info' / Array(this.num_prims, PrimitiveInfo)
)

Vertex36 = Struct(
    'x' / Float32l,
    'y' / Float32l,
    'z' / Float32l,
    'a' / Float32l,
    'b' / Float32l,
    'c' / Float32l,
    'color' / Int32ul, # Vertex R8G8B8A8, alpha always 0xFF
    'u' / Float32l,
    'v' / Float32l
)

Vertex32 = Struct(
    'x' / Float32l,
    'y' / Float32l,
    'z' / Float32l,
    'a' / Float32l,
    'b' / Float32l,
    'c' / Float32l,
    'u' / Float32l,
    'v' / Float32l
)

VertexBufferInfo = Struct(
    'ofs_start' / Int32ul,
    'stride' / Int32ul,
    'ofs_end' / Int32ul,
)

VertexBuffers = Struct(
    'len_all_vertex_buffers' / Int32ul,
    'num_vertex_buffers' / Int32ul,
    'vertex_buffer_infos' / Array(this.num_vertex_buffers, VertexBufferInfo),
    'vertex_data' / Array(this.num_vertex_buffers, Bytes(lambda this: this.vertex_buffer_infos[this._index].ofs_end))
)

Object = Struct(
    'len_object' / Int32ul,
    'num_bounding_volumes' / Int32ul,
    'bounding_volumes' / Array(this.num_bounding_volumes, BoundingVolume),
    #'prim_list' / PrimitiveList,
    #'vertex_buffers' / VertexBuffers,
    #'index_buffer' / Bytes(this.prim_list.len_index_buffer)
)

# "MapChunk" might be a better name for this?
ObjectGroup = Struct(
    'unk0' / Int32ul, # Object group index maybe?
    'len_object_group' / Int32ul,
    'prim_count' / Int32ul, # 0 to this value inclusive (NOT SURE)
    'unk_size' / Int32ul, # Only non-zero in MAPs that stream in chunks, size includes vertex buffer and index buffer
    'object' / Object
)

GeometrySubSection = Struct(
    'creation_date' / Int32ul,
    'unk0' / Int32ul,
    'len_geometry_sub_section' / Int32ul,
    'prim_count' / Int32ul, # 0 to this value inclusive
    'object_group' / ObjectGroup
)

GeometrySection = Struct(
    'section_index' / Int32ul,
    'len_data' / Int32ul,
    'unk0' / Int32ul,
    'unk1' / Int32ul,
    'geometry_sub_section' / GeometrySubSection,
    'materials' / Material # Does this go here?
)

Sh2Map = Struct(
    'creation_date' / Int32ul,
    'len_map' / Int32ul,
    'num_sections' / Int32ul,
    'unk' / Int32ul,
    'texture_section' / TextureSection,
    'geometry_section' / GeometrySection
)
