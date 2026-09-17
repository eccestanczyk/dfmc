#!/usr/bin/env python3
"""fx_lint - the authoring gate for the bank compositions (codex/VFX_SPEC.md, "Bank compositions").

  python tools/fx_lint.py                       # lint codex/move_vfx.csv (every row must be authored)
  python tools/fx_lint.py out/fx_lane_a.csv     # lint a lane file (Move_ID,FX_S1,FX_S2,FX_S3[,FX_Notes])

Exit 0 = every row parses, every id exists in codex/fx_bank.csv, budgets and family identity hold.
Prints one line per failing row and a RESULT line. Nothing here re-derives an assignment.
The same grammar is implemented by the client's VFX_BANK parser; this file is the reference.
"""
import csv, re, sys, os, argparse

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = {r['Id']: r for r in csv.DictReader(open(os.path.join(HERE, 'codex', 'fx_bank.csv'), encoding='utf-8'))}
FLAGS = ('!flash', '!shake', '!stop')
TOK = re.compile(r'^(sat|br|s|v|d|n|h|a|r|x|y|w)(-?\d+(?:\.\d+)?)$')
RANGE = {'s': (0.3, 3.5), 'v': (0.3, 4), 'd': (0, 1500), 'n': (1, 4), 'h': (0, 359), 'sat': (0, 1.5),
         'br': (0.3, 1.6), 'a': (0.2, 1), 'r': (-360, 360), 'x': (-100, 100), 'y': (-100, 100), 'w': (10, 100)}
BUDGET = {1: (1, 2, 700), 2: (2, 3, 900), 3: (3, 4, 1200), 'ULT': (4, 5, 2000)}
DIRECTIONAL_GROUPS = ('slash', 'impact', 'fire', 'lightning', 'water', 'flame', 'smoke')

# THE CASTER BEAT ON A TARGET-ANCHOR MOVE (2026-09-17, the pass-2 calibration lane).
# D's ruling has two halves and the linter only ever held one. The first - keep the beat only where
# the caster visibly does something - is a per-move reading and cannot be linted. The SECOND is
# timing: where a beat is kept on a move that lands on someone else, it must play BEHIND the hit, or
# the cast still reads as happening on the caster. `both-sides` already encoded exactly this idea
# (`user >= target + 100`) and target-anchor moves, which are 275 of the 419 rows, had nothing.
# The numbers are the pilot lane's own published rule, `d = max(160, first_target_layer_d + 120)`:
# the lag is 20 ms longer than the both-sides one because a both-sides move's user beat is part of
# the effect (the drain answers on the caster) while this one is an optional flourish and has to
# read as an answer to a hit that has already landed; the 160 ms floor is there because a target
# layer at d0 with a beat at d120 still arrives while the hit reaction is starting.
# ULT rows are EXEMPT: D ruled the 18 ultimates keep their beat and the recipes doc's reason is that
# an ultimate is spectacle and the caster performing it is the point, so its beat leads by design.
# The ultimates lane owns their timing.
CASTER_BEAT_FLOOR, CASTER_BEAT_LAG = 160, 120


