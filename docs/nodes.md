# Nodes

Nodes are how the world data is organised and structured. Nodes appear in GameZ files and mechlib archives. There are eight known node types in GameZ files:

* Camera
* Display
* Empty
* Light
* LOD (level of detail)
* Object3d
* Window
* World

The only valid node type in the mechlib archive is Object3d. We also think there are other node types from the animations:

* Sequence
* Animate or Animation
* Sound
* Switch (i.e. flow control)

Each node type has the same base structure, although some node types do not seem to use all the information in the base structure. The node types also have node-specific structures/information.

## Node organisation/relationships

Each node can have several parents, and several children. In fact, each node tracks both the children and the parents, and there doesn't seem to be a way of ensuring this data is consistent other than careful coding (e.g. when a child is removed, also remove it's reference to the parent).

In principle, this results in a directed graph structure. Cycles are also absolutely possible. Again this was presumably carefully avoided because a cyclic graph is not useful for most processing. Let's assume therefore that a valid representation of nodes inside the engine is a directed acyclic graph (DAG) at the very least.

In reality, the nodes are usually tree-like, although in a "tree" in the computer science sense, there can only be one root, and each node has exactly one parent. From what I can see, this isn't necessarily the case for MW3. Otherwise, why allow a node to have multiple parents?

However, when loading nodes from the mechlib or GameZ files, the nodes indeed only have either zero (0) or one (1) parent (at load time). We'll discuss further restrictions on the different node types shortly.

## Common data types

```rust
tuple Vec3(f32, f32, f32);
tuple Color(f32, f32, f32);
tuple Matrix(f32, f32, f32, f32, f32, f32, f32, f32, f32);

const MATRIX_EMPTY: Matrix = Matrix(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
const MATRIX_IDENTITY: Matrix = Matrix(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0);
```

## Node base/shared structure

This is the structure used by all nodes:

```rust
struct Node {
    name: [u8; 36],
    flags: NodeFlags,
    unk040: u32, // always 0
    unk044: u32,
    zone_id: u32,
    node_type: NodeType,
    data_ptr: u32,
    mesh_index: i32,
    environment_data: u32, // always 0
    action_priority: u32, // always 1
    action_callback: u32, // always 0
    area_partition_x: i32, // -1, or >= 0, <= 64
    area_partition_y: i32, // -1, or >= 0, <= 64
    parent_count: u32, // always 0 or 1
    parent_array_ptr: u32,
    children_count: u32,
    children_array_ptr: u32,
    unk100: u32, // always 0
    unk104: u32, // always 0
    unk108: u32, // always 0
    unk112: u32, // always 0
    unk116: Box3d,
    unk140: Box3d,
    unk164: Box3d,
    unk188: u32, // always 0
    unk192: u32, // always 0
    unk196: u32,
    unk200: u32, // always 0
    unk204: u32, // always 0
    unk208: u32,
} // 212 bytes

tuple Box3d(f32, f32, f32, f32, f32, f32);

enum NodeType: u32 {
    Empty = 0,
    Camera = 1,
    World = 2,
    Window = 3,
    Display = 4,
    Object3d = 5,
    Lod = 6,
    // Sequence = 7,
    // Animate = 8,
    Light = 9,
    // Sound = 10,
    // Switch = 11,
}

bitflags NodeFlags: u32 {
    // Unk00 = 1 << 0,
    // Unk01 = 1 << 1,
    Active = 1 << 2,
    AltitudeSurface = 1 << 3,
    IntersectSurface = 1 << 4,
    IntersectBbox = 1 << 5,
    // Proximity = 1 << 6,
    Landmark = 1 << 7,
    Unk08 = 1 << 8,
    HasMesh = 1 << 9,
    Unk10 = 1 << 10,
    // Unk11 = 1 << 11,
    // Unk12 = 1 << 12,
    // Unk13 = 1 << 13,
    // Unk14 = 1 << 14,
    Terrain = 1 << 15,
    CanModify = 1 << 16,
    ClipTo = 1 << 17,
    // Unk18 = 1 << 18,
    TreeValid = 1 << 19,
    // Unk20 = 1 << 20,
    // Unk21 = 1 << 21,
    // Unk22 = 1 << 22,
    // Override = 1 << 23,
    IdZoneCheck = 1 << 24,
    Unk25 = 1 << 25,
    // Unk26 = 1 << 26,
    // Unk27 = 1 << 27,
    Unk28 = 1 << 28,
    // Unk29 = 1 << 29,
    // Unk30 = 1 << 30,
    // Unk31 = 1 << 31,

    Base = Active | TreeValid | IdZoneCheck,
    Default = Base | AltitudeSurface | IntersectSurface,
}

const DEFAULT_ZONE_ID: u32 = 255;
```

