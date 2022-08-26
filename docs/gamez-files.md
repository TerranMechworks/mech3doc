# GameZ files

GameZ files hold the game's world assets (except for 'mech models).

## Investigation (MW3)

GameZ files begin with a header, which is a mish-mash of information:

```rust
struct Header {
    signature: u32, // always 0x02971222
    version: u32, // always 27
    texture_count: u32,
    textures_offset: u32,
    materials_offset: u32,
    meshes_offset: u32,
    node_array_size: u32,
    node_count: u32,
    nodes_offset: u32,
}
```

The signature (u32) is the magic number `0x02971222`. The version (u32) is always 27, which matches the [mechlib archives](mechlib-archives.md) version.

The other values are used for accessing the four big blocks of information: textures, materials, meshes, and nodes. This is also not so different from the mechlib archives, although there are significant differences in the way the data is read/written. It isn't known why this is. The offsets aren't strictly necessary for parsing, since the data is written without padding, and so can be used for verifying the different parsing stages were successful/parsed all the information.

### Textures

Reading the textures uses the texture count from the header. Expect this to be less than 4096 textures for sanity checking (if desired). There is no header, instead simply read texture count texture information structures:

```rust
struct TextureInfo {
    unk00: u32, // always 0
    unk04: u32, // always 0
    texture: [u8; 20], // suffixed
    usage: TextureUsage, // always Used (2)
    index: u32, // always 0
    unk36: i32, // always -1
}

enum TextureUsage: u32 {
    Unused = 0,
    Unknown1 = 1,
    Used = 2,
    Unknown3 = 3,
}

type TextureInfos = [TextureInfo; texture_count];
```

As with many structures, this seems to be a memory dump of an in-engine structure. So most of these fields are unimportant for simply reading the game data.

The only important field is the texture name, which is interesting to parse. Assume ASCII encoding. Firstly, it is shorter than most other fixed-length strings in game data (20 bytes, instead of the usual 32 bytes).

Secondly, it is suffixed. Basically, the name will be `texture\0tif\0\0`, that is the name of the texture/image as it appears in the texture packages, followed by a null byte, followed by the suffix/file extension `tif` (usually), finally padded with more null bytes until the length of 20 bytes. So it seems like the assets were Tag Image File Format (TIFF) images, and then the GameZ generation code didn't strip the file extension, but simply overwrote the period of the file extension with a null byte.

For code that only wants to read the texture name, this doesn't matter. Simply read until the first null byte and discard the rest. For code that wishes to e.g. round-trip this information in a binary-accurate way, it's more complicated. In every case, there will be an initial null byte. The suffix and further padding may be cut off by the 20 byte limit. Any padding after the suffix will also be only more null bytes. So restoring the period and therefore the file extension is a feasible approach.

Not much else is known about the other fields. `unk00` (u32?) is always zero (0), and could've been a pointer. `unk04` (u32?) is always zero (0). I'm told it could cause the engine to execute additional dynamic code on loading. The `usage` field (u32?) seems to allow tracking of if the texture is no longer in use by the engine and can be removed from memory. It will always be two (2) in the file, which corresponds to "Used". The `index` field (u32 or i32) tracks the texture's index in the global texture array. It will always be zero (0) in the file, since no index has been assigned until it is loaded. `unk36` (i32) is always negative one (-1).

### Materials

#### Materials header

The materials block does have a header:

```rust
struct MaterialHeader {
    array_size: i32, // always >= 0, <= 0xFFFF
    count: i32, // always >= 0, <= array_size
    index_max: i32, // always == count
    unk12: i32, // always -1
}
```

The field `unk12` is unknown, but is always negative one (-1).

The other fields are interdependent. The material array size indicates how big the material array for this world is expected to the in the worst case. This allows the engine to allocate more or less memory depending on the world. Expect this to be zero (0) or greater, and less than 65535/0xFFFF. Next is the actual count of materials in the file. Naturally, this must be zero (0) or greater, and less than the array size. Finally is the maximum index or next index, which is used to track which index to use for any further materials. This will always be the same as the material count, since they are loaded at once, producing contiguous indices. Shortly, we'll see that the material indices are i16 values. It's unclear why the values in the header are aligned to 32 bits/4 bytes. This is why I've indicated them to be read as i32, with additional bounds checking. Per C structure packing rules, you'd expected if they were i16 that the header would be smaller/more tightly packed.

Materials are read in three phases. The valid materials first, then zeroed-out materials, and then material cycle data.

#### Materials information

Next, count materials are read. Each material has a main structure, which is the same structure as the mechlib materials, but is read and interpreted slightly different. Unlike the mechlib materials, material indices are also read. First, the structures:

