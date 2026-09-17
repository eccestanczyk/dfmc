#!/usr/bin/env python3
"""THE SEEING TOOL (VFX pass 2, D 2026-09-17).

Pass 1 shipped 1221 compositions behind three gates that only ever proved a layer MOUNTED.
This one looks at the pixels: it drives the codex review page (vfx.html), which draws exactly
what the client draws, casts a composition, freezes every animation, scrubs it to N points
across its own length, screenshots the 1920x1080 stage at each point, and tiles the shots into
contact sheets a session can READ as images.

  python tools/vfx_shoot.py --census                       receipts for every row, no pixels
  python tools/vfx_shoot.py --ids M-THORNBACK-2,ULT-MAGE-3 --stage 3
  python tools/vfx_shoot.py --ids-file sample.txt --stage 3 --out ../local-only/vfxshots/b1

WHY SCRUBBING AND NOT SLEEPING. A screenshot costs 50-150ms, so sleeping to a timestamp lands
somewhere near it, never on it, and two runs of the same composition are never the same frame.
After the cast every animation is paused and its currentTime is SET, so a frame is exact and a
re-shoot after a retune is comparable to the shot before it.

SAME SEED, SAME STAGE. --seed pins the teams and the floor plate (rerollTeams and paintBackdrop
both draw from Math.random), so a re-shoot after a retune is comparable to the shot before it.
Two shoots of one sheet at the same seed differ on 0.018% of pixels and by no more than 8 levels
on any of them - the units' `floaty` idle is an infinite animation paused at whatever phase the
cast caught it in. Nothing a judgement rests on moves.

WHAT IT CANNOT SEE. !shake and the target's hit-jolt are created inside setTimeout, and
setTimeout is neutered during the cast so the layer-teardown timer cannot delete the layers
mid-scrub. Those two read as still frames. Everything drawn by VFX_BANK, and the !flash tint on
the target sprite (authored with a CSS delay, not a timer), is captured.

ART. codex/images/** and floors/** are outside this repo's sparse checkout; those requests are
routed to the published site so the stage carries the real creature, class and floor art.
"""
import argparse, io, json, os, re, socket, subprocess, sys, time
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
REMOTE = 'https://eccestanczyk.github.io/dfmc/'
STAGE_W, STAGE_H = 1920, 1080


def free_port(start=8410):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(('127.0.0.1', p)) != 0:
                return p
    sys.exit('no free port')


# ---------------------------------------------------------------- the page
OVERRIDE_JS = r"""
([id, stage, txt]) => {
  /* Author a composition WITHOUT touching codex/move_vfx.csv. The review page reads VFX[Move_ID],
     so a page-level override previews a candidate exactly as the client would draw it - which is
     how an authoring lane should look at a row before it writes one. Nothing is persisted. */
  if (!VFX[id]) return false;
  VFX[id]['FX_S' + stage] = txt;
  return true;
}
"""

CAST_JS = r"""
([id, stage, frames]) => {
  const mv = MOVE_BY_ID[id];
  if (!mv) return {err: 'no such move: ' + id};
  stopLoop(); playAll(false); clearFxNow();
  /* deterministic target: pick() takes index 0 of the legal list, every run */
  const _rnd = Math.random; Math.random = () => 0;
  /* the teardown timer would delete the layers while we scrub, and !shake / the hit-jolt
     would fire at wall-clock times we are not at. Neuter setTimeout for the cast only. */
  const _st = window.setTimeout; window.setTimeout = () => 0;
  let rc;
  try { rc = castNow(mv, stage, 'ally'); }
  finally { window.setTimeout = _st; Math.random = _rnd; }
  if (!rc) return {err: 'castNow returned null'};
  document.getAnimations().forEach(a => { try { a.pause(); } catch (e) {} });
  const len = Math.max(rc.lenMs || 0, 400);
  rc.times = frames.map(f => Math.round(len * f));
  rc.name = mv.Name || mv.Move_ID;
  const b = bankFor(id, stage);
  rc.anchors = b ? b.parsed.layers.map(l => l.id + '@' + l.anchor) : [];
  return rc;
}
"""

SCRUB_JS = r"""
(t) => { document.getAnimations().forEach(a => { try { a.currentTime = t; } catch (e) {} }); }
"""

