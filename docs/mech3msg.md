# Message table/translations (Mech3Msg)

The `Mech3Msg.dll` contains localised strings that are used by the game engine for displaying either English, German, or French text. Some of these strings are referred to by message keys (`MSG_`) in e.g. reader files.

## Investigation

`Mech3Msg.dll` has a single export:

```console
$ rabin2 -E Mech3Msg.dll
[Exports]

nth paddr      vaddr      bind   type size lib          name
――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
1   0x00000b20 0x10001720 GLOBAL FUNC 0    Mech3Msg.dll ZLocGetID
```

This is somewhat unusual for a DLL that is ~120 KB in size. It also doesn't use many functions:

```console
$ rabin2 -s Mech3Msg.dll
[Symbols]

nth paddr      vaddr      bind   type size lib          name
――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――
1   0x00000b20 0x10001720 GLOBAL FUNC 0    Mech3Msg.dll ZLocGetID
1   0x00001000 0x10002000 NONE   FUNC 0    MSVCRT.dll   imp._initterm
2   0x00001004 0x10002004 NONE   FUNC 0    MSVCRT.dll   imp.malloc
3   0x00001008 0x10002008 NONE   FUNC 0    MSVCRT.dll   imp._adjust_fdiv
4   0x0000100c 0x1000200c NONE   FUNC 0    MSVCRT.dll   imp.free
```

And only links to `msvcrt.dll` (`rabin2 -l Mech3Msg.dll`), which is Microsoft's Visual C Runtime (MSVCRT). This hints that the DLL does not contain much functionality code-wise.

Printing the sections (`rabin2 -S Mech3Msg.dll`) shows the `.rsrc` section is the biggest, followed by `.data`. Printing the strings (`rabin2 -z Mech3Msg.dll`) shows that there are a lot of strings in both of these sections. Printing the resources shows that it contains a message table:

```console
$ rabin2 -U Mech3Msg.dll
Resource 0
  name: 1
  timestamp: Thu Jan  1 00:00:00 1970
  vaddr: 0x1000e060
  size: 64.9K
  type: MESSAGETABLE
  language: LANG_ENGLISH
```

The German version predictably has the language `LANG_GERMAN`. This isn't an uncommon way of handling localisation, and is known as a [resource-only DLL](https://docs.microsoft.com/en-us/cpp/build/creating-a-resource-only-dll). Microsoft describes a similar approach to ["localizing message strings"](https://docs.microsoft.com/en-us/windows/win32/wes/localizing-message-strings). What is uncommon is the export, since resource-only DLLs usually contain no code.

The message table accounts for the strings in `.rsrc`, but not in `.data`.

However, the strings in the `.data` section all begin with the same prefix: `MSG_`. This also provides some indication of what the `ZLocGetID` function does. After simply trying some different arguments, it becomes apparent that when `ZLocGetID` is passed one of those message keys, it returns an unsigned 32-bit integer which corresponds to the entry ID in the table. So `ZLocGetID` and the `.data` section map human-readable strings to message table entry IDs. In Python - but only using a 32-bit version of Python and on Windows - this can be done as follows:

```python
import ctypes
import ctypes.wintypes

lib = ctypes.CDLL("Mech3Msg.dll")
ZLocGetID = lib.ZLocGetID
ZLocGetID.argtypes = [ctypes.c_char_p]
ZLocGetID.restype = ctypes.c_int32

message_id = ZLocGetID(message_name)
```

Of course, enumerating the message keys via `ZLocGetID` is also not easy; a brute-force approach could take a long time. So message keys still need to be extracted from the `.data` section (see below).

The internal workings of `Mech3Msg.dll` are otherwise not interesting to this project. I think the DLL probably uses binary search to be able to quickly look up the entry IDs by message keys (at least, that's how I would've done it in 1999 and with C). Binary search requires the message keys to be sorted, which could be done at compile time, or run time. For a replacement `Mech3Msg.dll`, with a modern language, a hash-table/dictionary lookup would be more than sufficient. Or using C on a modern processor, a linear search would be fast enough.

Bonus facts:

1. Not all messages are looked up by the message key! See below in "in-game use".
1. Not all messages have corresponding values in the message table - it was probably easier to leave them in, knowing they're unused in the engine than recreate this data.
1. Some messages are zeroed out by the patch, for example `MSG_GAME_NAME_DEBUG_VER`. Rather interesting.

## In-game use

Some messages are looked up directly by entry ID. I found this out when I didn't preserve the entry IDs in a replacement DLL, and the "insert CD" message was incorrect. Even though new messages are added and old messages are removed in the new versions/patches, they preserve entry ID numbering between versions. A replacement DLL should also do this. A re-implementation doesn't have to.

Presumably, most messages are looked up by message key by the engine. Some reader files also reference message keys, which are presumably dynamically looked up when interpreting reader files.

## Reading the message table

