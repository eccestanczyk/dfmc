#!/usr/bin/env python3
"""Merge authoring-lane outputs (Move_ID,FX_S1,FX_S2,FX_S3[,FX_Notes]) into codex/move_vfx.csv by Move_ID.

  python tools/merge_fx_lanes.py <lane_out.csv> [...]

Keeps the CSV's line endings, adds nothing but the three FX cells per row, refuses a Move_ID it does not
know, and prints what it touched. Run tools/fx_lint.py and tools/sync_move_vfx.py afterwards.
"""
import csv, os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(HERE, 'codex', 'move_vfx.csv')
raw = open(V, encoding='utf-8', newline='').read(); nl = '\r\n' if '\r\n' in raw else '\n'
rows = list(csv.DictReader(raw.splitlines(True))); cols = list(rows[0].keys())
by = {r['Move_ID']: r for r in rows}
n = 0; bad = 0
for path in sys.argv[1:]:
    k = 0
    for r in csv.DictReader(open(path, encoding='utf-8-sig')):
        mid = (r.get('Move_ID') or '').strip()
        if mid not in by: print('UNKNOWN Move_ID %r in %s' % (mid, path)); bad += 1; continue
        for c in ('FX_S1', 'FX_S2', 'FX_S3'):
            by[mid][c] = (r.get(c) or '').strip()
        k += 1
    print('%s: %d rows' % (os.path.basename(path), k)); n += k
with open(V, 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols, lineterminator=nl); w.writeheader(); w.writerows(rows)
empty = [m for m, r in by.items() if not r['FX_S1']]
print('merged %d rows; %d rows still without FX_S1%s' % (n, len(empty), (': ' + ', '.join(empty[:6])) if empty else ''))
sys.exit(1 if bad else 0)
