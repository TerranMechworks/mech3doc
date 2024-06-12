# Reader archives / binary reader files

Reader archives hold most of the games configuration in a Lisp-like list structure. Fair warning though that some of this information is duplicated inside `anim.zbd` files!

Binary and text reader files have the file extension `.zrd`, which could stand for Zipper Reader. Until 2022, I only knew of binary reader files. However, there exist [text reader files](text-reader-files.md), for example `DefaultCtlConfig.zrd`.

## Investigation (MW3)

Once it is known how to read [archive files](archive-files.md) (from e.g. the sound archives), the reader data is easy to figure out, since the binary structure is very simple and consistent.

To read a value, first a u32 (or i32) is read. This is the type of value, where 1 means integer (i32), 2 means float (f32), 3 means string, and 4 means list. No other types are seen. You can also think of the values as a tagged/discriminated union or a sum type.

For reading string values, read a u32 (or i32), which is the number of bytes in the string. Then read that many bytes. There is no zero-termination! One trap is that the string encoding is not exactly known. It could depend on the system's codepage. Interpreting the string as ASCII (0-127) seems to be the safest option, and the reader files never use values outside of ASCII. Another option would be to use codepage 1252 for the encoding.

For reading list values, simply read a u32 (or i32), which is the number of values in the list plus one (!). Then, read count - 1 items. Empty lists do exist, and list values can be of different types (so it is more like a tuple).

```rust
struct Integer {
    type_: u32, // always 1
    value: i32,
}

struct Float {
    type_: u32, // always 2
    value: f32,
}

struct String {
    type_: u32, // always 3
    length: u32,
    value: [u8; length], // not zero-terminated/padded
}

struct List {
    type_: u32, // always 4
    count: u32,
    values: [Integer/Float/String/List; count - 1],
}
```

The outermost value in a reader file seems to always be a list, so the data structure is self-terminating. This makes it easy to read the entire file.

While the binary structure is simple and consistent, the end result is not necessarily easy to consume. First, "keyed" data is annoying to look up for modern standards. There is no dictionary/map/object type. This means it's necessary to find the key in the list, and then the next index could be the data. There is no requirement a key is unique in a list. There is no requirement a key is followed by only one value. Sometimes, the following values are contained in a list (of size 1), sometimes, not:

```
[
    "key1",
    ["value1"],
    "key2",
    0.5,
    "key3",
    0.3,
    0.4,
]
```

Some lists are clearly a certain data type in the engine, but might contain different numbers of items, e.g. just a node name `["target_node"]`, a node name and translation `["target_node", 0.0, 0.0, 0.0]`, and potentially more forms.

So it seems like data lookup/interpretation is completely custom. Still, with a bit of care, it's possible to infer this and write code that uses the data.

## Investigation (PM)

In Pirate's Moon, reader archives gained a checksum. They are the only archive type this is used for. Presumably, this was to make game modification harder, maybe to curb cheating online? Otherwise, they haven't changed.

## In-game use

Reader files configure most of the game. However, animation definition archives (`anim.zbd`) contain the same animation definitions as the reader files, but compiled into better-defined C structures. So modifying an animation definition in a reader file may not change the game's behaviour. It's likely this was done because there are many animation definitions, and parsing them from the relatively unstructured reader files would make load times very long.

Converting reader files to animation definition archives faces the same problem as interpreting the reader data (custom code required). It's likely the development team had a tool to do this, or maybe the engine could dump animation definition archives from the loaded reader data (since the `anim.zbd` files look a lot like memory dumps with e.g. pointer values serialised).
