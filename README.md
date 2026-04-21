# Test Equipment — Notes, Manuals & Firmware

A personal archive of material collected while repairing, maintaining, or just
exploring vintage and not-so-vintage test equipment.

Nothing is collected for the sake of collecting. Every file here came out of a
real need — a repair, a firmware backup before prodding at something, or
curiosity that went deep enough to produce something worth keeping.

Content may include service manuals, EPROM dumps, firmware analysis, reverse
engineering notes, schematics, or anything else that seemed worth committing.

---

## Instruments

| Instrument | Type | Contents |
|------------|------|----------|
| [HP 8591E Spectrum Analyser](HP%208591E%20Spectrum%20Analyser/) | RF spectrum analyser | service manual, 4× EPROM dumps (fw 98-06-15 / rev L), combine tool, ROM analysis |
| [Leader 856 Multimeter](Leader%20856%20Multimeter/) | bench multimeter | service manual, 27C128 EPROM dump |

---

## Structure

Each instrument lives in its own folder and has its own `README.md` with
context specific to that device. Typical layout:

```
<Instrument Name>/
├── README.md          overview, key facts, firmware notes
├── *.pdf              service manual or datasheet
└── ROM/               EPROM dumps and related tooling
    ├── README.md      hardware layout, hashes, tool usage
    └── ...
```

---

*Personal archive — shared in case it helps someone else.*

