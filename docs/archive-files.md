# Archive files

For both the base game and expansion, archive files can be recognised by a table of contents (TOC) at the end of the `.zbd` file. This is a common strategy to be able to easily add entries to an archive without rewriting the entire archive. The new entry is written at the end, i.e. it overwrites the TOC, and then the TOC is written out fully with the new entry. This avoids having to rewrite the rest of the entries.

Known archive files are [sound archives](sound-archives.md), [reader archives](reader-archives.md), [motion archives](motion-archives.md), [mechlib archives](mechlib-archives.md), and save games. Other `.zbd` files may also contain multiple files, but are not archive-based (for example interpreter scripts, texture files).

## Investigation (MW3)

The sound archives are good candidates to follow along, since their contents makes it obvious that the entry data is written from the start of the file (so the TOC must be at the end), and once extracted, you get `.wav` files that are easily validated to be correct (by listening to them).

For the base game, there are two fields at the end of the file:

```rust
struct Footer {
    version: u32, // always 1
    count: u32,
}
```

The version of the TOC (u32, at -8), and number of entries in the TOC (u32, at -4). The version will always be 1.

Each entry in the TOC is 148 bytes long:

```rust
struct Entry {
    start: u32,
    length: u32,
    name: [u8; 64], // zero-terminated/padded
    garbage: [u8; 76],
}
```

The start of the TOC is found by calculating the length of the TOC (number of entries * 148), adding the TOC "footer" (count, version) to that, and subtracting it from the length of the file, or seeking from the end of the file. Then read the entries.

Each entry specifies the start of the entry's data in the file, the length of the entry's data in the file, the name of the entry (zero-terminated, and padded with null bytes), and a field I've called "garbage". This can largely be ignored. It was supposed to be flags, a comment and the file time:

```rust
struct Entry {
    start: u32,
    length: u32,
    name: [u8; 64],
    flags: u32,
    comment: [u8; 64],
    time: u64,
}
```

Where the time is actually a [Windows `FILETIME` structure](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-dtyp/2c57429b-fdd4-488f-b5fc-9e4cf020fcdf). Ignore the low and high parts in the documentation, the easiest way to read this is as a 64-bit value, which is then "the number of 100-nanosecond intervals that have elapsed since January 1, 1601, Coordinated Universal Time (UTC)." (i.e. the Windows epoch).

Unfortunately, in some files (like the mechlib), the entry data was not properly zeroed out, and so this contains random memory.

Another trap is that entries are not necessarily deduplicated. There can be two or more entries with the same name. In all the files I have, entries with the same name contain the same data, but this isn't a guarantee.

How the entry data is interpreted depends on the archive type.

## Investigation (PM)

The Pirate's Moon archives are similar to the base game, but there are three fields and the end of the file, and they do not have a backwards-compatible layout:

```rust
struct Footer {
    version: u32, // always 2
    count: u32,
    checksum: u32,
}
```

The version of the TOC (u32, at -12), the number of entries in the TOC (u32, at -8), and a checksum of the file data (u32, at -4). The version will always be 2. If they had left the version at -8, this would have made reading the file easier.

The new field is the checksum. For archive types other than reader archives, it will be 0. Maybe it was too time intensive to calculate the checksum for the bigger archives, or maybe they only introduced it to prevent cheating by modifiying the reader files, which are relatively easy to understand. It's unclear why it wasn't made backwards compatible though, or why the other archives didn't keep using version 1.

The checksum is an incorrectly implemented [cyclic redundancy check](https://en.wikipedia.org/wiki/Cyclic_redundancy_check) (CRC32). It seems to be based on Ross William's [A Painless Guide To CRC Error Detection Algorithms](http://ross.net/crc/download/crc_v3.txt), specifically the "Roll Your Own Table-Driven Implementation" section. As noted in Michael Pohoreski (aka. Michaelangel007) excellent 
[CRC32 Demystified](https://github.com/Michaelangel007/crc32), for the code given the bits in each data byte aren't reversed. Of note is additionally the initialization value of `0x00000000`, and the fact that the final value isn't inverted/xor'd with `0xFFFFFFFF`, as some other implementations do. Based on this information, I have managed to write code for calculating the Pirate's Moon checksums using a pre-calculated table. The pre-calculated table used is a standard CRC32 with the polynomial `0x04C11DB7`, roughly:

```rust
for index in 0..256u32 {
    let mut crc = index << 24;
    for _ in (1..9).rev() {
        if (crc & 0x80000000) == 0x80000000 {
            crc = (crc << 1) ^ 0x04C11DB7;
        } else {
            crc = crc << 1;
        }
    }
    CRC32_TABLE[index] = crc;
}
```

A running CRC32 can then easily be calculated for arbitrary input, starting with the initial value:

```rust
pub const CRC32_INIT: u32 = 0x00000000;

fn crc32_update(crc: u32, buf: &[u8]) -> u32 {
    let mut crc = crc;
    for byte in buf {
        let index = (crc >> 24) ^ (*byte as u32);
        crc = CRC32_TABLE[index as usize] ^ (crc << 8);
    }
    crc
}
```

The CRC32 of an archive is calculated over all the entry data in the archive, in the order they are listed in the TOC, but does not include the TOC itself.

There is one more oddity for motion archives in PM. For these, the entry length will always be 1. The entry length can be calculated from the previous entry starting position, so e.g. sorting the entries by start, reversing them, and using the start of the TOC for the first (reversed)/last (unreversed) entry. Or, since the motion reading code can be made self-limiting, code can simply jump to the start and read the motion data.
