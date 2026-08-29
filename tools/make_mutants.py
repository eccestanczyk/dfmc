"""Mutant generator — technique C+B: hue-cluster remap with neutral preservation.
Deterministic per-creature angles seeded from creature ID. Luminance untouched.
Output: WebP q95 with alpha, codex/images/mutants/{ID}.webp
"""
from PIL import Image
import numpy as np, csv, os, sys, hashlib

def to_hsv(rgb):
    mx = rgb.max(-1); mn = rgb.min(-1); diff = mx - mn + 1e-9
    r,g,b = rgb[...,0], rgb[...,1], rgb[...,2]
    h = np.zeros_like(mx)
    h = np.where(mx==r, (g-b)/diff % 6, h)
    h = np.where(mx==g, (b-r)/diff + 2, h)
    h = np.where(mx==b, (r-g)/diff + 4, h)
    return h/6.0, np.where(mx==0, 0, diff/(mx+1e-9)), mx

def to_rgb(h,s,v):
    i = (h*6).astype(int) % 6
    f = h*6 - np.floor(h*6)
    p = v*(1-s); q = v*(1-f*s); t = v*(1-(1-f)*s)
    out = np.zeros(h.shape + (3,), np.float32)
    for k,(rr,gg,bb) in enumerate([(v,t,p),(q,v,p),(p,v,t),(p,q,v),(t,p,v),(v,p,q)]):
        m = i==k
        out[...,0][m]=rr[m]; out[...,1][m]=gg[m]; out[...,2][m]=bb[m]
    return out

def mutate(path, cid, out_path, seed_key=None):
    img = Image.open(path).convert('RGBA')
    arr = np.array(img)
    rgb = arr[...,:3].astype(np.float32)/255.0
    alpha = arr[...,3:]
    h,s,v = to_hsv(rgb)
    vis = alpha[...,0] > 40

    # SEEDED ON THE LINE'S STAGE-1 ID, NOT ON EACH CREATURE (D 2026-08-29: 'Charybdis stage 3 is a
    # different mutant colour from its stage 1, which is pink - redo the s3 so that s3 is also the
    # same pink as s1'). The seed was the creature's OWN id, and a line's three stages have three
    # different ids, so the three got three different hue rotations BY CONSTRUCTION - STORMFATHER
    # ran +140, +162 and +215 degrees. Measured across the roster: ALL 100 lines disagreed, 52
    # degrees apart on average and 96 at worst. A mutation is a trait of the creature, not of the
    # stage it happens to be standing at.
    # THE KEY IS STAGE 1's ID AND NOT THE LINE NAME, deliberately: D named S1's pink as the one to
    # keep, and hashing the line name instead would have moved STORMFATHER to +124 and repainted the
    # very stage he wants left alone. Keyed this way, every stage-1 mutant is BYTE-IDENTICAL to what
    # already shipped and only the later stages move onto it. Still deterministic, still reproducible
    # from the CSV alone.
    seed = int(hashlib.sha1((seed_key or cid).encode()).hexdigest()[:8], 16)
    rot_main = (120 + seed % 101) / 360.0          # 120..220 deg
    rot_sec  = -(40 + (seed >> 8) % 71) / 360.0    # -40..-110 deg

    sat_thr = 0.22
    m = (s > sat_thr) & vis
    if m.sum() < 0.15 * max(vis.sum(), 1):
        sat_thr = 0.12
        m = (s > sat_thr) & vis
    if m.sum() < 0.10 * max(vis.sum(), 1):
        # near-monochrome creature: gentle global shift fallback (still deterministic)
        h2 = (h + rot_main) % 1.0
        s2 = np.clip(s*1.15 + 0.05, 0, 1)
        h3, s3 = np.where(vis, h2, h), np.where(vis, s2, s)
    else:
        med = np.median(h[m])
        band = np.abs(((h - med + 0.5) % 1.0) - 0.5) < 0.08
        c1 = m & band; c2 = m & ~band
        h3 = h.copy(); s3 = s.copy()
        h3[c1] = (h[c1] + rot_main) % 1.0
        h3[c2] = (h[c2] + rot_sec) % 1.0
        s3[m] = np.clip(s[m]*1.2, 0, 1)

    out = np.dstack([np.clip(to_rgb(h3,s3,v)*255,0,255).astype(np.uint8), alpha])
    Image.fromarray(out,'RGBA').save(out_path, 'WEBP', quality=95, method=4, exact=True)

if __name__ == '__main__':
    # `python3 tools/make_mutants.py [outdir] [bosses]`
    # Default source is codex/creatures.csv. Pass `bosses` to derive the Void Apex
    # uber-boss portraits from codex/bosses.csv instead (same remap, same determinism,
    # keyed on Boss_ID so BOSS-010.png -> mutants/BOSS-010.webp).
    outdir = sys.argv[1] if len(sys.argv) > 1 else 'codex/images/mutants'
    mode = sys.argv[2] if len(sys.argv) > 2 else 'creatures'
    os.makedirs(outdir, exist_ok=True)
    if mode == 'bosses':
        rows = [{'ID': r['Boss_ID'], 'Image_Path': r['Image_Path'], 'Seed_Key': r['Boss_ID']}
                for r in csv.DictReader(open('codex/bosses.csv'))]
    else:
        rows = list(csv.DictReader(open('codex/creatures.csv')))
        # every stage of a line adopts the palette of its stage 1
        base = {}
        for r in rows:
            if str(r.get('Stage','')).strip() == '1' and r.get('Line_ID'):
                base[r['Line_ID']] = r['ID']
        for r in rows:
            r['Seed_Key'] = base.get(r.get('Line_ID',''), r['ID'])
    done = skipped = 0
    for r in rows:
        p = r.get('Image_Path','').strip()
        if not p or not os.path.exists(p):
            skipped += 1; continue
        op = os.path.join(outdir, r['ID'] + '.webp')
        if os.path.exists(op): done += 1; continue
        mutate(p, r['ID'], op, seed_key=(r.get('Seed_Key') or r['ID']))   # bosses carry none: they key on their own id, unchanged
        done += 1
    print('mutants generated:', done, '| skipped:', skipped)
