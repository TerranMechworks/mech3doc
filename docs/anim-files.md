# Animation definition files

Animation definition files (anim files) hold compiled animation definitions for a game world.

The initial animation definitions are in the [reader archives](reader-archives.md), but they are quite free form and so probably complicated and slow to parse. I think this proved so slow that load times were unacceptable, and the solution the development team came up with was to load the reader files into the engine, and then dump out the in-memory representations of the parsed animation definitions.

It isn't known - because it hasn't been investigated - if the release version is capable of loading the animation definitions from the readers directly, or how to trigger this (for example, by removing the `anim.zbd` files).

## Investigation (MW3)

### Header and TOC

Anim files begin with a simple header:

```rust
struct Header {
    signature: u32, // always 0x08170616
    version: u32, // always 39
    entry_count: u32,
}
```

The signature (u32) is the magic number `0x02971222`. The version (u32) is always 39, which is different from the [mechlib archives](mechlib-archives.md) and [GameZ files](gamez-files.md) version. The entry count (u32) indicates how many animation definitions reader files are in the TOC that follows. This basically a list of the raw animation definition file paths:

```rust
struct Entry {
    path: [u8; 80],
    unk80: u32,
}

type Entries = [Entry; entry_count];
```

The path is an ASCII-encoded, zero-terminated string of up to 80 bytes. It is usually a relative path pointing to a `.zrd` file, such as `..\data\common\zrdr\commonAnim.zrd` (backslashes not escaped). Again, this points to a close connection to the various reader archives, which include matching files. Please note that the path data may occasionally contain non-zero bytes after the zero-termination, for example:

```plain
00000000  2e 2e 5c 64 61 74 61 5c  63 6f 6d 6d 6f 6e 5c 7a  |..\data\common\z|
00000010  72 64 72 5c 63 6f 6d 6d  6f 6e 41 6e 69 6d 2e 7a  |rdr\commonAnim.z|
00000020  72 64 00 02 90 02 3e 02  90 3d 3e 02 20 3e 3e 02  |rd....>..=>. >>.|
00000030  50 3e 3e 02 c8 bb 01 02  00 ff ff ff 04 02 00 00  |P>>.............|
00000040  00 00 00 00 c0 41 3e 02  d0 41 3e 02 90 43 3e 02  |.....A>..A>..C>.|
00000050  6a d8 95 37                                       |j..7|
```

Bytes from 0x00 (0) to 0x22 (34, exclusive) are the path, byte 0x22 (34) is the zero terminator, bytes from 0x23 (36) to 0x50 (80, exclusive) is garbage data from overwritten memory, and the four bytes from 0x50 (80) to 0x54 (84, exclusive) is an unknown integer (u32?). Given that for many entries, the trailing data is zero, it seems like this memory wasn't zeroed out properly in some cases.

### Animation definitions information

Following the TOC, there is some kind of information or book-keeping structure:

```rust
struct Info {
    unk00: u32, // always 0
    unk04: u32, // always 0
    unk08: u16, // always 0
    count: u16,
    unk12: u32, // always != 0, ptr?
    unk16: u32, // always 0
    unk20: u32, // always 0
    unk24: u32, // always != 0, ptr?
    gravity: f32,
    unk32: u32, // always 0
    unk36: u32, // always 0
    unk40: u32, // always 0
    unk44: u32, // always 0
    unk48: u32, // always 0
    unk52: u32, // always 0
    unk56: u32, // always 0
    unk60: u32, // always 1
    unk64: u32, // always 0
}

const GRAVITY: f32 = -9.8;

```

Most of the structure is zeroes, except for:

* The animation count (u16) at offset 10, which is greater than zero
* The two u32 values at offset 12 and 24, which are probably pointers and non-zero/non-null
* A f32 value at offset 28, which seems to be the gravity (of the world?) used for animation calculations, but is always set to -9.8 (0xC11CCCCD; or bytes 0xCD 0xCC 0x1C 0xC1).

### Animation definition structures

I'll describe the structures in full, before describing how to read animation definitions. The base animation definition structure is 316 bytes:

