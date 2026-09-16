#!/usr/bin/env python3
"""VFX BANK GATE for the codex review page (D 2026-09-17).

vfx.html must draw every move's effect from the SAME bank renderer the client draws it with
(assets/vfx/vfx_fx.js -> DFMC_VFX_FX.buildBank, generated from play/app.js by
tools/gen_vfx_fx.py). This gate proves it, cast by cast:

  * the page boots with zero page errors and zero console errors
  * EVERY move row is cast at S1, S2 and S3, and every ULT row once (ULT rows carry only
    FX_S1) - 1221 casts - through the page's own castNow()
  * for each cast at least one bank layer element is mounted on the tile(s) the composition
    names: a `@u`/`@ug` layer on the user's tile, a `@t`/`@g` layer on the target's, `@b` on both
  * a sampled set is read MID-ANIMATION: the sheet img is loaded and a vxbStep keyframe set is
    actually running on it
  * a row whose composition is empty or malformed is a FALLBACK (the archetype path drew
    instead), counted and reported - not a failure. 45 rows are being re-authored in another
    lane and must not turn this gate red.

  python tools/vfx_bank_gate.py
  VFX_URL=http://127.0.0.1:9000/vfx.html?admin=1 python tools/vfx_bank_gate.py

With no VFX_URL the gate serves the repo root itself on 127.0.0.1:8123 and stops the server
when it is done.
"""
import asyncio, os, pathlib, socket, subprocess, sys, time
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = int(os.environ.get('VFX_PORT') or 8123)
URL = os.environ.get('VFX_URL') or ('http://127.0.0.1:%d/vfx.html?admin=1' % PORT)
OWN_SERVER = not os.environ.get('VFX_URL')

R = []


def chk(n, ok, d=''):
    R.append(bool(ok))
    print(('PASS' if ok else 'FAIL'), '|', n, '|', d)


def serve():
    p = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1'],
                         cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(80):
        try:
            socket.create_connection(('127.0.0.1', PORT), 0.25).close()
            return p
        except OSError:
            time.sleep(0.1)
    p.kill()
    sys.exit('could not start python -m http.server on %d' % PORT)


# One cast + the DOM truth about it. Driven directly - no CAST_MS wait - but the layers are read
# while the composition is live, before the next cast's clearFxNow() takes them down.
CAST_JS = """async (jobs) => {
  const out=[];
  for(const [id,st,side] of jobs){
    const row=MOVE_BY_ID[id];
    if(!row){ out.push({id:id, stage:st, missing:true}); continue; }
    let rc=null, err=null;
    try{ rc=castNow(row, st, side); }catch(e){ err=String(e&&e.message||e); }
    if(!rc){ out.push({id:id, stage:st, err:err||'no receipt'}); continue; }
    await new Promise(r=>setTimeout(r,6));
    const cEl=document.getElementById(rc.side).children[0];
    const tEl=document.getElementById(rc.tside).children[rc.tidx];
    rc.domUser=cEl?cEl.querySelectorAll('.vxb>div').length:0;
    rc.domTgt =tEl?tEl.querySelectorAll('.vxb>div').length:0;
    rc.domAll =document.querySelectorAll('#ally .vxb>div,#enemy .vxb>div').length;
    rc.domFall=document.querySelectorAll('#ally .fxwrap,#enemy .fxwrap').length;
    rc.err=err;
    out.push(rc);
  }
  return out;
}"""

