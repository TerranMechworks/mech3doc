# Motion archives

Motion archives hold 'mech motion animation data, so how a 'mech model moves when it e.g. walks. However, the association of motion data with a 'mech model is determined by a reader file. Some 'mechs share motions/animations, and some motions are seemingly unused.

## Investigation (MW3)

Motion archives are [archive files](archive-files.md). Each motion file is named `<mech>_<motion>`, so for example "bushwhacker_jump". Motion files begin with a header:

```rust
struct Header {
    version: u32, // always 4
    loop_time: f32, // > 0.0
    frame_count: u32,
    part_count: u32,
    unk16: f32, // always -1.0
    unk20: f32, // always 1.0
}
```

The version field will always be four (4). The loop time is a non-negative floating point value that describes how long the motion plays for. The frame count is the number of frames in the motion, which is inclusive. This means there are actually frame count + 1 frames of data to read. The last frame is always the same as the first frame. Apparently, this is a common technique to make looping animations easier. The part count is the number of parts of the model that will be animated. The last two fields are unknown, but are always set to negative one (-1.0) and positive one (1.0). Maybe they describe the coordinate system?

Next count parts are read: 

```rust
struct Part {
    name_length: u32,
    name: [u8; name_length], // not zero-terminated
    flags: PartFlags, // always Translation + Rotation
    translations: [Vector3; frame_count + 1],
    rotations: [Quaternion; frame_count + 1],
}

bitflags PartFlags: u32 {
    Scale = 1 << 1,       // 0x02
    Rotation = 1 << 2,    // 0x04
    Translation = 1 << 3, // 0x08
}

struct Vector3 {
    x: f32,
    y: f32,
    z: f32,
}

struct Quaternion {
    w: f32,
    x: f32,
    y: f32,
    z: f32,
}
```

Each part begins with a variable-length string (ASCII). There is no zero-termination. This is the part of the 'mech model that the motion affects. The flags field always specify translation (8) and rotation (4), and never scale (2) for obvious reasons (scaling any part would look weird on 'mechs). So it will always be twelve (12).

Then, the translations are read sequentially, and then the rotations are read sequentially. Again, there is one more frame to read than frame count indicates, and the first and last values will be the same. I believe the quaternion order is wxyz, since the quaternions work fine in Blender, but not in Unity, which uses xyzw order.

## Investigation (PM)

Motion archive data doesn't change significantly in the expansion, but the archive does. Motion archives do not use checksumming; the checksum is always set to zero (0). Additionally, for some bizarre reason, the length of the data in the archive's TOC is always set to one (1). This can be highly inconvenient depending on the way archive entries are being read. A workaround is described in [archive files](archive-files.md).

## In-game use

Motions are used to animate 'mech models during missions. Which motion is used for which 'mech model is specified in the reader files (`dfn_<mech>.zrd` in `zbd/reader.zbd`). Some 'mechs share motions, and some motions are unused.