```rust
struct AnimDef {
    anim_name: [u8; 32],
    name: [u8; 32],
    anim_ptr: u32, // always != 0
    anim_root: [u8; 32],
    anim_root_ptr: u32,
    unk104: [u8; 44], // always 0
    flags: AnimDefFlags,
    unk152: u8, // always 0
    activation: AnimActivation,
    unk154: u8, // always 4
    unk155: u8, // always 2
    exec_by_range_min: f32,
    exec_by_range_max: f32,
    reset_time: f32,
    unk168: f32, // always 0
    max_health: f32,
    cur_health: f32,
    unk180: u32, // always 0
    unk184: u32, // always 0
    unk188: u32, // always 0
    unk192: u32, // always 0
    sequence_definitions_ptr: u32,
    reset_state: SequenceDefinition,
    sequence_definition_count: u8,
    object_count: u8,
    node_count: u8,
    light_count: u8,
    puffer_count: u8,
    dynamic_sound_count: u8,
    static_sound_count: u8,
    unknown_count: u8, // always zero
    activ_prereq_count: u8,
    activ_prereq_min_to_satisfy: u8,
    anim_ref_count: u8,
    unk275: u8, // always 0
    objects_ptr: u32,
    nodes_ptr: u32,
    lights_ptr: u32,
    puffers_ptr: u32,
    dynamic_sounds_ptr: u32,
    static_sounds_ptr: u32,
    unknown_ptr: u32,
    activ_prereqs_ptr: u32,
    anim_refs_ptr: u32,
    unk312: u32, // always 0
}

bitflags AnimDefFlags: u32 {
    ExecutionByRange = 1 << 1;
    ExecutionByZone = 1 << 3;
    HasCallbacks = 1 << 4;
    ResetTime = 1 << 5;
    NetworkLogSet = 1 << 10;
    NetworkLogOn = 1 << 11;
    SaveLogSet = 1 << 12;
    SaveLogOn = 1 << 13;
    AutoResetNodeStates = 1 << 16;
    ProximityDamage = 1 << 20;
}

enum AnimActivation: b8 {
    WeaponHit = 0,
    CollideHit = 1,
    WeaponOrCollideHit = 2,
    OnCall = 3,
    OnStartup = 4,
}
```

This is going to get complicated.

The first field is called "animation name" in the reader files, and is a 32 bytes, zero-terminated ASCII string with possible un-zeroed memory after the terminator. The second field is called simply "name" in the reader files, and is a 32 bytes, zero-terminated ASCII string (although this seems to only have zeros after the terminator). The next field is some kind of pointer (u32), possibly pointing to the engine-internal animation structure, and always non-zero/non-null. The third name is what I've called the "animation root". This is also a 32 bytes, zero-terminated ASCII string with possible un-zeroed memory after the terminator, and seems to be related to the object or node the animation is applied to. The next field is some kind of pointer (u32), possibly pointing to the engine-internal animation root, and always non-zero/non-null.

From what I could determine, if the `.flt` extension is stripped from the name, then if this matches the animation root name, the animation root pointer and animation pointer will be equal; otherwise, the animation root pointer and animation pointer will be unequal.

There are 44 zero bytes from offset 104 to 148 (exclusive).

At offset 148 are the flags, which indicate which optional features/values/fields the animation definition uses. I know of 10 of these:

* Execution by range (`EXECUTION_BY_RANGE` in reader files), likely that the animation definition is triggered if something (only the player?) is within range. Associated with two fields. If execution by range is set, execution by zone isn't set.
* Execution by zone (`EXECUTION_BY_ZONE` in reader files), a very uncommon trigger only appearing eleven times in all reader files. It isn't known how this works, since in the reader files the value to this key is an empty list. If execution by zone is set, execution by range isn't set.
* Has callbacks, set if any of the animation definition's sequences include a callback sequence event; otherwise unset (so this is derived, and not explicitly mentioned in the reader files). Probably to speed up callback look-ups?
* Reset time, likely whether the animation has a reset time. Definitely associated with one field, maybe two.
* Network log set and network log on. These work in tandem. In the reader files, if the `NETWORK_LOG` key is present, the "set" flag is set and the "on" flag is valid. The "on" flag is set if the `NETWORK_LOG` value is `ON`; if it is `OFF` the flag is unset. If the "set" flag isn't set, then the "on" flag isn't be set. These flags seem to control whether an animation definition is considered for transmission in a network/multiplayer game, and if it sent.
* Save log set and save log on. Similar to the network flags, these work in tandem. In the reader files, if the `SAVE_LOG` key is present, the "set" flag is set and the "on" flag is valid. The "on" flag is set if the `SAVE_LOG` value is `ON`; if it is `OFF` the flag is unset. If the "set" flag isn't set, then the "on" flag isn't be set. These flags seem to control whether an animation definition is considered for inclusion in a save game file, and if it is saved.
* Auto reset node states, or `AUTO_RESET_NODE_STATES` in the reader files might control whether the animation nodes or animation root is reset when the animation is reset or not. This seems to be the default behaviour, as the key `AUTO_RESET_NODE_STATES` is mostly followed by the value `OFF` in reader files.
* Proximity damage (`PROXIMITY_DAMAGE` in the reader files) is uncommon, and used 22 times in the reader files. The key has a value in the reader files, but it is always 0, so I haven't been able to confirm an associated field in the structure.