CENSUS_JS = r"""
(stages) => {
  const out = [];
  const _rnd = Math.random; Math.random = () => 0;
  const _st = window.setTimeout; window.setTimeout = () => 0;
  try {
    for (const row of ALLROWS) {
      const isUlt = /^ULT-/.test(row.Move_ID);
      for (const st of (isUlt ? [1] : stages)) {
        clearFxNow();
        const rc = castNow(row, st, 'ally');
        if (!rc) continue;
        const b = bankFor(row.Move_ID, st);
        const layers = b ? b.parsed.layers.map(l => ({id: l.id, a: l.anchor,
                                                      s: l.mods.s || 1, d: l.mods.d || 0,
                                                      v: l.mods.v || 1, n: l.mods.n || 1,
                                                      h: (l.mods.h == null ? null : l.mods.h),
                                                      ms: Math.round(BANK.layerMs(l, FXBANK, false)),
                                                      grp: (FXBANK[l.id] || {}).Group || ''})) : [];
        out.push({id: row.Move_ID, stage: rc.stage, bank: rc.bank, arch: rc.arch,
                  wantUser: rc.wantUser, wantTgt: rc.wantTgt,
                  onUser: rc.onUser, onTgt: rc.onTgt, back: rc.back,
                  lenMs: rc.lenMs, flags: rc.flags, layers: layers,
                  targets: (VFX[row.Move_ID] || {}).Targets || '',
                  anchor: (VFX[row.Move_ID] || {}).Target_Anchor || ''});
      }
    }
  } finally { window.setTimeout = _st; Math.random = _rnd; clearFxNow(); }
  return out;
}
"""


def open_page(pw, port):
    br = pw.chromium.launch(args=['--mute-audio', '--force-color-profile=srgb'])
    pg = br.new_page(viewport={'width': 2100, 'height': 1320}, device_scale_factor=1)

    cache = {}

    def to_remote(route):
        """Serve art from the published site. NOT route.continue_(url=...) - playwright refuses a
        cross-origin rewrite - so the bytes are fetched and fulfilled, memoised per path because a
        route intercept runs in front of the browser cache and every cast re-requests the same art."""
        path = route.request.url.split('/', 3)[3]
        if path not in cache:
            try:
                r = pg.request.get(REMOTE + path)
                cache[path] = (r.body(), r.headers.get('content-type', 'image/webp')) if r.ok else None
            except Exception:
                cache[path] = None
        hit = cache[path]
        if hit is None:
            return route.abort()
        route.fulfill(status=200, body=hit[0], content_type=hit[1])
    pg.route(re.compile(r'https?://127\.0\.0\.1:\d+/(codex/images|codex/thumbs|floors)/'), to_remote)
    pg.route(re.compile(r'dfmc-vfx\.duiliovarella\.workers\.dev'), lambda r: r.abort())
    pg.goto('http://127.0.0.1:%d/vfx.html' % port, wait_until='domcontentloaded')
    pg.wait_for_function('typeof ALLROWS !== "undefined" && ALLROWS.length > 400 '
                         '&& Object.keys(FXBANK).length >= 40', timeout=90000)
    pg.wait_for_timeout(1500)          # the sheets preload
    return br, pg


SEED_JS = r"""
(seed) => {
  /* THE SAME TEAMS AND THE SAME FLOOR, EVERY RUN. rerollTeams() and paintBackdrop() draw from
     Math.random, so two shoots of the same ids came back with different creatures on a different
     plate - and a difference you cannot attribute is worse than no shot at all. Math.random is
     replaced by a seeded LCG for the life of the page, so a re-shoot after a retune is comparable
     to the shot before it tile for tile. (CAST_JS pins it to 0 for the cast, then restores this.) */
  let s = seed >>> 0;
  Math.random = () => { s = (Math.imul(s, 1664525) + 1013904223) >>> 0; return s / 4294967296; };
  rerollTeams();
}
"""


def stage_box(pg):
    b = pg.locator('#stage').bounding_box()
    if not b:
        sys.exit('#stage has no box')
    return b


# ---------------------------------------------------------------- contact sheets
def sheet(shots, out_png, cols, tile_w, title):
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 15)
        big = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', 17)
    except Exception:
        font = big = ImageFont.load_default()
    tile_h = int(tile_w * STAGE_H / STAGE_W)
    lab = 22
    rows = (len(shots) + cols - 1) // cols
    W, H = cols * tile_w, 30 + rows * (tile_h + lab)
    im = Image.new('RGB', (W, H), (14, 14, 18))
    d = ImageDraw.Draw(im)
    d.text((8, 8), title, font=big, fill=(235, 225, 190))
    for i, (png, label, warn) in enumerate(shots):
        c, r = i % cols, i // cols
        x, y = c * tile_w, 30 + r * (tile_h + lab)
        t = Image.open(io.BytesIO(png)).convert('RGB').resize((tile_w, tile_h), Image.LANCZOS)
        im.paste(t, (x, y))
        d.rectangle([x, y, x + tile_w - 1, y + tile_h - 1], outline=(70, 70, 80))
        d.text((x + 5, y + tile_h + 3), label, font=font,
               fill=(255, 120, 110) if warn else (190, 195, 205))
    im.save(out_png)
    return out_png


