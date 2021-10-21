# Interpreter scripts

The interpreter scripts drive how the game engine loads the game data/worlds. They are all contained in a single file, `interp.zbd`.

## Investigation

This is a quite short file, which is good. It is not an archive file.

```rust
struct Header {
    signature: u32, // always 0x08971119
    version: u32, // always 7
    count: u32,
}
```
The file starts with a signature (u32, magic number `0x08971119`), a version (u32, always 7), and the number of scripts/count (u32). A table of contents (TOC) with script entries follows, which is easy to read since the count is known:

```rust
struct Entry {
    path: [u8; 120], // zero-terminated/padded
    last_modified: u32,
    offset: u32,
}

type Entries = [Entry; count];
```

The entry path seems to be an 120 byte string, ASCII, which is zero-terminated and padded with zeros/nulls. This can contain backslashes. They have the file extensions `.gw` and `.gs`, which one could guess to be game world and game script, respectively.

I have had success interpreting the last modified value as a timestamp, which gives datetimes around 1999 (for the v1.2 version). However, they may be some local timezone, and not UTC.

Finally, the offset is simply where the interpreter script data starts in the file. The the script data is written in the same order as the entries in the TOC, with no padding, so for reading all the data (instead of jumping to a script), it isn't strictly necessary. The script data must also be self-terminating, since the length isn't recorded in the TOC.

And indeed, immediately after the TOC the script data follows. Each script contains several lines. First, the size/length of the line (u32) is read. If it is zero (0), then the script is complete. Next, the token count of the line is read (u32). This indicates how many tokens the line contains.

The line is exactly size bytes. It contains exactly token count zero/null bytes (`\0`). These deliniate the arguments, so for two arguments, there are three tokens in a line: `CommandName\0Argument1\0Argument2\0`. The line should always end with a null byte (zero-terminated). There is no extra padding.

Null bytes or characters where probably chosen because they make splitting/tokenising the line trivial in C. However, since the command name and arguments don't contain spaces, it seems to be safe to convert the null bytes to spaces (if this is more convenient), and strip the final null byte.

```rust
struct Line {
    length: u32,
    token_count: u32,
    line: [u8; length],
}
```

Decoding the line as ASCII is safe, as is any ASCII-compatilbe encoding such as codepage 1251 or UTF-8. Encoding should probably be limited to ASCII though.

## In-game use

Although the workings of the interpreter are obviously game engine internals, the commands are all human readable and self-describing. Presumably, the interpreter is driven by these scripts, and so they affect how most of the data is loaded. This can be seen from e.g. `c1.gs`:

```
ifdef USEZBD
GameZReadZBDFile %GAMEZ%
endif
ifndef USEZBD
... world setup code
endif
```

This looks like the interpreter scripts enabled prototyping of worlds before the assets were packed into a `gamez.zbd` file, probably for faster game development iteration. It also gives a bit of insight in how the game data is structured. There are several references to nodes, which indicates world data is maybe represented as a tree-like structure.

A comprehensive study of the filepaths in the interpreter scripts could maybe reveal how the game engine loaded unpacked/loose asset files, and make modding the existing engine easier.
