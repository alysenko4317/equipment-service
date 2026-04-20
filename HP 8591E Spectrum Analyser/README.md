# HP 8591E Firmware Dump

This repository contains EPROM dumps from a Hewlett-Packard HP 8591E
spectrum analyzer.

## Overview

The HP 8591E stores its firmware in multiple EPROM devices on the processor
board. This repository preserves raw binary dumps of those ROMs for archival,
repair, and research purposes.

## Files

| Chip | Filename |
|------|----------|
| U6   | `27c020_u6_hp8591e.bin` |
| U7   | `27c020_u7_hp8591e.bin` |
| U23  | `27c020_u23_hp8591e.bin` |
| U24  | `27c020_u24_hp8591e.bin` |

All four files are dumps of 27C020 EPROMs.

## Verification

The dumps were verified by repeated reads and checksum comparison.
The matching checksum sets indicate that the files were read consistently.

## Checksums

### 27c020_u6_hp8591e.bin
- MD5: `8ce33a8056d244e2a780d6e935f64a3c`
- SHA1: `1a80cdd360fae29fbe6dcfc600fc5b42edfd62d6`
- SHA256: `898d90d41733e2583656e8228397783ae8c81fc796379a705e52ad423713c419`

### 27c020_u7_hp8591e.bin
- MD5: `e91365ad5bd8ccb27be93f50ab8fd58d`
- SHA1: `8ae0ebf417c4e19f78284a7898f7c17d3f7e1716`
- SHA256: `f74a1e3d89e42be7c8c2d713ae49f7aecbe7ee00bdb5183f8feb6628c5d8f844`

### 27c020_u23_hp8591e.bin
- MD5: `ca6a0057a1f3782b2682c50f967312f5`
- SHA1: `4113524578d56ee2cffedb20f81dcbf9e9b0b9f4`
- SHA256: `5ff08bc4bcb86576f182f6db4466fb970a2eb8b006162d0ab3418a84f6a6cf21`

### 27c020_u24_hp8591e.bin
- MD5: `0b11704fe6a522ea74dad13f966a8b96`
- SHA1: `10cc6ad77e8d0053e1e8d75dbce46d6b8e276def`
- SHA256: `13c43171f30a9d8013b6e3eb2e36fea47ac498dafb01fe7a7da3958fb72d0f73`

## Date Code and Revision Notes

The EPROM labels are marked `98-06-15`.

That marking is best interpreted as a firmware date code (1998-06-15), not as a
complete official HP revision label by itself.

Based on community-maintained HP 859xE firmware history, date code `98-06-15`
corresponds to **revision L**. A later **revision M** is documented with date
code `99-11-30`, so this dump does **not** appear to be the latest known
revision. However, revision L is still a relatively late firmware version for
this instrument family.

Because HP/Agilent firmware compatibility also depends on processor-board
revision and ROM kit type, the date code alone should not be treated as a full
compatibility guarantee.

## Related Notes

- Community discussion identifies `98.06.15` as **revision L**.
- Official HP/Agilent installation documentation identifies **revision M** with
  date code `991130`.
- Some older processor boards may only be upgradeable to specific firmware kits
  without board modifications.

## Intended Use

These files may be useful for:

- restoring corrupted EPROM contents
- repairing HP 8591E analyzers
- reverse engineering
- historical preservation

## Warning

Programming the wrong firmware into an incompatible board revision may prevent
an instrument from booting or operating correctly.

Always back up the original EPROM contents and correction constants before
making changes.

## Disclaimer

This repository is provided for archival, educational, and repair purposes.
Use the files at your own risk.

## Contributing

If you have:

- dumps from other firmware revisions
- official HP/Agilent firmware notes
- confirmed version strings from the instrument UI
- board revision compatibility details

please open an issue or pull request.