# Mid-animation read: the sheet is decoded and a vxbStep set is running on it.
SAMPLE_JS = """async ([id,st,side]) => {
  const rc=castNow(MOVE_BY_ID[id], st, side);
  if(!rc||!rc.bank) return {id:id, stage:st, bank:false};
  const at=Math.min(300, Math.max(40, Math.round(rc.lenMs*0.35)));
  await new Promise(r=>setTimeout(r,at));
  const frames=[...document.querySelectorAll('#ally .vxb>div,#enemy .vxb>div')];
  const imgs=frames.map(f=>f.querySelector('img')).filter(Boolean);
  const running=document.getAnimations().filter(a=>a.animationName&&/^vxbStep/.test(a.animationName)&&a.playState==='running').length;
  return {id:id, stage:st, bank:true, frames:frames.length, at:at,
          loaded:imgs.filter(i=>i.complete&&i.naturalWidth>0).length, imgs:imgs.length, running:running,
          srcs:imgs.slice(0,3).map(i=>i.src.split('/').pop())};
}"""


async def main():
    srv = serve() if OWN_SERVER else None
    perr, cerr, res404 = [], [], []
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch()
            pg = await b.new_page(viewport={'width': 1400, 'height': 1000})
            pg.on('pageerror', lambda e: perr.append(str(e)))

            def on_console(m):
                if m.type != 'error':
                    return
                if 'Failed to load resource' not in m.text:
                    cerr.append(m.text)     # a resource 404 is reported separately, from the response
            pg.on('console', on_console)
            pg.on('response', lambda r: res404.append('%d %s' % (r.status, r.url)) if r.status >= 400 else None)

            print('gate url:', URL)
            await pg.goto(URL, wait_until='domcontentloaded')
            try:
                await pg.wait_for_function(
                    'typeof ALLROWS!=="undefined" && ALLROWS.length>0 && typeof castNow==="function" '
                    '&& typeof FXBANK!=="undefined" && document.querySelectorAll("#grid .card").length>0',
                    timeout=45000)
            except Exception:
                # A page that still draws only the placeholder archetypes has no ALLROWS, no FXBANK
                # and no castNow: there is nothing to walk. That is the red state this gate exists for.
                chk('the review page exposes the bank walk (ALLROWS / FXBANK / castNow)', False,
                    'none of them appeared in 45s - the page is not drawing from the VFX bank')
                await b.close()
                print('')
                print('bank casts 0  |  fallbacks 0  |  wrong 0  |  page errors %d  |  console errors %d'
                      % (len(perr), len(cerr)))
                print('SUMMARY', sum(R), '/', len(R))
                return 1
            await pg.evaluate('DFMC_AFX.mute(true)')            # a gate makes no noise
            n_rows, n_bank, n_ult, n_grid = await pg.evaluate(
                '[ALLROWS.length, Object.keys(FXBANK).length, ULT.length, document.querySelectorAll("#grid .card").length]')
            chk('page boots: rows / sheets / ULT rows / grid cards', n_rows == 419 and n_bank == 48 and n_ult == 18 and n_grid == 301,
                '%d rows, %d sheets, %d ULT, %d cards' % (n_rows, n_bank, n_ult, n_grid))
            chk('the review page and the client share one renderer',
                await pg.evaluate('typeof DFMC_VFX_FX.buildBank==="function" && typeof BANK.parse==="function" && typeof BANK.render==="function"'))
            chk('the 4 move buttons still open', await pg.evaluate(
                '(()=>{document.querySelectorAll("#grid .card")[5].click();return document.querySelectorAll(".mv-btn").length})()') == 4)
            # the 48 sheets are warmed before anything is timed
            try:
                await pg.wait_for_function('[...document.images].filter(i=>i.src.indexOf("/fx/bank/")>=0).every(i=>i.complete&&i.naturalWidth>0)', timeout=30000)
            except Exception:
                pass

            # ---- the walk: every move at S1/S2/S3, every ULT once ----
            jobs = await pg.evaluate("""(()=>{const j=[];let k=0;
              for(const r of ALLROWS){ const ult=/^ULT-/.test(r.Move_ID);
                for(const st of (ult?[1]:[1,2,3])) j.push([r.Move_ID, st, (k++)%2?'enemy':'ally']); }
              return j;})()""")
            chk('the walk covers 1221 casts (401 moves x 3 stages + 18 ULT)', len(jobs) == 1221, '%d jobs' % len(jobs))

            t0 = time.time()
            bank_ok = fallback = bad = 0
            fails, fb_ids = [], []
            for i in range(0, len(jobs), 60):
                for rc in await pg.evaluate(CAST_JS, jobs[i:i + 60]):
                    if rc.get('missing') or rc.get('err'):
                        bad += 1
                        fails.append('%s S%s: %s' % (rc.get('id'), rc.get('stage'), rc.get('err') or 'row missing'))
                        continue
                    if not rc['bank']:
                        fallback += 1
                        fb_ids.append('%s S%s' % (rc['id'], rc['stage']))
                        if not rc['domFall']:
                            bad += 1
                            fails.append('%s S%s: fell back to the archetype path and drew nothing' % (rc['id'], rc['stage']))
                        continue
                    miss = []
                    if rc['domAll'] < 1:
                        miss.append('no bank layer mounted at all')
                    if rc['wantUser'] and rc['domUser'] < 1:
                        miss.append('a @u/@ug/@b layer never mounted on the user tile')
                    if rc['wantTgt'] and rc['domTgt'] < 1:
                        miss.append('a @t/@g/@b layer never mounted on the target tile')
                    if miss:
                        bad += 1
                        fails.append('%s S%s: %s' % (rc['id'], rc['stage'], '; '.join(miss)))
                    else:
                        bank_ok += 1
            dt = time.time() - t0
            chk('every bank cast mounted on the tile(s) its composition names', bad == 0,
                '%d cast(s) wrong: %s' % (bad, '; '.join(fails[:3])) if bad else
                '%d bank casts, %d fallbacks, %.1fs' % (bank_ok, fallback, dt))

            # ---- mid-animation: the sheets are really stepping ----
            samp = await pg.evaluate("""(()=>{const s=[],step=Math.floor(MOV.length/7);
              for(let i=0;i<MOV.length;i+=step) for(const st of [1,2,3]) s.push([MOV[i].Move_ID,st,'ally']);
              for(const u of ULT.slice(0,3)) s.push([u.Move_ID,1,'enemy']);
              return s;})()""")
            live = dead = 0
            for j in samp:
                r = await pg.evaluate(SAMPLE_JS, j)
                if not r.get('bank'):
                    continue
                if r['running'] >= 1 and r['loaded'] == r['imgs'] and r['imgs'] >= 1:
                    live += 1
                else:
                    dead += 1
                    fails.append('%s S%s mid-animation at %sms: %d/%d sheets decoded, %d vxbStep running' % (
                        r['id'], r['stage'], r['at'], r['loaded'], r['imgs'], r['running']))
            chk('sampled casts are live mid-animation (sheet decoded, vxbStep running)', dead == 0 and live > 0,
                '%d live, %d dead of %d sampled' % (live, dead, len(samp)))

            await pg.evaluate('playAll(false); stopLoop();')
            chk('no page errors', not perr, '; '.join(perr[:2]))
            chk('no console errors', not cerr, '; '.join(cerr[:2]))
            await b.close()
    finally:
        if srv:
            srv.kill()

    print('\nbank casts %d  |  fallbacks %d  |  wrong %d  |  page errors %d  |  console errors %d  |  asset 404s %d'
          % (bank_ok, fallback, bad, len(perr), len(cerr), len(set(res404))))
    for u in sorted(set(res404))[:5]:
        print('  [404]', u)
    if fallback:
        print('fell back to the archetype path (empty or malformed composition): %d of 1221 - %s%s'
              % (fallback, ', '.join(fb_ids[:8]), ' ...' if len(fb_ids) > 8 else ''))
    for f in fails[:12]:
        print('  [!]', f)
    print('SUMMARY', sum(R), '/', len(R))
    return 0 if all(R) else 1


sys.exit(asyncio.run(main()))