The field at offset 152 is unknown (u8), and is always zero (0). Next is the animation activation (`ACTIVATION` in the reader files), which can be:

* `WEAPON_HIT`, rare, 28 occurrences
* `COLLIDE_HIT`, uncommon, 119 occurrences
* `WEAPON_OR_COLLIDE_HIT`, uncommon, 108 occurrences
* `ON_CALL`, most common, 3026 occurrences
* `ON_STARTUP`, rare, 58 occurrences

The field at offset 154 is unknown (u8), and is always four (4). It could be related to a concept in the engine called action priority, but this isn't sure. The field at offset 155 is unknown (u8), and is always two (2).

The next two fields are the execution by range minimum (f32) and maximum (f32) range. If the execution by range flag is set, the minimum value is greater than or equal to 0.0 and the maximum value is greater than or equal to the minimum value; otherwise both values are zero (0.0).

Next is the reset time (f32). If the reset time flag is set, this value seems to range from -1.0 to 4.0 (-1.0, 0.0, 0.3, 0.65, 0.714, 1.0, 2.0, 3.0, 4.0). If the flag is unset, this value is always negative one (-1.0). This is followed by an unknown value, which I have typed as f32 based on the surrounding values, even though it could be anything. It is always zero (0.0). Interestingly in the reader files, there is at least one instance of a `RESET_TIME` key with two values. It could also track the "current" animation time - whatever that is.

The maximum health value (f32) is greater than or equal to zero (0.0), while the current health value (f32) is equal to the maximum. So these could be swapped. The reader files only mention `HEALTH`.

The next four fields (u32/i32/f32) are always zero (0).

I'll talk more about the sequence definition pointer value (u32) when discussing the sequence definitions. This is always non-zero/non-null, but then all animation definitions have at least one sequence definition.

