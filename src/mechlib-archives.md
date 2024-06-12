# Mechlib archives

Mechlib archives hold detailed and low-resolution 'mech models, 'mech cockpit models, and mechlib model data.

## Investigation (MW3)

Mechlib archives are [archive files](archive-files.md). They contain three unique files, `format`, `version`, `materials`. Otherwise, all files are models with the ending `.flt`.

### Format and version

Both of these files are four (4) bytes long, and can be read as either a u32 or i32. The format value is always one (1). The version value is 27 for the base game.

### Materials

The materials file is very similar to but slightly different than materials information in [GameZ files](gamez/).

The difference in the Mechlib is that the `texture_ident` field is a pointer, not the index. In the GameZ file, since the texture names are written first, the field holds the texture index, which is then replaced with a pointer to the texture. In the mechlib archive, this is the raw pointer value, since the texture name is written after the structure (discussed shortly).

So, in the material file, the number of materials in the file (`count`, u32 or i32) comes first. Next, `count` materials are read. Additionally, if the material is textured, a variable string that is the texture name follows the material structure immediately:

```rust
struct MaterialName {
    length: u32,
    name: [u8; length], // not zero-terminated
}
```

Assume this is ASCII. There is no zero-termination, so if this is required, allocate length + 1 bytes.

#### Textured materials

Textured materials are the same as GameZ, with the following exceptions:

* Mechlib materials cannot be cycled, so the `Cycled` flag (0x04) is never set, and the cycle pointer field is always zero (0)/null.
* As described, the `texture_ident` field is not an index, but a pointer. The pointer value is - as always - garbage from when the memory was dumped.
* The terrain/soil type is always `Default` (0).

#### Coloured materials

Untextured or coloured materials are the same as GameZ.

### Model files

Like the materials file, model files are very similar to but slightly different than models in `gamez.zbd` files. Model files are also quite complex.

First, some background. MechWarrior 3 uses so-called "nodes" to represent information in the engine. There are hints to this in the reader files and interpreter scripts. In `mechlib.zbd`, the only allowed node type is a 3D object node. GameZ files can contain other nodes.

I describe [all nodes](gamez/nodes.md) separately, since the structures are rather large. As a quick refresher, all nodes share a base structure, and then have node type specific data.

I also describe [mesh data structures in GameZ](gamez/#meshes_mw), since they are largely the same.

## Investigation (PM)

The expansion files are similar to the base game, however many data structures around the nodes have changed.

### Format and version

Both of these files are four (4) bytes long, and can be read as either a u32 or i32. The format value is always one (1). The version value is 41 for the expansion.

### Materials

Materials are read exactly the same as the base game.

### Model files

Model files are ready the same way as the base game, but many data structures are different. Note that while in the base game, only 3D object nodes are allowed, in the expansion both 3D object nodes and LOD (level of detail) nodes are present.

I describe [all nodes](gamez/nodes.md) separately, since the structures are rather large and shared with GameZ files.

I also describe [mesh data structures in GameZ](gamez/#meshes_pm), since they are largely the same.

## In-game use

These models are used in-game and in the mechlab screen.
