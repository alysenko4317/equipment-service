# HP 8591E Spectrum Analyser — Firmware Archive

EPROM dumps and tooling for the Hewlett-Packard HP 8591E spectrum analyser,
firmware date code **98-06-15** (1998-06-15, **revision L**).

---

## Repository layout

```
HP 8591E Spectrum Analyser/
├── README.md                   ← you are here
├── 08590-90316-Service Manual.pdf
└── ROM/                        EPROM dumps, tools, and analysis
    ├── README.md               ← technical detail starts here
    ├── hash.bat
    ├── 98-06-15 - copy 1/
    ├── 98-06-15 - copy 2/
    └── rom_analisys/
        ├── rom_combine.py
        └── rom_combined_image.bin
```

See **[ROM/README.md](ROM/README.md)** for:
- hardware layout (chip pinout, even/odd interleaving)
- known-good SHA-256 hashes per chip
- how to use `hash.bat` and `rom_combine.py`
- combined image key properties (CPU, reset vectors, ROM base)

---

## Firmware revision notes

| Date code  | Revision | Notes |
|------------|----------|-------|
| 98-06-15   | **L**    | this dump |
| 99-11-30   | M        | latest known revision |

The date code `98-06-15` is printed on the EPROM labels. Based on
community-maintained HP 859xE firmware history, this maps to **revision L**.
Revision M (date code `99-11-30`) is the latest known version, so this dump is
one revision behind the final release.

> **Compatibility note:** HP/Agilent firmware compatibility also depends on the
> A7 processor-board hardware revision and ROM kit type. The date code alone is
> not a full compatibility guarantee. Some older boards can only be upgraded to
> specific firmware kits without hardware modifications.

---

## Intended use

These files are useful for:

- restoring corrupted or failed EPROMs
- repairing HP 8591E analysers
- reverse engineering and historical preservation

> **Warning:** Programming the wrong firmware into an incompatible board
> revision may prevent the instrument from booting. Always back up the original
> EPROM contents and correction constants before making any changes.

---

## Contributing

Contributions welcome — especially:

- dumps from other firmware revisions (revision M / `99-11-30` in particular)
- confirmed version strings from the instrument's `REV` command output
- board revision compatibility details

Please open an issue or pull request.

---

*Provided for archival, educational, and repair purposes. Use at your own risk.*
