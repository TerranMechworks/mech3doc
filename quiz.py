from struct import pack

with open("quiz001.bin", "wb") as f:
    f.write(pack("<10i", 111, 9999, 10, 2000, 10, -200, 10, 0, 1, 100000))

with open("quiz002.bin", "wb") as f:
    f.write(pack("<iffiifi", 9999, 0.5, -0.5, 1, -1, 200, 200.0, 0))

with open("quiz003.bin", "wb") as f:
    f.write(pack("<32s", b"Lorem Ipsum"))
    f.write(bytes.fromhex("DEADBEEFDEADBEEFDEADBEEF"))
    v2 = b"The quick brown fox"
    f.write(pack("<I", len(v2)))
    f.write(v2)
    f.write(bytes.fromhex("DEADBEEFDEADBEEFDEADBEEF"))
    f.write(pack("<16s", b"DEADBEEF"))
    f.write(bytes.fromhex("DEADBEEFDEADBEEFDEADBEEF"))
    f.write(b"Hello world\0Padx")
    f.write(bytes.fromhex("DEADBEEFDEADBEEFDEADBEEF"))
    v4 = b"The quick brown fox\0"
    f.write(pack("<I", len(v4)))
    f.write(v4)

with open("quiz004.bin", "wb") as f:
    f.write(pack("<f16si", 1.5, b"You can do it", 8888))
