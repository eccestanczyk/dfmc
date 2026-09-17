#!/usr/bin/env python3
"""THE TINT SOLVER (VFX pass 2, D 2026-09-17).

D ruled: keep the white sheets, re-hue them dark per element. The `k` token makes a white sheet
colourable (it forces the neutral/sepia path; hue-rotate alone returns white for a white pixel).
But shooting it proved THE HUE THAT LANDS IS NOT THE HUE AUTHORED - every sheet is its own mix of
white core and coloured halo, so an authoring lane cannot write h134 and hope for green.

RE-SOLVED 2026-09-17 AFTER THE FILTER REORDER. The first run of this tool put 0 of 84 pairs over
the sat >= 25% leg, and that was the tool finding an ENGINE defect, not a limit of the sheets:
`sheetFilter` emitted `brightness` LAST, and a browser clamps to 8 bits between filter primitives,
so sepia(1) returned rgb(255,255,239) on a white pixel - two channels pinned - and every later pass
worked on a pixel whose chroma was gone. `brightness` now runs FIRST on the neutral path, which
moves the pixel off the ceiling before sepia and is worth about 40 points of saturation. Everything
in this file that assumed the old order has moved with it: `br` is no longer a numpy post-pass, it
is a browser axis (see solve_sheet), and the hue map is read dark rather than at br 1.0.

So each of the 12 near-white sheets needs its own token per element, measured once on that sheet and
then copied into every row that uses it: 12 x 7 = 84 measurements, not 1221 judgements. This tool
makes them and writes the table.

  python tools/vfx_calibrate.py                        all 12 sheets, all 7 elements
  python tools/vfx_calibrate.py --sheets FX-038 --elements green,blue --no-md
  python tools/vfx_calibrate.py --filter-check         the `k` chain, browser vs the spec matrices

THE TARGET, per sheet x element, measured on the TOP LUMINANCE DECILE of the layer's own painted
pixels:  hue within +/-18 deg of the element hue, HSL lightness <= 55%, flat-white fraction 0%
(HSV value >= 250 AND HSV saturation <= 0.08), and HSL saturation inside the element's BAND.
Search space is the grammar's own: h 0-359 integer, br 0.3-1.6, sat 0-1.5. `k` is always present.

THE BAND, added 2026-09-17 on D's ruling. The saturation leg used to be a floor and nothing else,
so the solver spent every point of chroma it could reach. That is right for an element that IS a
colour and wrong for one that is not: `bone` solved to a fully saturated gold (79-87% on 11 of the
12 sheets) and it is the DEFAULT element, 217 of the 419 moves. See SAT_BAND - an element listed
there is solved to sit inside its band, one that is not keeps the bare floor with no ceiling.

HOW IT MEASURES - vfx_shoot's method, and this file reuses its server, art routing, page and seeding
rather than re-growing them:
  1. ONE carrier move (--move, Targets=enemy so the layer lands on the enemy lead), one seed, one
     tile, one scale, for all 12 sheets - so the sheets are comparable to each other;
  2. the composition is a page-level override of FX_S3, exactly vfx_shoot --comp. Nothing is written
     to codex/move_vfx.csv;
  3. the cast receipt's lenMs is READ and the scrub lands INSIDE it (fractions 0.3/0.5/0.7, the
     brightest kept). Scrubbing to 300ms on a layer whose life is 292ms measures nothing and reads as
     the token failing; that happened once, it does not happen here;
  4. DIFFERENCE AGAINST A CLEAN PLATE OF THE SAME TILE: the effect frame is shot, then the .vxb
     wrappers alone are removed - every animation still paused at the same currentTime, so the
     creature has not moved a pixel - and the same clip is shot again;
  5. and then the SECOND way to measure the creature instead of the effect is closed too. A decile
     taken over the whole footprint picks the brightest pixels in it, and once the layer is darkened
     those are the ones the creature shines through. So the mask is the changed pixels WHERE THE
     PLATE IS DARK (--plate-max): the layer over the floor, alone. That mask is frozen for the sheet,
     so every token on it is measured on the same pixels.

WHY IT IS MINUTES AND NOT HOURS. The browser is asked for one shot per candidate HUE and one per
candidate `br`. `sat` is the LAST primitive in the chain, so it is applied to the measured pixels in
numpy to rank the sat axis for free, and only the winner is re-shot. Every number in the table is a
real screenshot measured by rule 5 - none is a prediction.

--filter-check renders a literal white div through BOTH orders of the `k` chain in the same browser,
beside the spec matrices, and prints the saturation each reaches. That is the receipt for the
reorder: `sepia(1) saturate(2.4) hue-rotate(60deg) brightness(0.7)` renders rgb(157,178,163), HSL
saturation 12%; `brightness(0.5) sepia(1) saturate(2.4) hue-rotate(60deg)` renders rgb(102,179,76),
40%. A MODEL OF A RENDERER IS NOT THE RENDERER - the first filter table in
dfmc-client/docs/vfx-pass2-recipes-2026-09-17.md composed the matrices and clamped once at the end,
reported rgb(142,178,106), and cost this run a whole calibration pass. Shoot it.

Output: the table on stdout, codex/VFX_SHEET_TINTS.md, and one contact sheet per sheet under --shots
(the untinted layer plus its 7 calibrated elements) so the table can be looked at and not only read.
"""
import argparse, csv, io, json, math, os, re, subprocess, sys, time
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vfx_shoot as VS                  # server, art routing, page, seeding - not re-grown here

ROOT = HERE.parent

# The 12 near-white sheets, in the order the sheet census ranked them by near-white fraction.
SHEETS = ['FX-051', 'FX-034', 'FX-038', 'FX-032', 'FX-045', 'FX-044',
          'FX-043', 'FX-029', 'FX-042', 'FX-036', 'FX-050', 'FX-008']

# VFX_Color -> hue, from the client's VFXHEX (and the same numbers as VXHITH, which is the point).
ELEMENTS = [('red', 0), ('rust', 19), ('bone', 38), ('green', 134),
            ('blue', 222), ('purple', 272), ('crimson', 357)]

HUE_TOL, LUM_MAX, SAT_MIN = 18.0, 55.0, 25.0        # the target, as numbers
LUM_AIM = 53.0                                      # sit just inside it, and spend the rest on chroma

