# Nodes (PM)

Nodes are how the world data is organised and structured. Please see [the general node overview](nodes.md) first. This page describes node data structures for Pirate's Moon only. Refer also to [MechWarrior 3 nodes](nodes-mw.md).

## Node base/shared structure

Only analysed in the mechlib.

This is the structure used by all nodes, and is 208 bytes in size. Please note that while this is the same size as `NodeMw`, the layout is different! Refer to the base game for any other types.

```rust
struct NodePm {
    name: [u8; 36],
    flags: NodeFlags,
    unk040: u32, // always 0
    unk044: u32,
    zone_id: u32, // always 255 (mechlib only?)
    node_type: NodeType,
    data_ptr: u32,
    mesh_index: i32,
    environment_data: u32, // always 0
    action_priority: u32, // always 1
    action_callback: u32, // always 0
    area_partition_x: i32, // -1, or >= 0, <= 64
    area_partition_y: i32, // -1, or >= 0, <= 64
    parent_count: u16, // always 0 or 1
    children_count: u16,
    parent_array_ptr: u32,
    children_array_ptr: u32,
    unk096: u32, // always 0
    unk100: u32, // always 0
    unk104: u32, // always 0
    unk108: u32, // always 0
    unk112: u32, // 0, 1, 2 (mechlib?)
    unk116: Box3d,
    unk140: Box3d,
    unk164: Box3d,
    unk188: u32, // always 0
    unk192: u32, // always 0
    unk196: u32, // always 0x000000A0 (mechlib?)
    unk200: u32, // always 0
    unk204: u32, // always 0
}
```

Preliminary analysis of nodes in the mechlib indicates this data structure is largely the same as the base game. The biggest change is around offset 84:

```diff
-    parent_count: u32, // always 0 or 1
-    parent_array_ptr: u32,
-    children_count: u32,
-    children_array_ptr: u32,
+    parent_count: u16, // always 0 or 1
+    children_count: u16,
+    parent_array_ptr: u32,
+    children_array_ptr: u32,
+    unk096: u32, // always 0
```

I.e. the `parent_count` and `children_count` have been changed from u32 values to u16 values. This has shifted the parent and child array pointers, and has introduced an extra field, `unk096` (u32), which is always zero (0).

Additionally, the field `unk112` (u32) is now variable, but always 0, 1, or 2.

### Camera nodes base structure

Not analysed yet.

### Display nodes base structure

Not analysed yet.

### Empty nodes base structure

Not analysed yet.

### Light nodes base structure

Not analysed yet.

### LOD nodes base structure

Preliminary analysis of nodes in the mechlib indicates LOD nodes always have the node flags:

* `BASE`
* `UNK08`
* `UNK10`
* `ALTITUDE_SURFACE`
* `INTERSECT_SURFACE`
* `UNK25`

The field `unk044` will always be one (1).

The zone ID will be the default zone ID (255), but this is probably down to the mechlib. Assuming the same behaviour as the base game, the zone ID will be either the default zone ID (255), or a value greater than or equal to one (1) and less than or equal to 80 (this upper bound is arbitrarily chosen based on usual zone IDs).

LOD nodes always have data associated with them, so the data pointer will always be non-zero/non-null.

Although LOD nodes cannot have a mesh, the mesh index does depend on whether the node is in a GameZ file or a mechlib archive. For a GameZ file, the mesh index is an index, so it is always negative one (-1). For a mechlib archive, the mesh index is actually a pointer value, since the data is already stored hierarchically. So it is always zero (0). See Object3d nodes for mode information.

There will be one parent, and therefore the parent array pointer is non-zero/non-null. There will be at last one child, and therefore the child array pointer is non-zero/non-null.

The fields `unk116` and `unk140` will always be zeros (0.0). The field `unk164` will be unequal to `(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)`.

The field `unk112` will always be 2. The field `unk196` will always be 160.

### Object3d nodes base structure

The field `unk044` will be either 1 or 45697.

The zone ID will be the default zone ID (255), but this is probably down to the mechlib. Assuming the same behaviour as the base game, the zone ID will be either the default zone ID (255), or a value greater than or equal to one (1) and less than or equal to 80 (this upper bound is arbitrarily chosen based on usual zone IDs).

Object3d nodes always have data associated with them, so the data pointer will always be non-zero/non-null.

The mesh index depends on the HasMesh flag, and whether the node is in a GameZ file or a mechlib archive. For a GameZ file, the mesh index is an index. So if the flag is set, then the index is greater than or equal to zero (0). If the flag is unset, then the index is always negative one (-1). For a mechlib archive, the mesh index is actually a pointer value, since the data is already stored hierarchically. So if the flag is set, this is non-zero/non-null. If the flag is unset, this is zero/null. Note that for the non-null case, if you are loading the value as a signed integer (i32), the memory on 32-bit machines was limited. In practice, it won't be greater than 2147483647 bytes, so you can also check if the value is greater than zero.

In short:

* `IsMechlib && !HasMesh` => `mesh_index == 0` (null ptr)
* `IsMechlib && HasMesh` => `mesh_index != 0` (non-null ptr)
* `IsGameZ && !HasMesh` => `mesh_index == -1` (invalid index)
* `IsGameZ && HasMesh` => `mesh_index > -1` (valid index)

The field `unk196` will always be 160.

Other fields have not been analysed in detail, since they are liable to change outside the Mechlib.

### Window nodes base structure

Not analysed yet.

### World nodes base structure

Not analysed yet.

## Node type data structures

All nodes except empty nodes have extra, type-specific data associated with them.

### Camera data

Not analysed yet.

### Display data

Not analysed yet.

### Empty data

Not analysed yet.

### Light data

Not analysed yet.

### LOD data

Only analysed in the mechlib.

```rust
struct LodPm {
    level: u32, // always 0 or 1
    range_near_sq: f32,
    range_far: f32,
    range_far_sq: f32,
    zero16: [u8; 44], // always 0
    unk60: f32, // always == 0.0
    unk64: f32, // always >= 0.0
    unk68: f32, // always == unk64 * unk64
    unk72: f32, // always >= 0.0
    unk76: f32, // always == unk72 * unk72
    unk80: u32, // always 1
    unk84: u32, // always 0
    unk88: u32, // always 0
}
```

The size of the LOD structure is 92 bytes.

The level field (u32) is always zero (0) or one (1). Usually, this would make it a Boolean, but I think it corresponds to the level of detail setting, so e.g. low and high (hence the name). The near range value (f32) is always greater than or equal to zero (0.0) and less than or equal to 1000.0 squared, so it's assumed this is the near range squared. The far range value is stored as the base value (f32), which is always greater than zero (0.0), and why I suspect this is the far range, and as a squared value (f32). These are guesses at best.

The `unk60` field (f32) is always zero (0.0). The `unk64` field (f32) is greater than or equal to zero (0.0), while the `unk68` field (f32) is this value squared. . The `unk72` field (f32) is greater than or equal to zero (0.0), while the `unk76` field (f32) is this value squared. The `unk80` field (u32) is always one (1). The `unk84` field (u32) and `unk88` field (u32) are both always zero (0).

### Object3d data

Only analysed in the mechlib.

This seems to be the same as the base game.

### Window data

Not analysed yet.

### World data

Not analysed yet.
