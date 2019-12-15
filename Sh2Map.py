# TODO: Could 1:1 Structs be combined? e.g. GeometrySection contains only one GeometrySubSection

from construct import *

TextureSection = Struct(
    'section_index' / Int32ul,
    'len_data' / Int32ul,
    'reserved0' / Int32ul, # Padding to 16 byte bounds?
    'reserved1' / Int32ul, # Same
    'data' / Bytes(this.len_data)
)

# One of these could be a pixel shader to use
# Potential bitfields
Material = Struct(
    'texture' / Int32ul, # Maybe an offset to the actual texture data?
    'unk0' / Int32ul,
    'specularity' / Int32ul, # ???
    'unk1' / Int32ul
)

SubPrimInfo = Struct(
    'num_prims' / Int16ul,
    'unk' / Int8ul, # usually 0, 1 = garbled polys, >1 = invisible
    'prim_len' / Int8ul,
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
    'color' / Int32ul, # Vertex A8R8G8B8, alpha always 0xFF, used for static lighting on certain maps
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

VertexBuffer = Struct(
    'len_all_vertex_buffers' / Int32ul,
    'num_vertex_buffers' / Int32ul,
    'vertex_buffer_infos' / Array(this.num_vertex_buffers, VertexBufferInfo),
    'vertex_data' / Array(this.num_vertex_buffers, Bytes(lambda this: this.vertex_buffer_infos[this._index].ofs_end))
)

Object = Struct(
    'len_object' / Int32ul, # len includes header, gets you to transparent geometry
    'object_index' / Int32ul, # ??? or maybe a count of sub structures?
    'unk0' / Int32ul,  #Maybe this is len_bounding_volume (TODO: Find map file with val other than 8)
    'bounding_volume' / Array(8, Float32l), # If bounding volume is not visible, geometry is culled? Haven't seen more complex than two points defining a box.
    'prim_list' / PrimitiveList,
    'vertex_buffers' / VertexBuffer,
    'index_buffer' / Bytes(this.prim_list.len_index_buffer)
)

# "MapChunk" might be a better name for this?
ObjectGroup = Struct(
    'unk0' / Int32ul, # SH2,3,4 Viewer (by perdedork@yahoo.com) calls this field 'Main primitive offset' and virtually always claims it's invalid
    'len_object_group' / Int32ul,
    'unk1' / Int32ul,
    'len_unk' / Int32ul, # Only non-zero in MAPs that stream in chunks, size includes vertex buffer and index buffer
    'object' / Object
)

GeometrySubSection = Struct(
    'magic' / Int32ul, # 0x20010730 in numbered map files, 0x19990901 in unnumbered (Creation date in hexspeak? 30/07/2001 and 01/09/1999 ddmmyyyy?)
    'object_group_count' / Int32ul,
    'len_geometry_sub_section' / Int32ul,
    'num_materials' / Int32ul,
    'object_groups' / Array(this.object_group_count, ObjectGroup),
    'materials' / Array(this.num_materials, Material)
)

GeometrySection = Struct(
    'section_index' / Int32ul,
    'len_data' / Int32ul,
    'reserved0' / Int32ul, # Padding to 16 byte bounds?
    'reserved1' / Int32ul, # Same
    'geometry_sub_section' / GeometrySubSection
)

Sh2Map = Struct(
    'magic' / Int32ul, # 0x20010510 (Creation date in hexspeak? 10/05/2001 ddmmyyyy?)
    'len_map' / Int32ul,
    'num_sections' / Int32ul,
    'reserved' / Int32ul, # Padding to 16 byte bounds?
    'texture_section' / TextureSection,
    'geometry_section' / GeometrySection
)

# WIP:
TransparentObjectGroup(
    'num_transparent_objects' / Int32ul,
    'len_transparent_object' / Int32ul, # Not always?
    'unk0' / Int32ul,
    'unk1' / Int32ul,
    'unk2' / Int32ul,
    'unk3' / Int32ul,
    'unk4' / Int32ul, # This could still be bounding volume length? (TODO: Find map file with val other than 8)
    'transparent_objects' / Array(num_transparent_objects, TransparentObject)
)

# Padded to 16 byte bounds
TransparentObject(
    'bounding_volume' / Array(8, Float32l),
    'len_bounding_vol_header' / Int32ul,
    'len_bounding_vol_header_and_vb' / Int32ul,
    'len_index_buffer' / Int32ul,

    # This chunk might be another sub-struct
    'unk0' / Int32ul,
    'material_index' / Int32ul,
    'vertex_buffer_index' / Int32ul,
    'verts_per_prim' / Int32ul, # strip_len maybe?
    'num_prims' / Int32ul, # total prims

    'vertex_buffers' / VertexBuffer,
    'index_buffer' / Bytes(this.len_index_buffer)
)
