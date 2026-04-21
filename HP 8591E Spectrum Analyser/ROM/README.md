# HP 8591E Spectrum Analyser — ROM Dumps

Firmware version **98-06-15** (dated 15 June 1998).  
Four 27C020 (256 KiB × 8-bit) EPROMs physically located on the A7 CPU board.

---

## Hardware layout

The HP 8591E uses a **Motorola 68000** CPU with a 16-bit data bus.  
Two 8-bit EPROMs supply the high and low byte of every 16-bit word in parallel,
split across two address banks:

| Bank  | EPROM | Data bus | Address range (combined image) |
|-------|-------|----------|-------------------------------|
| Low   | U24   | D15–D8   | even bytes 0x000000–0x07FFFE  |
| Low   | U7    | D7–D0    | odd  bytes 0x000001–0x07FFFF  |
| High  | U23   | D15–D8   | even bytes 0x080000–0x0FFFFE  |
| High  | U6    | D7–D0    | odd  bytes 0x080001–0x0FFFFF  |

The four chips must be **interleaved** before the image can be disassembled or
emulated. `rom_combine.py` (see below) performs this step automatically.

---

## Repository contents

```
ROM/
├── hash.bat                    Windows batch — compute & save MD5/SHA1/SHA256
├── rom_analisys/
│   ├── rom_combine.py          Python — assemble the four chips into one image
│   └── rom_combined_image.bin  Pre-built 1 MiB flat binary (result of rom_combine)
├── 98-06-15 - copy 1/          EPROM dumps with descriptive file names
│   ├── 27c020_u23_hp8591e.bin
│   ├── 27c020_u24_hp8591e.bin
│   ├── 27c020_u6_hp8591e.bin
│   ├── 27c020_u7_hp8591e.bin
│   └── md5.txt                 Hashes for this set
└── 98-06-15 - copy 2/          Second independent read, short file names
    ├── u23.bin
    ├── u24.bin
    ├── u6.bin
    ├── u7.bin
    └── md5.txt                 Hashes for this set
```

Both dumps were verified to be **byte-for-byte identical** — the hashes in both
`md5.txt` files match.

---

## Known-good chip hashes (firmware 98-06-15)

| Chip | SHA-256 |
|------|---------|
| U23  | `5ff08bc4bcb86576f182f6db4466fb970a2eb8b006162d0ab3418a84f6a6cf21` |
| U24  | `13c43171f30a9d8013b6e3eb2e36fea47ac498dafb01fe7a7da3958fb72d0f73` |
| U6   | `898d90d41733e2583656e8228397783ae8c81fc796379a705e52ad423713c419`  |
| U7   | `f74a1e3d89e42be7c8c2d713ae49f7aecbe7ee00bdb5183f8feb6628c5d8f844`  |

---

## Tools

### `hash.bat` — compute hashes

Computes MD5, SHA-1 and SHA-256 for every `*.bin` file in a folder using
Windows built-in `certutil`. Results are printed to the console and saved to
`md5.txt` in the same folder.

```bat
:: From the ROM root — hash a specific dump folder:
hash.bat "98-06-15 - copy 1"

:: From inside a dump folder (double-click or run without arguments):
hash.bat
```

Output format in `md5.txt`:

```
27c020_u24_hp8591e.bin
  MD5    0b11704fe6a522ea74dad13f966a8b96
  SHA1   10cc6ad77e8d0053e1e8d75dbce46d6b8e276def
  SHA256 13c43171f30a9d8013b6e3eb2e36fea47ac498dafb01fe7a7da3958fb72d0f73
```

---

### `rom_combine.py` — assemble the combined image

Reads the four individual EPROM files, interleaves them into a single 1 MiB
flat binary and runs a sanity check (reset vectors, expected firmware strings).
Requires **Python 3.9+**, no third-party packages.

```bash
# Default: looks for  27c020_u*.bin  in the current directory
python rom_combine.py

# Custom paths
python rom_combine.py --u24 u24.bin --u7 u7.bin --u23 u23.bin --u6 u6.bin

# Custom output file name
python rom_combine.py --output firmware_980615.bin

# Skip the post-assembly sanity check
python rom_combine.py --no-verify

# Skip SHA-256 comparison against known-good hashes
python rom_combine.py --no-hash-check
```

The pre-built result is stored as `rom_analisys/rom_combined_image.bin`
(1,048,576 bytes, Motorola 68000 big-endian, ROM base `0x000000`).

#### Equivalent `srec_cat` command (Linux/macOS)

```bash
srec_cat  u24.bin -binary -unsplit 2 0 \
          u7.bin  -binary -unsplit 2 1 \
          u23.bin -binary -unsplit 2 0 -offset 524288 \
          u6.bin  -binary -unsplit 2 1 -offset 524288 \
          -output all.bin -binary
```

---

## Combined image — key properties

| Property       | Value |
|----------------|-------|
| Size           | 1,048,576 bytes (1 MiB) |
| CPU            | Motorola 68000 (big-endian) |
| ROM base       | `0x000000` |
| Reset SSP      | `0x00FF948A` |
| Reset PC       | `0x00001B34` |
| Firmware date  | 1998-06-15 |

