# Beginner's guide to hex viewing

You'll need a hex viewer or editor. On Windows, I strongly recommend [HxD](https://mh-nexus.de/en/hxd/). This guide is specifically for 32-bit inspection, so 64-bit values are unlikely.

## Endianness

[Endianness](https://en.wikipedia.org/wiki/Endianness) is an important concept, but complicated. I'll cover the minimum necessary. x86 CPUs all use little endian. This means if you have a 32-bit value, for example `0xDEADBEEF`, it is stored in memory as `[0xEF, 0xBE, 0xAD, 0xDE]`.

```plain
0xDEADBEEF
  | | | |  (mem)
  | | | +- 0xEF
  | | +--- 0xBE
  | +----- 0xAD
  +------- 0xDE
```

This is slightly unintuitive, but luckily, most hex viewers will be able to display the decoded values.

## Integers

Integers can be either signed or unsigned. Unsigned integers can be zero, or positive. Signed integers can be negative, zero, or positive. Zero has no sign (there is only 0, not +0 and -0). Both signed and unsigned integers have a size; generally 8, 16, 32, or 64 bits (1, 2, 4, or 8 bytes).

Unsigned

| Size    | Min (dec) | Min (hex)  | Max (dec)  | Max (hex)  |
| :------ | --------: | :--------- | ---------: | :--------- |
| 8 bit   | 0         | 0x00       | 255        | 0xFF       |
| 16 bits | 0         | 0x0000     | 65535      | 0xFFFF     |
| 32 bits | 0         | 0x00000000 | 4294967295 | 0xFFFFFFFF |

Signed

| Size    | Min (dec)   | Min (hex)  | -1 (hex)   | 0 (hex)    | Max (dec)  | Max (hex)  |
| :------ | ----------: | :--------- | :--------- | :--------- | ---------: | :--------- |
| 8 bit   | -128        | 0x80       | 0xFF       | 0x00       | 127        | 0x7F       |
| 16 bits | -32768      | 0x8000     | 0xFFFF     | 0x0000     | 32767      | 0x7FFF     |
| 32 bits | -2147483648 | 0x80000000 | 0xFFFFFFFF | 0x00000000 | 2147483647 | 0x7FFFFFFF |

As you can see, for signed integers, the sign is encoded in the top-most bit (most significant bit or MSB). The negative values are also not intuitive, since they are encoded in [two's complement](https://en.wikipedia.org/wiki/Two%27s_complement). It's helpful to know this; but again most hex viewers can decode signed integers.

In general, unless you see an obviously signed value (for example, anything above 0x80000000 where > 2147483647 would be too large), it's impossible to tell if the type is signed or unsigned from the reverse engineering. Also, due to little endian storage, if you see the bytes `[0x7F, 0x00, 0x00, 0x00]` (`7F000000`), you cannot tell if this is a) a 32-bit integer with the value 127, b) two 16-bit integers with the values 127 and 0, or even c) four 8-bit integers with the values 127, 0, 0, 0.

### Quiz

The [quiz001](quiz001.bin) file contains some values, all of the same type. Can you tell what type of integer (and therefore how many they are), and what the values are?

<p><details>
<summary>Reveal answer</summary>
<p>
There were ten 32-bit signed integers: 111, 9999, 10, 2000, 10, -200, 10, 0, 1, 100000
</p>
</details></p>

## Floating point values

Floating point values basically encode a number in scientific notation, see [IEEE 754](https://en.wikipedia.org/wiki/IEEE_754). The information of a signed bit, the exponent, and the fraction is encoded into either 32 or 64 bits (called single or double precision, respectively). For example, a 32-bit floating point value is packed as follows:

```plain
0 01111100 01000000000000000000000 = 0.15625
| |      | |                     |
| exponent      fraction
sign
```

A normal human can't be expected to decode this; the hex viewer will help here also. However, with a small amount of practice, you can recognise some values.

* 1.0 is 0x3F80000
* -1.0 is 0xBF800000
* 10.0 is 0x41200000
* -10.0 is 0xC1200000
* 100.0 is 0x42c80000
* -100.0 is 0xC2C80000

However, 0.0 is 0x00000000, and so indistinguishable from an integer! In this documentation, I try to denote floating point values with a decimal point and at least one place to distinguish them from integers, e.g. 10 is an integer, 10.0 is a float.

### Quiz

The [quiz002](quiz002.bin) file contains a mix of 32-bit integers and 32-bit floats. Can you tell what the values are?

<p><details>
<summary>Reveal answer</summary>
<p>
The values were 9999, 0.5, -0.5, 1, -1, 200, 200.0, and indeterminate (could have been 0/integer or 0.0/float).
</p>
</details></p>

## Strings

Strings in C are basically arrays of ASCII/ANSI characters. Each character has a numeric value (see Wikipedia for an [ASCII table](https://en.wikipedia.org/wiki/ASCII)). This is why a lot of hex viewers also show an ASCII view next to the hex view, and simply skip non-printable characters. Because each character is a byte, you do not need to worry about endianness for ASCII strings:

```plain
b"Hello world" = 48 65 6c 6c 6f 20 77 6f 72 6c 64
```

Strings in C are usually terminated with a null or zero character (`\0`, 0xFF); this is called zero-terminated. So "Hello world" would actually be `48656c6c6f20776f726c6400`.

Strings are either stored as fixed length or with a known length encoded before the string. Fixed length strings are usually padded with zeros, so encoding "Hello world" as a 16 length string is:

```plain
b"Hello world\0\0\0\0\0" = 48656c6c6f20776f726c640000000000
```

However, the padding can also be garbage if the programmer forgets to zero the memory, so this is also "Hello world": `48656c6c6f20776f726c6400DEADBEEF` (note this is still zero-terminated). For a known-length string, "Hello world" could be either:

```plain
# Zero terminated
b"Hello world\0" = length 12 = 0c000000 48656c6c6f20776f726c6400
# (b'\x0c\x00\x00\x00Hello world\x00' in Python)
# Not terminated
b"Hello world" = length 11 = 0b000000 48656c6c6f20776f726c64
# (b'\x0b\x00\x00\x00Hello world' in Python)
```

Assuming the length is encoded as a 32-bit integer.

### Quiz

The [quiz003](quiz003.bin) file contains several strings. They are separated by `DEADBEEFDEADBEEFDEADBEEF`. Can you tell what type of strings they are, and what the values were?

<p><details>
<summary>Reveal answer</summary>
<p>
<ol>
<li>Fixed length of 32: "Lorem Ipsum"
<li>Variable length, not terminated: "The quick brown fox"
<li>Fixed length of 16: "DEADBEEF" (note that the string here is encoded in ASCII, which is not the same as <code>0xDE, 0xAD, 0xBE, 0xEF</code>)
<li>Fixed length of 16: "Hello world", with padding of "Padx"
<li>Variable length, zero terminated: "The quick brown fox\0"
</ol>
</p>
</details></p>

## Structures

This is a vast oversimplification, but structures basically describe a view/block of memory, that makes it easier to work with in code. They are usually collection of fields, although the field names are identifiers in the source code only, and not present in the actual memory. For example, given this C structure:

```C
struct Foo {
    uint32_t a;
    float a;
}
```

Then `Foo { a = 100, b = 100.0 }` would be encoded as:

```plain
64000000 0000c842
```

When reverse engineering, the structure definitions is what we're usually trying to recover. I'll be using pseudo-Rust code to describe structures, as in the rest of the documentation (as opposed to C code).

### Quiz

Reverse engineer the structure of [quiz004](quiz004.bin). All data types are 32-bit/32-bit aligned.

<p><details>
<summary>Reveal answer</summary>
<p>
The structure was:

```rust
struct Quiz010 {
    a: f32,
    b: [u8; 16],
    c: i32, // or u32
}
```

And the value was <code>Quiz004 { a: 1.5, b: "You can do it", c: 8888}</code>.
</p>
</details></p>
