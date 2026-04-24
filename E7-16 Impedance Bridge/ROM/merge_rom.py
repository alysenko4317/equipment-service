#!/usr/bin/env python3
"""
ROM merger for Е7-16 impedance bridge (CPU: К1816ВЕ39 = Intel 8039 clone, MCS-48 family)

Hardware configuration (verified by analysis):
  - Two 2716 EPROMs (2 KB each = 2048 bytes, total 4 KB)
  - 2716_115-0.bin  →  Bank 0, addresses 0x000–0x7FF  (A11 = 0)
  - 2716_115_1.bin  →  Bank 1, addresses 0x800–0xFFF  (A11 = 1)

Evidence:
  • File _0 contains numerous SEL MB0 (0xE5) instructions and several SEL MB1 (0xF5)
    followed by JMP/CALL — i.e. it lives in bank 0 and explicitly switches to bank 1
    to call upper-bank routines.
  • File _1 contains almost exclusively SEL MB1 (0xF5) instructions — it IS bank 1.
  • Sequential (not interleaved) addressing: the 8039 has an 8-bit data bus; no
    reason to interleave. A11 pin on the address bus selects between the two chips.
  • Naming convention: _0 = bank 0, _1 = bank 1.

MCS-48 memory bank switching recap:
  SEL MB0 (0xE5)  →  clears internal MB flip-flop; subsequent JMP/CALL targets have A11 = 0
  SEL MB1 (0xF5)  →  sets   internal MB flip-flop; subsequent JMP/CALL targets have A11 = 1
  Reset default  →  MB = 0 (CPU starts at 0x000 in bank 0)
  Interrupt vectors: 0x003 (INT), 0x007 (Timer) — both in bank 0

Directory layout expected next to this script:
  copy-1/
    2716_115-0.bin    ← bank 0  (primary dump)
    2716_115_1.bin    ← bank 1  (primary dump)
  copy-2/
    __2716_115_0.bin  ← bank 0  (verification dump)
    __2716_115_1.bin  ← bank 1  (verification dump)
  E7-16_merged.bin   ← OUTPUT (4 KB flat image)
"""

