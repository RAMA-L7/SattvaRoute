#!/usr/bin/env python3
"""Validate the D-012 macro placement origin against the ASAP7 track grid.

For every non-supply pin of sram_x4x4x1 at the chosen origin, report:
  * centre-on-track  -> what mpl's Snapper (MPL-0005) demands
  * track-crossing   -> what the detailed router actually needs
Supply pins (vdd/vss) are reported for information only: the Snapper skips
them (isSupply) and they are connected by the PDN instead.
"""
import re, sys

ORIGIN_X, ORIGIN_Y = 1.230, 8.184
LEF = "/mnt/d/SattvaRoute/benchmark/design/sattva_sram/macro/sram_x4x4x1.lef"

# platforms/asap7/openRoad/make_tracks.tcl
TRACKS = {"M3": {"x": (0.009, 0.036), "y": (0.009, 0.036)},
          "M4": {"x": (0.009, 0.036), "y": (0.012, 0.048)}}
# platforms/asap7/lef/asap7_tech_1x_201209.lef
DIRECTION = {"M3": "VERTICAL", "M4": "HORIZONTAL"}

lef = open(LEF).read()
pins = []
for m in re.finditer(r"PIN\s+(\S+)\s+(.*?)\n\s*END\s+\1", lef, re.S):
    name, body = m.group(1), m.group(2)
    lm = re.search(r"LAYER\s+(M\d)\s*;(.*?)END", body, re.S)
    if not lm:
        continue
    layer, port = lm.group(1), lm.group(2)
    rects = [(float(a), float(b), float(c), float(d)) for a, b, c, d in
             re.findall(r"RECT\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", port)]
    if not rects:
        continue
    pins.append(dict(name=name, layer=layer,
                     x1=min(r[0] for r in rects), x2=max(r[2] for r in rects),
                     y1=min(r[1] for r in rects), y2=max(r[3] for r in rects),
                     supply=name.lower() in ("vdd", "vss")))

print(f"origin = ({ORIGIN_X}, {ORIGIN_Y}) um   orientation R0   exact (no snap)\n")
print(f"{'PIN':10} {'LYR':4} {'SUP':3} {'dir':10} {'abs-center':>10} "
      f"{'centre-on-track':>16} {'track-crossing':>15}")
print("-" * 74)

bad_centre, bad_cross = [], []
for p in sorted(pins, key=lambda q: (q["layer"], q["supply"], q["name"])):
    if p["layer"] not in TRACKS:
        continue
    d = DIRECTION[p["layer"]]
    t = TRACKS[p["layer"]]
    if d == "VERTICAL":
        lo, hi = p["x1"] + ORIGIN_X, p["x2"] + ORIGIN_X
        off, pit = t["x"]
    else:
        lo, hi = p["y1"] + ORIGIN_Y, p["y2"] + ORIGIN_Y
        off, pit = t["y"]
    c = (lo + hi) / 2.0
    on = abs(((c - off) % pit)) < 1e-9 or abs(((c - off) % pit) - pit) < 1e-9
    k0 = int((lo - off) // pit)
    cross = any(lo < off + (k0 + i) * pit < hi for i in range(3))
    if not p["supply"]:
        if not on:
            bad_centre.append(p["name"])
        if not cross:
            bad_cross.append(p["name"])
    print(f"{p['name']:10} {p['layer']:4} {'YES' if p['supply'] else 'no':3} "
          f"{d:10} {c:10.4f} "
          f"{('YES' if on else 'no'):>16} {('YES' if cross else 'no'):>15}")

print()
sig = [p for p in pins if not p["supply"]]
print(f"signal pins: {len(sig)}")
print(f"  centre-on-track : {len(sig) - len(bad_centre)}/{len(sig)}"
      f"{'   (Snapper rule)' if not bad_centre else '   NOT all - snap impossible, hence -exact'}")
print(f"  track-crossing  : {len(sig) - len(bad_cross)}/{len(sig)}"
      f"   (router access requirement)")
if bad_centre:
    print(f"  centres off-grid: {', '.join(bad_centre)}")
if bad_cross:
    print(f"  !! NO crossing track: {', '.join(bad_cross)}")
    sys.exit(1)
print("\nPASS: every signal pin has an interior track crossing -> routable.")