I'm pretty sure the name is 36 bytes long, not the usual 32 bytes and another field. Assume ASCII. The "padding" for the name is also odd. It seems like all nodes are initialised with the name to `Default_node_name` (padded with zeros/nulls to 36 bytes). Then, when the name is filled in, it is overwritten with the node name (zero/null terminated). This is likely not important when only reading the data, but is important when trying to write a binary-accurate replica.

Many flags are unknown in their functionality. Which flags are valid for a node also depends on the node type, and are described further in the sub-sections. The following information is invariant, i.e. does not depend on the node type.

The fields `unk040`, `unk100`, `unk104`, `unk108`, `unk112`, `unk188`, `unk192`, `unk200`, and `unk204` are always zero (0).

The field `environment_data` is always zero (0). The field `action_callback` is always zero (0)/null (this is possibly a pointer). The field `action_priority` is always one (1).

The area partition values are tied to the world structure. These must either be both negative one (-1), which indicates no area partition is assigned to the node. Alternatively, both values must be greater than or equal to zero (0) and less than or equal to 64 (this upper bound is arbitrarily chosen based on usual area partition sizes), which indicates an area partition is assigned to the node. Once the world node data is loaded, these can be properly validated. Some node types can have stricter validation on this.

During loading, the parent count is always zero (0) or one (1). Some node types can have stricter validation on this. If the parent count is zero, then the parent array pointer is zero/null, otherwise it is non-zero/non-null. The child count is usually less than or equal to 64 (this upper bound is arbitrarily chosen based on usual child counts). Some node types can have stricter validation on this. If the child count is zero, then the child array pointer is zero/null, otherwise it is non-zero/non-null.

We currently think the fields `unk116`, `unk140`, and `unk164` are values of six floating point numbers that specify a box in three dimensions. They are likely some kind of bounding boxes.

Therefore, for any node in a GameZ file, after filtering the invariant data, the variable data is the name, the flags, `unk044`, the zone ID, the data pointer, the mesh index, the area partition values, the parent count (i.e. whether the node has a parent) and the parent array pointer, the child count and the child array pointer, `unk116`, `unk140`, `unk164`, and `unk196`.

### Camera nodes base structure

Since there can only be one camera node, the node name is always `camera1`. The flags will always be the default node flags. The field `unk044` will always be zero (0). The zone ID will always be the default zone ID (255). Camera nodes always have data associated with them, so the data pointer will always be non-zero/non-null. The mesh index will always be negative one (-1). The area partition will always be unassigned (-1, -1). There will be no parents, and therefore the parent array pointer is zero/null. There will be no children, and therefore the child array pointer is zero/null. The fields `unk116`, `unk140`, and `unk164` will always be zeros (0.0). The field `unk196` will always be zero (0).

Therefore, the variable data is the data pointer.

### Display nodes base structure

There can be one or two display nodes, which always have the name `display`. The flags will always be the default node flags. The field `unk044` will always be zero (0). The zone ID will always be the default zone ID (255). Display nodes always have data associated with them, so the data pointer will always be non-zero/non-null. The mesh index will always be negative one (-1). The area partition will always be unassigned (-1, -1). There will be no parents, and therefore the parent array pointer is zero/null. There will be no children, and therefore the child array pointer is zero/null. The fields `unk116`, `unk140`, and `unk164` will always be zeros (0.0). The field `unk196` will always be zero (0).

Therefore, the variable data is the data pointer.

### Empty nodes base structure

The field `unk044` will be 1, 3, 5, or 7. The zone ID will be either one (1) or the default zone ID (255). Empty nodes don't have data associated with them, so the data pointer will always be zero/null. The mesh index will always be negative one (-1). The area partition will always be unassigned (-1, -1). There will be no parents, and therefore the parent array pointer is zero/null. There will be no children, and therefore the child array pointer is zero/null. The field `unk196` will always be zero (0).

Therefore, the variable data is the name, flags, `unk044`, the zone ID, `unk116`, `unk140`, and `unk164`. Additionally, empty nodes do have a parent index, but when using a GameZ and mechlib-compatible base structure, this is stored outside the base structure. This will be discussed during loading in more detail, but it might be useful to include a field for this here.

### Light nodes base structure

Since there is only one light node, the node name is always `sunlight`. The flags will always be the default node flags and Unk08 (0x100). The field `unk044` will always be zero (0). The zone ID will always be the default zone ID (255). Light nodes always have data associated with them, so the data pointer will always be non-zero/non-null. The mesh index will always be negative one (-1). The area partition will always be unassigned (-1, -1). There will be no parents, and therefore the parent array pointer is zero/null. There will be no children, and therefore the child array pointer is zero/null. The field `unk116` will always have the values `(1.0, 1.0, -2.0, 2.0, 2.0, -1.0)`. The fields `unk140` and `unk164` will always be zeros (0.0). The field `unk196` will always be zero (0).

