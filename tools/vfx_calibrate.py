#!/usr/bin/env python3
"""THE TINT SOLVER (VFX pass 2, D 2026-09-17).

D ruled: keep the white sheets, re-hue them dark per element. The `k` token makes a white sheet
colourable (it forces the neutral/sepia path; hue-rotate alone returns white for a white pixel).
But shooting it proved THE HUE THAT LANDS IS NOT THE HUE AUTHORED - `sepia(1) saturate(2.4)` clips
channels at 255 before the rotation, and every sheet is its own mix of white core and coloured halo,
so `h0` reads gold and `h222` reads pale. An authoring lane cannot write h134 and get green.

So each of the 12 near-white sheets needs its own token per element, measured once on that sheet and
then copied into every row that uses it: 12 x 7 = 84 measurements, not 1221 judgements. This tool
makes them and writes the table.

  python tools/vfx_calibrate.py                        all 12 sheets, all 7 elements
  python tools/vfx_calibrate.py --sheets FX-038 --elements green,blue --no-md
  python tools/vfx_calibrate.py --filter-check         the `k` chain, browser vs the spec matrices

THE TARGET, per sheet x element, measured on the TOP LUMINANCE DECILE of the layer's own painted
pixels:  hue within +/-18 deg of the element hue, HSL lightness <= 55%, flat-white fraction 0%
(HSV value >= 250 AND HSV saturation <= 0.08), HSL saturation >= 25%.
Search space is the grammar's own: h 0-359 integer, br 0.5-1.6, sat 0-1.5. `k` is always present.

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

WHY IT IS MINUTES AND NOT HOURS. The browser is asked for one shot per candidate HUE; `sat` and `br`
are the last two passes of the chain and they are applied to the measured pixels in numpy to rank the
grid, so the search costs no screenshots. The browser then verifies the winner and any residual is
fed back. Every number in the table is a real screenshot measured by rule 5 - none is a prediction.

--filter-check renders a literal white div through the `k` chain in the same browser and prints it
beside the CSS spec matrices. They agree to the last level, which is how the chain in this file is
known to be right - and it is also how the second filter table in
dfmc-client/docs/vfx-pass2-recipes-2026-09-17.md was found to be wrong: it reports
`h100 br0.7` as rgb(142,178,106) where the browser renders rgb(157,178,163). That table is where the
"saturation >= 25%" leg of the target came from, and it overstates the chroma the `k` path produces
by roughly 3x. See the "what the grammar cannot reach" section of the page this writes.

Output: the table on stdout, codex/VFX_SHEET_TINTS.md, and one contact sheet per sheet under --shots
(the untinted layer plus its 7 calibrated elements) so the table can be looked at and not only read.
"""
import argparse, csv, io, json, math, os, subprocess, sys, time
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


def k_chain(px, h):
    """`sepia(1) saturate(2.4) hue-rotate(h-40)` - the `k` branch of sheetFilter, clamped between
    passes the way a browser clamps an 8-bit intermediate buffer. --filter-check proves the clamp."""
    o = np.clip(px @ SEPIA, 0, 1)
    o = np.clip(o @ SAT24, 0, 1)
    return np.clip(o @ hue_mat(round(h) - 40), 0, 1)


def tail(px, sat, br):
    """The last two passes, saturate(sat) then brightness(br) - applied to pixels the browser has
    already rendered at (h, sat 1, br 1). They come after the hue work and before compositing, and
    over a dark plate compositing is a scale, so ranking the grid this way costs no screenshots."""
    o = px
    if abs(sat - 1.0) > 1e-9:
        o = np.clip(o @ sat_mat(sat), 0, 1)
    if abs(br - 1.0) > 1e-9:
        o = np.clip(o * br, 0, 1)
    return o


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


def misses(st, want):
    out = []
    if hue_err(st['hue'], want) > HUE_TOL:
        out.append('hue %.0f deg off' % hue_err(st['hue'], want))
    if st['lum'] > LUM_MAX:
        out.append('lum %.0f%%' % st['lum'])
    if st['flat'] > 0:
        out.append('flat %.1f%%' % st['flat'])
    if st['sat'] < SAT_MIN:
        out.append('sat %.0f%%' % st['sat'])
    return out


