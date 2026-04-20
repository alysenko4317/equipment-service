#!/usr/bin/env python3
"""
rom_combine.py — HP 8591E / HP 8590 series ROM image combiner
==============================================================

Reassembles the four 27C020 (256 KiB × 8-bit) EPROM dumps into a single
1 MiB flat binary image suitable for disassembly or emulation.

Hardware layout (firmware version 980615 used as the reference)
---------------------------------------------------------------
The HP 8591E uses a Motorola 68000 CPU with a 16-bit data bus.
Two 8-bit EPROMs supply each byte of every 16-bit word in parallel:

  Bank   EPROM   Data bus    Address range
  ─────  ─────   ─────────   ─────────────────────────
  Low    U24     D15–D8      even bytes  0x000000–0x07FFFF  (high / MSB)
  Low    U7      D7–D0       odd  bytes  0x000001–0x07FFFF  (low  / LSB)
  High   U23     D15–D8      even bytes  0x080000–0x0FFFFE  (high / MSB)
  High   U6      D7–D0       odd  bytes  0x080001–0x0FFFFF  (low  / LSB)

Equivalent srec_cat command
---------------------------
  srec_cat  u24.bin -binary -unsplit 2 0  \\
            u7.bin  -binary -unsplit 2 1  \\
            u23.bin -binary -unsplit 2 0  -offset 524288  \\
            u6.bin  -binary -unsplit 2 1  -offset 524288  \\
            -output all.bin -binary

Usage
-----
  # Default: expects files named like  27c020_u24_hp8591e.bin  in the CWD
  python rom_combine.py

  # Custom file names / output
  python rom_combine.py --u24 u24.bin --u7 u7.bin --u23 u23.bin --u6 u6.bin
  python rom_combine.py --u24 u24.bin --u7 u7.bin --u23 u23.bin --u6 u6.bin \\
                        --output firmware_980615.bin

  # Skip the post-assembly sanity check
  python rom_combine.py --no-verify

Known-good SHA-256 hashes for firmware 980615
---------------------------------------------
  U24  13c43171f30a9d8013b6e3eb2e36fea47ac498dafb01fe7a7da3958fb72d0f73
  U7   f74a1e3d89e42be7c8c2d713ae49f7aecbe7ee00bdb5183f8feb6628c5d8f844
  U23  5ff08bc4bcb86576f182f6db4466fb970a2eb8b006162d0ab3418a84f6a6cf21
  U6   898d90d41733e2583656e8228397783ae8c81fc796379a705e52ad423713c419
"""

import argparse
import hashlib
import struct
import sys
from pathlib import Path

# ── known-good hashes (firmware 980615) ──────────────────────────────────────
KNOWN_SHA256: dict[str, str] = {
    "u24": "13c43171f30a9d8013b6e3eb2e36fea47ac498dafb01fe7a7da3958fb72d0f73",
    "u7":  "f74a1e3d89e42be7c8c2d713ae49f7aecbe7ee00bdb5183f8feb6628c5d8f844",
    "u23": "5ff08bc4bcb86576f182f6db4466fb970a2eb8b006162d0ab3418a84f6a6cf21",
    "u6":  "898d90d41733e2583656e8228397783ae8c81fc796379a705e52ad423713c419",
}

EPROM_SIZE = 256 * 1024          # 27C020 = 256 KiB


# ── helpers ───────────────────────────────────────────────────────────────────

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def interleave(high: bytes, low: bytes) -> bytes:
    """Interleave two equal-length byte strings into one.

    high → even positions (D15–D8, MSB of each 16-bit word)
    low  → odd  positions (D7–D0,  LSB of each 16-bit word)
    """
    if len(high) != len(low):
        raise ValueError(
            f"EPROM images must be the same size "
            f"(got {len(high)} and {len(low)} bytes)"
        )
    out = bytearray(len(high) * 2)
    out[0::2] = high
    out[1::2] = low
    return bytes(out)


def load_eprom(path: Path, label: str, verify_hash: bool) -> bytes:
    """Read an EPROM image, check its size, and optionally verify its hash."""
    if not path.is_file():
        sys.exit(f"ERROR: {label} image not found: {path}\n"
                 f"       Use --{label} <path> to specify a different location.")
    data = path.read_bytes()
    if len(data) != EPROM_SIZE:
        sys.exit(
            f"ERROR: {label} image has unexpected size "
            f"({len(data):,} bytes, expected {EPROM_SIZE:,}).\n"
            f"       File: {path}"
        )
    digest = sha256(data)
    known  = KNOWN_SHA256.get(label)
    if verify_hash and known:
        match = "✓ match" if digest == known else "✗ MISMATCH (unknown firmware version?)"
        print(f"  {label.upper():<4}  SHA-256: {digest[:16]}…  {match}")
    else:
        print(f"  {label.upper():<4}  SHA-256: {digest[:16]}…")
    return data


