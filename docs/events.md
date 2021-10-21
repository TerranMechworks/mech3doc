# Sequence events

## Events by index

| Event                                                         | Type  |
| :------------------------------------------------------------ | ----: |
| [`SOUND`](#sound)                                             |     1 |
| [`SOUND_NODE`](#sound-node)                                   |     2 |
| [`LIGHT_STATE`](#light-state)                                 |     4 |
| [`LIGHT_ANIMATION`](#light-animation)                         |     5 |
| [`OBJECT_ACTIVE_STATE`](#object-active-state)                 |     6 |
| [`OBJECT_TRANSLATE_STATE`](#object-translate-state)           |     7 |
| [`OBJECT_SCALE_STATE`](#object-scale-state)                   |     8 |
| [`OBJECT_ROTATE_STATE`](#object-rotate-state)                 |     9 |
| [`OBJECT_MOTION`](#object-motion)                             |    10 |
| [`OBJECT_MOTION_FROM_TO`](#object-motion-from-to)             |    11 |
| [`OBJECT_MOTION_SI_SCRIPT`](#object-motion-si-script)         |    12 |
| [`OBJECT_OPACITY_STATE`](#object-opacity-state)               |    13 |
| [`OBJECT_OPACITY_FROM_TO`](#object-opacity-from-to)           |    14 |
| [`OBJECT_ADD_CHILD`](#object-add-child)                       |    15 |
| [`OBJECT_CYCLE_TEXTURE`](#object-cycle-texture)               |    17 |
| [`OBJECT_CONNECTOR`](#object-connector)                       |    18 |
| [`CALL_OBJECT_CONNECTOR`](#call-object-connector)             |    19 |
| [`CALL_SEQUENCE`](#call-sequence)                             |    22 |
| [`STOP_SEQUENCE`](#stop-sequence)                             |    23 |
| [`CALL_ANIMATION`](#call-animation)                           |    24 |
| [`STOP_ANIMATION`](#stop-animation)                           |    25 |
| [`RESET_ANIMATION`](#reset-animation)                         |    26 |
| [`INVALIDATE_ANIMATION`](#invalidate-animation)               |    27 |
| [`FOG_STATE`](#fog-state)                                     |    28 |
| [`LOOP`](#loop)                                               |    30 |
| [`IF`](#if)                                                   |    31 |
| [`ELSE`](#else)                                               |    32 |
| [`ELSEIF`](#elseif)                                           |    33 |
| [`ENDIF`](#endif)                                             |    34 |
| [`CALLBACK`](#callback)                                       |    35 |
| [`FBFX_COLOR_FROM_TO`](#fbfx-color-from-to)                   |    36 |
| [`DETONATE_WEAPON`](#detonate-weapon)                         |    41 |
| [`PUFFER_STATE`](#puffer-state)                               |    42 |

## Events by name

| Event                                                         | Type  |
| :------------------------------------------------------------ | ----: |
| [`CALL_ANIMATION`](#call-animation)                           |    24 |
| [`CALL_OBJECT_CONNECTOR`](#call-object-connector)             |    19 |
| [`CALL_SEQUENCE`](#call-sequence)                             |    22 |
| [`CALLBACK`](#callback)                                       |    35 |
| [`DETONATE_WEAPON`](#detonate-weapon)                         |    41 |
| [`ELSE`](#else)                                               |    32 |
| [`ELSEIF`](#elseif)                                           |    33 |
| [`ENDIF`](#endif)                                             |    34 |
| [`FBFX_COLOR_FROM_TO`](#fbfx-color-from-to)                   |    36 |
| [`FOG_STATE`](#fog-state)                                     |    28 |
| [`IF`](#if)                                                   |    31 |
| [`INVALIDATE_ANIMATION`](#invalidate-animation)               |    27 |
| [`LIGHT_ANIMATION`](#light-animation)                         |     5 |
| [`LIGHT_STATE`](#light-state)                                 |     4 |
| [`LOOP`](#loop)                                               |    30 |
| [`OBJECT_ACTIVE_STATE`](#object-active-state)                 |     6 |
| [`OBJECT_ADD_CHILD`](#object-add-child)                       |    15 |
| [`OBJECT_CONNECTOR`](#object-connector)                       |    18 |
| [`OBJECT_CYCLE_TEXTURE`](#object-cycle-texture)               |    17 |
| [`OBJECT_MOTION_FROM_TO`](#object-motion-from-to)             |    11 |
| [`OBJECT_MOTION_SI_SCRIPT`](#object-motion-si-script)         |    12 |
| [`OBJECT_MOTION`](#object-motion)                             |    10 |
| [`OBJECT_OPACITY_FROM_TO`](#object-opacity-from-to)           |    14 |
| [`OBJECT_OPACITY_STATE`](#object-opacity-state)               |    13 |
| [`OBJECT_ROTATE_STATE`](#object-rotate-state)                 |     9 |
| [`OBJECT_SCALE_STATE`](#object-scale-state)                   |     8 |
| [`OBJECT_TRANSLATE_STATE`](#object-translate-state)           |     7 |
| [`PUFFER_STATE`](#puffer-state)                               |    42 |
| [`RESET_ANIMATION`](#reset-animation)                         |    26 |
| [`SOUND_NODE`](#sound-node)                                   |     2 |
| [`SOUND`](#sound)                                             |     1 |
| [`STOP_ANIMATION`](#stop-animation)                           |    25 |
| [`STOP_SEQUENCE`](#stop-sequence)                             |    23 |

## Sequence events

```rust
struct EventHeader {
    event_type: u8, // could also be an enum
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

The event type (u8) indicates just that, the type of the event, and therefore how to interpret the data following the header. The start offset (u8) can either be animation (1), sequence (2), or event (3). The explicit padding at offset 2 is always zero (0). The size indicates the size of this event's entire data (including the header). The start time indicates the event's start time relative to the start offset/parent (probably).

The event structures and their sizes specified in this document are all without the header, for convenience. Subtract 12 bytes (the size of the header) from the size in the header to get the event sizes specified.

## Index lookups

Sequence events can refer to information in their associated animation definition, for example:

* Object3d nodes
* Sound nodes (dynamic sounds)
* Other nodes (just called nodes)
* Sounds (static sounds)
* Lights
* Puffers

Based on the packing of some structures and the general size of the arrays in GameZ, I assume node indices are 2 bytes/16 bits, so u16 or i16. We do see negative numbers, so I assume it's i16, leaving a maximum index of 32767 - still a lot larger than the usual array sizes.

As mentioned, there are negative numbers that seem to have special meanings. For example, if the reader file says `INPUT_NODE`, this is translated to the index -200.

```rust
const INPUT_NODE_INDEX: i16 = -200;
```

It's unknown if this is allowed for all node indices, or only some.

## Sound

Reader name: `SOUND`, Type: 1, Size: 16

Also called "static sound" in this project.

```rust
struct Sound {
    sound_index: i16,
    node_index: i16,
    translation: Vec3,
}
```

The sound index (i16) is used to look up the static sound in the animation definition. The node index (i16) is used to look up the parent/at node in the animation definition. The translation (Vec3) is presumably the sound's translation from the node.

## Sound node

Reader name: `SOUND_NODE`, Type: 2, Size: 60

Also called "dynamic sound" in this project.

```rust
struct SoundNode {
    name: [u8; 32],
    unk32: u32, // always 1
    flags: SoundNodeFlags,
    active_state: u32, // always 0 or 1 (bool)
    node_index: i16,
    pad46: u16, // always 0
    translation: Vec3,
}

bitflags SoundNodeFlags: u32 {
    InheritTranslation = 1 << 1; // 0x2
}
```

The sound node's name (32 bytes) is zero-terminated and zero padded. It's unclear why dynamic sounds aren't looked up by index, maybe this event creates a new node? The next field (u32) is always one (1). The flags field (u32) seems to be a bit field and is either zero (0) or two (2). The active state (u32) is either zero (0, false) or one (1, true). The node index (i16) is used to look up the parent/at node in the animation definition. The next field (u16) is padding and will always be zero (0). The translation (Vec3) is presumably the sound's translation from the node. If inherit translation flag (1 << 1 or 0x2) is unset, then the node index and the translation will be zero (0/0.0). 

## Light state

Reader name: `LIGHT_STATE`, Type: 4, Size: 120

```rust
struct LightState {
    name: [u8; 32],
    light_index: i16,
    pad34: u16, // always 0
    flags: LightFlags,
    active_state: u32, // always 0 or 1 (bool)
    point_source: u32, // always 1
    directional: u32, // always 0 or 1 (bool)
    saturated: u32, // always 0 or 1 (bool)
    subdivide: u32, // always 0 or 1 (bool)
    static: u32, // always 0 or 1 (bool)
    node_index: i32,
    translation: Vec3,
    rotation: Vec3,
    range_near: f32,
    range_far: f32,
    color: Color,
    ambient: f32,
    diffuse: f32,
}

// Also used for light nodes in GameZ
bitflags LightFlags: u32 {
    // This flag never occurs in sequence events
    TranslationAbs = 1 << 0; // 0x001
    Translation = 1 << 1;    // 0x002
    // This flag never occurs in sequence events
    Rotation = 1 << 2;       // 0x004
    Range = 1 << 3;          // 0x008
    Color = 1 << 4;          // 0x010
    Ambient = 1 << 5;        // 0x020
    Diffuse = 1 << 6;        // 0x040
    Directional = 1 << 7;    // 0x080
    Saturated = 1 << 8;      // 0x100
    Subdivide = 1 << 9;      // 0x200
    Static = 1 << 10;        // 0x400
    
    Inactive = 0;
    Default = TranslationAbs
    | Translation
    | Range
    | Directional
    | Saturated
    | Subdivide;
}
```

The light node's name (32 bytes) is zero-terminated and zero padded. The light node's index (i16) is used to look up the light in the animation definition. It's unclear why the light state contains both the light node's name and index. When looked up by index, that name matches the name in this structure. The next field (u16) is padding and will always be zero (0).

The light flags (u32) are also used for light nodes in GameZ, and indicate which further fields/states are valid and should be set. The `TranslationAbs` flag (1 << 0, 0x001) is never set in sequence events/in `anim.zbd` that we have.

The active state (u32) is always zero (0, false) or one (1, true). The point source field (u32) indicates whether the light is directed (0, never occurs) or a point source (1, always). The directional field (u32) is always zero (0, false) or one (1, true). If the directional flag (1 << 7, 0x080) is unset, this is always false. The saturated field (u32) is always zero (0, false) or one (1, true). If the saturated flag (1 << 8, 0x100) is unset, this is always false. The subdivide field (u32) is always zero (0, false) or one (1, true). If the subdivide flag (1 << 9, 0x200) is unset, this is always false. The static field (u32) is always zero (0, false) or one (1, true). If the static flag (1 << 10, 0x400) is unset, this is always false.

The node index (i32) is used to look up the parent/at node in the animation definition.

It's unclear why dynamic sounds aren't looked up by index, maybe this event creates a new node? The next field (u32) is always one (1). Inherit translation (u32) seems to be a bit field and is either zero (0) or two (2). The active state (u32) is either zero (0, false) or one (1, true).

The node index (i16) is used to look up the parent/at node in the animation definition. This is sometimes set to the special input node value. The next field (u16) is padding and will always be zero (0). The translation (Vec3) is presumably the sound's translation from the node. If the translation flag (1 << 1, 0x002) is unset, then both the node index and translation will be zero (0/0.0).

The rotation or direction (Vec3) is always zero (0.0), because the rotation flag (1 << 2, 0x004) is never set in sequence events/in `anim.zbd` that we have.

The near range (f32) and far range (f32) likely indicate the light's range. The near range is greater than or equal to zero (0.0), and the far range is greater than or equal to the near range. If the range flag (1 << 3, 0x008) is unset, then both are zero (0.0).

The colour (Color) is the RGB value of the light, and all values between zero (0.0) and one (1.0), inclusive of both. If the colour flag (1 << 4, 0x010) is unset, all values are zero (0.0). Finally, the ambient (f32) and diffuse (f32) control two aspects of lighting used in computer graphics. Both values are between zero (0.0, inclusive) and one (1.0, inclusive). If the ambient flag (1 << 5, 0x020) or diffuse flag (1 << 6, 0x040) are unset, the respective value will be zero (0.0). 

## Light animation

Reader name: `LIGHT_ANIMATION`, Type: 5, Size: 100

## Object active state

Reader name: `OBJECT_ACTIVE_STATE`, Type: 6, Size: 8

## Object translate state

Reader name: `OBJECT_TRANSLATE_STATE`, Type: 7, Size: 20

## Object scale state

Reader name: `OBJECT_SCALE_STATE`, Type: 8, Size: 16

## Object rotate state

Reader name: `OBJECT_ROTATE_STATE`, Type: 9, Size: 20

## Object motion

Reader name: `OBJECT_MOTION`, Type: 10, Size: 320

## Object motion from to

Reader name: `OBJECT_MOTION_FROM_TO`, Type: 11, Size: 132

## Object motion SI script

Reader name: `OBJECT_MOTION_SI_SCRIPT`, Type: 12, Size: Variable, at least 24

## Object opacity state

Reader name: `OBJECT_OPACITY_STATE`, Type: 13, Size: 12

## Object opacity from to

Reader name: `OBJECT_OPACITY_FROM_TO`, Type: 14, Size: 24

## Object add child

Reader name: `OBJECT_ADD_CHILD`, Type: 15, Size: 4

## Object cycle texture

Reader name: `OBJECT_CYCLE_TEXTURE`, Type: 17, Size: 8

## Object connector

Reader name: `OBJECT_CONNECTOR`, Type: 18, Size: 76

## Call object connector

Reader name: `CALL_OBJECT_CONNECTOR`, Type: 19, Size: 68

## Call sequence

Reader name: `CALL_SEQUENCE`, Type: 22, Size: 36

## Stop sequence

Reader name: `STOP_SEQUENCE`, Type: 23, Size: 36

## Call animation

Reader name: `CALL_ANIMATION`, Type: 24, Size: 68

## Stop animation

Reader name: `STOP_ANIMATION`, Type: 25, Size: 36

## Reset animation

Reader name: `RESET_ANIMATION`, Type: 26, Size: 36

## Invalidate animation

Reader name: `INVALIDATE_ANIMATION`, Type: 27, Size: 36

## Fog state

Reader name: `FOG_STATE`, Type: 28, Size: 68

## Loop

Reader name: `LOOP`, Type: 30, Size: 8

## If

Reader name: `IF`, Type: 31, Size: 12

## Else

Reader name: `ELSE`, Type: 32, Size: 0

## Elseif

Reader name: `ELSEIF`, Type: 33, Size: 12

## Endif

Reader name: `ENDIF`, Type: 34, Size: 0

## Callback

Reader name: `CALLBACK`, Type: 35, Size: 4

## FBFX color from to

Reader name: `FBFX_COLOR_FROM_TO`, Type: 36, Size: 52

Presumably, FBFX stands for "frame buffer effect".

## Detonate weapon

Reader name: `DETONATE_WEAPON`, Type: 41, Size: 24

## Puffer state

Reader name: `PUFFER_STATE`, Type: 42, Size: 580

```rust
struct PufferState {
    name: [u8; 32],
    puffer_index: i16,
    pad34: u16, // always 0
    flags: PufferStateFlags,
    active_state: i32,
    node_index: u32,
    translation: Vec3,
    local_velocity: Vec3,
    world_velocity: Vec3,
    min_random_velocity: Vec3,
    max_random_velocity: Vec3,
    world_acceleration: Vec3,
    interval_type: u32,
    interval_value: f32,
    size_range: Vec2,
    lifetime_range: Vec2,
    start_age_range: Vec2,
    deviation_distance: f32,
    unk156: f32, // always 0.0
    unk160: f32, // always 0.0
    fade_range: Vec2,
    friction: f32,
    unk176: u32, // always 0
    unk180: u32, // always 0
    unk184: u32, // always 0
    unk188: u32, // always 0
    tex192: [u8; 36],
    tex228: [u8; 36],
    tex264: [u8; 36],
    tex300: [u8; 36],
    tex336: [u8; 36],
    tex372: [u8; 36],
    unk408: [u8; 120], // always 0
    unk528: u32,
    unk532: u32, // always 0
    unk536: f32,
    unk540: f32,
    growth_factor: f32,
    unk548: [u8; 32], // always 0
}

bitflags PufferStateFlags: u32 {
    // this might not be right?
    Translate = 1 << 0;          // 0x00001
    GrowthFactor = 1 << 1;       // 0x00002
    // this might not be right?
    State = 1 << 2;              // 0x00004
    LocalVelocity = 1 << 3;      // 0x00008
    WorldVelocity = 1 << 4;      // 0x00010
    MinRandomVelocity = 1 << 5;  // 0x00020
    MaxRandomVelocity = 1 << 6;  // 0x00040
    IntervalType = 1 << 7;       // 0x00080
    // this might not be right?
    IntervalValue = 1 << 8;      // 0x00100
    SizeRange = 1 << 9;          // 0x00200
    LifetimeRange = 1 << 10;     // 0x00400
    DeviationDistance = 1 << 11; // 0x00800
    FadeRange = 1 << 12;         // 0x01000
    Active = 1 << 13;            // 0x02000
    CycleTexture = 1 << 14;      // 0x04000
    StartAgeRange = 1 << 15;     // 0x08000
    WorldAcceleration = 1 << 16; // 0x10000
    Friction = 1 << 17;          // 0x20000

    Inactive = 0;
}
```

The puffer's name (32 bytes) is zero-terminated and zero padded. The puffer's index (i16) is used to look up the puffer in the animation definition. It's unclear why the puffer state contains both the puffer's name and index. When looked up by index, that name matches the name in this structure. The next field (u16) is padding and will always be zero (0).

The puffer state's flags (u32) indicate which further fields/states are valid and should be set. If the state flag (1 << 3, 0x00008) is unset, then no other flags are set in the sequence events/in `anim.zbd` that we have. This seems to indicate whether the puffer is disabled/inactive. At least, that's the best guess. However, there's also an active flag and an active state, which seems to be slightly different.

The active or lifetime state (i32) seems to allow for a range of values. If the active flag is set, then the active state will be greater than or equal to one (1), and less than or equal to five (5). If the active flag (1 << 13, 0x02000) is unset, then the active state is always negative one (-1).

TODO
