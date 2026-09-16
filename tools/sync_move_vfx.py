#!/usr/bin/env python3
"""Copy the effect columns from codex/move_vfx.csv (the source of truth, VFX_SPEC.md) onto the matching
row of codex/moves.csv by Move_ID, adding any column moves.csv lacks. Ultimate rows (ULT-*) have no
moves.csv row and are skipped. Run after every edit to move_vfx.csv; the review page reads moves.csv."""
import csv, os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(HERE, 'codex', 'move_vfx.csv'); M = os.path.join(HERE, 'codex', 'moves.csv')
vfx = {r['Move_ID']: r for r in csv.DictReader(open(V, encoding='utf-8'))}
vcols = [c for c in next(iter(vfx.values())).keys() if c not in ('Move_ID', 'Name')]
raw = open(M, encoding='utf-8', newline='').read(); nl = '\r\n' if '\r\n' in raw else '\n'
rows = list(csv.DictReader(raw.splitlines(True))); cols = list(rows[0].keys())
for c in vcols:
    if c not in cols: cols.append(c)
n = 0
for r in rows:
    v = vfx.get(r['Move_ID'])
    if not v: print('moves.csv row without a move_vfx row:', r['Move_ID']); continue
    for c in vcols:
        if r.get(c, '') != v[c]: r[c] = v[c]; n += 1
    for c in cols: r.setdefault(c, '')
with open(M, 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols, lineterminator=nl); w.writeheader(); w.writerows(rows)
print('sync_move_vfx: %d cells updated on %d rows' % (n, len(rows)))