Luckily, Windows resources are somewhat well documented, either by Microsoft or third-parties. There are two options. On Windows, it is possible to use Windows APIs to read these resources, via [`LoadLibraryEx`](https://docs.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibraryexw), and then `FindResource`/`LoadResource`, or [`FormatMessage`](https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-formatmessage) specifically for message tables. The problem with the former functions are they less helpful for message tables, as the raw message table still needs to be parsed. The problem with the latter function is that it requires a message ID to load a specific message. Alternatively, it's trivial to read the entire message table on any platform/operating system.

There exist many libraries for parsing Portable Executables (PE), which is the ["file format for executables, object code, DLLs and others used in 32-bit and 64-bit versions of Windows operating systems"](https://en.wikipedia.org/wiki/Portable_Executable). They can often parse resource definitions also. So getting the raw message table data should be easy, especially since there is only one resource in the DLL. If a library doesn't support this, then the best approach is to [parse the `.rsrc` section](https://docs.microsoft.com/en-us/windows/win32/debug/pe-format#the-rsrc-section) and look for `RT_MESSAGETABLE = 11 (0x000B)`, and the appropriate locale ID `en_US = 1033 (0x0409)`.

The format of the message table is described by [`MESSAGE_RESOURCE_DATA`](https://docs.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-message_resource_data), [`MESSAGE_RESOURCE_BLOCK`](https://docs.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-message_resource_block), and [`MESSAGE_RESOURCE_ENTRY`](https://docs.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-message_resource_entry), although they are pseudo-structures. Note that since MechWarrior 3 is a 32-bit application (as discussed in the introduction), the alignment for data is 32-bit or 4 bytes.

First, the number of blocks is read (u32). Next, the blocks are read, which are the low ID (u32), high ID (u32), and the offset to entries (u32):

```rust
struct Block {
    low_id: u32,
    high_id: u32,
    offset_to_entries: u32,
}

struct Data {
    count: u32,
    blocks: [Blocks; count],
}
```

Finally, the entries are read by iterating over the blocks, the most complicated step (but still easy).

For each block, it's offset from the start of the message table data is given. Blocks should be sequential, so it should be possible to simply iterate through the data, but I would recommend seeking to the position anyway. Since the entries are grouped into blocks, the entries from low ID (inclusive) to high ID (inclusive!) are read per block. The inclusive high ID can be a bit of a trap. It's very easy to not read the highest ID in a block by being off-by-one. For a block with only one message, the low ID and high ID are the same. For a block with two messages, the low ID could be e.g. 1 and the high ID would be e.g. 2. So in Python, the entry ID would be: `for entry_id in range(low_id, high_id + 1)`.

```rust
struct Entry {
    length: u16,
    flags: u16,
    message: [u8; length - 4], // zero-terminated/padded
}
```

For each entry, the length is read first (u16), which is the length of the entire entry. Then the Unicode flags are read (u16). Expect this to be 0, since the messages are not Unicode (which in Microsoft-land means UTF-16 LE). Instead, the messages are encoded using the codepage appropriate for the language of the message table (aka. locale ID). Luckily for extraction, the English, German, and French locale IDs map to the same codepage (1251). This means that the messages simply need to be read with the codepage encoding, and they will decode properly (I have tested this on the German strings). So it is simply a matter of reading length - 4 bytes (remember, the length includes itself and the flags field) to get the message data, which is not quite the same as the message.

Messages are padded to be 32-bit aligned with null bytes (`\0`). Even though the length is known, messages have at least one null byte at the end (zero-terminated), presumably for C interoperability. Since codepage 1251 shares the first 128 characters with ASCII, these can be safely stripped before decoding the string (i.e. in byte form), or afterwards.

Additionally, even single line messages are terminated with the DOS/Windows line ending `\r\n` (this isn't always the case, but common and true in this case). As long as they are at the end of the message, you may wish to also strip these for convenience. Messages can also contain DOS/Windows newlines within the message, which should be preserved.

It's also worth pointing out that some of the messages contain formatting placeholders, that are specific to those messages. There is no way of knowing what values were intended, other than looking for the format placeholders (e.g. `%1`, `%2`) and inferring this from the context of the message (or reverse-engineering the engine, which this project does not encourage).

## Reading the message keys

Presumably, you'll be using a PE parsing library. Start from the `.data` section. The first bytes are not important to understand. They are part of [the common runtime (CRT) initialisation](https://docs.microsoft.com/en-us/cpp/c-runtime-library/crt-initialization), generally called `.CRT$XCA`/`__xc_a`, `.CRT$XCU_`, and `.CRT$XCZ`/`__xc_z`. For MechWarrior 3 or Pirate's Moon, simply skip or read these four (4) u32 values (16 bytes). They should all be zero. For Recoil, skip 48 bytes.

The data that follows are clearly constants defined in the original code. There is a sort of entry table for the message keys, that consists of the absolute memory offset of the message key string (u32), and the corresponding message table entry ID (u32). There is no easy way of knowing when the table has fully been read. I suggest checking if the offset is in the bounds of the `.data` section, since the string data produces values outside this range when accidentally interpreted as an integer.

Given the memory offset of the start of the `.data` section, the relative offset of the message key is easy to determine by subtracting the start offset from the absolute offset read previously. Seek to that position, and read the message key until encountering a null byte (`\0`). All message keys will be ASCII.

For manual verification, it's possible to use e.g. `rabin2` to extract the strings, filter only the ones beginning with `MSG_`, and compere that to the result of parsing the `.data` section.