```rust
struct Material {
    alpha: u8, // maybe?
    flags: MaterialFlags,
    rgb: u16, // maybe?
    red: f32,
    green: f32,
    blue: f32,
    texture_ident: u32,
    unk20: f32, // always 0.0
    unk24: f32, // always 0.5
    unk28: f32, // always 0.5
    unk32: f32,
    cycle_ptr: u32,
}

bitflags MaterialFlags: u8 {
    Textured = 1 << 0, // 0x01
    Unknown = 1 << 1,  // 0x02
    Cycled = 1 << 2,   // 0x04
    Always = 1 << 4,   // 0x08
    Never = 1 << 5,    // 0x10
}

struct MaterialIndices {
    index1: i16,
    index2: i16,
}
```

First, read the material information. Then read the material indices. Repeat until count materials have been read.

A lot isn't known about the material information. It seems to be dump of an in-game structure, as it contains what seem to be pointers. Some fields are always set to the same value. The always flag is always set, the never flag is never set. The most important bit of information is the textured flag. This indicates whether the material has a texture or not.

#### Textured materials

Textured materials always have alpha set to 255/0xFF, since textures can include their own alpha data. The `rgb` field set to 32767/0x7FFF, and the red, green, and blue fields set to 255.0 (which is white). The unknown flag may or may not be set, and the `unk32` field is also indeterminate. This field could be specularity or some other material property.

Only textured materials can have the cycled flag set, which indicates that the material has multiple textures that are cycled through, creating an animated effect. Unlike mechlib materials, GameZ materials can be cycled. If this flag is set, the cycle pointer should be non-zero/non-null. If the flag is unset, the cycle pointer field is always zero (0)/null.

In short, for textured materials in the mechlib archive, the variable information is the `unk32` field, the unknown flag, the cycled flag/cycle pointer, and the `texture_ident` field. In the GameZ file, this holds the texture index on load, which is then replaced with a pointer to the texture. In the mechlib archive, this is the raw pointer value, since the texture name is written after the structure. For the GameZ case, the texture index must be less than the texture count.

Code that only wants to draw the materials can basically discard most of this information, except for if the material is textured, the texture index (via the `texture_ident` field), and if the material is cycled.

#### Coloured materials

Untextured or coloured materials always have the unknown flag and cycled flag unset. The `rgb` field is always zero (0/0x0000). This deserved a bit of discussion. Textures use a packed colour value format known as RGB565, and textured materials have their colour set to white. For textured materials, `rgb` is set to 0x7FFF, which corresponds to white in the RGB555 format. So I have assumed this field was intended to be used as a packed colour, but for some reason wasn't used. Both the material and cycle pointers are always zero (0)/null. The red, green, and blue fields indicate the colour of the material. In short, for coloured materials, the variable information is the red/green/blue fields, alpha, and `unk32` field.

#### Material indices

The expected indices can be calculated from the material index when reading. Say `index` is the value from 0 to count when reading the materials. The expected value for `index1` and `index2` are:

```rust
let mut expected_index1 = index + 1;
if expected_index1 >= count {
    expected_index1 = -1;
}
let mut expected_index2 = index - 1;
if expected_index2 < 0 {
    expected_index2 = -1;
}
```

So basically, `index1` is the next index, and `index2` is the previous. It seems like these are used for bookkeeping. Since they are so easy to calculate, discarding them is fine.

#### Zeroed-out materials

If there is a difference between the material count and the array size, then there will be array size - count zeroed-out material structures. This means all bytes/fields will be zero. You can basically loop from count to array size, and this is in fact advisable since the material indices will not be zeroed out. In fact, they will be the reverse of the filled in materials:

```rust
let mut expected_index1 = index - 1;
if expected_index1 < count {
    expected_index1 = -1;
}
let mut expected_index2 = index + 1;
if expected_index2 >= array_size {
    expected_index2 = -1;
}
```

This especially indicates these files are just dumps of in-engine data, if the (assumed) raw pointer values weren't enough evidence. It really does seem like this is just a dump of some internal array, since there is really no reason to write these zeroed-out structures (they contain no real information, so space could have been saved here).

#### Material cycle data

Finally, after the materials information, and zeroed-out materials, the material cycle data is read. This is basically in-order, so loop through all the previously read non-zeroed-out materials, and if they have the cycled flag set/cycled pointer non-null, read the cycle information:

