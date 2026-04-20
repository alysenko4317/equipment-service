# Leader 856 Multimeter Firmware Dump

This repository contains a ROM dump from a Leader 856 digital multimeter.

## Overview

The Leader 856 is a bench multimeter that uses an external EPROM to store its firmware.  
The ROM is based on a 27C128 chip (16 KB).

According to available information, the instrument architecture includes:
- 8051-compatible microcontroller
- external EPROM (firmware storage)
- peripheral I/O controllers

This repository provides a raw binary dump of the firmware for archival and repair purposes.

## File

| Chip | Type   | Filename |
|------|--------|----------|
| ROM  | 27C128 | `27C128_Leader856.bin` |

## Integrity

The dump was verified by:
- multiple reads
- hash comparison

## Checksums

MD5:    e9fcb1a3cedfde3d9002fa6c1d7bd82a  
SHA1:   dd40939136abb40a27bce2c2ff799ea3b1c575b0  
SHA256: 89359a88510a212a8e495f023951274ce79e9c3873497237a2815edbcc5e56fb  

## Notes

- This is a direct dump of the EPROM contents.
- No modifications or patches were applied.
- File size: 16 KB (expected for 27C128).

## Firmware Version

No explicit version string has been identified in the ROM.

If you have:
- another revision of this firmware
- documentation identifying firmware versions
- decoded version strings

please contribute.

## Usage

This dump may be useful for:
- restoring non-working units
- reverse engineering
- studying legacy instrument firmware
- archival purposes

⚠️ Writing incorrect firmware to an EPROM may damage your instrument.

## Disclaimer

This repository is provided for educational and archival purposes only.  
Use at your own risk.

## Contributing

Contributions are welcome:
- additional dumps (different revisions)
- PCB photos
- reverse engineering notes
- disassembly / analysis

Please open an issue or pull request.