def parse(txt):
    """-> (layers, flags, errors). layer = dict(id, anchor, mods)."""
    layers, flags, errs = [], [], []
    for raw in (txt or '').split('|'):
        raw = raw.strip()
        if not raw:
            errs.append('empty layer'); continue
        toks = raw.split()
        if toks[0] in FLAGS:
            if len(toks) > 1: errs.append('flag %s takes no modifiers' % toks[0])
            if toks[0] in flags: errs.append('flag %s repeated' % toks[0])
            flags.append(toks[0]); continue
        m = re.match(r'^(FX-\d{3})@(u|t|g|ug|b)$', toks[0])
        if not m:
            errs.append('bad head token %r (want FX-NNN@u|t|g|ug|b or a !flag)' % toks[0]); continue
        fid, anchor = m.group(1), m.group(2)
        if fid not in BANK: errs.append('unknown sheet %s' % fid)
        mods = {}
        for t in toks[1:]:
            if t in ('f', 'm', 'z', 'k'):
                if t in mods: errs.append('%s repeats the %s flag' % (toks[0], t))
                mods[t] = True; continue
            mm = TOK.match(t)
            if not mm: errs.append('bad token %r in %s' % (t, toks[0])); continue
            k, v = mm.group(1), float(mm.group(2))
            # A REPEATED MODIFIER IS SILENTLY THE LAST ONE. `... sat0.8 k h40 br0.35 sat0.35` parses,
            # renders at sat0.35, and reads to a human as if sat0.8 were doing something. That is how a
            # calibrated token gets pasted on top of an authored one and nobody sees it. Refuse it.
            if k in mods:
                errs.append('%s writes %s twice (%s%g then %s%s) - the last one silently wins'
                            % (toks[0], k, k, mods[k], k, mm.group(2)))
            lo, hi = RANGE[k]
            if not (lo <= v <= hi): errs.append('%s%s out of range %s-%s' % (k, mm.group(2), lo, hi))
            if k in ('d', 'n') and v != int(v): errs.append('%s must be an integer' % k)
            mods[k] = v
        if fid in BANK:
            row = BANK[fid]
            # the +/-90 clamp protects a COLOURED sheet from being rotated far off its own hue into mud.
            # `k` discards that hue (sepia(1) first), so with k there is nothing left to protect. Mirrors
            # VFX_BANK.parse in the client's play/app.js, token for token.
            if 'h' in mods and row['Colored'] == 'yes' and 'k' not in mods:
                hue = float(row['Hue']); diff = abs((mods['h'] - hue + 180) % 360 - 180)
                if diff > 90: errs.append('%s h%d is %d deg from the sheet hue %d (limit 90)' % (fid, mods['h'], diff, hue))
            # A BARE `Colored=yes` LAYER PAINTS THE SHEET'S OWN HUE, NOT THE MOVE'S (2026-09-17).
            # Nothing in the grammar said so and nothing checked it, so 168 rows carry a layer that
            # ignores the move's element and renders whatever colour the art happens to be: FX-039
            # is hue 179, so a bare FX-039 on a purple move paints cyan-white spikes (D, on
            # M-THORNBACK-1). `Colored=no` is not the same case - that sheet has no hue of its own
            # to impose and a bare layer of it is neutral art, which is a choice an author may make.
            if row['Colored'] == 'yes' and 'h' not in mods and 'k' not in mods:
                errs.append('%s is Colored=yes and bare - it paints its own hue %s, not the move\'s. '
                            'Give it h<element>, or the k token from codex/VFX_SHEET_TINTS.md where '
                            'the 90 deg clamp refuses that hue' % (fid, row['Hue']))
            # `br` IS NOT OPTIONAL ON THE `k` PATH - VFX_SPEC.md, the filter-order entry. It is the
            # FIRST primitive there, and without it sepia(1) clamps the white core at 255 and the
            # layer stays a pale flash whatever h and sat say. Every token in VFX_SHEET_TINTS.md
            # carries one; this stops a lane writing `k h40` from memory.
            if 'k' in mods and 'br' not in mods:
                errs.append('%s has k without br - br is the first primitive on that path and '
                            'without it the layer stays a pale flash' % fid)
            if 'f' in mods and row['Group'] not in DIRECTIONAL_GROUPS:
                errs.append('%s (%s) is radial - no f' % (fid, row['Group']))
        layers.append({'id': fid, 'anchor': anchor, 'mods': mods})
    return layers, flags, errs


def length(layer):
    row = BANK.get(layer['id'])
    if not row: return 0
    m = layer['mods']
    return m.get('d', 0) + int(row['Frames']) / (24 * m.get('v', 1)) * m.get('n', 1) * 1000