# THE SATURATION CEILING, per element. The leg was a FLOOR and nothing else, so the solver spent
# everything it had on chroma. `bone` came out of the 84/84 solve at saturation 79-87% on 11 of the
# 12 sheets - a vivid gold, the loudest tile on its own contact sheet, louder in chroma than the
# untinted white it replaced. Three things make that wrong and they compound:
#   1. `bone` is the DEFAULT element, 217 of the 419 moves. A vivid gold there is a uniform gold
#      wash over half the game's abilities; `bone` is the "no strong element" case and has to read
#      as restrained.
#   2. Its own hex is #d8cfc0, a light NEUTRAL. Nothing in the element table asks for gold.
#   3. `vxHitBone` measures 3.8% saturation over real creature art. Solved against a bare floor the
#      LAYER flashes vivid gold while the SPRITE tints near-grey - and layer and flash agreeing is
#      the whole reason the element hue table and VXHITH share their numbers.
# So: a table, not a special case in a branch, because a later element may want one too. An element
# absent from here keeps (SAT_MIN, None) - the bare floor, no ceiling, nothing changed.
SAT_BAND = {                                   # element -> (floor %, ceiling %)
    'bone': (0.0, 18.0),                       # a dim, faintly warm neutral, never a colour
}


def band(name):
    return SAT_BAND.get(name, (SAT_MIN, None))


def sat_aim(name):
    """Where inside the band to sit. With no ceiling that is 'as high as the rest of the target
    allows'. With one it is just UNDER the ceiling and not at zero: hue is a chroma-weighted mean,
    so a layer with no chroma at all has no measurable hue and would fail the hue leg instead."""
    lo, hi = band(name)
    return lo if hi is None else max(lo, hi - 3.0)

# The search axes. `sat` is the LAST pass in the chain, so it is ranked in numpy on pixels already
# shot; `br` is the FIRST pass since 2026-09-17, so every value of it costs a screenshot.
# SATS STOPS AT 0.8 ON PURPOSE, though the grammar allows 0. Measured on FX-051 red: the whole
# 0-1.5 range lets the solver buy 5 points of luminance (71% -> 66%, still outside the 55% leg)
# for 37 points of chroma (sat 63% -> 26%). That trade turns the layer back into the tinted grey
# D rejected and does not satisfy the leg it was spent on, so the axis is floored where the row
# still reads as a colour. Raise it here, with a screenshot, if that judgement is ever revisited.
SATS = [round(0.8 + i * 0.05, 3) for i in range(15)]        # 0.80 .. 1.50
# A BANDED element is the case that floor was protecting against, and it wants the opposite: the
# whole point of a ceiling is that the row must NOT spend chroma, so its axis is the grammar's
# entire range. It costs nothing - `sat` is the last primitive, so the axis is ranked in numpy on
# pixels already shot and only the winner is re-shot in the browser.
SATS_FULL = [round(i * 0.05, 3) for i in range(31)]        # 0.00 .. 1.50


def sats_for(name):
    return SATS if band(name)[1] is None else SATS_FULL
import fx_lint as FL                    # the grammar's own RANGE - not a third copy of the floor
BR_MIN = FL.RANGE['br'][0]              # 0.3 since 2026-09-17; it was 0.5, and 52 of 84 pairs sat
                                        # on the old floor and still could not reach lum <= 55%
BRS = [round(BR_MIN + i * 0.05, 3) for i in range(15)]      # 0.30 .. 1.00, one shot each
HMAP_BR = 0.6                                       # the hue map is read DARK - see solve_sheet


# ---------------------------------------------------------------- the page, on top of vfx_shoot's
CAST_JS = r"""
([id, stage, txt]) => {
  const mv = MOVE_BY_ID[id];
  if (!mv) return {err: 'no such move: ' + id};
  if (!VFX[id]) return {err: 'no vfx row: ' + id};
  VFX[id]['FX_S' + stage] = txt;              /* page-level override; the CSV is never touched */
  stopLoop(); playAll(false); clearFxNow();
  const _rnd = Math.random; Math.random = () => 0;               /* pick() takes index 0, always */
  const _st = window.setTimeout; window.setTimeout = () => 0;    /* no teardown mid-scrub */
  let rc;
  try { rc = castNow(mv, stage, 'ally'); }
  finally { window.setTimeout = _st; Math.random = _rnd; }
  if (!rc) return {err: 'castNow returned null'};
  if (!rc.bank) return {err: 'the parser rejected: ' + txt};
  if (!rc.onTgt) return {err: 'no target-side layer mounted for: ' + txt};
  document.getAnimations().forEach(a => { try { a.pause(); } catch (e) {} });
  const tEl = document.getElementById(rc.tside).children[rc.tidx];
  const b = tEl.getBoundingClientRect();
  return {lenMs: rc.lenMs, tile: {x: b.x + scrollX, y: b.y + scrollY, w: b.width, h: b.height}};
}
"""

# the layers alone, by class: clearFxNow() also rewrites the units' inline animation style, and the
# plate has to be the same frame of the same paused idle as the effect shot.
STRIP_JS = "() => { document.querySelectorAll('#ally .vxb,#enemy .vxb').forEach(n => n.remove()); }"


# ---------------------------------------------------------------- the CSS filter chain, in numpy
def _mat(m):
    return np.array(m, dtype=np.float64).reshape(3, 3).T        # spec rows -> column-apply


SEPIA = _mat([0.393, 0.769, 0.189, 0.349, 0.686, 0.168, 0.272, 0.534, 0.131])


def sat_mat(s):
    return _mat([0.213 + 0.787 * s, 0.715 - 0.715 * s, 0.072 - 0.072 * s,
                 0.213 - 0.213 * s, 0.715 + 0.285 * s, 0.072 - 0.072 * s,
                 0.213 - 0.213 * s, 0.715 - 0.715 * s, 0.072 + 0.928 * s])


