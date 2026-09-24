#!/usr/bin/env python3
"""afx_lint - the authoring gate for the AFX bank compositions (codex/AFX_SPEC.md).

  python tools/afx_lint.py                        # lint codex/move_vfx.csv (every row must be authored)
  python tools/afx_lint.py --allow-empty          # same, but an unauthored row is reported, not failed
  python tools/afx_lint.py out/afx_lane_a.csv     # lint a lane file (Move_ID,AFX_S1,AFX_S2,AFX_S3[,AFX_Notes])

Exit 0 = every authored row parses, every id exists in codex/afx_bank.csv, budgets, family identity,
hygiene, groups and timing all hold. Prints one line per failing row and a RESULT line.

This file is the REFERENCE for the grammar. The client implements the same verdicts in AFX_BANK.parse
(play/app.js), lifted into assets/vfx/afx_bank.js by tools/gen_vfx_fx.py - if the two disagree, the
sound a reviewer approves is not the sound a player hears, which is the defect this repo keeps
relearning. Nothing here re-derives an assignment; it only refuses a bad one.
"""
import argparse, csv, os, re, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = {r['Id']: r for r in csv.DictReader(open(os.path.join(HERE, 'codex', 'afx_bank.csv'), encoding='utf-8'))}

# codex/AFX_SPEC.md, "The grammar". A token appears at most once in a layer; the range is inclusive.
TOK = re.compile(r'^(g|p|d|n|i|j)(-?\d+(?:\.\d+)?)$')
RANGE = {'g': (0.05, 1.5), 'p': (-12, 12), 'd': (0, 2000), 'n': (1, 4), 'i': (30, 600), 'j': (0, 3)}
INT = ('p', 'd', 'n', 'i', 'j')
# (min layers, max layers, max ms)
BUDGET = {1: (1, 2, 900), 2: (1, 3, 1200), 3: (2, 4, 1600), 'ULT': (3, 5, 2600)}

# A MOVE IS NOT A MENU. The bank pools eight Kenney packs and four of their groups belong to the
# interface, not to a creature hitting another creature: `ui` is the click the player makes, `coin`
# and `jingle` are the casino and the fanfare (standing rule 4, no cheerful chimes, no casino), and
# `door` is furniture. They stay in the bank because afx_events.csv needs them; they are refused here.
MOVE_GROUPS = ('impact', 'material', 'melee', 'blast', 'arcane', 'machine', 'creature', 'foley', 'footstep')
REFUSED_GROUPS = ('ui', 'coin', 'jingle', 'door')

# Standing rule 1, judged by measurement, not by ear: a clip with a fifth of its energy above 3 kHz
# is SHRILL and may only be used pitched down (2^(p/12) moves its whole spectrum with it); a clip
# that already peaks over 0 dBFS is CLIPPED and may only be used quiet.
SHRILL_OVER3K, SHRILL_MAX_P = 20.0, -3
CLIP_PEAK, CLIP_MAX_G = 0.0, 0.7
# Rule 3, at the mix rather than in the file: layers that land together add up. 60 ms is the window
# inside which two onsets read as one hit.
SIMUL_MS, SIMUL_MAX_G = 60, 1.6
# The sound follows the picture. A composition that starts before or after the VFX it is scoring
# reads as a different event; 40 ms is about where a listener stops hearing one impact.
ALIGN_MS = 40
# A cast beat is quieter than the hit: if the picture's contact is more than 100 ms away, a layer
# sitting at d0 is the wind-up, and a wind-up louder than half does not read as one.
CAST_BEAT_MS, CAST_BEAT_MAX_G = 100, 0.5


