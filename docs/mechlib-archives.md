# Mechlib archives

Mechlib archives hold detailed and low-resolution 'mech models, 'mech cockpit models, and mechlib model data.

## Investigation (MW3)

Mechlib archives are [archive files](archive-files.md). They contain three unique files, `format`, `version`, `materials`. Otherwise, all files are models with the ending `.flt`.

### Format and version

Both of these files are four (4) bytes long, and can be read as either a u32 or i32. The format value is always one (1). The version value is 27 for the base game.

### Materials

The materials file is very similar to but slightly different than materials information in `gamez.zbd` archives. It starts with the number of materials in the file (count, u32 or i32).

Each material has a main structure:

```rust
struct Material {
    alpha: u8, // maybe?
    flags: MaterialFlags,
    rgb: u16, // maybe?
    red: f32,
    green: f32,
    blue: f32,
    texture_ident: u32, // a pointer in mechlib
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
```

This is the same structure as GameZ materials, but is read and interpreted slightly different.

A lot isn't known about the material information. It seems to be dump of an in-game structure, as it contains what seem to be pointers. Some fields are always set to the same value. The always flag is always set, the never flag is never set. The most important bit of information is the textured flag. This indicates whether the material has a texture or not.

#### Textured materials

Textured materials always have alpha set to 255/0xFF, since textures can include their own alpha data. The `rgb` field set to 32767/0x7FFF, and the red, green, and blue fields set to 255.0 (which is white). The unknown flag may or may not be set, and the `unk32` field is also indeterminate. This field could be specularity or some other material property.

Only textured materials can have the cycled flag set, which indicates that the material has multiple textures that are cycled through, creating an animated effect. However, mechlib materials cannot be cycled, so this flag is never set, and the cycle pointer field is always zero (0)/null.

In short, for textured materials in the mechlib archive, the variable information is the `unk32` field, the unknown flag, and the `texture_ident` field. In the GameZ file, this holds the texture index on load, which is then replaced with a pointer to the texture. In the mechlib archive, this is the raw pointer value, since the texture name is written after the structure (discussed shortly). Code that only wants to draw the materials can basically discard almost all this information, except for if the material is textured.

If the material is textured, a variable string that is the texture name follows the material structure immediately:

```rust
struct MaterialName {
    length: u32,
    name: [u8; length], // not zero-terminated
}
```

Assume this is ASCII. There is no zero-termination, so if this is required, allocate length + 1 bytes.

#### Coloured materials

Untextured or coloured materials always have the unknown flag and cycled flag unset. The `rgb` field is always zero (0/0x0000). This deserved a bit of discussion. Textures use a packed colour value format known as RGB565, and textured materials have their colour set to white. For textured materials, `rgb` is set to 0x7FFF, which corresponds to white in the RGB555 format. So I have assumed this field was intended to be used as a packed colour, but for some reason wasn't used. Both the material and cycle pointers are always zero (0)/null. The red, green, and blue fields indicate the colour of the material. In short, for coloured materials, the variable information is the red/green/blue fields, alpha, and the `unk32` field.

### Model files

Like the materials file, model files are very similar to but slightly different than models in `gamez.zbd` archives. Model files are also quite complex.

First, some background. MechWarrior 3 uses so-called "nodes" to represent information in the engine. There are hints to this in the reader files and interpreter scripts. In `mechlib.zbd`, the only allowed node type is a 3D object node. GameZ files can contain other nodes.

I describe [all nodes](nodes.md) separately, since the structures are rather large. As a quick refresher, all nodes share a base structure, and then have node type specific data.

I also describe [mesh data structures in GameZ](gamez-files.md#meshes_mw), since they are largely the same.

## Investigation (PM)

The expansion files are similar to the base game, however many data structures around the nodes have changed.

### Format and version

Both of these files are four (4) bytes long, and can be read as either a u32 or i32. The format value is always one (1). The version value is 41 for the expansion.

### Materials

Materials are read exactly the same as the base game.

### Model files

Model files are ready the same way as the base game, but many data structures are different. Note that while in the base game, only 3D object nodes are allowed, in the expansion both 3D object nodes and LOD (level of detail) nodes are present.

I describe [all nodes](nodes.md) separately, since the structures are rather large and shared with GameZ files.

I also describe [mesh data structures in GameZ](gamez-files.md#meshes_pm), since they are largely the same.

## In-game use

These models are used in-game and in the mechlab screen.