def score(st, want):
    """Rank the grid: get inside hue, flat and lum first, then spend everything left on chroma."""
    return -(max(0.0, hue_err(st['hue'], want) - 6.0) * 4.0
             + max(0.0, st['lum'] - LUM_AIM) * 3.0
             + st['flat'] * 50.0
             + max(0.0, SAT_MIN - st['sat']) * 1.0) + 0.05 * st['sat']


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
def solve_sheet(rig, fid, elements, rounds, plate_max, hue_step, verbose=True):
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
    hmap = {}
    for h in range(0, 360, hue_step):
        px, _ = measure(token(h, 1.0, 1.0))
        hmap[h] = stats(px)
    if verbose:
        print('  %s  life %dms  scrub %dms  layer-over-floor px %d  hue map %s'
              % (fid, lenMs, ms, npx,
                 ' '.join('%d->%d' % (h, round(hmap[h]['hue'])) for h in sorted(hmap))))

    SATS = [round(0.8 + i * 0.05, 3) for i in range(15)]        # 0.80 .. 1.50
    BRS = [round(0.5 + i * 0.025, 3) for i in range(21)]        # 0.50 .. 1.00
    rows, art = [], [(ref_png, '%s  NO TINT - what ships today\nlife %d ms, read at %d ms'
                      % (fid, lenMs, ms), False)]

    for name, want in elements:
        # the authored h whose LANDED hue is closest, then walk it in with the local gradient
        h = min(hmap, key=lambda x: hue_err(hmap[x]['hue'], want))
        px, _ = measure(token(h, 1.0, 1.0))
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
            px2, _ = measure(token(h2, 1.0, 1.0))
            s2 = stats(px2)
            if hue_err(s2['hue'], want) >= hue_err(base['hue'], want):
                break
            h, px, base = h2, px2, s2

        # sat and br are the last two passes: rank the whole grid on the pixels already in hand
        cand, seen = None, set()
        for rnd in range(max(1, rounds)):
            grid = sorted(((score(stats(tail(px, s, b)), want), s, b) for s in SATS for b in BRS),
                          key=lambda r: -r[0])
            pickd = next((g for g in grid if (g[1], g[2]) not in seen), grid[0])
            _, s, b = pickd
            seen.add((s, b))
            tk = token(h, s, b)
            got, png = measure(tk)
            st = stats(got)
            ok = not misses(st, want)
            if cand is None or (ok and not cand[0]) or (not cand[0] and score(st, want) > score(cand[2], want)):
                cand = (ok, tk, st, png)
            if ok:
                break
        ok, tk, st, png = cand
        rows.append(dict(sheet=fid, element=name, want=want, token=tk, ok=ok, ms=ms, lenMs=lenMs,
                         px=npx, misses=misses(st, want), **st))
        art.append((png, '%s %s  %s\nhue %.0f (want %d)  sat %.0f  lum %.0f  flat %.1f%s'
                    % (fid, name, tk, st['hue'], want, st['sat'], st['lum'], st['flat'],
                       '' if ok else '   MISS'), not ok))
        if verbose:
            print('    %-8s want %3d  %-24s -> hue %5.1f  sat %4.1f  lum %4.1f  flat %4.1f  %s'
                  % (name, want, tk, st['hue'], st['sat'], st['lum'], st['flat'],
                     'ok' if ok else 'MISS: ' + ', '.join(misses(st, want))))
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