```rust
struct CycleInfo {
    unk00: u32, // always 0 or 1 (boolean)
    unk04: u32,
    unk08: u32, // always 0
    unk12: f32, // always >= 2.0 and <= 16.0
    count1: u32,
    count2: u32, // always == count1
    data_ptr; u32, // always != 0
}
```

Not much is known about this structure, again it is probably used for keeping track of the material's cycle data. `unk00` is always zero (0) or one (1), so a Boolean. `unk04` is variable. `unk08` is always zero (0). `unk12` is a floating point value always greater or equal to 2.0, and less than or equal to 16.0. The two count values are always equal, and indicate the cycle length/number of textures in the cycle. Finally, the pointer is always non-zero, presumably this pointed to a block of memory that held the texture indices or pointers for the cycle, which are read next.

The important piece of information is the cycle count. Read this many u32 after the cycle information, which are the cycle's texture indices, basically:

```rust
struct CycleTextures {
    texture_index: [u32; count1],
}
```

Again, all of these values should be less than the total texture count. As far as I can see, the texture index (`texture_ident`) from the materials information isn't used for cycled textures, instead it's only these. 

### Meshes

In the gamez.zbd main header, the member meshes_offset gives the file offset to the main mesh header, which looks like this:

```rust
struct MeshesHeader {
    array_size: i32, // always >= 0, <= 0xFFFF
    count: i32, // always >= 0, <= array_size
    index_max: i32, // always == count
}
```

This is very similar to the materials header.  The fields are interdependent. The mesh array size indicates how big the mesh array for this world is expected to the in the worst case. Expect this to be zero (0) or greater, and less than 65535/0xFFFF. Next is the actual count of meshes in the file. Naturally, this must be zero (0) or greater, and less than the array size. Finally is the maximum index or next index, which is used to track which index to use for any further meshes. This will always be the same as the mesh count.

Meshes are read in three phases. The valid mesh headers or mesh information first, then zeroed-out mesh headers/information, and then mesh data.

#### Mesh information

In order to decode individual meshes, we need to locate the header for the mesh in question. If data is not read sequentially, use the following formula to find the offset for a mesh (C++):

meshHeaderOffset = MW3GameZHeader->meshes_offset + sizeof(MeshesHeader) + i * sizeof(MeshInfo);

The mesh information is a large structure:

```rust
struct MeshInfo {
    unk00: u32, // always 0 or 1 (bool)
    unk04: u32, // always 0 or 1 (bool)
    unk08: u32,
    parent_count: u32,  // 12, always > 0
    polygon_count: u32, // 16
    vertex_count: u32,  // 20
    normal_count: u32,  // 24
    morph_count: u32,   // 28
    light_count: u32,   // 32
    unk36: u32, // always 0
    unk40: f32,
    unk44: f32,
    unk48: u32, // always 0
    polygons_ptr: u32, // 52
    vertices_ptr: u32, // 56
    normals_ptr: u32,  // 60
    lights_ptr: u32,   // 64
    morphs_ptr: u32,   // 68
    unk72: f32,
    unk76: f32,
    unk80: f32,
    unk84: f32,
    unk88: u32, // always 0
    dataOffset: u32
} // 96 bytes

type MeshOffset = u32; // or i32
type MeshIndex = i32;
type MeshInfos = [MeshInfo + MeshOffset; count];
type ZeroInfos = [MeshInfo + MeshIndex; (array_size - count)];
```

The most important piece of information is the polygon count. If this is zero (0), then the vertex count, normal count, and morph count will all be zero (0). Note that the counts can also be zero if the polygon count is non-zero. You might expect the light count to also be zero, and this would make sense, but is not true in at least one case.

Pointers will be zero/null if the corresponding count is zero (0), and will be non-zero/non-null if the corresponding count is positive. The pointers may have been valid at the time the file was created, but they have no obvious use in a file on disk. It is possible to read the data structures into memory and adjust the pointers after loading, though.

The fields `unk00` and `unk04` will always be zero (0) or one (1), a Boolean. The parent count will always be greater than zero. The fields `unk36`, `unk48`, and `unk88` will always be zero (0). The other fields are unknown.

The mechlib archive has a similar data structure, which does not include the final member. dataOffset indicates the absolute offset of the mesh data in the GameZ file. Since the mesh data is written in order, the mesh data offset must be greater than the last (or for the first, after all the mesh information and zeroed-out mesh information), and less than the next block (the nodes).

As an aside, internally this is probably used as the next mesh index, just like the materials did.

#### Zeroed-out mesh information

If there is a difference between the meshes count and the array size, then there will be array size - count zeroed-out mesh information structures. This means all bytes/fields will be zero. You can basically loop from count to array size, and this is in fact advisable since in this case, the mesh data offset is instead the mesh index. The mesh index wants to be loaded as an i32, not a u32 as might be more useful for the mesh data offset: 

