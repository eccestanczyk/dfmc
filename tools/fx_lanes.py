r"""BUILD THE SIX AUTHORING LANES (VFX pass 2 re-author, D 2026-09-17).

The re-author brief splits 419 moves by DOMINANT SHEET GROUP. A move's group is the group of the
sheet that carries the most layers across its three stages; ties break on the S3 layer, then on the
first layer authored, so the answer is stable between runs.

  python tools/fx_lanes.py                 print the split, write nothing
  python tools/fx_lanes.py --write <dir>   write <lane>.txt id lists for tools/vfx_shoot.py --ids-file

Lanes, as the brief names them: impact-a / impact-b (impact, split in half), slash, holy-buff,
wind-smoke, and small-groups (explosion, lightning, dark, water, ice, fire, flame).
"""
import csv, os, re, sys, collections

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(HERE, 'codex', 'fx_bank.csv')
MOVES = os.path.join(HERE, 'codex', 'move_vfx.csv')
FX_RE = re.compile(r'\bFX-\d{3}\b')

LANES = [('slash', {'slash'}), ('holy-buff', {'holy', 'buff'}), ('wind-smoke', {'wind', 'smoke'}),
         ('small-groups', {'explosion', 'lightning', 'dark', 'water', 'ice', 'fire', 'flame'})]


def group_of_move(row, gby):
    tally = collections.Counter()
    order = []
    for st in ('FX_S1', 'FX_S2', 'FX_S3'):
        for fid in FX_RE.findall(row.get(st) or ''):
            g = gby.get(fid)
            if g:
                tally[g] += 1
                order.append((st, g))
    if not tally:
        return None
    top = max(tally.values())
    tied = sorted(g for g, c in tally.items() if c == top)
    if len(tied) == 1:
        return tied[0]
    for st in ('FX_S3', 'FX_S1', 'FX_S2'):
        for s, g in order:
            if s == st and g in tied:
                return g
    return tied[0]


def main():
    gby = {r['Id']: r['Group'] for r in csv.DictReader(open(BANK, encoding='utf-8-sig'))}
    moves = list(csv.DictReader(open(MOVES, encoding='utf-8-sig')))
    lanes = collections.OrderedDict((n, []) for n, _ in
                                    [('impact-a', 0), ('impact-b', 0)] + [(n, 0) for n, _ in LANES])
    lanes['unassigned'] = []
    impact = []
    for r in moves:
        mid = r['Move_ID']
        g = group_of_move(r, gby)
        if g == 'impact':
            impact.append(mid); continue
        for name, groups in LANES:
            if g in groups:
                lanes[name].append(mid); break
        else:
            lanes['unassigned'].append(mid)
    half = (len(impact) + 1) // 2
    lanes['impact-a'] = impact[:half]
    lanes['impact-b'] = impact[half:]

    total = 0
    for name, ids in lanes.items():
        if not ids and name == 'unassigned':
            continue
        print('%-14s %4d' % (name, len(ids))); total += len(ids)
    print('%-14s %4d of %d rows' % ('TOTAL', total, len(moves)))
    if lanes['unassigned']:
        print('NOTE: %d row(s) carry no bank sheet at all - they are in unassigned and need a read.'
              % len(lanes['unassigned']))

    if '--write' in sys.argv:
        out = sys.argv[sys.argv.index('--write') + 1]
        os.makedirs(out, exist_ok=True)
        for name, ids in lanes.items():
            if not ids:
                continue
            p = os.path.join(out, name + '.txt')
            open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(ids) + '\n')
            print('wrote %s (%d)' % (p, len(ids)))


if __name__ == '__main__':
    main()
