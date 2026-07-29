#!/usr/bin/env python3
"""Display-size derivatives for every raster class the game ships.

Nothing here is destructive: originals stay exactly where they are and the derivatives land
under a parallel `opt/` path. The client points at the derivative; the original remains the
master for any future re-export.

Rule of thumb baked into TARGETS below: a derivative is authored at 2x the largest box the
asset is ever painted into, capped at the original's own size. 2x covers retina without
paying for pixels nobody can see. See ASSET_PIPELINE.md for the full policy.

    python3 tools/make_derivatives.py            # write anything missing or stale
    python3 tools/make_derivatives.py --report   # show sizes, write nothing
"""
import os, sys, glob
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (source glob, output dir, max edge, quality, note)
TARGETS = [
    ('assets/ui/move_icons/*.png',        'assets/ui/opt/move_icons',   64,  88, 'status chips paint at 33x33'),
    ('assets/ui/medals/*.png',            'assets/ui/opt/medals',      128,  88, 'medal badges'),
    ('assets/ui/icons/*.png',             'assets/ui/opt/icons',       160,  88, 'menu tile icons'),
    ('codex/images/classes/*.png',        'codex/images/opt/classes', 1024,  92, 'avatar paints 480px, roster 341px; @2x that is ~960/683 device px - keep master res'),
    ('codex/images/eggs/*.png',           'codex/images/opt/eggs',     256,  88, 'egg tiles paint at 250x250'),
    ('codex/images/items/*.png',          'codex/images/opt/items',    128,  88, 'inventory tiles paint at 33-50px'),
    ('_parking/game-mirror/Inventory/*.png', 'assets/ui/opt/frames',   160,  90, 'tile frames paint behind a 50px icon'),
    ('codex/images/mutants/*.webp',       'codex/images/opt/mutants',  512,  90, 'match codex/images/med, same 110-128px box'),
]

def run(report=False):
    grand_src = grand_out = 0
    for pat, outdir, edge, q, note in TARGETS:
        srcs = sorted(f for f in glob.glob(os.path.join(ROOT, pat)) if os.path.isfile(f))
        if not srcs:
            print('  %-30s (no sources)' % pat); continue
        od = os.path.join(ROOT, outdir)
        if not report: os.makedirs(od, exist_ok=True)
        sb = ob = 0; wrote = 0
        for f in srcs:
            sb += os.path.getsize(f)
            out = os.path.join(od, os.path.splitext(os.path.basename(f))[0] + '.webp')
            if report or (os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(f)):
                if os.path.exists(out): ob += os.path.getsize(out)
                continue
            im = Image.open(f).convert('RGBA')
            im.thumbnail((edge, edge), Image.LANCZOS)
            im.save(out, 'WEBP', quality=q, method=6)
            ob += os.path.getsize(out); wrote += 1
        grand_src += sb; grand_out += ob
        print('  %-30s %4d files  %7.1f MB -> %6.2f MB  (%s)%s'
              % (outdir.split('/')[-1], len(srcs), sb/1048576, ob/1048576, note,
                 '' if report else '  [%d written]' % wrote))
    print('  %-30s %19.1f MB -> %6.2f MB' % ('TOTAL', grand_src/1048576, grand_out/1048576))

if __name__ == '__main__':
    run('--report' in sys.argv)
