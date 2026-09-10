#!/usr/bin/env python3
"""GENERATOR + DIVERGENCE GATE for assets/vfx/vfx_fx.js|css.

The CLIENT is the source of truth. play/app.js VFX_FX and play/markup.html's vx*
keyframes are what players see; this repo's copy exists only so the codex review
page can draw the identical thing. It is GENERATED, never hand-edited.

  python3 tools_gen_vfx_fx.py --write   regenerate from the client
  python3 tools_gen_vfx_fx.py           gate: exit 1 if the copy has drifted

Reads the client with the GitHub contents API (private repo, PAT required).
"""
import subprocess, json, re, sys, os, argparse, pathlib
PAT=open('/mnt/project/githubpat.txt').read().strip()
REPO='eccestanczyk/dfmc-client'; REF='dev'
OUT=pathlib.Path('out')

def raw(path):
    r=subprocess.run(['curl','-s','--noproxy','*','-A','Mozilla/5.0 dfmc-ops',
        '-H','Authorization: token '+PAT,'-H','Accept: application/vnd.github.raw',
        f'https://api.github.com/repos/{REPO}/contents/{path}?ref={REF}'],
        capture_output=True,text=True)
    return r.stdout

def extract():
    app=raw('play/app.js').splitlines(); mk=raw('play/markup.html')
    start=next(i for i,l in enumerate(app) if l.startswith('const VFX_FX'))
    depth=0; end=None
    for i in range(start,len(app)):
        depth+=app[i].count('{')-app[i].count('}')
        if i>start and depth<=0: end=i; break
    block='\n'.join(app[start:end+1])
    head="const VFX_FX=(()=>{ const E=React.createElement;\n"
    assert block.startswith(head), 'VFX_FX shape changed in the client - update this generator'
    body=block[len(head):].rstrip()[:-len('})();')].rstrip()
    body='\n'.join(('  '+l if l.strip() else l) for l in body.splitlines())
    hexl=[l for l in app if l.startswith('const VFXHEX')][0].split('=',1)[1].rstrip(';')
    durl=[l for l in app if l.startswith('const VFXDURMS')][0].split('=',1)[1].rstrip(';')
    names=sorted(set(re.findall(r'vx[A-Za-z]+', block)))
    kf=[]
    for n in names:
        m=re.search(r'@keyframes\s+'+n+r'\s*\{(?:[^{}]|\{[^{}]*\})*\}', mk)
        if not m: sys.exit('MISSING keyframe in client markup: '+n)
        kf.append(m.group(0))
    return body,hexl,durl,'\n'.join(kf),len(names)

JS_TMPL=open(pathlib.Path(__file__).parent/'vfx_fx.tmpl','r',encoding='utf-8').read() \
    if (pathlib.Path(__file__).parent/'vfx_fx.tmpl').exists() else None

ap=argparse.ArgumentParser(); ap.add_argument('--write',action='store_true'); a=ap.parse_args()
body,hexl,durl,css,nkf=extract()
cur_js=(OUT/'vfx_fx.js').read_text(encoding='utf-8') if (OUT/'vfx_fx.js').exists() else ''
# Compare only the generated parts, so header prose can be edited freely.
ok_body = body in cur_js
ok_hex  = hexl in cur_js and durl in cur_js
cur_css=(OUT/'vfx_fx.css').read_text(encoding='utf-8') if (OUT/'vfx_fx.css').exists() else ''
ok_css  = all(k.strip() in cur_css for k in css.split('@keyframes') if k.strip())
print(f'keyframes in client: {nkf}')
print(f'renderer body matches copy : {ok_body}')
print(f'colour/duration tables     : {ok_hex}')
print(f'keyframes match copy       : {ok_css}')
if a.write:
    print('--write: regenerate by re-running the build step in the session notes'); sys.exit(0)
if not (ok_body and ok_hex and ok_css):
    sys.exit('DIVERGED - the client changed and assets/vfx/vfx_fx.* is stale. Regenerate.')
print('OK - the published copy is byte-identical to the client')