def flush(shots, a, ix):
    cols = len(a.frames.split(','))
    title = '%s  stage %d  frames %s  seed %d  (%d moves)' % (a.tag, a.stage, a.frames, a.seed,
                                                                 len(shots) // cols)
    out = os.path.join(a.out, '%s_s%d_%02d.png' % (a.tag, a.stage, ix + 1))
    return sheet(shots, out, cols, a.tile, title)


def summarise(rows):
    from collections import Counter
    bank = [r for r in rows if r['bank']]
    print('compositions: %d  (bank %d / archetype %d)' % (len(rows), len(bank), len(rows) - len(bank)))
    silent = [r for r in bank if r['wantTgt'] and not r['onTgt']]
    nouser = [r for r in bank if r['wantUser'] and not r['onUser']]
    notgt = [r for r in bank if not r['wantTgt']]
    print('  target layers asked for but NOT mounted : %d' % len(silent))
    print('  caster layers asked for but NOT mounted : %d' % len(nouser))
    print('  compositions with NO target layer at all: %d' % len(notgt))
    cu = Counter()
    ct = Counter()
    for r in bank:
        for l in r['layers']:
            (cu if l['a'] in ('u', 'ug') else ct)[l['id']] += 1
    print('  top caster-anchored sheets:', cu.most_common(6))
    print('  top target-anchored sheets:', ct.most_common(6))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--ids-file', default='')
    ap.add_argument('--stage', type=int, default=3)
    ap.add_argument('--frames', default='0.15,0.4,0.65,0.9')
    ap.add_argument('--per-sheet', type=int, default=6, help='moves per contact sheet')
    ap.add_argument('--tile', type=int, default=480)
    ap.add_argument('--out', default=str(ROOT.parent / 'local-only' / 'vfxshots'))
    ap.add_argument('--tag', default='sheet')
    ap.add_argument('--census', action='store_true')
    ap.add_argument('--census-stages', default='1,2,3')
    ap.add_argument('--seed', type=int, default=1234, help='teams + floor plate; same seed = same stage')
    ap.add_argument('--comp', action='append', default=[], metavar='ID=TEXT',
                    help='preview a candidate composition for ID at --stage without touching the CSV; '
                         'repeatable. The id is shot in the order given.')
    a = ap.parse_args()

    ids = [s.strip() for s in a.ids.split(',') if s.strip()]
    if a.ids_file:
        ids += [l.strip() for l in open(a.ids_file, encoding='utf-8')
                if l.strip() and not l.startswith('#')]
    if not ids and not a.census and not a.comp:
        sys.exit('nothing to do: pass --ids/--ids-file, --comp or --census')

    from playwright.sync_api import sync_playwright
    port = free_port()
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1',
                            '--directory', str(ROOT)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.8)
    os.makedirs(a.out, exist_ok=True)
    made = []
    try:
        with sync_playwright() as pw:
            br, pg = open_page(pw, port)
            pg.evaluate(SEED_JS, a.seed)
            pg.wait_for_timeout(900)      # the seeded team's art
            if a.census:
                stages = [int(s) for s in a.census_stages.split(',')]
                rows = pg.evaluate(CENSUS_JS, stages)
                p = os.path.join(a.out, 'census.json')
                json.dump(rows, open(p, 'w', encoding='utf-8'))
                print('census rows: %d -> %s' % (len(rows), p))
                summarise(rows)
                br.close()
                return

            for spec in a.comp:
                mid, _, txt = spec.partition('=')
                mid = mid.strip()
                if not pg.evaluate(OVERRIDE_JS, [mid, a.stage, txt]):
                    sys.exit('--comp: no such move id: ' + mid)
                if mid not in ids:
                    ids.append(mid)
                print('override %s S%d = %s' % (mid, a.stage, txt))

            fr = [float(x) for x in a.frames.split(',')]
            box = stage_box(pg)
            clip = {'x': box['x'], 'y': box['y'], 'width': box['width'], 'height': box['height']}
            shots, n = [], 0
            for mid in ids:
                rc = pg.evaluate(CAST_JS, [mid, a.stage, fr])
                if rc.get('err'):
                    print('SKIP %s: %s' % (mid, rc['err']))
                    continue
                warn = (rc['wantTgt'] and not rc['onTgt']) or (rc['wantUser'] and not rc['wantTgt'])
                for t in rc['times']:
                    pg.evaluate(SCRUB_JS, t)
                    png = pg.screenshot(clip=clip, type='png')
                    lbl = '%s S%d %4dms  u%d/t%d %s' % (mid, rc['stage'], t, rc['onUser'],
                                                        rc['onTgt'], ' '.join(rc['flags']))
                    shots.append((png, lbl, warn))
                pg.evaluate('() => clearFxNow()')
                n += 1
                if n % a.per_sheet == 0:
                    made.append(flush(shots, a, len(made)))
                    shots = []
            if shots:
                made.append(flush(shots, a, len(made)))
            br.close()
        for m in made:
            print(m)
    finally:
        srv.terminate()


if __name__ == '__main__':
    main()