```rust
let mut expected_index: i32 = index + 1;
if expected_index >= array_size {
    expected_index = -1;
}
```

#### Mesh data

Next, the mesh data is read for any filled in mesh information (not zeroed-out). The start offset for the mesh data can be determined from MeshInfo.dataOffset or by simply reading the file sequentially without seeking.

Reading the mesh data is dynamic, based on the counts:

* Read vertex count vertices (where each is a vector of three f32)
* Read normal count normals (where each is a vector of three f32)
* Read morph count morphs(?) (where each is a vector of three f32)
* Read the lights (each light seems to take 80 bytes)
* Read the polygons

```rust
struct Vec3 {
    x: f32,
    y: f32,
    z: f32,
}

struct Vertices {
    vertices: [Vec3; vertex_count],
}

struct Normals {
    normals: [Vec3; normal_count],
}

struct Morphs {
    morphs: [Vec3; morph_count],
}
```

##### Light information and data

The light information is largely unexplored and read in two phases. First, light count light information structures are read:

```rust
struct LightInfo {
    unk00: u32,
    unk04: u32,
    unk08: u32,
    extra_count: u32,
    unk16: u32,
    unk20: u32,
    unk24: u32,
    unk28: f32,
    unk32: f32,
    unk36: f32,
    unk40: f32,
    ptr: u32,
    unk48: f32,
    unk52: f32,
    unk56: f32,
    unk60: f32,
    unk64: f32,
    unk68: f32,
    unk72: f32,
    unk76: u32
} // 80 bytes in total

// probably good to combine lights + extras
// in real code
struct Lights {
    lights: [LightInfo; light_count],
    // pseudo-code: extra_count is variable!
    extras: [[Vec3; extra_count]; light_count],
}
```

The important field here is at offset 12, which is a u32 or i32 and indicates how much extra data to read. This data is read after all the light information. In this case, loop over the light information, and read extra count vertices (where each is a vector of the f32).

More research is needed on what the lights do.

##### Polygon information and data

```rust
struct PolygonInfo {
    vertex_info: u32, // always <= 0x3FF
    unk04: u32, // always >= 0, <= 20
    vertices_ptr: u32, // always != 0
    normals_ptr: u32,
    uvs_ptr: u32,
    colors_ptr: u32, // always != 0
    unk_ptr: u32, // always != 0
    material_index: u32,
    material_info: u32,
} // 36 bytes

type PolygonInfos = [PolygonInfo; polygon_count];
```

The vertex info field is a compound field, and could also be read as u8 values. The lower byte can be masked via `vertex_info & 0xFF`, and provides the number of vertices in the polygon. This must be greater than zero (0), since every polygon must have at least one vertex, and therefore the vertices pointer, colours pointer, and an unknown pointer are also non-zero/non-null.

There are additionally two flags, an unknown flag masked with `(vertex_info & 0x100) != 0` and the normals flag masked with `(vertex_info & 0x200) != 0`. The use of the unknown flag is predictably unknown. The normals flag indicates whether the polygon has normals. Additionally, whether the polygon has UVs is determined by whether the UV pointer is non-zero/non-null. It's unclear why the normals pointer doesn't do this and a flag was used.

The material index indicates which material the polygon uses. The material info is currently unknown. 

After all the polygon information has been read, the polygon data is read.

The data is based on the number of vertices in the polygon (vertex count). For each polygon:

* The vertex indices are always read, which are u32 that index the mesh's vertices. Read vertex count of these.
* The normal indices are only read if the flag is set, and are u32 that index the mesh's normals. Read vertex count of these.
* The UV data is only read if the UV pointer is non-zero/non-null. Each UV is two f32 (u, v). To use these, we had to subtract the v value from 1.0, so `v = 1.0 - v`. Read vertex count UVs.
* The vertex colours are always read. Each colour is three f32 (r, g, b), the same structure as `Vec3`. Read vertex count colours.

With this information and the mesh information, the polygons can be reconstructed.

### Nodes

Finally, the nodes block. If you thought the previous information was complex to read, the nodes turn this to eleven.

Because the node data is very complicated, I describe [all nodes](nodes.md) separately. Please refer to that document for detailed information. I will however go over how to read the data here.

In principle, this works a lot like the other blocks. The node count and node array size was given by the GameZ header. The nodes are also read in a phased manner, and also have zeroed-out nodes. If data is not read sequentially, node i can be found at the offset