Next follows the reset state sequence definition (thanks Skyfaller for the analysis). This will be read later separately again (see [reset sequence](#reset_sequence)). This might seem odd, but the reset state can contain a variable number of events, and so must be read after the animation definition. Likely they just used the generic sequence definition serialisation/deserialisation functions here, so the data is duplicated.

Several counts of things associated with the animation definition follow. They are all u8 values:

* The number of sequence definitions
* The number of objects (Object3d nodes)
* The number of other nodes
* The number of lights
* The number of puffers
* The number of dynamic sounds
* The number of static sounds
* The number of an unknown thing, always zero (0)
* The number of activation prerequisite conditions
* The minimum number of activation prerequisites necessary for activation, either 0, 1, or 2 in the files, but could be higher. Has to be less than or equal to the number of conditions.
* The number of animation references
* Likely a padding byte at offset 275, always zero (0)

These are immediately followed with pointers for these things (u32), except for the sequence definitions (this pointer was at offset 196):

* The objects array pointer
* The nodes array pointer
* The lights array pointer
* The puffers array pointer
* The dynamic sounds array pointer
* The static sounds array pointer
* The unknown things array pointer, always zero (0)
* The activation prerequisite conditions array pointer
* The animation references array pointer

As a general rule, if the count is zero (0), then the pointer will be zero/null; otherwise, the pointer will be non-zero/non-null. These also trigger extra reads.

The final field at offset 312 (u32/i32) is unknown, and is always zero (0).

### Animation definition reading

Animation definitions are read sequentially. The number of animation definitions to read was provided in the info structure. Also, when reading the animation definition array, the first item will always be zeroed out. This is a common occurrence for dynamic arrays in the anim file. Except not quite in this case! Field 153, the activation value won't be zero (0), but instead five (5), which corresponds to the on call activation.

After each animation definition structure is read, further reads based on the counts can be triggered (described in the following sections). This is also the case for the zeroed out item! It also has a zeroed out reset state!

### Object3d nodes

If the object count was greater than zero, the object array is read. Each item is a 96 byte structure. When reading the array, the first item will always be zeroed out.


```rust
struct ObjectRef {
    name: [u8; 36],
    unk36: [u8; 60],
}
```

The name is a node name for a Object3d node, and so is 36 bytes long. Assume ASCII. The "padding" for the name is also odd. It seems like all nodes are initialised with the name to `Default_node_name` (padded with zeros/nulls to 36 bytes). Then, when the name is filled in, it is overwritten with the node name (zero/null terminated).

I haven't been able to figure out what the rest of the data (60 bytes) does.

### Other nodes

If the nodes count was greater than zero, the nodes array is read. Each item is a 40 byte structure. When reading the array, the first item will always be zeroed out.

```rust
struct NodeRef {
    name: [u8; 36],
    pointer: u32,
}
```

The name is a node name for a node, and so is 36 bytes long. Assume ASCII. The "padding" for the name is also odd. It seems like all nodes are initialised with the name to `Default_node_name` (padded with zeros/nulls to 36 bytes). Then, when the name is filled in, it is overwritten with the node name (zero/null terminated).

The pointer (u32) is always non-zero/non-null, except for the first item.

### Light nodes

If the lights count was greater than zero, the lights array is read. Each item is a 44 byte structure. When reading the array, the first item will always be zeroed out. This structure is also used for other things.

```rust
struct ThingRef {
    name: [u8; 36],
    pointer: u32,
    unk40: u32, // always 0
}
```

The name is a node name for a node, and so is 36 bytes long. Assume ASCII. The "padding" for the name is also odd. It seems like all nodes are initialised with the name to `Default_node_name` (padded with zeros/nulls to 36 bytes). Then, when the name is filled in, it is overwritten with the node name (zero/null terminated).

The pointer (u32) is always non-zero/non-null, except for the first item. The unknown field (u32?) is always zero (0).

### Puffer nodes?

If the puffer count was greater than zero, the puffer array is read. Each item is a 44 byte structure. When reading the array, the first item will always be zeroed out.

```rust
struct PufferRef {
    name: [u8; 32],
    unk32: u32,
    pointer: u32,
    unk40: u32, // always 0
}
```

Since puffers don't seem to be nodes, the name is 32 bytes long. Assume ASCII. The name is padded/filled with zeros after the zero terminator.

The first unknown field (u32) is very strange. The lower three bytes are always zero (0), so `unk32 ^ 0x00FFFFFF == 0`. The high byte is sometimes non-zero.

The pointer (u32) is always non-zero/non-null, except for the first item. The second unknown field (u32?) is always zero (0).

### Dynamic sounds/sound nodes

If the dynamic sounds count was greater than zero, the dynamic sounds array is read. Each item is a 44 byte structure. When reading the array, the first item will always be zeroed out. This is the same structure used by the lights.

### Static sounds

If the static sounds count was greater than zero, the static sounds array is read. Each item is a 36 byte structure. When reading the array, the first item will always be zeroed out.

```rust
struct StaticSoundRef {
    name: [u8; 32],
    unk32: u32, // always 0
}
```

Since static sounds don't seem to be nodes, the name is 32 bytes long. Assume ASCII. The name is not cleanly zero-filled after the zero terminator. The unknown field (u32) is always zero (0).

### Unknown items

Since the unknown count is always zero, this is never read. I presume - based on the other fields/ordering - that it would be read here. Since no such items are read, I don't know what structure this might have.

### Activation prerequisite conditions

If the animation prerequisite conditions (APC) count was greater than zero, the APC array is read. Each item is a 48 byte structure. Unlike other arrays, the first item is not zeroed out!

This is by far the most complicated to read. There are essentially three types of APCs. Based on the type, the data read is interpreted differently (i.e. it has the same size, but different types/layout). Let me first describe the opaque layout:

```rust
// APC = Activation prerequisite condition
struct Apc {
    optional: u32, // always 0 or 1 (bool)
    type: ApcType,
    type_dependent: [u8; 40],
}

enum ApcType: u32 {
    Animation = 1,
    Object = 2,
    Parent = 3,
}
```

The optional field (u32) is always zero (0) or one (1), a Boolean, and signifies whether the APC is required or optional for activation. Animation-type APCs seem to be always required, i.e. not optional. The type field (u32) is an enumeration, where:

* One (1) means the data is interpreted as a animation-type APC
* Two (2) means the data is interpreted as an object-type APC
* Three (3) means the data is interpreted as an object-type APC in the parent role

Next, the type dependent data:

```rust
struct ApcAnim {
    name: [u8; 32],
    unk32: u32, // always 0
    unk36: u32, // always 0
}

struct ApcObject {
    active: u32, // always 0 or 1 (bool)
    name: [u8; 32],
    pointer: u32,
}
```

For animation-type APCs, the name is 32 bytes, ASCII, zero-terminated, and padded with zeros/properly zeroed-out. The next two fields are 4 bytes in size each (u32?), and always zero (0).

For object-type APCs, the active field (u32) is always zero (0) or one (1), a Boolean. However, for object-type APCs with the parent role, they are always inactive (0). The name is also 32 bytes, ASCII, zero-terminated, and padded with zeros/properly zeroed-out. Finally, the pointer (u32) is always non-null/non-zero.

I haven't explored if there is any ordering to APCs, e.g. how parent APCs know which APCs are their children.

### Animation references

If the animation references count was greater than zero, the animation references array is read. Each item is a 72 byte structure. Unlike other arrays, the first item is not zeroed out!

```rust
struct AnimRef {
    name: [u8; 64],
    unk64: u32, // always 0
    unk68: u32, // always 0
}
```

I'm not sure if the name field is actually 64 bytes long. Some values are properly zero-terminated at 32 bytes and beyond, but not all. Again, this is possibly a lack of zeroing out the memory. In any case, it's a zero-terminated, ASCII string. The next two fields are 4 bytes in size each (u32?), and always zero (0).

There's one animation reference per `CALL_ANIMATION` sequence event, and there may be duplicates to the same animation since multiple calls might needed.

### Reset sequence

The reset sequence is read next, and is read unconditionally, i.e. every animation definition has a reset sequence - even the zeroed out first animation definition!

The reset sequence is special in that it always has the same name (`RESET_SEQUENCE`), and a separate reference to it is kept. Otherwise, it is largely the same as any other sequence:

```rust
struct SequenceDefinition {
    name: [u8; 32],
    flags: u32, // always 0 or 0x0303
    unk36: [u8, 20], // always 0
    pointer: u32,
    size: u32,
}

enum SequenceActivation: u32 {
    Initial = 0,
    OnCall = 3,
}
```

For any sequence, the name is 32 bytes long, ASCII, zero-terminated, and properly zeroed out.

The flags can either be zero (0) or 0x0303. This corresponds to the activation of either initial (0) or on call (3). But there are likely others we don't know about because they don't appear in the file.

The next 20 bytes (at offset 36) are unknown and always zero (0). Finally, the pointer (u32) and size (u32). If the size is zero (0), then the pointer will be zero/null, and no further data is read. This indicates an empty reset sequence. Otherwise, size bytes of sequence event data is read. I'll describe how to read sequence event data shortly.

For the reset sequence, the name will always be `RESET_SEQUENCE`. The flags will always be zero, an initial activation. It will always match the reset state in the animation definition.

### Sequence definitions

If the sequence definitions count was greater than zero, the sequence definitions are read. Please see the reset sequence section for the sequence definitions structure.

### Sequence events

Is this file not complicated enough yet? Sequence events will fix that. It starts easy. The size of the sequence event data (in bytes) is known from the sequence definition. Simply keep reading the events until that many bytes have been read. Each event starts with a header:

```rust
struct EventHeader {
    event_type: u8,
    start_offset: StartOffset,
    pad02: u16, // always 0
    size: u32,
    start_time: f32,
}

enum StartOffset: u8 {
    Animation = 1,
    Sequence = 2,
    Event = 3,
}
```

The event type (u8) indicates just that. We'll get to these. The start offset (u8) can either be animation (1), sequence (2), or event (3). The explicit padding at offset 2 is always zero (0). The size indicates the size of this event's total data (including the header). The start time indicates the event's start time relative to the start offset/parent (probably).

There are 33 known event types, and they are described separately in [sequence events](events.md). Fun story, these each require parsing.