import hashlib
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# MCS-48 / К1816ВЕ39 opcode table
#   None  = undefined / illegal opcode
#   1     = 1-byte instruction
#   2     = 2-byte instruction (opcode + operand)
# ---------------------------------------------------------------------------
def build_oplen():
    t = [None] * 256

    # ---- 1-byte instructions -----------------------------------------------
    one = [
        0x00,  # NOP
        0x02,  # OUTL BUS, A
        0x05,  # EN I
        0x07,  # DEC A
        0x08,  # INS A, BUS
        0x09,  # IN A, P1
        0x0A,  # IN A, P2
        0x0C,  # MOVD A, P4
        0x0E,  # MOVD A, P6
        0x0F,  # MOVD A, P7
        0x10,  # RRC A
        0x11,  # (variant)
        0x15,  # DIS I
        0x17,  # INC A
        0x18,  # INC R0
        0x19,  # INC R1
        0x1A,  # INC R2
        0x1B,  # INC R3
        0x1C,  # INC R4  / MOVD P4, A
        0x1D,  # INC R5  / MOVD P5, A
        0x1E,  # INC R6  / MOVD P6, A
        0x1F,  # INC R7  / MOVD P7, A
        0x20,  # XCH A, @R0
        0x21,  # XCH A, @R1
        0x25,  # DIS TCNTI
        0x27,  # CLR A
        0x28,  # XCH A, R0
        0x29,  # XCH A, R1
        0x2A,  # XCH A, R2
        0x2B,  # XCH A, R3
        0x2C,  # XCH A, R4
        0x2D,  # XCH A, R5
        0x2E,  # XCH A, R6
        0x2F,  # XCH A, R7
        0x30,  # XCHD A, @R0
        0x31,  # XCHD A, @R1
        0x35,  # EN TCNTI
        0x37,  # CPL A
        0x38,  # OUTL P0, A (variant)
        0x39,  # OUTL P1, A
        0x3A,  # OUTL P2, A
        0x3B,  # (MOVD P4, A in some variants)
        0x40,  # ORL A, @R0
        0x41,  # ORL A, @R1
        0x45,  # STRT CNT
        0x47,  # CLR C
        0x48,  # ORL A, R0
        0x49,  # ORL A, R1
        0x4A,  # ORL A, R2
        0x4B,  # ORL A, R3
        0x4C,  # ORL A, R4
        0x4D,  # ORL A, R5
        0x4E,  # ORL A, R6
        0x4F,  # ORL A, R7
        0x50,  # ANL A, @R0
        0x51,  # ANL A, @R1
        0x55,  # STRT T
        0x57,  # CPL C
        0x58,  # ANL A, R0
        0x59,  # ANL A, R1
        0x5A,  # ANL A, R2
        0x5B,  # ANL A, R3
        0x5C,  # ANL A, R4
        0x5D,  # ANL A, R5
        0x5E,  # ANL A, R6
        0x5F,  # ANL A, R7
        0x60,  # ADD A, @R0
        0x61,  # ADD A, @R1
        0x65,  # STOP TCNT
        0x67,  # DA A
        0x68,  # ADD A, R0
        0x69,  # ADD A, R1
        0x6A,  # ADD A, R2
        0x6B,  # ADD A, R3
        0x6C,  # ADD A, R4
        0x6D,  # ADD A, R5
        0x6E,  # ADD A, R6
        0x6F,  # ADD A, R7
        0x70,  # ADDC A, @R0
        0x71,  # ADDC A, @R1
        0x75,  # ENT0 CLK
        0x77,  # RLC A
        0x78,  # ADDC A, R0
        0x79,  # ADDC A, R1
        0x7A,  # ADDC A, R2
        0x7B,  # ADDC A, R3
        0x7C,  # ADDC A, R4
        0x7D,  # ADDC A, R5
        0x7E,  # ADDC A, R6
        0x7F,  # ADDC A, R7
        0x80,  # MOVX A, @R0
        0x81,  # MOVX A, @R1
        0x83,  # RET
        0x85,  # CLR F0
        0x87,  # (variant)
        0x8C,  # ORLD P4, A
        0x8D,  # ORLD P5, A
        0x8E,  # ORLD P6, A
        0x8F,  # ORLD P7, A
        0x90,  # MOVX @R0, A
        0x91,  # MOVX @R1, A
        0x93,  # RETR
        0x95,  # CPL F0
        0x97,  # (variant)
        0x9C,  # ANLD P4, A
        0x9D,  # ANLD P5, A
        0x9E,  # ANLD P6, A
        0x9F,  # ANLD P7, A
        0xA0,  # MOV @R0, A
        0xA1,  # MOV @R1, A
        0xA3,  # MOVP A, @A
        0xA5,  # CPL F1
        0xA8,  # MOV R0, A
        0xA9,  # MOV R1, A
        0xAA,  # MOV R2, A
        0xAB,  # MOV R3, A
        0xAC,  # MOV R4, A
        0xAD,  # MOV R5, A
        0xAE,  # MOV R6, A
        0xAF,  # MOV R7, A
        0xC3,  # (variant)
        0xC5,  # SEL RB0
        0xC7,  # MOV PSW, A
        0xC8,  # DEC R0
        0xC9,  # DEC R1
        0xCA,  # DEC R2
        0xCB,  # DEC R3
        0xCC,  # DEC R4
        0xCD,  # DEC R5
        0xCE,  # DEC R6
        0xCF,  # DEC R7
        0xD0,  # XRL A, @R0
        0xD1,  # XRL A, @R1
        0xD5,  # SEL RB1
        0xD7,  # MOV A, PSW
        0xD8,  # XRL A, R0
        0xD9,  # XRL A, R1
        0xDA,  # XRL A, R2
        0xDB,  # XRL A, R3
        0xDC,  # XRL A, R4
        0xDD,  # XRL A, R5
        0xDE,  # XRL A, R6
        0xDF,  # XRL A, R7
        0xE3,  # MOVP3 A, @A
        0xE5,  # SEL MB0   ← bank switch to lower 2 KB
        0xE7,  # RL A
        0xF0,  # MOV A, @R0
        0xF1,  # MOV A, @R1
        0xF5,  # SEL MB1   ← bank switch to upper 2 KB
        0xF7,  # MOV A, PSW
        0xF8,  # MOV A, R0
        0xF9,  # MOV A, R1
        0xFA,  # MOV A, R2
        0xFB,  # MOV A, R3
        0xFC,  # MOV A, R4
        0xFD,  # MOV A, R5
        0xFE,  # MOV A, R6
        0xFF,  # MOV A, R7
    ]

    # ---- 2-byte instructions (opcode + immediate/address byte) -------------
    # JMP family: lower 5 bits = 0b00100 (0x04), upper 3 bits encode A[10:8]
    jmp_ops  = [page << 5 | 0x04 for page in range(8)]  # 0x04,0x24,0x44,...,0xE4
    # CALL family: lower 5 bits = 0b10100 (0x14)
    call_ops = [page << 5 | 0x14 for page in range(8)]  # 0x14,0x34,0x54,...,0xF4

    two = jmp_ops + call_ops + [
        0x03,  # ADD A, #data
        0x06,  # JNT0  addr
        0x12,  # JB0   addr
        0x13,  # ADDC A, #data
        0x16,  # JT0   addr
        0x22,  # (JB1 or DJNZ variant)
        0x23,  # MOV A, #data
        0x26,  # JNT1  addr
        0x32,  # JB2   addr
        0x36,  # JT1   addr
        0x42,  # JB3   addr
        0x43,  # ORL A, #data
        0x46,  # JF0   addr
        0x52,  # JB4   addr
        0x53,  # ANL A, #data
        0x56,  # JNIBF addr (or JNI)
        0x62,  # JB5   addr
        0x66,  # JZ    addr
        0x72,  # JB6   addr
        0x76,  # JF1   addr
        0x82,  # ANL BUS, #data
        0x86,  # JC    addr
        0x88,  # ORL BUS, #data
        0x92,  # (JB7 / variant)
        0x96,  # JNZ   addr
        0x99,  # ANL P1, #data
        0x9A,  # ANL P2, #data
        0xA2,  # (variant)
        0xA6,  # JNC   addr
        0xB0,  # MOV @R0, #data
        0xB1,  # MOV @R1, #data
        0xB2,  # (JB / variant)
        0xB8,  # MOV R0, #data
        0xB9,  # MOV R1, #data
        0xBA,  # MOV R2, #data
        0xBB,  # MOV R3, #data
        0xBC,  # MOV R4, #data
        0xBD,  # MOV R5, #data
        0xBE,  # MOV R6, #data
        0xBF,  # MOV R7, #data
        0xC6,  # JZ    addr
        0xD3,  # XRL A, #data
        0xE6,  # JNC   addr
        0xE8,  # DJNZ R0, addr
        0xE9,  # DJNZ R1, addr
        0xEA,  # DJNZ R2, addr
        0xEB,  # DJNZ R3, addr
        0xEC,  # DJNZ R4, addr
        0xED,  # DJNZ R5, addr
        0xEE,  # DJNZ R6, addr
        0xEF,  # DJNZ R7, addr
        0xF6,  # (variant cond. jump)
    ]

    for op in one:
        t[op] = 1
    for op in two:
        t[op] = 2
    return t