nodeOffset = MW3GameZHeader->nodesOffset + i * sizeof(MW3GameZNodeHeader)

Unfortunately, to me it seems the node count is wildly inaccurate for some files. Since this seems like a memory dump, it's possible that only node count nodes should actually be read. But the nodes between count and the array size may not be zeroed out. So I resorted to reading all the node base structures until I found a zeroed out one, and then stopped. That allowed me to get the actual count.

#### Node base structures

Because the node count is inaccurate, a strategy is needed. Either look for the first zeroed-out nodes while reading the base structures and break out of the loop (all further nodes will be zeroed-out), or read all of them and e.g. ignore the zeroed out nodes when reading node data. To detect zeroed out nodes, a good indication is if the first byte of the name is zero (0).

In both cases, read array size node base structures.

Next, read a u32 value. For empty node types, this is the parent index (!). For other node types, this is the offset of their type-specific data in the file. For zeroed-out nodes, this is:

```rust
let mut expected_index = index + 1;
if expected_index >= array_size {
    // we'll never know why???
    expected_index = 0xFFFFFF;
}
```

And indeed, it's unclear why this isn't 0xFFFFFFFF (-1 for i32), or even 0xFFFF (-1 for i16). But that's what it is.

Optionally assert the node index rules for GameZ files:

* There can only be a single world node, and it must be the first node in the file (index 0)
* There can only be a single window node, and it must be the second node in the file (index 1)
* There can only be a single camera node, and it must be the third node in the file (index 2)
* There is at least one display node, and it must be the fourth node in the file (index 3). If there is another display node, it must be the fifth node in the file (index 4)
* There can only be a single light node, although its position in the file is variable
* Zeroed out nodes must be at the end of the array, and contiguous.

#### Zeroed-out nodes

Zeroed-out nodes will be all zero, except for the mesh index, which will be negative one (-1).

#### Node type-specific data

Then, read the type-specific data. Empty nodes do not have node data, and zeroed-out nodes don't either. Otherwise; the data is read in the same order as the base structure, based on the node type.

If a node had a non-zero parent count and/or child count on the node base structure, then these indices are read after the node's data. In the base game, these are the only nodes that have non-zero counts:

* LOD: Always one parent, always multiple children
* Object3d: Zero or one parent, sometimes children
* World: No parent, always children

But the logic could be generic simply based on the count. After the type data, the parent indices (u32) are read first, then the child indices (u32). Then the next node's type data follows.

#### Node relationships

As a final step, you can transform the linearly arranged nodes into a graph/tree structure.

## Investigation (PM)

The data structures differ slightly for MW3:PM. For the main header, there is an unknown, 32-bit integer between the members version and textureCount. 

```rust
struct PMMeshInfo {
    unk00: u32, // always 0 or 1 (bool)
    unk04: u32, // always 0 or 1 (bool)
    unk08: u32,
    parent_count: u32,  // 12, always > 0
    polygon_count: u32, // 16
    vertex_count: u32,  // 20
    normal_count: u32,  // 24
    morph_count: u32,   // 28
    light_count: u32,   // 32
    unk36: u32, // always 0
    unk40: f32,
    unk44: f32,
    unk48: u32, // always 0
    polygons_ptr: u32, // 52
    vertices_ptr: u32, // 56
    normals_ptr: u32,  // 60
    lights_ptr: u32,   // 64
    morphs_ptr: u32,   // 68
    unk72: f32,
    unk76: f32,
    unk80: f32,
    unk84: f32,
    unk88: u32,
    unk92: u32,
    unk96: u32,
    dataOffset: u32
} // 104 bytes
```

```rust
struct PMPolygonInfo {
    vertex_info: u32, // always <= 0x3FF
    polygonMode: u8, // always >= 0, <= 20
    flags2: u8,
    flags3: u8,
    zero: u8,
    vertices_ptr: u32, // always != 0
    uvs_ptr: u32,
    normals_ptr: u32,
    colors_ptr: u32, // always != 0
    unk_ptr: u32, // always != 0
    material_index: u32,
    material_info: u32,
    flags4: u32,
} // 40 bytes
```

The important addition here is polygonMode. If polygonMode equals 0x30, we are not dealing with a single polygon, but a triangle strip instead. A triangle strip is read like a polygon, but instead of creating a polygon of vertex_info vertices, (vertex_info-2) triangles are created instead. After reading one triangle, advance the pointer to the vertex indices by 4 bytes. After reading all data for one triangle strip, the vertex index has to be increased by an additional 8 to account for the last two vertices in the triangle strip.

## In-game use

These models are used in-game and in the mechlab screen.
