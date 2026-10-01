#!/usr/bin/env python3
"""FX-056 Meteor Fall - the bank sheet Cataclysm's meteors are drawn from (D 2026-10-01, Rulings board row
`plume`: "add meteors falling down, you can take the meteor we made for the meteor trap in Herumon Dungeon and
review it with the new cheap vfx tools we learned from Aether website").

SOURCE. Herumon Dungeon's meteor trap (E:/Herumon-Dungeon/dfmc-dungeon/play/index.html, the `kind === 'meteor'`
theatre, #179/#185): an FX-009 Pyre Orb II sphere under one FX-013 Slender Flame tail, both multiplied by
#b0231c, falling STRAIGHT DOWN with an accelerating ease (u^2) so the tail sits above the head, then an FX-007
blast. Same owner (D); the three sheets are the same CC0 Unity Labs Paris art this bank already carries, so the
licence is the bank's own.

THE CHEAP WAY (#1052, dfmc-client tools/make_portal_art.py). The dungeon moves its sprites per frame in script;
the Tower's VFX_BANK only steps a sheet (`vxbStep<F>x<C>`, transform only, no filter or blur keyframes). So the
fall is PRE-BAKED: every frame of this sheet already holds the rocks where they are at that instant, and the
client plays it like any other bank sheet - no renderer change, no new sheet type.

SHAPE. 24 frames, 6 columns (a shape VFX_BANK.SHAPES already carries), frame 192 x 256 (portrait: the rocks
come in from above the tile). Three meteors, staggered: the centre one lands on frame 5 (208 ms at v1, so a
layer at d0 lands with the 200 ms impact beat), the left on 9, the right on 12. Each lands in the fire half of an
FX-006 Ember Blast (frames 0-8, before it turns to smoke) and leaves a short FX-012 flame that dies out by the last frame.

  python tools/make_meteor_sheet.py      -> assets/fx/bank/fx-056.webp (+ prints Hue / Sat for fx_bank.csv)
"""
import colorsys, os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, 'assets', 'fx', 'bank')
OUT = os.path.join(BANK, 'fx-056.webp')
F, C, FW, FH = 24, 6, 192, 256
TINT = np.array([0xb0, 0x23, 0x1c], np.float32) / 255.0   # the dungeon tail's dark red

def frames(fid, cols=6, fw=128, fh=128, n=24):
    im = Image.open(os.path.join(BANK, fid + '.webp')).convert('RGBA')
    return [im.crop(((i % cols) * fw, (i // cols) * fh, (i % cols + 1) * fw, (i // cols + 1) * fh)) for i in range(n)]

ROCK, TAIL, BURST, FLAME = frames('fx-009'), frames('fx-013', fw=64), frames('fx-006'), frames('fx-012', fw=64)

def hot(im, red=0.55, gain=1.0, alpha=1.0):
    """The dungeon's tint, made for a transparent sheet: mix the art toward its dark-red multiply (the dungeon's
    `tint`) and lift the alpha for its two additive passes."""
    a = np.asarray(im, np.float32) / 255.0
    rgb = a[..., :3] * ((1 - red) + red * TINT * 2.2) * gain
    out = np.dstack([np.clip(rgb, 0, 1), np.clip(a[..., 3] * alpha, 0, 1)])
    return Image.fromarray((out * 255).astype(np.uint8), 'RGBA')

def paste(dst, im, cx, cy, w, h, op=1.0):
    im = im.resize((max(1, int(w)), max(1, int(h))), Image.LANCZOS)
    if op < 1:
        a = np.asarray(im).copy(); a[..., 3] = (a[..., 3] * op).astype(np.uint8); im = Image.fromarray(a, 'RGBA')
    layer = Image.new('RGBA', dst.size)
    layer.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
    return Image.alpha_composite(dst, layer)

# (centre x, landing y, landing frame, rock size): the centre rock first and biggest
METEORS = [(96, 196, 5, 62), (50, 184, 9, 48), (146, 202, 12, 52)]
FALL = 5           # frames from above the frame to the ground
TOP = -70

def frame(k):
    fr = Image.new('RGBA', (FW, FH))
    for x, ly, land, size in METEORS:
        t0 = land - FALL
        if t0 <= k < land:
            u = (k - t0 + 1) / FALL
            y = TOP + (ly - TOP) * u * u
            # ONE tail, drawn first so it sits behind the head, its base inside the head's top edge (dungeon #185)
            fr = paste(fr, hot(TAIL[(k * 3) % 24], red=0.45, alpha=1.6), x, y - size * 1.0, size * 1.0, size * 2.0)
            r = hot(ROCK[(k * 2) % 24], red=0.35, alpha=1.5)
            fr = paste(fr, r, x, y, size, size)
            fr = paste(fr, r, x, y, size * 0.8, size * 0.8)        # the second additive pass, a touch tighter
        elif k >= land:
            j = k - land
            if j < 9:      # the burst: FX-006's fire frames 0-8 one to one, never its smoke half
                bw = size * 2.2
                fr = paste(fr, BURST[min(8, j)], x, ly - bw * 0.25, bw, bw * 0.9, 1.0 if j < 6 else (9 - j) / 4)
            if 2 <= j:     # the fire it leaves, dying with the sheet
                left = (F - 1) - k
                op = max(0.0, min(1.0, left / 6.0)) * (1.0 if j < 12 else 0.8)
                if op > 0:
                    fr = paste(fr, FLAME[(k * 2 + x) % 24], x, ly - size * 0.6, size * 0.9, size * 1.6, op)
    return fr

def main():
    sheet = Image.new('RGBA', (C * FW, (F + C - 1) // C * FH))
    for k in range(F):
        sheet.paste(frame(k), ((k % C) * FW, (k // C) * FH))
    sheet.save(OUT, 'WEBP', quality=88, method=6)
    a = np.asarray(sheet, np.float32) / 255.0
    m = a[..., 3] > 0.3
    rgb = a[..., :3][m]
    hs = np.array([colorsys.rgb_to_hsv(*p)[:2] for p in rgb[:: max(1, len(rgb) // 20000)]])
    ang = np.angle(np.mean(np.exp(1j * hs[:, 0] * 2 * np.pi))) / (2 * np.pi) * 360 % 360
    print('wrote %s %dx%d  Hue %d  Sat %.2f' % (OUT, sheet.width, sheet.height, round(ang), hs[:, 1].mean()))

if __name__ == '__main__':
    main()