Therefore, the variable data is the data pointer.

### LOD nodes base structure

The field `unk044` will always be one (1). The zone ID will be either the default zone ID (255), or a value greater than or equal to one (1) and less than or equal to 80 (this upper bound is arbitrarily chosen based on usual zone IDs). LOD nodes always have data associated with them, so the data pointer will always be non-zero/non-null. The mesh index will always be negative one (-1). There will be one parent, and therefore the parent array pointer is non-zero/non-null. There will be at last one child, and therefore the child array pointer is non-zero/non-null. The field `unk116` will be unequal to `(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)`, and the field `unk164` will be equal to `unk116`. The field `unk140` will always be zeros (0.0). The field `unk196` will always be 160.

Therefore, the variable data is the name, flags, the zone ID, the data pointer, the area partition values, the parent array pointer, the child count, the child array pointer, and `unk116`. 

### Object3d nodes base structure

The field `unk044` will always be one (1). The zone ID will be either the default zone ID (255), or a value greater than or equal to one (1) and less than or equal to 80 (this upper bound is arbitrarily chosen based on usual zone IDs). Object3d nodes always have data associated with them, so the data pointer will always be non-zero/non-null.

The mesh index depends on the HasMesh flag, and whether the node is in a GameZ file or a mechlib archive. For a GameZ file, the mesh index is an index. So if the flag is set, then the index is greater than or equal to zero (0). If the flag is unset, then the index is always negative one (-1). For a mechlib archive, the mesh index is actually a pointer value, since the data is already stored hierarchically. So if the flag is set, this is non-zero/non-null. If the flag is unset, this is zero/null. Note that for the non-null case, if you are loading the value as a signed integer (i32), the memory on 32-bit machines was limited. In practice, it won't be greater than 2147483647 bytes, so you can also check if the value is greater than zero.

The field `unk196` will always be 160.

Therefore, the variable data is the name, flags, the zone ID, the data pointer, the area partition values, the parent count, the parent array pointer, the child count, the child array pointer, `unk116`, `unk140`, and `unk164`.

### Window nodes base structure

Since there can only be one window node, the node name is always `window1`. The flags will always be the default node flags. The field `unk044` will always be zero (0). The zone ID will always be the default zone ID (255). Window nodes always have data associated with them, so the data pointer will always be non-zero/non-null. The mesh index will always be negative one (-1). The area partition will always be unassigned (-1, -1). There will be no parents, and therefore the parent array pointer is zero/null. There will be no children, and therefore the child array pointer is zero/null. The fields `unk116`, `unk140`, and `unk164` will always be zeros (0.0). The field `unk196` will always be zero (0).

Therefore, the variable data is the data pointer.

### World nodes base structure

Since there can only be one world node, the node name is always `world1`. The flags will always be the default node flags. The field `unk044` will always be zero (0). The zone ID will always be the default zone ID (255). World nodes always have data associated with them, so the data pointer will always be non-zero/non-null. The mesh index will always be negative one (-1). The area partition will always be unassigned (-1, -1). There will be no parents, and therefore the parent array pointer is zero/null. There will be at last one child, and therefore the child array pointer is non-zero/non-null. The fields `unk116`, `unk140`, and `unk164` will always be zeros (0.0). The field `unk196` will always be zero (0).

Therefore, the variable data is the data pointer, the child count, and the child array pointer.

## Node type data structures

All nodes except empty nodes have extra, type-specific data associated with them.

### Camera data

```rust
struct Camera {
    world_index: i32, // always 0
    window_index: i32, // always 1
    focus_node_xy: i32, // always -1
    focus_node_xz: i32, // always -1
    flags: u32, // always 0
    translation: Vec3, // always 0.0
    rotation: Vec3, // always 0.0
    world_translate: Vec3, // always 0.0
    world_rotate: Vec3, // always 0.0
    mtw_matrix: Matrix, // always 0.0
    unk104: Vec3, // always 0.0
    view_vector: Vec3, // always 0.0
    matrix: Matrix, // always 0.0
    alt_translate: Vec3, // always 0.0
    clip_near_z: f32
    clip_far_z: f32,
    zero184: [u8; 24], // always 0
    lod_multiplier: f32, // always 1.0
    lod_inv_sq: f32, // always 1.0
    fov_h_zoom_factor: f32, // always 1.0
    fov_v_zoom_factor: f32, // always 1.0
    fov_h_base: f32,
    fov_v_base: f32,
    fov_h: f32,
    fov_v: f32,
    fov_h_half: f32,
    fov_v_half: f32,
    unk248: u32, // always 1
    zero252: [u8; 60], // always 0
    unk312: u32, // always 1
    zero316: [u8; 72], // always 0
    unk388: u32, // always 1
    zero392: [u8; 72], // always 0
    unk464: u32, // always 0
    fov_h_cot: f32,
    fov_v_cot: f32,
    stride: i32, // always 0
    zone_set: i32, // always 0
    unk484: i32, // always -256
}
```