def parse(txt):
    """-> (layers, errs). layer = dict(id, mods). Mirrors AFX_BANK.parse in the client."""
    layers, errs = [], []
    for raw in (txt or '').split('|'):
        raw = raw.strip()
        if not raw:
            errs.append('empty layer'); continue
        toks = raw.split()
        if not re.match(r'^AFX-\d{3}$', toks[0]):
            errs.append('bad head token %r (want AFX-NNN)' % toks[0]); continue
        cid = toks[0]
        row = BANK.get(cid)
        if row is None:
            errs.append('unknown clip %s' % cid)
        mods = {}
        for t in toks[1:]:
            m = TOK.match(t)
            if not m:
                errs.append('bad token %r in %s' % (t, cid)); continue
            k, v = m.group(1), float(m.group(2))
            # A repeated token is silently the last one - the same trap fx_lint closed on the VFX side.
            if k in mods:
                errs.append('%s writes %s twice (%s%g then %s%s) - the last one silently wins'
                            % (cid, k, k, mods[k], k, m.group(2)))
            lo, hi = RANGE[k]
            if not (lo <= v <= hi):
                errs.append('%s %s%s out of range %s..%s' % (cid, k, m.group(2), lo, hi))
            if k in INT and v != int(v):
                errs.append('%s %s must be an integer' % (cid, k))
            mods[k] = v
        if 'i' in mods and mods.get('n', 1) <= 1:
            errs.append('%s has i%g without n>1 - nothing to space' % (cid, mods['i']))
        if row is not None:
            over3k, peak = float(row['Over3k_Pct']), float(row['Peak_dBFS'])
            if over3k >= SHRILL_OVER3K and mods.get('p', 0) > SHRILL_MAX_P:
                errs.append('%s is SHRILL (%.1f%% above 3 kHz) and needs p<=%d, has p%g'
                            % (cid, over3k, SHRILL_MAX_P, mods.get('p', 0)))
            if peak > CLIP_PEAK and mods.get('g', 1) > CLIP_MAX_G:
                errs.append('%s is CLIPPED (peak %+.1f dBFS) and needs g<=%s, has g%g'
                            % (cid, peak, CLIP_MAX_G, mods.get('g', 1)))
            if row['Group'] in REFUSED_GROUPS:
                errs.append('%s is a %s clip - refused on a move (interface and fanfare groups)'
                            % (cid, row['Group']))
            elif row['Group'] not in MOVE_GROUPS:
                errs.append('%s is group %r, which is not a move group' % (cid, row['Group']))
        layers.append({'id': cid, 'mods': mods})
    return layers, errs


def layer_end(layer):
    """d + (n-1)*i + the clip's own length, which p stretches or shortens with the playback rate."""
    row = BANK.get(layer['id'])
    if not row:
        return 0.0
    m = layer['mods']
    n, i = m.get('n', 1), m.get('i', 90)
    return m.get('d', 0) + (n - 1) * i + float(row['Seconds']) * 1000.0 / (2 ** (m.get('p', 0) / 12.0))


def length_ms(layers):
    return max([layer_end(l) for l in layers] or [0.0])


def fx_anchor(fx_txt):
    """(align_d, hit_d) read off an FX_S<stage> composition: the delay of its first TARGET layer,
    falling back to its first layer for a self / ground-on-user move that plays on nobody else.

    FIRST MEANS EARLIEST, NOT LEFTMOST. A composition's layers are usually written in time order and
    are not required to be - ULT-WARRIOR-1 opens with `FX-047@u d180` and its second layer is at d0 -
    so taking the leftmost would anchor the sound 180 ms behind a picture that has already started.
    tools/fx_lint.py reads its own target beat with min() for the same reason."""
    ds, tds = [], []
    for raw in (fx_txt or '').split('|'):
        raw = raw.strip()
        if not raw or raw.startswith('!'):
            continue
        m = re.match(r'^FX-\d{3}@(u|t|g|ug|b)\b', raw)
        if not m:
            continue
        d = 0
        for t in raw.split()[1:]:
            mm = re.match(r'^d(-?\d+(?:\.\d+)?)$', t)
            if mm:
                d = float(mm.group(1))
        ds.append(d)
        if m.group(1) in ('t', 'g', 'b'):
            tds.append(d)
    pool = tds or ds
    if not pool:
        return None, None
    at = min(pool)
    return at, at