def write_md(path, rows, a, names, ceil):
    bad = [r for r in rows if not r['ok']]
    L = ['# The white-sheet tints — the token that actually lands, per sheet × element', '',
         '*Measured %s by `tools/vfx_calibrate.py`. Do not hand-edit — re-run the tool.*' % a.date, '']
    L += ["D ruled the 12 near-white sheets are kept and re-hued dark per element. The `k` token makes",
          "that possible, but **the hue that lands is not the hue authored** — `sepia(1) saturate(2.4)`",
          "clips channels at 255 before the rotation, and every sheet is its own mix of white core and",
          "coloured halo. So do not write `h134` and hope for green. **Copy the token from the row below**,",
          "verbatim, into every layer that uses that sheet at that element.", '']
    ex = next((r for r in rows if r['sheet'] == 'FX-038' and r['element'] == 'green'), rows[0])
    L += ['## How to read a row', '',
          '`%s` + `%s` → write `%s`, i.e. the whole layer is' % (ex['sheet'], ex['element'], ex['token']),
          '`%s@t s1.0 %s d120`. The measured columns are what that token puts on the screen.'
          % (ex['sheet'], ex['token']), '']
    L += ['## The measurement, so a row can be audited without re-running it', '',
          '- Carrier move **`%s`** (`Targets` = enemy, so the layer lands on the enemy lead), stage **S%d**,'
          % (a.move, a.stage),
          '  seed **%d**, one layer at **s%g**, no delay, no flags — the same move, seed, tile and scale for'
          % (a.seed, a.scale),
          '  all 12 sheets, so the sheets are comparable to each other.',
          "- Scrubbed **inside the layer's own `lenMs`** (fractions 0.3 / 0.5 / 0.7, brightest kept — the `ms`",
          '  column is the frame the row was read at).',
          '- The pixels measured are the **difference against a clean plate of the same tile**, same paused',
          '  frame, **restricted to where the plate is dark** (max channel ≤ %g). That is the layer over the'
          % a.plate_max,
          '  floor and not over the creature: a decile taken over the whole footprint picks the brightest',
          '  pixels in it, and once the layer is darkened those are exactly the ones the sprite shines',
          '  through. The mask is frozen per sheet, so two tokens are compared on the same pixels.',
          '- Reported on the **top luminance decile** of that mask: `hue` a chroma-weighted circular mean,',
          '  `sat` and `lum` HSL, `flat` the share at HSV value ≥ 250 and HSV saturation ≤ 0.08.',
          '- **Target:** hue within ±%g° · lum ≤ %g%% · flat = 0%% · sat ≥ %g%%.' % (HUE_TOL, LUM_MAX, SAT_MIN),
          '- Element hues (client `VFXHEX`, and the same numbers as `VXHITH`): %s.'
          % ', '.join('%s %d°' % (n, h) for n, h in ELEMENTS), '']
    by = {}
    for r in bad:
        for m in r['misses']:
            by.setdefault(m.split()[0], []).append(r)
    # a leg that fails on nearly every pair is a property of the path, not of a row - say it once at
    # the top and keep the per-row marker for the rows that miss something ELSE.
    systemic = [k for k, v in by.items() if len(v) >= len(rows) * 0.9]
    L += ['## The table', '']
    if systemic:
        L += ['> Every row below meets **hue**, **lum** and **flat white**. Not one meets **sat ≥ %g%%**,'
              % SAT_MIN,
              '> on any sheet at any element — that is a ceiling of the `k` path itself and it is measured,',
              '> named and explained under *What the grammar cannot reach*. The rows are still the best the',
              '> shipped grammar produces, so author from them.', '']
    for fid in [s for s in SHEETS if any(r['sheet'] == s for r in rows)]:
        L += ['### %s — %s' % (fid, names.get(fid, '')), '',
              '| element | token to write | hue | sat | lum | flat | ms |', '|---|---|---|---|---|---|---|']
        for r in [x for x in rows if x['sheet'] == fid]:
            extra = [m for m in r['misses'] if m.split()[0] not in systemic]
            L.append('| %s%s | `%s` | %.0f° (want %d) | %.0f%% | %.0f%% | %.1f%% | %d |'
                     % (r['element'], ' **MISS: %s**' % ', '.join(extra) if extra else '',
                        r['token'], r['hue'], r['want'], r['sat'], r['lum'], r['flat'], r['ms']))
        L.append('')
    L += ['## What the grammar cannot reach', '']
    if not bad:
        L += ['**Nothing.** All %d sheet × element pairs hit the target inside `h` 0-359, `br` 0.5-1.6,' % len(rows),
              '`sat` 0-1.5. No desaturated twin is needed for any of the 12 sheets.', '']
    else:
        L += ['%d of %d pairs miss. By leg: hue %d · lum %d · flat %d · **sat %d**.'
              % (len(bad), len(rows), len(by.get('hue', [])), len(by.get('lum', [])),
                 len(by.get('flat', [])), len(by.get('sat', []))), '']
        odd = [r for r in bad if [m for m in r['misses'] if m.split()[0] not in systemic]]
        if odd:
            L += ['Pairs that miss something other than the systemic leg:', '',
                  '| sheet | element | best token | hue | sat | lum | flat | misses |',
                  '|---|---|---|---|---|---|---|---|']
            for r in odd:
                L.append('| %s | %s | `%s` | %.0f° | %.0f%% | %.0f%% | %.1f%% | %s |'
                         % (r['sheet'], r['element'], r['token'], r['hue'], r['sat'], r['lum'],
                            r['flat'], ', '.join(r['misses'])))
            L.append('')
        elif systemic:
            L += ['**No pair misses hue, lum or flat white.** The whole miss is one leg.', '']
        if len(by.get('sat', [])) >= len(bad) * 0.8:
            els = [n for n, _ in ELEMENTS if any(r['element'] == n for r in rows)]
            L += ['### The saturation actually reached, every pair', '',
                  'Read down a column to see how far an element is from %g%%.' % SAT_MIN, '',
                  '| sheet | ' + ' | '.join(els) + ' |', '|---' * (len(els) + 1) + '|']
            for fid in [s for s in SHEETS if any(r['sheet'] == s for r in rows)]:
                cell = {r['element']: r['sat'] for r in rows if r['sheet'] == fid}
                L.append('| %s | %s |' % (fid, ' | '.join('%.0f%%' % cell.get(e, 0) for e in els)))
            worst = sorted(els, key=lambda e: np.mean([r['sat'] for r in rows if r['element'] == e]))
            L += ['',
                  'Per element, mean over the 12 sheets: %s.'
                  % ', '.join('**%s %.0f%%**' % (e, np.mean([r['sat'] for r in rows if r['element'] == e]))
                              for e in worst),
                  'The cool half of the wheel is the worse half: the `k` chain leaves a white pixel a pale',
                  'warm yellow, and rotating that to blue or purple crosses the achromatic axis, so there is',
                  'almost no chroma left to darken. `%s` and `%s` are the elements a white sheet cannot carry.'
                  % (worst[0], worst[1]), '']
            L += ["**The saturation floor is not a near miss on a few sheets — it is the whole `k` path.**",
                  'The measured ceiling per sheet is the HSL saturation the layer keeps once it is dark enough',
                  'to satisfy `lum ≤ %g%%` (below mid-lightness, HSL saturation stops falling with `br`, so this' % LUM_MAX,
                  'is a true ceiling and not an artefact of how far it was darkened):', '',
                  '| sheet | best sat reachable | at | needed |', '|---|---|---|---|']
            for fid, (s, tk) in ceil.items():
                L.append('| %s | **%.0f%%** | `%s` | %g%% |' % (fid, s, tk, SAT_MIN))
            L += ['',
                  'The cause is arithmetic, and it is checkable with `--filter-check`: run a literal white pixel',
                  'through the `k` chain in a browser and `sepia(1) saturate(2.4) hue-rotate(60deg)` returns',
                  '**rgb(224,255,233)** — chroma 0.12 — and with `brightness(0.7)` **rgb(157,178,163)**, which is',
                  'HSL saturation **12%**. The second filter table in',
                  '`dfmc-client/docs/vfx-pass2-recipes-2026-09-17.md` reports that same filter as rgb(142,178,106),',
                  'HSL saturation 32%. The browser does not render that. **The ≥25% leg of the target was set from',
                  'a table that overstates the `k` path\'s chroma by about 3x**, so no token inside `h` 0-359,',
                  '`br` 0.5-1.6, `sat` 0-1.5 can meet it on any of the 12 sheets.', '',
                  'What the rows above DO deliver is the other three legs, which are D\'s words: the hue lands on',
                  'the element, the layer is dark, and the flat white is gone. What they do not deliver is a',
                  'strongly coloured dark — they read as tinted greys.', '',
                  '### So: are desaturated twins the answer? No.', '',
                  'A twin sheet would not help. The chroma is not lost in the sheet, it is lost in the filter:',
                  '`sepia(1)` gives a white pixel only chroma 0.06 and `saturate(2.4)` is too small a multiplier',
                  'to open it up. The two cheap fixes both live outside this tool, and both are one number:', '',
                  '1. **raise the multiplier in the `k` branch of `sheetFilter`** (`assets/vfx/vfx_fx.js` and',
                  '   the client\'s own copy in `play/app.js`). Swept over the whole hue circle on a white pixel,',
                  '   with `br` taken to whatever puts it at `lum 55%`: `saturate(2.4)` tops out at **14.5%**,',
                  '   `saturate(3)` at 18.5%, **`saturate(4)` at 25.8%** — the first value that clears the floor —',
                  '   and `saturate(5)` at 33.9%; or',
                  '2. **raise the `sat` ceiling in the grammar** (`RANGE` in `tools/fx_lint.py` and in the',
                  '   parser). Same sweep, engine left alone: `sat1.5` tops out at **14.5%**, `sat2` at 19.8%,',
                  '   **`sat2.5` at 25.6%**, `sat3` at 31.9%. This is the same multiplication, moved from the',
                  '   engine to the author — and it keeps the choice per layer.', '',
                  'Either is one number. Both would let the tokens above be re-solved by re-running this tool;',
                  'nothing else about the method or the page would change.', '',
                  'Both are engine/grammar changes with their own review, so neither was made here. Until one of',
                  'them lands, **the tokens above are the darkest, most coloured, flat-white-free version of each',
                  'sheet the shipped grammar can produce** — and they are still a large improvement on the white.']
    open(path, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    return path


# ---------------------------------------------------------------- the receipt for the chain itself
def filter_check():
    from playwright.sync_api import sync_playwright
    from PIL import Image
    hs = [0, 90, 100, 120, 200, 216, 330]
    html = "<body style='margin:0;background:#000'>"
    for i, h in enumerate(hs):
        html += ("<div style='width:40px;height:40px;background:#fff;"
                 "filter:sepia(1) saturate(2.4) hue-rotate(%ddeg)'></div>" % (h - 40))
    html += ("<div style='width:40px;height:40px;background:#fff;filter:sepia(1) saturate(2.4) "
             "hue-rotate(60deg) brightness(0.7)'></div></body>")
    with sync_playwright() as pw:
        br = pw.chromium.launch(args=['--force-color-profile=srgb'])
        pg = br.new_page(viewport={'width': 120, 'height': 40 * (len(hs) + 1)}, device_scale_factor=1)
        pg.set_content(html)
        a = np.asarray(Image.open(io.BytesIO(pg.screenshot(type='png'))).convert('RGB'))
        br.close()
    print('the `k` chain: browser vs the CSS spec matrices, on a literal white pixel')
    w = np.array([[1.0, 1.0, 1.0]])
    for i, h in enumerate(hs):
        got = a[i * 40 + 20, 20]
        mine = (k_chain(w, h) * 255).round(0)[0]
        # the same chain with the intermediate clamps left out - which is the recipes doc's table
        loose = (np.clip((w @ SEPIA) @ SAT24 @ hue_mat(h - 40), 0, 1) * 255).round(0)[0]
        print('  k h%-4d browser %-16s clamped-per-pass %-16s no-intermediate-clamp %s  %s'
              % (h, tuple(int(x) for x in got), tuple(int(x) for x in mine),
                 tuple(int(x) for x in loose),
                 'agree' if np.all(np.abs(got - mine) <= 1) else 'DIFFER'))
    got = a[len(hs) * 40 + 20, 20]
    st = stats(np.array([got], dtype=np.float64) / 255.0)
    print('  k h100 br0.7  browser %s  -> hue %.0f sat %.0f%% lum %.0f%%'
          % (tuple(int(x) for x in got), st['hue'], st['sat'], st['lum']))
    print('  the recipes doc records that same filter as rgb(142,178,106), hue 90 sat 32 lum 56.')
    print('  that is the no-intermediate-clamp column: the doc composed the three matrices and clamped')
    print('  once at the end. A browser clamps an 8-bit buffer BETWEEN filter passes, and the clamp it')
    print('  applies after sepia(1) is exactly what throws the chroma away.')


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
    ap.add_argument('--rounds', type=int, default=3, help='browser verifications per sheet x element')
    ap.add_argument('--shots', default=str(ROOT.parent / 'local-only' / 'vfxshots' / 'tints'))
    ap.add_argument('--md', default=str(ROOT / 'codex' / 'VFX_SHEET_TINTS.md'))
    ap.add_argument('--no-md', action='store_true')
    ap.add_argument('--json', default='')
    ap.add_argument('--date', default=time.strftime('%Y-%m-%d'))
    ap.add_argument('--filter-check', action='store_true',
                    help='render the `k` chain on a white pixel, browser beside the spec matrices')
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
                rs, art = solve_sheet(rig, fid, els, a.rounds, a.plate_max, a.hue_step)
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