The size of the camera structure is 488 bytes. This is large, but considering there is only one camera, it probably made sense to trade a bit of memory for storing intermediate results to speed up computation.

We understand a lot of the camera structure, although most of the information when loaded from a file is zeroed out, and is then initialised after loading (possibly by the interpreter).

The important fields are the near Z (f32) and far Z (f32) clipping values at offset 176, and the horizontal (f32) and vertical (f32) field of view values (FoV) at offset 232. The clipping near Z must be greater than 0.0, and the far Z must be greater than the near Z.

Many of the other FoV-related values are directly derived from the FoV. The FoV base values are equal to the FoV, because the zoom factor is one (1.0). The FoV half values are equal to the FoV divided by two (2.0). And the FoV cotangent values are derived from the cotangent of the FoV half values.

Therefore, for loading a level, the clipping and FoV values are the only important parts.

### Display data

```rust
const CLEAR_COLOR: Color = Color(
    0.3919999897480011,
    0.3919999897480011,
    1.0
);

struct Display {
    origin_x: u32, // always 0
    origin_y: u32, // always 0
    resolution_x: u32, // always 640
    resolution_y: u32, // always 400
    clear_color: Color, // always CLEAR_COLOR
}
```

The size of the display structure is 28 bytes.

The display data is completely constant when loading. The origin x and y values (u32 or i32) are always zero (0). The resolution x and y values (u32 or i32) are always 640 and 400, respectively. The clear colour is always 0.3919999897480011, 0.3919999897480011, and 1.0, which is a blue-ish colour (#6464ff). 

### Empty data

Empty nodes do not have data.

### Light data

```rust
struct Light {
    direction: Vec3,
    translation: Vec3, // always 0.0
    zero024: [u8; 112], // always 0
    unk136: f32, // always 1.0
    unk140: f32, // always 0.0
    unk144: f32, // always 0.0
    unk148: f32, // always 0.0
    unk152: f32, // always 0.0
    diffuse: f32, // always >= 0.0, <= 1.0
    ambient: f32, // always >= 0.0, <= 1.0
    color: Color, // always 1.0
    flags: LightFlags, // always Default
    range_near: f32, // always > 0.0
    range_far: f32,
    range_near_sq: f32,
    range_far_sq: f32,
    range_inv: f32,
    unk200: u32, // always 1
    unk204: u32, // always != 0
    // Possibly not part of the light structure
    unk208: u32, // always 0
}

// Also used for light state events in Anim
bitflags LightFlags: u32 {
    Inactive = 0;
    TranslationAbs = 1 << 0;
    Translation = 1 << 1;
    Rotation = 1 << 2;
    Range = 1 << 3;
    Color = 1 << 4;
    Ambient = 1 << 5;
    Diffuse = 1 << 6;
    Directional = 1 << 7;
    Saturated = 1 << 8;
    Subdivide = 1 << 9;
    Static = 1 << 10;
    
    Default = TranslationAbs
    | Translation
    | Range
    | Directional
    | Saturated
    | Subdivide;
}
```

The size of the light structure either 208 bytes, or 212 bytes (more on this shortly).

What's known about the light structure comes a lot from the animations. There is a vast block of the structure at offset 24 with a length of 112 bytes that is completely unknown and zeroed out.

The direction (Vec3) of the light is given. The translation (Vec3) is always zero (0.0). The diffuseness of the light (f32) is greater or equal to zero (0.0) and less than or equal to one (1.0). The ambient value (f32) is greater or equal to zero (0.0) and less than or equal to one (1.0). It isn't quite clear what this does, since the only colour in the structure is white (1.0, 1.0, 1.0). The flags indicate which members of the structure are valid, although it is always set to the default alias (TranslationAbs, Translation, Range, Directional, Saturated, and Subdivide). The near range (f32) is always greater than zero (0.0), while the far range (f32) is always greater than the near range. The squared range values are simply that, the near and far range values squared. The inverse range value is one over the range difference or delta (far minus near), so `1.0 / (range_far - range_near)`.

I've been told the last three fields are something to do with the light's parent. The current theory is that it is a dynamic array. The `unk200` field is a count, and `unk204` is an array of size count with node indices or pointers. That would make `unk208` a dump of the array, and variable/not part of the light structure. If this is the case, then the light structure is 208 bytes in size. If the count is zero (0) - which it never is - then presumably the pointer would be zero/null, otherwise the pointer would be non-zero/non-null (which we do see). And then after the light structure is read, count u32 or i32 values would be read (but since count is always 1, it's only one value), which then indicates the indices of the parents. Since this is always zero (0), the light is parented to the world. This seems nuts; it isn't clear why lights don't use the default parent fields on the node base structure. It doesn't matter for MW3, but might be useful for PM. We'll also see similar indications of dynamic arrays in other structures (e.g. the world data).

### LOD data

```rust
struct Lod {
    level: u32, // always 0 or 1
    range_near_sq: f32,
    range_far: f32,
    range_far_sq: f32,
    zero16: [u8; 44], // always 0
    unk60: f32,
    unk64: f32,
    unk68: u32, // always 1
    unk72: u32, // always 0 or 1 (bool)
    unk76: u32,
}
```

The size of the LOD structure is 80 bytes.

The level field (u32) is always zero (0) or one (1). Usually, this would make it a Boolean, but I think it corresponds to the level of detail setting, so e.g. low and high (hence the name). The near range value (f32) is always greater than or equal to zero (0.0) and less than or equal to 1000.0 squared, so it's assumed this is the near range squared. The far range value is stored as the base value (f32), which is always greater than zero (0.0), and why I suspect this is the far range, and as a squared value (f32). These are guesses at best.

The `unk60` field (f32) is greater than or equal to zero (0.0), while the `unk64` field (f32) is this value squared. The `unk68` field (u32) is always one (1). The `unk72` field (u32) is either zero (0) or one (0), a Boolean. If `unk72` is zero/false, then the `unk76` field (u32) is also zero (0). If `unk72` is one/true, then the `unk76` field is non-zero/non-null, which makes it likely a pointer.

### Object3d data

```rust
struct Object3d {
    flags: Object3dFlags,
    opacity: f32, // always 0.0
    unk008: f32, // always 0.0
    unk012: f32, // always 0.0
    unk016: f32, // always 0.0
    unk020: f32, // always 0.0
    rotation: Vec3,
    scale: Vec3, // always 1.0
    rot_matrix: Matrix,
    translation: Vec3,
    zero096: [u8; 48], // always 0
}

bitflags Object3dFlags: u32 {
    HasOpacity = 1 << 2, // 0x02
    NoCoordinates = 1 << 3, // 0x08
    Unk20 = 1 << 5, // 0x20
}
```

The size of the Object3d structure is 144 bytes. This is a surprisingly large overhead, because there are many objects in a game world. It's also unclear why Euler angles and a matrix were used instead of Quaternions (which the motions use).

The flags (u32) are basically unknown. Only two values occur, 32 or 40. So an unknown flag (Unk20, 0x20) is always set, and then a flag I've named "NoCoordinates" (0x08) can either be set or unset. From some of the animation work and testing, it seems like there is a flag for if the object has opacity (0x02). Since this is always unset in GameZ files and mechlib archives, opacity (f32) is always zero (0.0), otherwise we can probably expect opacity to be greater or equal to zero (0.0) and less than or equal to one (1.0). There are four fields that are always zero (0.0), we don't even strictly know if they are floating point (f32) because of this.

Next follows the rotation (Vec3), presumably the scale (Vec3) which is always one (1.0), a matrix (Matrix, 3x3), and the translation (Vec3). If the no coordinates flag is set, then the rotation and translation will be zeros (0.0), and the matrix will be the identity matrix (`MATRIX_IDENTITY`). If the no coordinates flag is unset, then the rotation components will each be greater than or equal to negative Pi and less than or equal to positive Pi, and the translation while unspecified should be used. In most cases, the matrix can be calculated from the rotation, which is the x, y, z Euler angles:

```rust
fn euler_to_matrix(rotation: &Vec3) -> Matrix {
    let x = -rotation.0;
    let y = -rotation.1;
    let z = -rotation.2;

    let (sin_x, cos_x) = x.sin_cos();
    let (sin_y, cos_y) = y.sin_cos();
    let (sin_z, cos_z) = z.sin_cos();

    // optimized m(z) * m(y) * m(x)
    Matrix(
        cos_y * cos_z,
        sin_x * sin_y * cos_z - cos_x * sin_z,
        cos_x * sin_y * cos_z + sin_x * sin_z,
        cos_y * sin_z,
        sin_x * sin_y * sin_z + cos_x * cos_z,
        cos_x * sin_y * sin_z - sin_x * cos_z,
        -sin_y,
        sin_x * cos_y,
        cos_x * cos_y,
    )
}
```

In 2% of all Object3d nodes, this calculation is slightly off. This seems like either a bug or inaccuracy in the written data.

An additional trap for bit-perfect `gamez.zbd` writing is that negative zero (-0.0) and positive zero (+0.0) floating point values have different bit patterns per IEEE 754. And -0.0 is equal to 0.0. So for bit-perfect round-tripping, it is necessary to preserve the zero signs, even in the case where the no coordinates flag is set.

### Window data

```rust
struct Window {
    origin_x: u32, // always 0
    origin_y: u32, // always 0
    resolution_x: u32, // always 320
    resolution_y: u32, // always 200
    zero016: [u8; 212], // always 0
    buffer_index: i32, // always -1
    buffer_ptr: u32, // always 0
    unk236: u32, // always 0
    unk240: u32, // always 0
    unk244: u32, // always 0
}
```

The size of the Window structure is 248 bytes.

The origin x (u32) and y (u32) are always set to zero (0). The resolution x (u32) and y (u32) are always set to 320 and 200, respectively. Observant readers will note this is half the default display node resolution. Most of the rest of the structure from offset 16 with a length of 212 bytes is zero. The next non-zero value is at offset 228, which is what we think is the buffer index (i32), and is always negative one (-1). The next field is the buffer pointer, and this is always zero/null. Finally, the next three values (e.g. u32) are all zero (0).

### World data

```rust
struct World {
    unk000: u32, // always 0
    area_partition_used: u32, // always 0
    area_partition_count: u32,
    area_partition_ptr: u32,
    fog_state: u32, // always 1
    fog_color: Color, // always 0.0
    fog_range_near: f32, // always 0.0
    fog_range_far: f32, // always 0.0
    fog_altitude_high: f32, // always 0.0
    fog_altitude_low: f32, // always 0.0
    fog_density: f32, // always 0.0
    area_left: f32,
    area_bottom: f32,
    area_width: f32,
    area_height: f32,
    area_right: f32,
    area_top: f32,
    unk076: u32, // always 16
    virtual_partition: u32, // always 1
    virt_partition_x_min: u32, // always 1
    virt_partition_y_min: u32, // always 1
    virt_partition_x_max: u32,
    virt_partition_y_max: u32,
    virt_partition_x_size: f32, // always +256.0
    virt_partition_y_size: f32, // always -256.0
    virt_partition_x_half: f32, // always +128.0
    virt_partition_y_half: f32, // always -128.0
    virt_partition_x_inv: f32, // always 1.0 / +256.0
    virt_partition_y_inv: f32, // always 1.0 / -256.0
    virt_partition_diag: f32, // always -192.0
    partition_inclusion_tol_low: f32, // always 3.0
    partition_inclusion_tol_high: f32, // always 3.0
    virt_partition_x_count: u32,
    virt_partition_y_count: u32,
    virt_partition_ptr: u32,
    unk148: f32, // always 1.0
    unk152: f32, // always 1.0
    unk156: f32, // always 1.0
    unk160: u32, // always 1
    unk164: u32, // always != 0
    unk168: u32, // always != 0
    unk172: u32, // always 0
    unk176: u32, // always 0
    unk180: u32, // always 0
    unk184: u32, // always 0
    unk188: u32,
}
```

The size of the World structure is 188 or 192 bytes.

#### World structure

The first field `unk000` (u32) is always zero (0).

The area partition information is partially derived from later fields. At load time, the used count (u32) is always zero (0). The count (u32) can be validated later, from the virtual partition information. The pointer (u32) is always non-zero/non-null.

The fog state (u32) is always one (1), which corresponds to a linear fog. Exponential fog is two (2), but is never set. The fog colour is always zero/black (0.0, 0.0, 0.0). The fog near and far range values (f32) and the fog altitude high and low values (f32) are always zero (0.0), as well as the fog density (f32). This can be set by the interpreter when loading the world, or by the corresponding `anim.zbd`.

The area values describe the area of the game world. Although these are floating point numbers, they are truncated, and can be converted to integers. The right coordinate must be larger than the left coordinate, and the bottom coordinate must be larger than the top. The width and height can be calculated from the right/left and top/bottom values, respectively.

The field `unk076` (u32) is always 16.

The virtual partition information is fairly regular. It's not clear why this is called "virtual partition", except that the interpreter has a commands. For example, `WorldSetVirtualPartition on`, which is why the virtual partition field (u32) is always one (1). The minimum x and y values (u32) are always one (1). The maximum x and y values (u32) give the partition size. The x size (f32) is always 256.0, and the y size (f32) is always -256.0. The half x size (f32) is predictably 128.0, and the half y size is -128.0. The inverse x size (f32) is 1.0 / 256.0, and the inverse y size (f32) is 1.0 / -256.0. The partition diagonal half size is always -192.0. It's a bit of an odd calculation: likely the square root of the x and y size divided by two (2.0), or alternatively times 0.5. But if the x and y size are actually used, it comes out as -181.0. As far as I can see, this is a result of a poor square root approximation that a is well-known bit hack. For example, I have found it referenced in a paper named "A benchmark for C program verification" ([arXiv:1904.01009v1](https://arxiv.org/pdf/1904.01009.pdf)), or in a thread from 2014 titled "Floating Point Hacks" on the [dark bit factory](http://www.dbfinteractive.com/forum/index.php?topic=6269.0) forums. Here is a reproduction of the paper's C code:

```C
float
sqrt_approx(float x)
{
    union { float x; unsigned i; } u;
    u.x = x;
    u.i = (u.i >> 1) + 0x1fc00000;
    return u.x;
}
```

Translated to Rust:

```rust
fn approx_sqrt(value: f32) -> f32 {
    let cast = i32::from_ne_bytes(value.to_ne_bytes());
    let approx = (cast >> 1) + 0x1FC00000;
    f32::from_ne_bytes(approx.to_ne_bytes())
}

fn main() {
    let x_size = 256.0f32;
    let y_size = -256.0f32;
    let size = x_size * x_size + y_size * y_size;
    let diag_good = size.sqrt() * 0.5;
    let diag_poor = approx_sqrt(size) * 0.5;
    println!("{} {}", diag_good, diag_poor);
} 
```

This prints 181.01933 and 192, respectively, so a good fit. It isn't clear why an approximate square root was needed here (what's the speed reason?). But we will see this approximate square root function in the partition code later.

The partition inclusion low and high tolerance (f32) are always three (3.0), this also matches the values set in `interp.zbd`.

The virtual partition x count (u32) is the number of steps from area left to area right in y size (256) steps or increments, so roughly `(area_right - area_left) / 256` (this may need to be rounded up). The virtual partition y count (u32) is the number of steps from area bottom to area top in y size (-256) steps/increments. This is therefore inverted! So roughly `(area_top - area_bottom) / -256` (this may need to be rounded down?). Also, the virtual partition x max is equal to the virtual partition x count minus one (1), and the virtual partition y max is equal to the virtual partition y count minus one (1).

The virtual partition total count (not part of the structure) can also now be calculated, and the area partition count will be equal to this, except for the T1 world (the training), where it is the count minus one (1).

The virtual partition pointer (u32) is always non-zero/non-null. The fields `unk148`, `unk152`, and `unk156` (f32) are always one (1.0).

The field `unk160` (u32) is always one (1), and the fields `unk164` and `unk168` (u32) are always non-zero/non-null - likely pointers. The fields `unk172`, `unk176`, `unk180`, and `unk184` (u32, maybe) are always zero (0). Finally, the field `unk188` (u32) is variable.

Just like the lights structure, it seems like the fields `unk160`, `unk164`, `unk168`, and possibly `unk172` could be dynamic arrays. This would make the world structure 188 bytes, and then e.g. `unk160` indicates how many values to read.

In short, the variable data is the area partition count and pointer, the area (although only 4 values are needed), the virtual partition x and y counts (since the maximum extent can be calculated from this), the virtual partition pointer, and the fields `unk164`, `unk168`, and `unk188`.

The area ranges (left to right, bottom to top) are also needed to read the partitions.

#### World partitions

The partitions depend on the area. Specifically, partitions are read in a nested loop, roughly:

```rust
let mut y = area_bottom;
while y >= area_top {
    let mut x = area_left;
    while x <= area_right {
        read_partition(x, y);
        x  += 256;
    }
    y += -256;
}
```

I'm not 100% sure the maths is correct, but you get the idea.

```rust
struct Partition {
    unk00: i32, // always 256/0x100
    unk04: i32, // always -1
    part_x: f32, // always x
    part_y: f32, // always y
    x_min: f32, // always x
    z_min: f32,
    y_min: f32, // always y + -256.0
    x_max: f32, // always x + 256.0
    z_max: f32,
    y_max: f32, // always y
    x_mid: f32, // always x + 128.0
    z_mid: f32,
    y_mid: f32, // always y + -128.0
    diagonal: f32,
    unk56: u16, // always 0
    count: u16,
    ptr: u32,
    unk64: u32, // always 0
    unk68: u32, // always 0
}
```

The size of a partition structure is 72 bytes.

The first field (i32?) could be the partition x size, but could also be bit flags. It is always 256/0x100. The second field (i32) is always negative one (-1), so this could be the partition y scaling. It's just an odd way to store this information.

The partition x and y are the same as the area x and y from the loop, but as floating point numbers.

The next fields give the minimum, maximum, and mean x, z, and y values (all f32). Because of the step values, `x_min` is always equal to x, and `y_min` is always equal to y + -256.0 (or y - 256.0). `x_max` is always equal to x + 256.0, and `y_max` is always equal to y.  I am not sure how `z_min` or `z_max` is determined, possibly from the geometry of the partition.

Therefore, the mid-points can easily be calculated. First, division is usually avoided, especially on old CPUs, since it was slower than multiplication. We can write `x / 2.0` as `x * 0.5`. The average is then `(max + min) * 0.5`. The x and y calculations simplify further.

Since `x_min = x` and `x_max = x + 256.0`:

1. `x_mid = (x_max + x_min) * 0.5`
1. `x_mid = (x_min + x_max) * 0.5`
1. `x_mid = (x + (x + 256.0)) * 0.5`
1. `x_mid = (2.0 * x + 256.0) * 0.5`
1. `x_mid = x + 128.0`

Since `y_min = y + -256.0` and `y_max = y`:

1. `y_mid = (y_max + y_min) * 0.5`
1. `y_mid = (y + (y + -256.0)) * 0.5`
1. `y_mid = (2.0 * y + -256.0) * 0.5`
1. `y_mid = y + -128.0`

Obviously, simplification isn't possible for `z_mid`, because `z_min` and `z_max` are derived from the geometry. `z_mid` is even more frustrating though:

```rust
let z_mid = (z_max + z_min) * 0.5;
```

If we attempt the calculation with single-precision floating point, out of the total 22016 partitions from all versions, 21812 match this exactly, and 204 do not match exactly, only closely. I've seen another formulation of the average calculation that is rumoured to help with accuracy, but this is disputed (see ["Rounding error in computing average" from StackOverflow](https://stackoverflow.com/questions/48740200/rounding-error-in-computing-average)).

```rust
let z_mid = z_min + (z_max - z_min) * 0.5;
```

This is actually worse, failing in 2068 cases. Only when using double-precision does it produce the same result. The previous calculation does not change when using double-precision.

For most use-cases, this doesn't really matter, although it does affect the diagonal calculation, which is the next field (f32). Effectively, this is the square root of the square of the sides:

```rust
let x_side = (x_max - x_min) * 0.5;
let z_side = (z_max - z_min) * 0.5;
let y_side = (y_max - y_min) * 0.5;
let diagonal = (x_side * x_side + z_side * z_side + y_side * y_size).sqrt();
```

Naturally, `x_side` simplifies to 128.0, and `y_size` to -128.0, although due to the squaring the sign does not matter. Also note that because of the squaring, any error in `z_side` compounds quickly, so I've found it necessary to cast `z_max` and `z_min` to f64, and perform the entire calculation up to the square root as double-precision:

```rust
let z_side = (z_max as f64 - z_min as f64) * 0.5;
let temp = 2.0 * 128.0 * 128.0 + z_side * z_side;
```

But this is where it gets silly. The partitions also use the (poor) approximate square root discussed above for the world structure (`approx_sqrt`). So all the precision is "lost", although it is still required to produce the same result in my testing.

Moving on, the field `unk56` (u16) is always zero (0), and the fields `unk64` and `unk68` (u32) are also always zero (0).

The count and pointer fields are part of a dynamic array. If the count is zero (0), then the pointer is zero/null. If the count is greater than zero, then the pointer is non-zero/non-null. In this case, read count u32 values after the structure. These should be indices of nodes in the given partition.

## Node parents and children

In principle, all nodes could have multiple parents, and multiple children. In practice, no nodes have multiple parents, and as described above:

* Camera nodes don't have a parent or children
* Display nodes don't have a parent or children
* Empty nodes don't have a parent or children (at least not for the purposes of this part)
* Light nodes don't have a parent or children
* LOD nodes always have a parent, and always have children
* Object3d nodes can have a parent and children
* Window nodes don't have a parent or children
* World nodes don't have a parent, but do have children

The reason I describe this in such detail is that it helps understand how the game nodes are structured. 

In the general case, both the parent and children indices are dynamic arrays. Read parent count u32 values first for the parent index/indices, and then read child count u32 values next for the child indices. (Obviously, if the count is zero, it isn't necessary to read anything.)

## Node positions in the GameZ file

There are also restrictions on which nodes can appear where in a GameZ file. Mechlib archives can only contain Object3d nodes, so this does not apply.

When loading a GameZ file:

* There can only be a single world node, and it must be the first node in the file (index 0)
* There can only be a single window node, and it must be the second node in the file (index 1)
* There can only be a single camera node, and it must be the third node in the file (index 2)
* There is at least one display node, and it must be the fourth node in the file (index 3). If there is another display node, it must be the fifth node in the file (index 4)
* There can only be a single light node, although its position in the file is variable
* Zeroed out nodes must be at the end of the array, and contiguous.
