# Texture packages

Texture packages hold textures or images, used throughout the game.

## Investigation

I've had to awkwardly name the texture files "packages". They contain several textures/images, but are not [archive-based](archive-files.md). Most of them are for textures, but textures are simply images mapped to 3D surfaces. Since all textures are images, but not all images are textures, I'll call the data an image, not a texture.

MW3 and PM texture packages are read in exactly the same way. The only difference is that in the base game, no package uses global palettes.

## File structure

Packages start with a header:

```rust
struct Header {
    unk00: u32, // always 0
    unk04: u32, // always 1
    global_palette_count: i32, // or u32
    image_count: u32, // or i32
    unk16: u32, // always 0
    unk20: u32, // always 0
}
```

Only two fields in the header are useful. The global palette count (i32 or u32) indicates how many global palettes are used. The base game doesn't use them, so this will be zero (0). The expansion does for some packages. It's recommended to read this as an i32, as textures that don't use a global palette signify this with -1. The image count (u32 or i32) is self-explanatory, and should be at least one (1) or more. Next there is a table of contents, with image count entries:

```rust
struct Entry {
    name: [u8; 32], // zero-terminated/padded
    start_offset: u32,
    global_palette_index: i32,
}
```

The name of the image is a 32 byte string; assume ASCII encoding. It is zero-terminated and padded with zeros/nulls. The start offset (u32) is the offset of the image data in the package. This means the image data must be self-describing/self-terminating. The global palette index indicates if/which global palette is used. Images that don't use a global palette have this set to -1; otherwise the index is between 0 (inclusive) and global palette count (exclusive).

If there are any global palettes, they are read next. Global palettes are always 512 bytes long, or 256 * u16 packaged colour values in RGB565 format. How to interpret and unpack these values is described a bit later.

```rust
struct GlobalPalette {
    values: [u16; 256], 
}
// alternatively
struct GlobalPalette {
    values: [u8; 256 * 2],
}
```

Next, the image data is read in the same order as in the TOC. The data is read contiguously, so the start offset isn't needed. Or, it can be used for verification that the image data has been read completely, since the length of the image data isn't known from the TOC.

Each images starts with a header of information:

```rust
struct ImageInfo {
    flags: ImageFlags,
    width: u16,
    height: u16,
    unk08: u32, // always 0
    palette_count: u16,
    stretch: ImageStretch,
}

enum ImageStretch: u16 {
    None = 0,
    Vertical = 1,
    Horizontal = 2,
    Both = 3,
}

bitflags ImageFlags: u32 {
    ColorDepth = 1 << 0,    // 0x01
    HasAlpha = 1 << 1,      // 0x02
    NoAlpha = 1 << 2,       // 0x04
    FullAlpha = 1 << 3,     // 0x08
    GlobalPalette = 1 << 4, // 0x10
    ImageLoaded = 1 << 5,   // 0x20
    AlphaLoaded = 1 << 6,   // 0x40
    PaletteLoaded = 1 << 7, // 0x80 
}
```

First, the flags. The first flag, which is assumed to be related to colour depth, is always set and isn't further important - the colour depth is always 16 bit/2 bytes per pixel.

Next are the alpha channel flags, which are a mess. If "no alpha" is set, then "has alpha" and "full alpha" must not be set. This indicates the image has no alpha channel. If "no alpha" is unset, then "has alpha" must be set. This indicates the image has an alpha channel. If "full alpha" is set, then the alpha channel data is 8 bits/1 byte per pixel; otherwise, the alpha channel/transparency is derived from the colour information and there is no alpha channel data. The exact way the alpha channel is loaded is discussed with the image data.

The global palette flag is set if and only if the entry in the TOC specified a global palette index.

Finally, the last three flags are assumed to be some indication of what data the game engine has loaded. They can be safely ignored for interpreting the image data, but do occur in the files.