OPLEN = build_oplen()

SEL_MB0 = 0xE5
SEL_MB1 = 0xF5


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def md5hex(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def sha1hex(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def score_stream(data: bytes) -> dict:
    """Walk byte stream as MCS-48 instructions and gather statistics."""
    pos, valid_insns, invalid_bytes = 0, 0, 0
    while pos < len(data):
        ol = OPLEN[data[pos]]
        if ol is None:
            invalid_bytes += 1
            pos += 1
        else:
            valid_insns += 1
            pos += ol
    total = valid_insns + invalid_bytes
    return {
        "valid_insns":   valid_insns,
        "invalid_bytes": invalid_bytes,
        "validity_pct":  100.0 * valid_insns / total if total else 0.0,
    }


def find_bank_switches(data: bytes, base_addr: int = 0) -> list:
    """Return list of (offset, mnemonic, context_hex) for all SEL MB0/MB1."""
    results = []
    for i, b in enumerate(data):
        if b in (SEL_MB0, SEL_MB1):
            ctx = data[max(0, i - 3): i + 6]
            mnem = "SEL MB0" if b == SEL_MB0 else "SEL MB1"
            ctx_hex = " ".join(f"{x:02X}" for x in ctx)
            results.append((base_addr + i, mnem, ctx_hex))
    return results


def hexdump(data: bytes, start_addr: int = 0, length: int = 64) -> None:
    for i in range(0, min(length, len(data)), 16):
        chunk = data[i: i + 16]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        ascii_part = "".join(chr(b) if 0x20 <= b < 0x7F else "." for b in chunk)
        print(f"  {start_addr + i:04X}: {hex_part:<48}  {ascii_part}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    rom_dir = Path(__file__).parent

    # Primary dumps (copy-1)
    f0_path  = rom_dir / "copy-1" / "2716_115-0.bin"
    f1_path  = rom_dir / "copy-1" / "2716_115_1.bin"
    # Verification dumps (copy-2)
    v0_path  = rom_dir / "copy-2" / "__2716_115_0.bin"
    v1_path  = rom_dir / "copy-2" / "__2716_115_1.bin"
    out_path = rom_dir / "E7-16_merged.bin"

    print("=" * 70)
    print("Е7-16 ROM merger  —  CPU: К1816ВЕ39 (Intel 8039 clone, MCS-48)")
    print("=" * 70)

    # ---- load & verify ------------------------------------------------------
    for p in (f0_path, f1_path):
        if not p.exists():
            sys.exit(f"ERROR: cannot find {p}")

    d0 = f0_path.read_bytes()
    d1 = f1_path.read_bytes()

    print(f"\n{'File':<40} {'Size':>6}  MD5")
    print("-" * 70)
    for path, data in [(f0_path, d0), (f1_path, d1)]:
        print(f"  {path.name:<38} {len(data):>6}  {md5hex(data)}")

    if len(d0) != 2048 or len(d1) != 2048:
        print("\nWARNING: unexpected file size — expected 2048 bytes (2716 EPROM).")

    # Cross-verify with second dump set if available
    print()
    all_ok = True
    for prim, verf, label in [(f0_path, v0_path, "_0"), (f1_path, v1_path, "_1")]:
        if verf.exists():
            vdata = verf.read_bytes()
            pdata = prim.read_bytes()
            diffs = sum(a != b for a, b in zip(pdata, vdata))
            status = "IDENTICAL ✓" if diffs == 0 else f"DIFFER: {diffs} bytes !"
            print(f"  Integrity check {label}  copy-1 vs copy-2: {status}")
            if diffs:
                all_ok = False
        else:
            print(f"  Integrity check {label}: copy-2 not found, skipping.")
    if not all_ok:
        print("\n  WARNING: dumps differ — ROM may have read errors.")

    # ---- analysis -----------------------------------------------------------
    print("\n--- Individual ROM analysis ---\n")
    for label, data, base in [
        ("2716_115-0.bin  (bank 0, 0x0000–0x07FF)", d0, 0x000),
        ("2716_115_1.bin  (bank 1, 0x0800–0x0FFF)", d1, 0x800),
    ]:
        sc = score_stream(data)
        ff_count = data.count(0xFF)
        print(f"  {label}")
        print(f"    Valid insns  : {sc['valid_insns']}")
        print(f"    Invalid bytes: {sc['invalid_bytes']}")
        print(f"    Validity     : {sc['validity_pct']:.1f}%")
        print(f"    0xFF bytes   : {ff_count}")
        switches = find_bank_switches(data, base_addr=base)
        mb0 = sum(1 for _, m, _ in switches if m == "SEL MB0")
        mb1 = sum(1 for _, m, _ in switches if m == "SEL MB1")
        print(f"    SEL MB0 count: {mb0}   SEL MB1 count: {mb1}")
        if mb0 + mb1 <= 30:          # print them all if not too many
            for addr, mnem, ctx in switches:
                print(f"      0x{addr:04X}  {mnem}  [{ctx}]")
        print()

    # ---- merge strategy comparison ------------------------------------------
    print("--- Merge strategy comparison ---\n")
    strategies = [
        ("Sequential: _0 (0x0000-0x07FF) + _1 (0x0800-0x0FFF)  [CHOSEN]", d0 + d1),
        ("Sequential: _1 (0x0000-0x07FF) + _0 (0x0800-0x0FFF)  [reversed]", d1 + d0),
        ("Interleaved: even bytes=_0, odd bytes=_1", bytes(b for p in zip(d0, d1) for b in p)),
        ("Interleaved: even bytes=_1, odd bytes=_0", bytes(b for p in zip(d1, d0) for b in p)),
    ]
    for name, data in strategies:
        sc = score_stream(data)
        marker = "  ◄" if "CHOSEN" in name else ""
        print(f"  {name}{marker}")
        print(f"    Valid: {sc['valid_insns']:4d}  Invalid: {sc['invalid_bytes']:3d}"
              f"  Validity: {sc['validity_pct']:.1f}%")
        print()

    # ---- build & write merged image -----------------------------------------
    merged = d0 + d1

    out_path.write_bytes(merged)

    print("=" * 70)
    print(f"Merged ROM written : {out_path}")
    print(f"Total size         : {len(merged)} bytes  (0x{len(merged):04X})")
    print(f"MD5                : {md5hex(merged)}")
    print(f"SHA1               : {sha1hex(merged)}")
    print(f"\nAddress map:")
    print(f"  0x0000–0x07FF  →  {f0_path.name}  (bank 0, A11=0)")
    print(f"  0x0800–0x0FFF  →  {f1_path.name}  (bank 1, A11=1)")

    print(f"\n--- First 64 bytes of merged ROM (reset / interrupt vectors) ---")
    hexdump(merged, start_addr=0x0000, length=64)

    print("""
--- Disassembler hints ---
  CPU family : MCS-48  (Intel 8039 clone / К1816ВЕ39)
  ROM size   : 4096 bytes (0x1000)
  Load at    : 0x0000
  Entry point: 0x0000  (power-on reset)
  INT vector : 0x0003  (external interrupt INT pin)
  Timer vec  : 0x0007  (timer/counter overflow)

  Recommended tools:
    • dasm48 / dis48  (CLI disassembler for 8048/8039)
    • IDA Pro: select processor "8048", load as binary at base 0x0000
    • Ghidra: 8048 processor module available as plugin

  Bank-switching note:
    SEL MB0 (opcode 0xE5) — sets A11=0 for subsequent JMP/CALL targets
    SEL MB1 (opcode 0xF5) — sets A11=1 for subsequent JMP/CALL targets
    In the merged flat image both banks are contiguous; 12-bit absolute
    addresses work directly (0x000–0x7FF = bank 0, 0x800–0xFFF = bank 1).
""")


if __name__ == "__main__":
    main()