def check_row(mid, stages, fx, is_ult):
    """stages/fx: {stage: text}. -> list of error strings."""
    errs, parsed = [], {}
    for st, txt in sorted(stages.items()):
        layers, e = parse(txt)
        errs += ['S%d: %s' % (st, x) for x in e]
        parsed[st] = layers
        lo, hi, ms = BUDGET['ULT' if is_ult else st]
        if not (lo <= len(layers) <= hi):
            errs.append('S%d has %d layers (want %d-%d)' % (st, len(layers), lo, hi))
        L = length_ms(layers)
        if L > ms:
            errs.append('S%d is %d ms long (limit %d)' % (st, round(L), ms))
        # layers that land inside one 60 ms window add up on the sfx bus
        for a in layers:
            da = a['mods'].get('d', 0)
            tot = sum(b['mods'].get('g', 1) for b in layers if abs(b['mods'].get('d', 0) - da) <= SIMUL_MS)
            if tot > SIMUL_MAX_G:
                errs.append('S%d: %.2f of gain lands within %d ms of d%g (limit %s)'
                            % (st, tot, SIMUL_MS, da, SIMUL_MAX_G))
                break
        # the sound follows the picture
        at, hit = fx_anchor(fx.get(st))
        if at is not None and layers:
            # THE TWO TIMING RULES COMPOSE, AND ONLY ONE ORDER OF READING LETS THEM. The pin is on the
            # composition's MAIN beat - the first layer loud enough to be heard as the hit. The quiet
            # d0 wind-up the second rule contemplates would otherwise be impossible to write on any
            # move whose picture lands late: aligning it would break the pin and keeping it would break
            # the alignment. So a layer at or under g0.5 is exempt from the pin and bound by the beat
            # rule instead, and a composition of nothing but quiet layers pins its earliest.
            loud = [l for l in layers if l['mods'].get('g', 1) > CAST_BEAT_MAX_G] or layers
            d0 = min(l['mods'].get('d', 0) for l in loud)
            if abs(d0 - at) > ALIGN_MS:
                errs.append('S%d: the main beat is at d%g but the FX composition starts at d%g (+/-%d ms)'
                            % (st, d0, at, ALIGN_MS))
            if hit > CAST_BEAT_MS:
                for l in layers:
                    if l['mods'].get('d', 0) == 0 and l['mods'].get('g', 1) > CAST_BEAT_MAX_G:
                        errs.append('S%d: %s sits at d0 with g%g while the hit lands at d%g - a cast '
                                    'beat needs g<=%s' % (st, l['id'], l['mods'].get('g', 1), hit,
                                                          CAST_BEAT_MAX_G))
    # FAMILY IDENTITY. One creature's move has to be recognisable as itself across its three stages,
    # so the clip S1 leads with must still be audible at S2 and S3. It may be re-pitched or re-timed.
    if not is_ult and all(parsed.get(s) for s in (1, 2, 3)):
        prim = parsed[1][0]['id']
        for s in (2, 3):
            if prim not in [l['id'] for l in parsed[s]]:
                errs.append('family: S1 leads with %s and S%d never plays it' % (prim, s))
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file', nargs='?')
    ap.add_argument('--allow-empty', action='store_true',
                    help='report unauthored rows instead of failing them (the pre-authoring state)')
    a = ap.parse_args()

    ref = {r['Move_ID']: r for r in csv.DictReader(
        open(os.path.join(HERE, 'codex', 'move_vfx.csv'), encoding='utf-8'))}
    src = a.file or os.path.join(HERE, 'codex', 'move_vfx.csv')
    rows = list(csv.DictReader(open(src, encoding='utf-8-sig')))

    bad = empty = 0
    seen = set()
    for r in rows:
        mid = (r.get('Move_ID') or '').strip()
        if mid not in ref:
            print('FAIL %s: not a move_vfx row' % mid); bad += 1; continue
        if mid in seen:
            print('FAIL %s: duplicate row' % mid); bad += 1; continue
        seen.add(mid)
        is_ult = mid.startswith('ULT-')
        keys = [1] if is_ult else [1, 2, 3]
        stages = {s: (r.get('AFX_S%d' % s) or '').strip() for s in keys}
        if not any(stages.values()):
            empty += 1
            print('UNAUTHORED %s (%s): no AFX composition at any stage' % (mid, ref[mid]['Name']))
            continue
        blank = [s for s in keys if not stages[s]]
        if blank:
            bad += 1
            print('FAIL %s (%s): S%s empty while other stages are authored'
                  % (mid, ref[mid]['Name'], ','.join(str(s) for s in blank)))
            continue
        fx = {s: ref[mid].get('FX_S%d' % s) for s in keys}
        errs = check_row(mid, stages, fx, is_ult)
        if errs:
            bad += 1
            for e in errs:
                print('FAIL %s (%s): %s' % (mid, ref[mid]['Name'], e))

    missing = [m for m in ref if m not in seen]
    if missing and not a.file:
        bad += len(missing)
        print('FAIL %d rows of move_vfx.csv absent from this file, e.g. %s' % (len(missing), missing[:5]))
    print('RESULT afx_lint: %d rows checked, %d authored, %d unauthored, %d failing, %d rows of '
          'move_vfx.csv not in this file%s'
          % (len(seen), len(seen) - empty, empty, bad, len(missing),
             '  [--allow-empty]' if a.allow_empty else ''))
    sys.exit(1 if bad or (empty and not a.allow_empty) else 0)


if __name__ == '__main__':
    main()
