#!/usr/bin/env python3
"""REGENERATE Floor_Found FROM THE WILD-ENCOUNTER TABLE (auto-report triage 2026-08-20).

A player camped floor 72 for Charybdis because the codex told him to; the game spawns it on 79.
He found Wychroot on 71; the codex said 67-77-87-97. He was right both times, systemically:
142 declared floors carried nothing and 209 spawning floors were undocumented.

WHICH SIDE IS TRUTH WAS SETTLED BY MEASUREMENT, not preference: floor_creature_rarity.csv is
GENERATED (d07c9bb "Regenerate wild-encounter table") and since d2030d1 each floor presents the
stage the line's advancement threshold dictates for that floor — verified 900/900 rows reproduce
exactly from that rule. Floor_Found was the hand-written summary that predates the mixed-stage
regeneration and never moved with it. The table drives the live server (SPAWN_DATA_REF -> the
same codex ref the worker pins); the codex column is documentation of it, so the column follows
the table, never the other way.

RULES:
  - A creature's Floor_Found = every floor <= 100 where the table carries ITS id, ascending,
    ';'-joined. Apex floors (101+) stay undocumented here, matching the existing convention
    (no Floor_Found row has ever listed one).
  - Idempotent: a second run changes nothing.
  - Only the Floor_Found cell of changed rows is rewritten; every other byte of the file is
    preserved by re-emitting only changed lines (the file is LF-only with no embedded newlines,
    verified 2026-08-20: CRLF 0, quoted-newline records 0).

Run from the repo root:  python3 tools/make_floorfound.py [--check]
  --check  verify only (exit 1 on any divergence), for use after any table regeneration.
"""
import csv, io, sys, collections

CHECK = '--check' in sys.argv
CR = 'codex/creatures.csv'
FR = 'codex/floor_creature_rarity.csv'

raw = open(CR, newline='', encoding='utf-8').read()
lines = raw.split('\n')
head = next(csv.reader([lines[0]]))
I_ID = head.index('ID'); I_FF = head.index('Floor_Found')

table = collections.defaultdict(set)
for f, cid, tier in list(csv.reader(open(FR, newline='', encoding='utf-8')))[1:]:
    if int(f) <= 100:
        table[cid].add(int(f))

changed = 0; out = [lines[0]]; report = []
for ln in lines[1:]:
    if not ln.strip():
        out.append(ln); continue
    row = next(csv.reader([ln]))
    if len(row) <= max(I_ID, I_FF):
        out.append(ln); continue
    want = ';'.join(str(f) for f in sorted(table.get(row[I_ID], set())))
    if row[I_FF] == want:
        out.append(ln); continue
    changed += 1
    report.append((row[I_ID], row[I_FF], want))
    row2 = list(row); row2[I_FF] = want
    buf = io.StringIO()
    csv.writer(buf, lineterminator='').writerow(row2)
    out.append(buf.getvalue())

if CHECK:
    if changed:
        print('FLOORFOUND CHECK: FAIL — %d row(s) diverge from the wild-encounter table' % changed)
        for cid, old, new in report[:10]:
            print('  %s: %r -> %r' % (cid, old, new))
        sys.exit(1)
    print('FLOORFOUND CHECK: green — every Floor_Found matches the table (<=100)')
    sys.exit(0)

if changed:
    open(CR, 'w', newline='', encoding='utf-8').write('\n'.join(out))
print('rewrote %d Floor_Found cell(s); %d creature rows total' % (changed, len(lines) - 2))
for cid, old, new in report[:8]:
    print('  %s: %s -> %s' % (cid, old or '(empty)', new))
if len(report) > 8:
    print('  ... +%d more' % (len(report) - 8))