def verify_image(rom: bytes) -> bool:
    """Run a quick sanity check on the assembled image."""
    ok = True

    ssp = struct.unpack_from(">I", rom, 0x000000)[0]
    pc  = struct.unpack_from(">I", rom, 0x000004)[0]

    print(f"\n  Reset SSP = 0x{ssp:08x}", end="")
    if ssp == 0x00FF948A:
        print("  (known-good value for fw 980615)")
    else:
        print("  ⚠  unexpected value")

    print(f"  Reset PC  = 0x{pc:08x}", end="")
    if pc % 2 != 0:
        print("  ✗ ERROR: odd address — image is likely byte-swapped or corrupted!")
        ok = False
    elif 0 < pc < len(rom):
        print("  ✓ even address, within ROM")
    else:
        print("  ⚠  out of range")
        ok = False

    # look for a handful of expected firmware strings
    EXPECTED = [b"SYSTEM ERROR", b"Bus Error", b"NORMAL", b"Memory Exceeded"]
    missing = [s for s in EXPECTED if s not in rom]
    if missing:
        print(f"  ⚠  expected strings not found: {[s.decode() for s in missing]}")
        ok = False
    else:
        print(f"  ✓ firmware strings present "
              f"({', '.join(s.decode() for s in EXPECTED)})")

    return ok


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Combine four 27C020 EPROM dumps into a single HP 8591E ROM image.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--u24", metavar="FILE",
        default="27c020_u24_hp8591e.bin",
        help="U24 EPROM image — even bytes, D15–D8 (default: %(default)s)",
    )
    parser.add_argument(
        "--u7", metavar="FILE",
        default="27c020_u7_hp8591e.bin",
        help="U7 EPROM image  — odd  bytes, D7–D0  (default: %(default)s)",
    )
    parser.add_argument(
        "--u23", metavar="FILE",
        default="27c020_u23_hp8591e.bin",
        help="U23 EPROM image — even bytes, D15–D8, upper bank (default: %(default)s)",
    )
    parser.add_argument(
        "--u6", metavar="FILE",
        default="27c020_u6_hp8591e.bin",
        help="U6 EPROM image  — odd  bytes, D7–D0,  upper bank (default: %(default)s)",
    )
    parser.add_argument(
        "--output", "-o", metavar="FILE",
        default="all.bin",
        help="Output file name (default: %(default)s)",
    )
    parser.add_argument(
        "--no-verify", action="store_true",
        help="Skip the post-assembly sanity check (reset vectors, expected strings)",
    )
    parser.add_argument(
        "--no-hash-check", action="store_true",
        help="Do not compare SHA-256 against known-good 980615 hashes",
    )
    args = parser.parse_args()

    print("HP 8591E ROM combiner")
    print("=" * 50)

    # ── load ──────────────────────────────────────────────────────────────────
    print("\nLoading EPROM images:")
    verify_hashes = not args.no_hash_check
    u24 = load_eprom(Path(args.u24), "u24", verify_hashes)
    u7  = load_eprom(Path(args.u7),  "u7",  verify_hashes)
    u23 = load_eprom(Path(args.u23), "u23", verify_hashes)
    u6  = load_eprom(Path(args.u6),  "u6",  verify_hashes)

    # ── interleave ────────────────────────────────────────────────────────────
    print("\nInterleaving:")
    low  = interleave(u24, u7)
    high = interleave(u23, u6)
    rom  = low + high
    print(f"  Lower bank (U24+U7):  {len(low):,} bytes  (0x000000–0x07FFFF)")
    print(f"  Upper bank (U23+U6):  {len(high):,} bytes  (0x080000–0x0FFFFF)")
    print(f"  Combined image:       {len(rom):,} bytes")

    # ── verify ────────────────────────────────────────────────────────────────
    if not args.no_verify:
        print("\nSanity check:")
        ok = verify_image(rom)
        if not ok:
            print("\n  ⚠  Verification failed — the output may be incorrect.")
            print("     Common cause: wrong EPROM file assigned to wrong chip label.")
    else:
        ok = True

    # ── write ─────────────────────────────────────────────────────────────────
    out_path = Path(args.output)
    out_path.write_bytes(rom)
    out_digest = sha256(rom)
    print(f"\nOutput: {out_path}  ({len(rom):,} bytes)")
    print(f"  SHA-256: {out_digest}")

    if ok:
        print("\nDone. ✓")
    else:
        print("\nDone with warnings — review output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