def check_row(mid, stages, anchor_col, is_ult):
    """stages: {1: txt, 2: txt, 3: txt} (ULT: {1: txt}). -> list of error strings."""
    errs = []
    parsed = {}
    for st, txt in stages.items():
        if not (txt or '').strip():
            errs.append('S%d empty' % st); continue
        layers, flags, e = parse(txt)
        errs += ['S%d: %s' % (st, x) for x in e]
        parsed[st] = (layers, flags)
        lo, hi, ms = BUDGET['ULT' if is_ult else st]
        if not (lo <= len(layers) <= hi): errs.append('S%d has %d sheet layers (want %d-%d)' % (st, len(layers), lo, hi))
        L = max([length(l) for l in layers] or [0])
        if L > ms: errs.append('S%d is %d ms long (limit %d)' % (st, L, ms))
        if '!shake' in flags and not is_ult and st < 3: errs.append('S%d has !shake (S3/ULT only)' % st)
        tl = [l for l in layers if l['anchor'] in ('t', 'g', 'b')]
        ul = [l for l in layers if l['anchor'] in ('u', 'ug')]
        if tl and min(l['mods'].get('d', 0) for l in tl) > 200: errs.append('S%d: first target layer starts after 200 ms' % st)
        if anchor_col == 'self' and tl: errs.append('S%d: a self move plays on the target' % st)
        if anchor_col in ('target', 'ground') and not tl: errs.append('S%d: a target move plays nothing on the target' % st)
        if anchor_col in ('target', 'ground') and tl and ul and not is_ult:
            td = min(l['mods'].get('d', 0) for l in tl)
            need = max(CASTER_BEAT_FLOOR, td + CASTER_BEAT_LAG)
            got = min(l['mods'].get('d', 0) for l in ul)
            if got < need:
                errs.append('S%d: the caster beat starts at d%d - on a target-anchor move it must '
                            'start behind the hit, at d%d or later (max(%d, first target layer d%d '
                            '+ %d))' % (st, got, need, CASTER_BEAT_FLOOR, td, CASTER_BEAT_LAG))
        if anchor_col == 'both-sides':
            if not tl or not ul: errs.append('S%d: a both-sides move needs a target layer AND a user layer' % st)
            elif min(l['mods'].get('d', 0) for l in ul) < min(l['mods'].get('d', 0) for l in tl) + 100:
                errs.append('S%d: both-sides user beat must start >= 100 ms after the target beat' % st)
        if '!flash' in flags and anchor_col == 'self': errs.append('S%d: !flash on a self move' % st)
    if not is_ult and all(s in parsed for s in (1, 2, 3)):
        ids = {s: {l['id'] for l in parsed[s][0]} for s in (1, 2, 3)}
        if not ids[1] <= ids[2]: errs.append('family: S1 sheets %s missing at S2' % sorted(ids[1] - ids[2]))
        if not ids[2] <= ids[3]: errs.append('family: S2 sheets %s missing at S3' % sorted(ids[2] - ids[3]))
        prim = parsed[1][0][0]['id'] if parsed[1][0] else None

        def pscale(s):
            for l in parsed[s][0]:
                if l['id'] == prim: return l['mods'].get('s', 1.0)
            return None
        s1, s2, s3 = pscale(1), pscale(2), pscale(3)
        # D 2026-09-17, the pass-2 artifact Q1: "a harder cut (0.7 / 0.85 / 1.0 / 1.35)" - S1/S2/S3/ULT.
        # The ladder is a fraction of the 380px TILE and a creature's opaque art is 85% of it, so s1.0 already
        # draws the effect at ~118% of the body. The band centres on D's 0.7; the growth checks below carry S2/S3.
        if s1 is not None and not (0.55 <= s1 <= 0.85): errs.append('primary scale at S1 is %s (want 0.55-0.85)' % s1)
        if None not in (s1, s2) and s2 < s1: errs.append('primary scale shrinks S1->S2 (%s -> %s)' % (s1, s2))
        if None not in (s2, s3) and s3 < s2: errs.append('primary scale shrinks S2->S3 (%s -> %s)' % (s2, s3))
    return errs


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('file', nargs='?')
    a = ap.parse_args()
    ref = {r['Move_ID']: r for r in csv.DictReader(open(os.path.join(HERE, 'codex', 'move_vfx.csv'), encoding='utf-8'))}
    src = a.file or os.path.join(HERE, 'codex', 'move_vfx.csv')
    rows = list(csv.DictReader(open(src, encoding='utf-8')))
    bad = 0; seen = set()
    for r in rows:
        mid = r.get('Move_ID', '')
        if mid not in ref: print('FAIL %s: not a move_vfx row' % mid); bad += 1; continue
        if mid in seen: print('FAIL %s: duplicate row' % mid); bad += 1; continue
        seen.add(mid)
        is_ult = mid.startswith('ULT-')
        st = {1: r.get('FX_S1', '')} if is_ult else {1: r.get('FX_S1', ''), 2: r.get('FX_S2', ''), 3: r.get('FX_S3', '')}
        errs = check_row(mid, st, ref[mid]['Target_Anchor'], is_ult)
        if errs:
            bad += 1
            for e in errs: print('FAIL %s (%s): %s' % (mid, ref[mid]['Name'], e))
    missing = [m for m in ref if m not in seen]
    if missing and not a.file:
        bad += len(missing); print('FAIL %d rows without compositions, e.g. %s' % (len(missing), missing[:5]))
    print('RESULT fx_lint: %d rows checked, %d failing, %d rows of move_vfx.csv not in this file' % (len(seen), bad, len(missing)))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
