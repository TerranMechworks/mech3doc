# Pseudo-code conventions

All data types are little endian, unless noted otherwise. All strings are 8-bit US-ASCII, unless noted otherwise (i.e. a character occupies a byte, but only the lower 7 bits are used, the most significant bit is always zero).

All data types and structures are specified in pseudo-Rust code. If you do not know Rust, it should still be familiar.

Unsigned types are designated with `u<bits>`:

* `u8` is `uint8_t` or `unsigned char`/`byte` in C
* `u16` is `uint16_t`
* `u32` is `uint32_t`
* `u64` is `uint64_t`

Signed types are designated with `i<bits>`:

* `i8` is `int8_t` or `signed char`/`char` in C
* `i16` is `int16_t`
* `i32` is `int32_t`
* `i64` is `int64_t`

Floating point types are designated with `f<bits>`:

* `f32` is a single-precision IEEE 754 floating point number, `float` in C
* `f64` is a double-precision IEEE 754 floating point number, `double` in C

Note that for many integer data types, we don't know the exact bit size, or even if they are signed or unsigned, unless e.g. an obviously signed value was observed.

Fixed-length and variable length arrays are designated with `[<type>; <length>]`, where the length may not be a valid Rust definition (for example, if it depends on another field).

Constants are aliases for a certain value that makes it convenient to reference by name. Constants will always have a data type specified.

``` rust
const EXAMPLE: u32 = 1;
```

Structures are basically memory views/instructions on how to interpret a block of memory. Assume a C-compatible layout and 32 bit alignment (discussed more shortly). They have a name, and then list fields by name followed by a value. An example:

``` rust
struct Example {
    foo: u32,
    bar: [f32; foo - 4],
}
```

This means read an unsigned integer of 32 bits/4 bytes, and then read `foo - 4` 32 bits/4 bytes floating point numbers.

For structures where the use of a field isn't known, they will be designated with "unk" and the offset of the field in the structure, e.g. `unk08`. Because MechWarrior 3 is a 32-bit executable and most likely written in C++ (based on the dependencies), the structures the game actually uses will follow those padding rules. The structures provided will either be already 32-bit aligned, or will have explict padding fields, designated with "pad" and the offset.

Tuples are sequences of types/elements. This is similar to structures, except that the fields aren't named:

``` rust
tuple Example(f32, f32, f32);
```

This means a structure of 3 floating point values where the field names/usages aren't considered important. I will try to avoid tuples, but they are occasionally useful. You may always translate tuples into structures by naming the fields.

Enumerations are exclusive values, so only a single value is valid. The enumeration will have a integer type that indicates it's size when read. Zero (0) is not generally a valid value unless explicitly named:

```rust
enum Example: u16 {
    A = 1,
    B = 2,
}
```

Bitflags are similar to enumerations, but can have multiple values set or unset:


``` rust
bitflags Example: u16 {
    A = 1 << 0, // 0x1
    B = 1 << 1, // 0x2
}
```

This means that zero (0) is generally valid (this means all unset). For the example, valid values are:

* 0
* 1 = A
* 2 = B
* 3 = A | B

Bitflags may also contain aliases of common flag combinations.