def hue_mat(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return _mat([0.213 + c * 0.787 - s * 0.213, 0.715 - c * 0.715 - s * 0.715, 0.072 - c * 0.072 + s * 0.928,
                 0.213 - c * 0.213 + s * 0.143, 0.715 + c * 0.285 + s * 0.140, 0.072 - c * 0.072 - s * 0.283,
                 0.213 - c * 0.213 - s * 0.787, 0.715 - c * 0.715 + s * 0.715, 0.072 + c * 0.928 + s * 0.072])


SAT24 = sat_mat(2.4)


def k_chain(px, h, br=1.0):
    """`brightness(br) sepia(1) saturate(2.4) hue-rotate(h-40)` - the `k` branch of sheetFilter as it
    is emitted since 2026-09-17, clamped between passes the way a browser clamps an 8-bit
    intermediate buffer. BRIGHTNESS IS FIRST and that is the whole point: sepia(1) on a white pixel
    returns rgb(255,255,239), two channels pinned at 255, and everything after it then works on a
    pixel whose chroma has already been thrown away. --filter-check renders both orders and shows
    the gap (12% saturation against 40% on the same hue). Used only by --filter-check; every number
    in the table is a screenshot."""
    o = np.clip(px * br, 0, 1)
    o = np.clip(o @ SEPIA, 0, 1)
    o = np.clip(o @ SAT24, 0, 1)
    return np.clip(o @ hue_mat(round(h) - 40), 0, 1)


def tail(px, sat):
    """THE ONLY pass still applicable after the fact: saturate(sat) is the last primitive in the
    chain, so it can be applied in numpy to pixels the browser has already rendered at (h, br, sat 1)
    and the grid is ranked without a screenshot. `br` USED to be here too and no longer can be - it
    now runs BEFORE sepia(1), so it changes what every later pass sees and has to be a browser axis.
    That is why this solver shoots a br ladder per element where it used to shoot none."""
    if abs(sat - 1.0) > 1e-9:
        return np.clip(px @ sat_mat(sat), 0, 1)
    return px


# ---------------------------------------------------------------- the four numbers
def stats(px):
    """hue / HSL saturation / HSL lightness / flat-white share, over the TOP LUMINANCE DECILE.
    hue is a chroma-weighted circular mean - an achromatic pixel has no hue worth averaging."""
    L0 = (px.max(1) + px.min(1)) / 2.0
    k = max(1, int(round(len(px) * 0.10)))
    p = px[np.argsort(L0)[-k:]]
    mx, mn = p.max(1), p.min(1)
    L, ch = (mx + mn) / 2.0, mx - mn
    den = 1.0 - np.abs(2 * L - 1.0)
    S = np.where(den > 1e-6, ch / np.maximum(den, 1e-6), 0.0)
    r, g, b = p[:, 0], p[:, 1], p[:, 2]
    d = np.where(ch < 1e-9, 1.0, ch)
    hu = np.where(mx == r, ((g - b) / d) % 6.0,
                  np.where(mx == g, (b - r) / d + 2.0, (r - g) / d + 4.0)) * 60.0
    hu = np.where(ch < 1e-9, 0.0, hu % 360.0)
    ang = np.radians(hu)
    H = math.degrees(math.atan2(float((ch * np.sin(ang)).sum()),
                                float((ch * np.cos(ang)).sum()))) % 360.0
    hsv_s = np.where(mx > 1e-6, ch / np.maximum(mx, 1e-6), 0.0)
    return {'hue': H, 'sat': float(S.mean() * 100), 'lum': float(L.mean() * 100),
            'flat': float(np.mean((mx >= 250 / 255.0) & (hsv_s <= 0.08)) * 100.0)}


def hue_err(a, b):
    return abs(((a - b + 180.0) % 360.0) - 180.0)


def misses(st, want, name=None):
    lo, hi = band(name) if name is not None else (SAT_MIN, None)
    out = []
    if hue_err(st['hue'], want) > HUE_TOL:
        out.append('hue %.0f deg off' % hue_err(st['hue'], want))
    if st['lum'] > LUM_MAX:
        out.append('lum %.0f%%' % st['lum'])
    if st['flat'] > 0:
        out.append('flat %.1f%%' % st['flat'])
    if st['sat'] < lo:
        out.append('sat %.0f%% under the %g%% floor' % (st['sat'], lo))
    if hi is not None and st['sat'] > hi:
        out.append('sat %.0f%% over the %g%% ceiling' % (st['sat'], hi))
    return out


def score(st, want, name=None):
    """Rank the grid: get inside hue, flat and lum first, then spend what is left on chroma - or,
    for a BANDED element, on getting back down under its ceiling. The ceiling is weighted like the
    hue leg, because for `bone` it is exactly as much of a ruling as the hue is."""
    lo, hi = band(name) if name is not None else (SAT_MIN, None)
    s = -(max(0.0, hue_err(st['hue'], want) - 6.0) * 4.0
          + max(0.0, st['lum'] - LUM_AIM) * 3.0
          + st['flat'] * 50.0
          + max(0.0, lo - st['sat']) * 1.0)
    if hi is None:
        return s + 0.05 * st['sat']
    return s - max(0.0, st['sat'] - hi) * 4.0 - 0.05 * abs(st['sat'] - sat_aim(name))


def br_of(tk):
    """the `br` a written token carries, 1.0 when it omits one - so a solved row can be asked
    whether it is sitting on the grammar's floor."""
    m = re.search(r'\bbr([0-9.]+)', tk)
    return float(m.group(1)) if m else 1.0


def token(h, sat, br):
    t = 'k h%d' % (int(round(h)) % 360)
    if abs(br - 1.0) > 1e-9:
        t += ' br%g' % round(br, 3)
    if abs(sat - 1.0) > 1e-9:
        t += ' sat%g' % round(sat, 3)
    return t


# ---------------------------------------------------------------- the rig
class Rig(object):
    def __init__(self, pg, move, stage, scale, pad):
        self.pg, self.move, self.stage, self.scale, self.pad = pg, move, stage, scale, pad
        self.clip = None
        self.casts = 0

    def cast(self, fid, mods=''):
        txt = ('%s@t s%g %s' % (fid, self.scale, mods)).strip()
        rc = self.pg.evaluate(CAST_JS, [self.move, self.stage, txt])
        if rc.get('err'):
            sys.exit('%s: %s' % (txt, rc['err']))
        self.casts += 1
        if self.clip is None:           # frozen on the first cast: every shot is the same pixels
            t = rc['tile']
            self.clip = {'x': max(0.0, t['x'] - t['w'] * self.pad),
                         'y': max(0.0, t['y'] - t['h'] * self.pad),
                         'width': t['w'] * (1 + 2 * self.pad), 'height': t['h'] * (1 + 2 * self.pad)}
        return rc

    def shot(self, ms):
        self.pg.evaluate(VS.SCRUB_JS, int(ms))
        return self.pg.screenshot(clip=self.clip, type='png')

    def strip(self):
        self.pg.evaluate(STRIP_JS)


def rgb(png):
    from PIL import Image
    return np.asarray(Image.open(io.BytesIO(png)).convert('RGB'), dtype=np.float64) / 255.0


# ---------------------------------------------------------------- one sheet
def solve_sheet(rig, fid, elements, plate_max, hue_step, carry=None, verbose=True):
    # --- where in the layer's own life is it brightest, and which pixels are the layer's
    best = None
    for f in (0.3, 0.5, 0.7):
        rc = rig.cast(fid)
        ms = int(round(rc['lenMs'] * f))
        eff = rig.shot(ms)
        rig.strip()
        A, P = rgb(eff), rgb(rig.shot(ms))
        m = (np.abs(A - P).max(2) >= 12 / 255.0) & (P.max(2) <= plate_max)
        if m.sum() < 300:
            continue
        lit = float(A[m].max(1).mean()) * m.sum()
        if best is None or lit > best[0]:
            best = (lit, ms, m, eff, rc['lenMs'])
    if best is None:
        sys.exit('%s: no pixels of this layer sit over the floor at any fraction of its life' % fid)
    _, ms, mask, ref_png, lenMs = best
    npx = int(mask.sum())

    def measure(mods):
        rig.cast(fid, mods)
        png = rig.shot(ms)
        return rgb(png)[mask], png

    # --- the hue the sheet actually lands, per authored h. One shot each; nothing else needs one.
    # READ AT HMAP_BR, NOT AT br 1.0: brightness is the FIRST pass now, and at br 1.0 sepia(1) still
    # pins the white core at 255 and the landed hue is the clamped one. The map has to be made in
    # the regime the tokens are written in, or the walk below aims at a hue no dark token reaches.
    hmap = {}
    for h in range(0, 360, hue_step):
        px, _ = measure(token(h, 1.0, HMAP_BR))
        hmap[h] = stats(px)
    if verbose:
        print('  %s  life %dms  scrub %dms  layer-over-floor px %d  hue map %s'
              % (fid, lenMs, ms, npx,
                 ' '.join('%d->%d' % (h, round(hmap[h]['hue'])) for h in sorted(hmap))))

    rows, art = [], [(ref_png, '%s  NO TINT - what ships today\nlife %d ms, read at %d ms'
                      % (fid, lenMs, ms), False)]

    # CARRIED ROWS ARE RE-SHOT BUT NOT RE-SOLVED. When one element is re-solved the others
    # are settled and their published tokens must not move, so their token is rendered on
    # this same rig for the contact sheet - which stays the eight-tile comparison it is
    # looked at as - while the row itself is the published one, carried verbatim.
    solving = dict(elements)
    carry = carry or {}
    for name, _w in ELEMENTS:
        if name not in solving:
            r = carry.get(name)
            if r is None:
                continue
            _, png = measure(r['token'])
            art.append((png, '%s %s  %s\nhue %.0f (want %d)  sat %.0f  lum %.0f  '
                             'flat %.1f%s\ncarried, not re-solved'
                        % (fid, name, r['token'], r['hue'], r['want'], r['sat'],
                           r['lum'], r['flat'], '' if r['ok'] else '   MISS'),
                        not r['ok']))
            rows.append(r)
            if verbose:
                print('    %-8s want %3d  %-24s -> hue %5.1f  sat %4.1f  lum %4.1f  '
                      'flat %4.1f  carried'
                      % (name, r['want'], r['token'], r['hue'], r['sat'], r['lum'],
                         r['flat']))
            continue
        want = solving[name]
        # the authored h whose LANDED hue is closest, then walk it in with the local gradient
        h = min(hmap, key=lambda x: hue_err(hmap[x]['hue'], want))
        px, _ = measure(token(h, 1.0, HMAP_BR))
        base = stats(px)
        for _ in range(3):
            e = ((want - base['hue'] + 180) % 360) - 180
            if abs(e) <= 4.0:
                break
            nb = sorted(hmap, key=lambda x: hue_err(x, h))[1:3]
            g = 0.0
            for o in nb:
                d = ((hmap[o]['hue'] - base['hue'] + 180) % 360) - 180
                s = ((o - h + 180) % 360) - 180
                if abs(s) > 1e-6 and abs(d) > 1e-6:
                    g = max(g, abs(d / s))
            step = int(round(e / g)) if g > 1e-6 else int(round(e))
            step = max(-40, min(40, step)) or (1 if e > 0 else -1)
            h2 = (h + step) % 360
            px2, _ = measure(token(h2, 1.0, HMAP_BR))
            s2 = stats(px2)
            if hue_err(s2['hue'], want) >= hue_err(base['hue'], want):
                break
            h, px, base = h2, px2, s2

        # THE BR LADDER, IN THE BROWSER. br is the FIRST pass in the chain since 2026-09-17, so it
        # is no longer a post-pass that can be applied in numpy - it changes what sepia(1) sees and
        # therefore the whole result. One shot per br; `sat` is still last, so the sat axis is still
        # free and is ranked on the pixels each shot already returns.
        cand = None
        for b in BRS:
            got, png = measure(token(h, 1.0, b))
            s = max(sats_for(name), key=lambda x: score(stats(tail(got, x)), want, name))
            if abs(s - 1.0) > 1e-9:                      # verify the sat pick in the browser too
                got, png = measure(token(h, s, b))
            st = stats(got)
            ok = not misses(st, want, name)
            if cand is None or (ok and not cand[0]) or (ok == cand[0]
                    and score(st, want, name) > score(cand[2], want, name)):
                cand = (ok, token(h, s, b), st, png)
        ok, tk, st, png = cand
        rows.append(dict(sheet=fid, element=name, want=want, token=tk, ok=ok, ms=ms, lenMs=lenMs,
                         px=npx, misses=misses(st, want, name), **st))
        art.append((png, '%s %s  %s\nhue %.0f (want %d)  sat %.0f  lum %.0f  flat %.1f%s'
                    % (fid, name, tk, st['hue'], want, st['sat'], st['lum'], st['flat'],
                       '' if ok else '   MISS'), not ok))
        if verbose:
            print('    %-8s want %3d  %-24s -> hue %5.1f  sat %4.1f  lum %4.1f  flat %4.1f  %s'
                  % (name, want, tk, st['hue'], st['sat'], st['lum'], st['flat'],
                     'ok' if ok else 'MISS: ' + ', '.join(misses(st, want, name))))
    return rows, art


# ---------------------------------------------------------------- output
def contact(art, out_png, title, cols=4, tile_w=360):
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 13)
        big = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', 17)
    except Exception:
        font = big = ImageFont.load_default()
    ims = [Image.open(io.BytesIO(p)).convert('RGB') for p, _, _ in art]
    nlab = max(len(l.split('\n')) for _, l, _ in art)
    tile_h, lab = int(tile_w * ims[0].height / float(ims[0].width)), 6 + 16 * nlab
    rows = (len(ims) + cols - 1) // cols
    im = Image.new('RGB', (cols * tile_w, 30 + rows * (tile_h + lab)), (14, 14, 18))
    d = ImageDraw.Draw(im)
    d.text((8, 8), title, font=big, fill=(235, 225, 190))
    for i, (t, (_, lbl, warn)) in enumerate(zip(ims, art)):
        x, y = (i % cols) * tile_w, 30 + (i // cols) * (tile_h + lab)
        im.paste(t.resize((tile_w, tile_h), Image.LANCZOS), (x, y))
        d.rectangle([x, y, x + tile_w - 1, y + tile_h - 1], outline=(70, 70, 80))
        for j, line in enumerate(lbl.split('\n')):
            d.text((x + 4, y + tile_h + 3 + 16 * j), line, font=font,
                   fill=(255, 120, 110) if warn else (190, 195, 205))
    im.save(out_png)
    return out_png


MD_HEAD = re.compile(r'^### (FX-\d+)')
MD_ROW = re.compile(
    r'^\|\s*([a-z]+)(?:\s+\*\*MISS:\s*([^*]+)\*\*)?\s*\|\s*`([^`]+)`\s*\|'
    r'\s*([\d.]+)\u00b0 \(want (\d+)\)\s*\|\s*([\d.]+)%\s*\|\s*([\d.]+)%\s*\|'
    r'\s*([\d.]+)%\s*\|\s*(\d+)\s*\|')


def read_md(path):
    """The rows of a previously published page, back as rows. The table is this tool's own output
    and every measured column it prints is one this tool wrote, so the page round-trips - which is
    what lets ONE element be re-solved without re-shooting, or disturbing, the six that are settled.
    `lenMs`/`px` are not on the page and are not carried; nothing downstream of here reads them."""
    out, fid = [], None
    for line in open(path, encoding='utf-8'):
        h = MD_HEAD.match(line)
        if h:
            fid = h.group(1)
            continue
        m = MD_ROW.match(line)
        if m and fid:
            miss = [x.strip() for x in (m.group(2) or '').split(',') if x.strip()]
            out.append(dict(sheet=fid, element=m.group(1), token=m.group(3),
                            hue=float(m.group(4)), want=int(m.group(5)), sat=float(m.group(6)),
                            lum=float(m.group(7)), flat=float(m.group(8)), ms=int(m.group(9)),
                            ok=not miss, misses=miss, lenMs=None, px=None, carried=True))
    if not out:
        sys.exit('%s: no table rows to carry' % path)
    return out


def write_md(path, rows, a, names, ceil):
    bad = [r for r in rows if not r['ok']]
    L = ['# The white-sheet tints \u2014 the token that actually lands, per sheet \u00d7 element', '',
         '*Measured %s by `tools/vfx_calibrate.py`. Do not hand-edit \u2014 re-run the tool.*' % a.date, '']
    L += ["D ruled the 12 near-white sheets are kept and re-hued dark per element. The `k` token makes",
          "that possible, but **the hue that lands is not the hue authored** \u2014 every sheet is its own mix",
          "of white core and coloured halo, so do not write `h134` and hope for green. **Copy the token from",
          "the row below**, verbatim, into every layer that uses that sheet at that element.", '']
    low = [r for r in rows if br_of(r['token']) < 0.5]
    L += ['> **Re-solved %s, after the filter order was fixed.** The first solve of this table put *none*' % a.date,
          '> of the 84 pairs over the saturation leg. That was this tool finding an engine defect rather than a',
          '> limit of the art: `sheetFilter` emitted `brightness` **last**, a browser clamps to 8 bits between',
          '> filter primitives, and `sepia(1)` on a white pixel returns rgb(255,255,239) \u2014 two channels already',
          '> pinned \u2014 so every pass after it worked on a pixel whose chroma was gone. `brightness` is now emitted',
          '> **first** on the neutral/sepia path, which moves the pixel off the ceiling before `sepia` runs. The',
          '> tokens below are all re-measured against that chain; any older copy of this page is void.', '']
    L += ['> **Re-solved again %s, after the `br` floor came down 0.5 \u2192 %g.** The reorder bought the' % (a.date, BR_MIN),
          '> saturation leg and lost the luminance one: that solve hit the full target on 32 of 84 pairs and',
          '> all 52 misses were `lum \u2264 %g%%`, every one of them sitting on the old floor with nowhere left to' % LUM_MAX,
          '> go. The floor is one number in two places - `RANGE` in `tools/fx_lint.py` and in the client\'s',
          '> `VFX_BANK` parser - and lowering it closed all 52. **%d of the %d tokens below now carry a `br`'
          % (len(low), len(rows)),
          '> under 0.5**, so this page is void against any client older than that change: an older parser',
          '> rejects those rows outright rather than rendering them wrong.', '']
    cap = [n for n in SAT_BAND if any(r['element'] == n for r in rows)]
    if cap:
        for n in cap:
            lo, hi = SAT_BAND[n]
            L += ['> **`%s` re-solved %s, and only `%s`: the saturation leg was a floor with no'
                  % (n, a.date, n),
                  '> ceiling, and the solver duly spent everything it had on chroma.** That is right for an',
                  '> element that IS a colour and wrong for one that is not. `%s` had come out a vivid gold -'
                  % n,
                  '> 79-87% saturation on 11 of the 12 sheets, the loudest tile on its own contact sheet, and',
                  '> louder in chroma than the untinted white it was replacing. Three things make that wrong and',
                  '> they compound: `%s` is the **default** element and carries **217 of the 419 moves**, so a' % n,
                  '> vivid gold there is a uniform gold wash over half the game; its own hex `#d8cfc0` is a light',
                  '> **neutral**; and `vxHitBone` measures **3.8%** saturation over real creature art, so the layer',
                  '> would have flashed gold while the sprite tinted near-grey. Layer and flash agreeing is the',
                  '> whole reason the element hue table and `VXHITH` share their numbers. The target now carries a',
                  '> per-element **band** (`SAT_BAND` in the tool, a table and not a branch, because a later',
                  '> element may want one): `%s` is solved to **%g%% \u2264 sat \u2264 %g%%** with `lum \u2264 %g%%` unchanged.'
                  % (n, lo, hi, LUM_MAX),
                  '> **The other six elements were not re-solved and their tokens below are the published ones,',
                  '> carried verbatim** - re-shot for the contact sheets, never re-measured.', '']
    ex = next((r for r in rows if r['sheet'] == 'FX-038' and r['element'] == 'green'), rows[0])
    L += ['## How to read a row', '',
          '`%s` + `%s` \u2192 write `%s`, i.e. the whole layer is' % (ex['sheet'], ex['element'], ex['token']),
          '`%s@t s1.0 %s d120`. The measured columns are what that token puts on the screen.'
          % (ex['sheet'], ex['token']), '']
    L += ['## The measurement, so a row can be audited without re-running it', '',
          '- Carrier move **`%s`** (`Targets` = enemy, so the layer lands on the enemy lead), stage **S%d**,'
          % (a.move, a.stage),
          '  seed **%d**, one layer at **s%g**, no delay, no flags \u2014 the same move, seed, tile and scale for'
          % (a.seed, a.scale),
          '  all 12 sheets, so the sheets are comparable to each other.',
          "- Scrubbed **inside the layer's own `lenMs`** (fractions 0.3 / 0.5 / 0.7, brightest kept \u2014 the `ms`",
          '  column is the frame the row was read at).',
          '- The pixels measured are the **difference against a clean plate of the same tile**, same paused',
          '  frame, **restricted to where the plate is dark** (max channel \u2264 %g). That is the layer over the'
          % a.plate_max,
          '  floor and not over the creature: a decile taken over the whole footprint picks the brightest',
          '  pixels in it, and once the layer is darkened those are exactly the ones the sprite shines',
          '  through. The mask is frozen per sheet, so two tokens are compared on the same pixels.',
          '- Reported on the **top luminance decile** of that mask: `hue` a chroma-weighted circular mean,',
          '  `sat` and `lum` HSL, `flat` the share at HSV value \u2265 250 and HSV saturation \u2264 0.08.',
          '- **Target:** hue within \u00b1%g\u00b0 \u00b7 lum \u2264 %g%% \u00b7 flat = 0%% \u00b7 sat \u2265 %g%%,'
          % (HUE_TOL, LUM_MAX, SAT_MIN),
          '  **except where the element carries a band** \u2014 %s. A banded element is solved to sit *inside*'
          % (', '.join('`%s` %g\u2013%g%%' % (n, lo, hi) for n, (lo, hi) in sorted(SAT_BAND.items()))
             or 'none'),
          '  its band, just under the ceiling rather than at zero, because hue is a chroma-weighted mean and a',
          '  layer with no chroma has no measurable hue to put on the element.',
          '- The chain a `k` layer renders through is `brightness(br) sepia(1) saturate(2.4) hue-rotate(h\u221240)',
          '  saturate(sat)`. `br` is the **first** primitive, so every candidate value of it costs a screenshot',
          '  here; `sat` is the last, so that axis is ranked on pixels already shot and only the winner is re-shot.',
          '- Element hues (client `VFXHEX`, and the same numbers as `VXHITH`): %s.'
          % ', '.join('%s %d\u00b0' % (n, h) for n, h in ELEMENTS), '']
    by = {}
    for r in bad:
        for m in r['misses']:
            by.setdefault(m.split()[0], []).append(r)
    systemic = [k for k, v in by.items() if len(v) >= len(rows) * 0.9]
    L += ['## The table', '']
    if systemic:
        L += ['> Every row below meets the legs not named here. Not one meets **%s** \u2014 that is a property of'
              % ', '.join(systemic),
              '> the path rather than of a row, and it is named once here so the per-row marker can stay for',
              '> rows that miss something *else*.', '']
    for fid in [s for s in SHEETS if any(r['sheet'] == s for r in rows)]:
        L += ['### %s \u2014 %s' % (fid, names.get(fid, '')), '',
              '| element | token to write | hue | sat | lum | flat | ms |', '|---|---|---|---|---|---|---|']
        for r in [x for x in rows if x['sheet'] == fid]:
            extra = [m for m in r['misses'] if m.split()[0] not in systemic]
            L.append('| %s%s | `%s` | %.0f\u00b0 (want %d) | %.0f%% | %.0f%% | %.1f%% | %d |'
                     % (r['element'], ' **MISS: %s**' % ', '.join(extra) if extra else '',
                        r['token'], r['hue'], r['want'], r['sat'], r['lum'], r['flat'], r['ms']))
        L.append('')
    els = [n for n, _ in ELEMENTS if any(r['element'] == n for r in rows)]
    L += ['## The saturation reached, every pair', '',
          'The leg that could not be met at all before the reorder. Read down a column to see how an element',
          'fares across the sheets; the floor is %g%% for an unbanded element%s.'
          % (SAT_MIN,
             ''.join(', and %s is capped at %g%%' % (n, hi) for n, (lo, hi) in sorted(SAT_BAND.items()))),
          '', '**Read the banded columns downwards, not across:** a banded element is deliberately the',
          'quietest column on the page and is not competing with the rest.', '',
          '| sheet | ' + ' | '.join(els) + ' |', '|---' * (len(els) + 1) + '|']
    for fid in [s for s in SHEETS if any(r['sheet'] == s for r in rows)]:
        cell = {r['element']: r['sat'] for r in rows if r['sheet'] == fid}
        L.append('| %s | %s |' % (fid, ' | '.join('%.0f%%' % cell.get(e, 0) for e in els)))
    order = sorted(els, key=lambda e: np.mean([r['sat'] for r in rows if r['element'] == e]))
    L += ['',
          'Per element, mean over the sheets solved: %s.'
          % ', '.join('**%s %.0f%%**' % (e, np.mean([r['sat'] for r in rows if r['element'] == e]))
                      for e in order), '']
    L += ['## What the grammar cannot reach', '']
    if not bad:
        L += ['**Nothing.** All %d sheet \u00d7 element pairs hit the target inside `h` 0-359, `br` %g-1.6,'
              % (len(rows), BR_MIN),
              '`sat` 0-1.5 \u2014 hue on the element, lum \u2264 %g%%, no flat white, sat \u2265 %g%%. No desaturated twin is'
              % (LUM_MAX, SAT_MIN),
              'needed for any of the sheets, no new art, and neither engine lever the first solve proposed',
              '(raising `saturate(2.4)`, or lifting the `sat` ceiling) was required: each was worth about 7',
              'points of saturation where the filter reorder was worth about 40.', '']
    else:
        L += ['%d of %d pairs miss. By leg: hue %d \u00b7 lum %d \u00b7 flat %d \u00b7 sat %d.'
              % (len(bad), len(rows), len(by.get('hue', [])), len(by.get('lum', [])),
                 len(by.get('flat', [])), len(by.get('sat', []))), '',
              '| sheet | element | best token | hue | want | sat | lum | flat | misses |',
              '|---|---|---|---|---|---|---|---|---|']
        for r in bad:
            L.append('| %s | %s | `%s` | %.0f\u00b0 | %d\u00b0 | %.0f%% | %.0f%% | %.1f%% | %s |'
                     % (r['sheet'], r['element'], r['token'], r['hue'], r['want'], r['sat'],
                        r['lum'], r['flat'], ', '.join(r['misses'])))
        L += ['', 'These are the best the shipped grammar produces on those pairs; author from them anyway,',
              'and do not raise a lever to chase one leg without shooting it first.', '']
        onfloor = [r for r in bad if abs(br_of(r['token']) - BR_MIN) < 1e-9]
        if len(by.get('lum', [])) >= len(bad) * 0.8:
            L += ['### Why luminance is the leg that still fails, and what is left of it', '',
                  'The reorder traded one leg for the other. Before it, **0 of %d** pairs met `sat`' % len(rows),
                  'and all met `lum`; after it, **all** meet `sat` and %d miss `lum`.' % len(by.get('lum', [])),
                  '',
                  "`sepia(1)` is not a dimming matrix \u2014 its red row sums to 1.351, so it has *gain*. Darkening",
                  'before it is therefore partly undone by it, and `saturate(2.4)` then pushes the red channel',
                  'back against 255 on the sheets with the brightest cores.', '',
                  "**The `br` floor was the first lever and it has been pulled.** The grammar's floor went",
                  '0.5 \u2192 %g on 2026-09-17 - `RANGE` in `tools/fx_lint.py` and in the client parser, both -'
                  % BR_MIN,
                  'and this solve searched down to it. %d of the %d remaining misses still sit on the new'
                  % (len(onfloor), len(bad)),
                  'floor, so on those pairs it is the sheet that is bright and not the token that is timid.', '',
                  'The lever that is left is **lowering `saturate(2.4)`** in the `k` branch of `sheetFilter`.',
                  'It is not free: chroma is exactly what the reorder bought and the rows above spend it.',
                  'Shoot it before taking it. A miss of a few points of lightness on a layer that is correctly',
                  'hued, fully coloured and free of flat white is a far smaller defect than the white pop this',
                  'pass set out to remove.', '']
    L += ['## The highest saturation each sheet can reach', '',
          'The most chroma any element got out of each sheet, and the token that got it. Not to be confused',
          'with the per-element **ceiling** above: this is what the art allows, that is what a ruling permits.',
          '', '| sheet | best sat reached | at | floor |', '|---|---|---|---|']
    for fid, (sv, tk) in ceil.items():
        L.append('| %s | **%.0f%%** | `%s` | %g%% |' % (fid, sv, tk, SAT_MIN))
    L += ['',
          '*A model of a renderer is not the renderer.* The first version of this page was written against a',
          'filter table that composed the CSS matrices and clamped once at the end; a browser clamps between',
          'primitives, and that difference was the entire "the `k` path cannot be saturated" finding. Every',
          'number on this page is a screenshot. `python tools/vfx_calibrate.py --filter-check` renders both',
          'orders of the chain side by side if it needs settling again.']
    open(path, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    return path


# ---------------------------------------------------------------- the receipt for the chain itself
def filter_check():
    """THE RECEIPT FOR THE REORDER, on a literal white div, in a real browser.

    Left: the OLD chain (brightness last) - what shipped until 2026-09-17 and what put the whole
    calibration under 20% saturation. Right: the NEW chain (brightness first). Same hue, same
    saturate, same brightness; the only difference is which primitive the browser applies first, and
    it is worth about 40 points of chroma because sepia(1) pins a white pixel at 255 in two channels
    and nothing after that can give the chroma back."""
    from playwright.sync_api import sync_playwright
    from PIL import Image
    hs = [0, 90, 100, 120, 200, 216, 330]
    BR = 0.7
    css_old = 'sepia(1) saturate(2.4) hue-rotate(%ddeg) brightness(%g)'
    css_new = 'brightness(%g) sepia(1) saturate(2.4) hue-rotate(%ddeg)'
    html = "<body style='margin:0;background:#000'>"
    for h in hs:
        html += ("<div style='display:flex'>"
                 "<div style='width:40px;height:40px;background:#fff;filter:%s'></div>"
                 "<div style='width:40px;height:40px;background:#fff;filter:%s'></div></div>"
                 % (css_old % (h - 40, BR), css_new % (BR, h - 40)))
    html += "</body>"
    with sync_playwright() as pw:
        br = pw.chromium.launch(args=['--force-color-profile=srgb'])
        pg = br.new_page(viewport={'width': 120, 'height': 40 * len(hs)}, device_scale_factor=1)
        pg.set_content(html)
        a = np.asarray(Image.open(io.BytesIO(pg.screenshot(type='png'))).convert('RGB'))
        br.close()
    print('the `k` chain on a literal white pixel, br %g - OLD order (brightness last) vs NEW '
          '(brightness first)' % BR)
    print('  %-8s %-34s %-34s' % ('token', 'brightness LAST', 'brightness FIRST'))
    for i, h in enumerate(hs):
        o = a[i * 40 + 20, 20]
        n = a[i * 40 + 20, 60]
        so = stats(np.array([o], dtype=np.float64) / 255.0)
        sn = stats(np.array([n], dtype=np.float64) / 255.0)
        print('  k h%-6d %-16s hue %3.0f sat %2.0f%%   %-16s hue %3.0f sat %2.0f%%'
              % (h, tuple(int(x) for x in o), so['hue'], so['sat'],
                 tuple(int(x) for x in n), sn['hue'], sn['sat']))
    # and the matrices, in the new order, against the browser - the model is only ever a cross-check
    w = np.array([[1.0, 1.0, 1.0]])
    agree = all(np.all(np.abs(a[i * 40 + 20, 60] - (k_chain(w, h, BR) * 255).round(0)[0]) <= 1)
                for i, h in enumerate(hs))
    print('  spec matrices, clamped between passes, reproduce the NEW column: %s'
          % ('yes' if agree else 'NO - trust the browser, not the model'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sheets', default=','.join(SHEETS))
    ap.add_argument('--elements', default=','.join(n for n, _ in ELEMENTS))
    ap.add_argument('--move', default='M-THORNBACK-1', help='carrier move; its Targets must be enemy')
    ap.add_argument('--stage', type=int, default=3)
    ap.add_argument('--seed', type=int, default=1234)
    ap.add_argument('--scale', type=float, default=1.4, help='the layer s, so the mask has pixels')
    ap.add_argument('--pad', type=float, default=0.25, help='clip = the target tile, inflated')
    ap.add_argument('--plate-max', type=float, default=0.16, dest='plate_max',
                    help='a pixel is the layer\'s only where the plate under it is this dark')
    ap.add_argument('--hue-step', type=int, default=15, dest='hue_step')
    ap.add_argument('--shots', default=str(ROOT.parent / 'local-only' / 'vfxshots' / 'tints'))
    ap.add_argument('--md', default=str(ROOT / 'codex' / 'VFX_SHEET_TINTS.md'))
    ap.add_argument('--no-md', action='store_true')
    ap.add_argument('--json', default='')
    ap.add_argument('--date', default=time.strftime('%Y-%m-%d'))
    ap.add_argument('--filter-check', action='store_true',
                    help='render the `k` chain on a white pixel, browser beside the spec matrices')
    ap.add_argument('--carry', default='',
                    help='a published VFX_SHEET_TINTS.md: every element NOT in --elements is carried '
                         'from it verbatim - re-shot for the contact sheet, never re-solved')
    ap.add_argument('--from-json', default='', dest='from_json',
                    help='re-write the page from a previous run\'s --json, shooting nothing')
    a = ap.parse_args()
    if a.filter_check:
        return filter_check()

    names = {r['Id']: r['Name'] for r in csv.DictReader(open(ROOT / 'codex' / 'fx_bank.csv',
                                                             encoding='utf-8'))}
    if a.from_json:
        rows = json.load(open(a.from_json, encoding='utf-8'))
        ceil = {}
        for fid in [s for s in SHEETS if any(r['sheet'] == s for r in rows)]:
            top = max((r for r in rows if r['sheet'] == fid), key=lambda r: r['sat'])
            ceil[fid] = (top['sat'], top['token'])
        print('table -> %s' % write_md(a.md, rows, a, names, ceil))
        return

    ids = [s.strip() for s in a.sheets.split(',') if s.strip()]
    want = [x.strip() for x in a.elements.split(',')]
    els = [(n, h) for n, h in ELEMENTS if n in want]
    if not ids or not els:
        sys.exit('nothing to calibrate')

    # the settled elements, carried off the published page rather than re-solved
    carry = {}
    if a.carry:
        for r in read_md(a.carry):
            if r['element'] not in want:
                carry.setdefault(r['sheet'], {})[r['element']] = r
        print('carrying %d rows from %s (elements %s)'
              % (sum(len(v) for v in carry.values()), a.carry,
                 ','.join(sorted({r for v in carry.values() for r in v}))))

    from playwright.sync_api import sync_playwright
    t0 = time.time()
    port = VS.free_port(8520)
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1',
                            '--directory', str(ROOT)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.8)
    os.makedirs(a.shots, exist_ok=True)
    rows, made, ceil = [], [], {}
    try:
        with sync_playwright() as pw:
            br, pg = VS.open_page(pw, port)
            pg.evaluate(VS.SEED_JS, a.seed)
            pg.wait_for_timeout(900)
            rig = Rig(pg, a.move, a.stage, a.scale, a.pad)
            for fid in ids:
                rs, art = solve_sheet(rig, fid, els, a.plate_max, a.hue_step,
                                      carry=carry.get(fid))
                rows += rs
                top = max(rs, key=lambda r: r['sat'])
                ceil[fid] = (top['sat'], top['token'])
                made.append(contact(art, os.path.join(a.shots, 'tint_%s.png' % fid.replace('-', '')),
                                    '%s %s   move %s  S%d  seed %d  s%g' %
                                    (fid, names.get(fid, ''), a.move, a.stage, a.seed, a.scale)))
            casts = rig.casts
            br.close()
    finally:
        srv.terminate()

    ok = [r for r in rows if r['ok']]
    print('')
    print('%d/%d sheet x element pairs hit the target; %d miss' % (len(ok), len(rows), len(rows) - len(ok)))
    leg = {}
    for r in rows:
        for m in r['misses']:
            leg[m.split()[0]] = leg.get(m.split()[0], 0) + 1
    if leg:
        print('  misses by leg: %s' % ', '.join('%s %d' % kv for kv in sorted(leg.items())))
    if a.json:
        json.dump(rows, open(a.json, 'w', encoding='utf-8'), indent=1)
    if not a.no_md:
        print('table -> %s' % write_md(a.md, rows, a, names, ceil))
    for m in made:
        print(m)
    print('%d casts, %.1fs' % (casts, time.time() - t0))


if __name__ == '__main__':
    main()
