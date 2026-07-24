#!/usr/bin/env python3
"""Generate codex/item_drops.csv from codex/items.csv — zone gear/enhancement family weights.
Baseline: every canonical family available on all wild floors at uniform weight.
Tune by narrowing Floor_Lo/Floor_Hi per zone or adjusting Weight; never add families
that don't exist in items.csv (client resolves candidates by family/slot name).
Schema (client contract, app.js dropDb): Floor_Lo, Floor_Hi, Item_Category, Item_Base, Weight
Item_Category must be one of: Weapon, Armour, Accessory, Gem, Rune, Scroll."""
import csv, io, urllib.request, sys

src = 'https://raw.githubusercontent.com/eccestanczyk/dfmc/main/codex/items.csv'
rows = list(csv.DictReader(io.StringIO(urllib.request.urlopen(src).read().decode('utf-8'))))
CATS = ['Weapon', 'Armour', 'Accessory', 'Gem', 'Rune', 'Scroll']
fams = {}
for r in rows:
    c = (r.get('Category') or '').strip()
    if c in CATS:
        fams.setdefault(c, set()).add((r.get('Family') or '').strip())
out = [('Floor_Lo', 'Floor_Hi', 'Item_Category', 'Item_Base', 'Weight')]
for c in CATS:
    for f in sorted(fams.get(c, [])):
        if f: out.append(('1', '100', c, f, '1'))
dst = sys.argv[1] if len(sys.argv) > 1 else 'codex/item_drops.csv'
with open(dst, 'w', newline='') as fh:
    csv.writer(fh).writerows(out)
print('wrote', dst, len(out) - 1, 'rows')