The width (u16) and height (u16) are obvious. The next value (u32) is unknown, but always zero (0). The palette count (u16) specifies how many colour values the palette contains. Images that aren't palette-based have this set to zero (0). Importantly, this applies to both global and local palettes. So even though global palettes have enough data for 256 colour values, fewer colours may be used when interpreting image data.

Lastly, the stretch field indicates if an image should be stretched after it has been decoded/before it is displayed. This seems to be used for e.g. environment textures that require more vertical resolution than horizontal resolution, possibly to save space but still have the image be square (I think square textures used to provide a performance benefit for some graphics cards/operations). 

## Image data

### Colour image pixel data (not palette-based)

Colour images are images with a zero palette count. The colour data is read first. It is a bitmap with two (2) bytes per pixel of size width * height (so width * height * 2 bytes in total).

```rust
struct ColorData {
    values: [u16; width * height], 
}
// alternatively
struct ColorData {
    values: [u8; width * height * 2], 
}
```

Each pixel is 2 bytes/16 bits, and is a packed RGB format known as 565. This was determined by trying out different packed RGB formats and seeing if the colours look correct. The RGB565 format means red has 5 bits, green has 6 bits, and blue has 5 bits of information. This is the layout in memory, where each cell is a byte/u8:

```
|GGGBBBBB|RRRRRGGG|
|7      0|7      0|
```

If read as one little-endian u16 (the default on x86), this is the layout:

```
|BBBBBGGG GGGRRRRR|
|^    ^      ^   ^|
|0    5 7 8  11 15|
```

While it is important to know the bit patterns, there's a temptation to extract the individual colour values. But in my experience, this isn't a good approach. Let's take a minute to think about how to map an RGB565 encoded pixel to the standard RGB888 encoding (where each colour value occupies 1 byte). Simply shifting a 5 or 6 bit value doesn't produce full brightness:

```rust
let value = (0b11111 << 3);
value == 0b11111000; // => true
value < 0b11111111; // => true
```

So simple shifting produces a darker than usual image. Instead, the values have to be interpolated. I don't know enough about computer graphics to say if it is important to apply gamma correction when mapping from RGB565 to RGB888, so I've assumed the assets are stored in linear RGB and therefore linear interpolation is correct.

5 bit values range from 0 to 31 (inclusive), 6 bit values range from 0 to 63 (inclusive), and 8 bit values range from 0 to 255 (inclusive). This means that the values can be mapped to a floating point value in the range of 0.0 to 1.0 (inclusive) by dividing by the maximum (either 31 or 63), and then the floating point value can be mapped to the 8 bit range by multiplying by the maximum (255). For floating point accuracy reasons, I believe it's best to multiply first, and then divide. The result should be the same.

Finally, the floating point value must be converted to an integer. Rounding should be considered, as often, converting to an integer often simply truncates the fractional/decimal part. But rounding is also complicated, and there are several strategies like banker's rounding/rounding half to even. Given the input is limited in precision, I've simply chosen to round up, with a nice trick that adding 0.5 to a (positive) floating point value before truncating rounds up.

With this, it's easy to build a lookup table to map any RGB565 colour value to an RGB888 values, which is much faster than doing this conversion for each pixel. A Rust implementation could look like this:

```rust
let rgb888: Vec<u32> = (u16::MIN..=u16::MAX)
    .map(|rgb565| {
        let red_bits = (rgb565 >> 11) & 0b11111;
        assert!(red_bits <= 31, "r5 {:#b}", red_bits);
        let red_lerp = ((red_bits as f64) * 255.0 / 31.0 + 0.5) as u32;
        assert!(red_lerp < 256, "r8 {:#b}", red_lerp);
    
        let green_bits = (rgb565 >> 5) & 0b111111;
        assert!(green_bits <= 63, "g6 {:#b}", green_bits);
        let green_lerp = ((green_bits as f64) * 255.0 / 63.0 + 0.5) as u32;
        assert!(green_lerp < 256, "g8 {:#b}", green_lerp);
    
        let blue_bits = (rgb565>> 0) & 0b11111;
        assert!(blue_bits <= 31, "b5 {:#b}", blue_bits);
        let blue_lerp = ((blue_bits as f64) * 255.0 / 31.0 + 0.5) as u32;
        assert!(blue_lerp < 256, "b8 {:#b}", blue_lerp);
    
        (red_lerp << 16) | (green_lerp << 8) | (blue_lerp << 0)
    })
    .collect();

// black
assert_eq!(rgb888[0b0000000000000000], 0x000000);
// white
assert_eq!(rgb888[0b1111111111111111], 0xFFFFFF);
// red
assert_eq!(rgb888[0b1111100000000000], 0xFF0000);
// green
assert_eq!(rgb888[0b0000011111100000], 0x00FF00);
// blue
assert_eq!(rgb888[0b0000000000011111], 0x0000FF);
// red + green
assert_eq!(rgb888[0b0000011111111111], 0x00FFFF);
// red + blue
assert_eq!(rgb888[0b1111100000011111], 0xFF00FF);
// green + blue
assert_eq!(rgb888[0b1111111111100000], 0xFFFF00);
```

The same approach can be used for decoding colour image data and palette colour data.

### Colour image simple alpha

The alpha channel for a colour image with simple alpha (so not full alpha) is derived from the colour data. A completely black pixel (`0x0000`) is 0% opaque/100% transparent (usually 0), any other colour is 100% opaque/0% transparent (usually 255).

### Colour image full alpha data

For an image with full alpha, the alpha channel data is read after the image data. It is a bitmap with one (1) byte per pixel of size width * height (so width * height bytes in total).

```rust
struct FullAlphaData {
    values: [u8; width * height], 
}
```

The values range from 0, which is 0% opaque/100% transparent, to 255, which is 100% opaque/0% transparent.

### Palette-based image pixel data

Palette-based images are images with a greater-than zero palette count. This means the image data is an array of palette indices, that are then mapped to colours via the palette. Palette-based images can either use a predefined global palette, or a palette specific to the image (local palette).

The palette index data is read first. It is a bitmap with one (1) byte per pixel of size width * height (so width * height bytes in total).

```rust
struct PaletteIndexData {
    values: [u8; width * height], 
}
```

I'll shortly discuss how to map this palette index data to colour data.

### Palette-based image simple alpha

It currently isn't known how to derive a simple alpha channel for palette-based images. This is due to a lack of interest. Since the palette-based images are more limited in colour due to palette quantisation (a maximum of 256 distinct colours), there is little reason to use them on modern PCs. Consequently, it hasn't been investigated. A common strategy for simple transparency in other palette-based image formats is to designate one index as transparent (e.g. likely the first, possibly the last, but some allow any index to be the transparent one).

### Palette-based image full alpha data

This is exactly like the colour image. It is a bitmap with one (1) byte per pixel of size width * height (so width * height bytes in total).

### Palette-based image palette colour data

If the image isn't using a global palette, the palette colour data is read after the palette index data and full alpha data (if any).

```rust
struct LocalPalette {
    values: [u16; palette_count], 
}
// alternatively
struct LocalPalette {
    values: [u8; palette_count * 2], 
}
```

Just like colour image data and global palette data, these are RGB565 format colour values.

If the image is using a global palette, then that must be restricted to the number of colour values indicated by palette count.

### Using palette-based image data

There are several options here. Some image formats support palette-based images. However, few support palette-based colour channels and a full alpha channel. For preservation, the best strategy might be to output the image data as a palette PNG and the alpha data as a grey scale PNG. Alternatively, it's obviously possible to map each pixel to RGB888 via the palette, and optionally store the palette separately.

## Recap

* All images have an image header
* For colour images:
  * Read the image data
  * Read the full alpha channel (if the image has one)
* For palette-based images:
  * Read the palette index data
  * Read the full alpha channel (if the image has one)
  * Read the local palette colour data (if not using a global palette)

## In-game use

Textures and images are used basically everywhere.
