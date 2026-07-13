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

def mutate(path, cid, out_path):
    img = Image.open(path).convert('RGBA')
    arr = np.array(img)
    rgb = arr[...,:3].astype(np.float32)/255.0
    alpha = arr[...,3:]
    h,s,v = to_hsv(rgb)
    vis = alpha[...,0] > 40

    seed = int(hashlib.sha1(cid.encode()).hexdigest()[:8], 16)
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
    outdir = sys.argv[1] if len(sys.argv) > 1 else 'codex/images/mutants'
    os.makedirs(outdir, exist_ok=True)
    rows = list(csv.DictReader(open('codex/creatures.csv')))
    done = skipped = 0
    for r in rows:
        p = r.get('Image_Path','').strip()
        if not p or not os.path.exists(p):
            skipped += 1; continue
        op = os.path.join(outdir, r['ID'] + '.webp')
        if os.path.exists(op): done += 1; continue
        mutate(p, r['ID'], op)
        done += 1
    print('mutants generated:', done, '| skipped:', skipped)
