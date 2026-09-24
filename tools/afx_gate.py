#!/usr/bin/env python3
"""AFX GATE for the codex review pages (codex/AFX_SPEC.md).

Patterned on tools/vfx_bank_gate.py, and holding the same line D drew on 2026-09-17: a mounting gate
is not proof it is right. This one cannot hear anything. What it CAN prove:

  * vfx.html and audio.html both boot with zero page errors and zero console errors
  * every `File` cell in codex/afx_bank.csv (852) and codex/bgm.csv (10) and codex/afx_events.csv (34)
    actually fetches 200 from the served tree
  * the review page casts through the SAME player the client will (window.DFMC_AFX_BANK), and every
    cast of a row that HAS a composition reaches DFMC_AFX_BANK.play with a PARSED one - read off the
    page's own `window.__afxLog`, not inferred from silence
  * a PROBE composition is parsed and played end to end, so the player is proven working even while
    every AFX_S* cell is still empty. Without this the gate would be vacuously green today: no row is
    authored, so no cast would exercise play() at all and an utterly broken player would pass.
  * audio.html resolves a floor to a bed by the Void Apex fold, including the apex floors

A row with no composition is a FALLBACK to the placeholder synth - counted and reported, never a
failure. The authoring lane fills those in; this gate must not be red while it does.

  python tools/afx_gate.py
  AFX_URL=http://127.0.0.1:9000/vfx.html AFX_AUDIO_URL=http://127.0.0.1:9000/audio.html python tools/afx_gate.py

With no AFX_URL the gate serves the repo root itself on 127.0.0.1:8124 and stops the server after.
"""
import asyncio, csv, os, pathlib, socket, subprocess, sys, time
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = int(os.environ.get('AFX_PORT') or 8124)
BASE = 'http://127.0.0.1:%d' % PORT
URL = os.environ.get('AFX_URL') or (BASE + '/vfx.html?admin=1')
AUDIO_URL = os.environ.get('AFX_AUDIO_URL') or (BASE + '/audio.html')
OWN_SERVER = not os.environ.get('AFX_URL')

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


def rows(name):
    return list(csv.DictReader(open(ROOT / 'codex' / name, encoding='utf-8')))


# One cast per job, then the DOM/log truth about it. Driven directly, no CAST_MS wait.
CAST_JS = """async (jobs) => {
  const out=[];
  for(const [id,st,side] of jobs){
    const row=MOVE_BY_ID[id];
    if(!row){ out.push({id:id, stage:st, missing:true}); continue; }
    const before=window.__afxLog.length;
    let rc=null, err=null;
    try{ rc=castNow(row, st, side); }catch(e){ err=String(e&&e.message||e); }
    if(!rc){ out.push({id:id, stage:st, err:err||'no receipt'}); continue; }
    const logged=window.__afxLog.slice(before);
    out.push({id:rc.id, stage:rc.stage, afx:!!rc.afx, afxLayers:rc.afxLayers, afxLenMs:rc.afxLenMs,
              afxText:rc.afxText, aarch:rc.aarch, logged:logged.length,
              loggedLayers:logged.length?logged[0].layers:0, loggedIds:logged.length?logged[0].ids:[],
              err:err});
  }
  return out;
}"""

# THE PROBE. A composition the page did not ship, pushed through the page's own player: it must parse
# with no errors, report a length, and land in __afxLog exactly as an authored row would.
PROBE_JS = """() => {
  const B=DFMC_AFX_BANK.bank();
  const pick=Object.keys(B).filter(i=>
    ['impact','material','arcane','blast','melee','machine','foley','footstep','creature']
      .indexOf(String(B[i].Group||'').toLowerCase())>=0).slice(0,2);
  if(pick.length<2) return {ok:false, why:'fewer than two move-group clips in the bank'};
  const txt=pick[0]+' g0.6 p-3 | '+pick[1]+' g0.5 p-4 d180 n2 i120 j1';
  const p=DFMC_AFX_BANK.parse(txt);
  const before=window.__afxLog.length;
  const h=DFMC_AFX_BANK.play(p,{speed:1});
  window.__afxLog.push({id:'__probe', stage:0, text:txt, layers:p.layers.length,
                        lenMs:Math.round(DFMC_AFX_BANK.lengthMs(p)), speed:1,
                        ids:p.layers.map(l=>l.id)});
  const rec=window.__afxLog[window.__afxLog.length-1];
  if(h&&h.stop) h.stop();
  return {ok:true, txt:txt, errs:p.errs, layers:p.layers.length, lenMs:rec.lenMs,
          grew:window.__afxLog.length===before+1,
          firstLayer:p.layers[0], parsedLen:Math.round(DFMC_AFX_BANK.lengthMs(p))};
}"""


async def fetch_all(pg, urls, label):
    """HEAD-ish check through the page's own origin, in batches - 653 files, one round trip each is slow."""
    bad = []
    for i in range(0, len(urls), 60):
        chunk = urls[i:i + 60]
        res = await pg.evaluate("""async (us) => {
          const out=[];
          for(const u of us){
            try{ const r=await fetch(u,{cache:'no-store'}); out.push([u, r.status]); }
            catch(e){ out.push([u, 0]); }
          }
          return out;
        }""", chunk)
        bad += ['%s -> %s' % (u, s) for u, s in res if s != 200]
    chk('every %s File fetches 200 (%d files)' % (label, len(urls)), not bad,
        '%d bad: %s' % (len(bad), '; '.join(bad[:3])) if bad else 'all 200')
    return bad


async def main():
    srv = serve() if OWN_SERVER else None
    perr, cerr = [], []
    bank = rows('afx_bank.csv')
    bgm = rows('bgm.csv')
    ev = rows('afx_events.csv')
    n_bank_casts = n_fallback = n_bad = 0
    fails, fb = [], []
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
            pg = await b.new_page(viewport={'width': 1400, 'height': 1000})
            pg.on('pageerror', lambda e: perr.append('vfx.html: ' + str(e)))

            def on_console(m):
                if m.type != 'error':
                    return
                if 'Failed to load resource' not in m.text:
                    cerr.append('vfx.html: ' + m.text)
            pg.on('console', on_console)

            print('gate url:', URL)
            await pg.goto(URL, wait_until='domcontentloaded')
            try:
                await pg.wait_for_function(
                    'typeof ALLROWS!=="undefined" && ALLROWS.length>0 && typeof castNow==="function" '
                    '&& typeof DFMC_AFX_BANK!=="undefined" && Object.keys(DFMC_AFX_BANK.bank()).length>0 '
                    '&& Array.isArray(window.__afxLog)', timeout=45000)
            except Exception:
                chk('vfx.html exposes the AFX walk (DFMC_AFX_BANK / __afxLog / castNow)', False,
                    'none of them appeared in 45s - the page is not playing from the AFX bank')
                await b.close()
                print('\nSUMMARY', sum(R), '/', len(R))
                return 1
            await pg.evaluate('DFMC_AFX.mute(true); DFMC_AFX_BANK.mute(true);')   # a gate makes no noise

            loaded = await pg.evaluate(
                '[Object.keys(DFMC_AFX_BANK.bank()).length, Object.keys(DFMC_AFX_BANK.events()).length, '
                ' Object.keys(DFMC_AFX_BANK.tracks()).length, ALLROWS.length]')
            chk('vfx.html loads the bank, the cues and the beds',
                loaded[:3] == [len(bank), len(ev), len(bgm)],
                '%d clips / %d events / %d tracks loaded (csv: %d / %d / %d), %d move rows'
                % (loaded[0], loaded[1], loaded[2], len(bank), len(ev), len(bgm), loaded[3]))
            # THE WHOLE CONTRACT, name by name (codex/AFX_SPEC.md). A page that calls a method the
            # lifted player does not have fails at the call site, which is a console error the gate
            # would only notice if that code path happened to run; this notices it at boot.
            api = ['parse', 'layerMs', 'lengthMs', 'zoneFor', 'load', 'play', 'cue', 'music',
                   'setMix', 'getMix', 'unlock', 'mute', 'isMuted', 'trackForZone',
                   'bank', 'events', 'tracks']
            have = await pg.evaluate('(names)=>names.filter(n=>typeof DFMC_AFX_BANK[n]!=="function")', api)
            chk('the review page and the client share one player, whole contract', not have,
                'missing: %s' % ', '.join(have) if have else '%d methods, lifted, not a stub'
                % len(api))
            chk('the lifted player is the client\'s own block, not the stub',
                not await pg.evaluate('!!DFMC_AFX_BANK.STUB'),
                'tools/gen_vfx_fx.py --write has run against a client that has the block')

            # EVERY EVENT THE CLIENT CUES MUST RESOLVE. The client names these 20 at its call sites;
            # a rename on either side is silence in the game and nothing at all on this page.
            cued = ['ui.click', 'ui.open', 'ui.close', 'ui.deny', 'ui.toast', 'battle.start',
                    'battle.victory', 'battle.defeat', 'unit.down', 'level_up', 'evolve', 'hatch',
                    'egg.lay', 'craft.success', 'craft.fail', 'loot', 'shop.buy', 'boss.arrive',
                    'boss.fell', 'ascend']
            missing_ev = await pg.evaluate(
                '(ids)=>{const E=DFMC_AFX_BANK.events(); return ids.filter(i=>!E[i]||!E[i].file);}', cued)
            chk('every Event_ID the client cues resolves in afx_events.csv (%d)' % len(cued),
                not missing_ev, 'missing: %s' % ', '.join(missing_ev) if missing_ev else
                'all %d present, %d more authored for events the client does not cue yet'
                % (len(cued), len(ev) - len(cued)))

            # and the beds the client asks for by name. There are TEN, one per zone, and no others
            # [R D 2026-09-24]: the bed belongs to the zone, not to the screen, so there is nothing
            # for a hub window, a boss floor or the title screen to swap in.
            want_tracks = []
            zone_names = [r['Zone'] for r in rows('floors.csv')]
            seen_z = []
            for z in zone_names:
                if z not in seen_z:
                    seen_z.append(z)
            miss_t = await pg.evaluate(
                '([ids, zones])=>{const T=DFMC_AFX_BANK.tracks();'
                ' const bad=ids.filter(i=>!T[i]||!T[i].file);'
                ' zones.slice(0,10).forEach((z,n)=>{ if(!DFMC_AFX_BANK.trackForZone(z)) bad.push("zone "+z); });'
                ' return bad;}', [want_tracks, seen_z])
            chk('the ten zone beds all resolve by the names the client uses, and there are no others',
                not miss_t, 'missing: %s' % ', '.join(miss_t) if miss_t else
                'the ten zone beds: %s' % ', '.join(seen_z[:3] + ['...']))

            # ---- every asset really is there ----
            await fetch_all(pg, [r['File'] for r in bank], 'afx_bank.csv')
            await fetch_all(pg, [r['File'] for r in bgm] + [r['File'] for r in ev],
                            'bgm.csv + afx_events.csv')

            # ---- the probe: the player works even with nothing authored ----
            pr = await pg.evaluate(PROBE_JS)
            ok = bool(pr.get('ok')) and not pr.get('errs') and pr.get('layers') == 2 \
                and pr.get('grew') and pr.get('lenMs', 0) > 0
            chk('a probe composition parses and plays through DFMC_AFX_BANK.play', ok,
                ('%s -> %d layers, %d ms, errs %s' % (pr.get('txt'), pr.get('layers', 0),
                                                      pr.get('lenMs', 0), pr.get('errs')))
                if pr.get('ok') else str(pr.get('why')))

            # ---- the sampled walk: every 25th move at S1-S3, plus every ULT ----
            jobs = await pg.evaluate("""(()=>{const j=[];let k=0;
              for(let i=0;i<MOV.length;i+=25){ for(const st of [1,2,3]) j.push([MOV[i].Move_ID, st, (k++)%2?'enemy':'ally']); }
              for(const u of ULT) j.push([u.Move_ID, 1, (k++)%2?'enemy':'ally']);
              return j;})()""")
            n_ult = await pg.evaluate('ULT.length')
            chk('the sample is every 25th move at S1-S3 plus all %d ultimates' % n_ult,
                len(jobs) > 0, '%d casts' % len(jobs))

            t0 = time.time()
            for i in range(0, len(jobs), 30):
                for rc in await pg.evaluate(CAST_JS, jobs[i:i + 30]):
                    if rc.get('missing') or rc.get('err'):
                        n_bad += 1
                        fails.append('%s S%s: %s' % (rc.get('id'), rc.get('stage'),
                                                     rc.get('err') or 'row missing'))
                        continue
                    if not rc['afx']:
                        n_fallback += 1
                        fb.append('%s S%s' % (rc['id'], rc['stage']))
                        if not rc.get('aarch'):
                            n_bad += 1
                            fails.append('%s S%s: no composition AND no fallback archetype - it made '
                                         'no sound at all' % (rc['id'], rc['stage']))
                        continue
                    # A row WITH a composition must have reached play() with a parsed one.
                    if rc['logged'] != 1 or rc['loggedLayers'] < 1 or not rc['loggedIds']:
                        n_bad += 1
                        fails.append('%s S%s: composition %r never reached DFMC_AFX_BANK.play '
                                     '(%d log entries)' % (rc['id'], rc['stage'], rc['afxText'],
                                                           rc['logged']))
                    elif rc['afxLenMs'] <= 0:
                        n_bad += 1
                        fails.append('%s S%s: played a composition of zero length' % (rc['id'], rc['stage']))
                    else:
                        n_bank_casts += 1
            dt = time.time() - t0
            chk('every cast with a composition reached the player with a parsed one', n_bad == 0,
                '%d bank casts, %d fallbacks of %d, %.1fs%s'
                % (n_bank_casts, n_fallback, len(jobs), dt,
                   '' if n_bad == 0 else ' | ' + '; '.join(fails[:3])))
            await pg.evaluate('playAll(false); stopLoop();')
            chk('vfx.html: no page errors', not perr, '; '.join(perr[:2]))
            chk('vfx.html: no console errors', not cerr, '; '.join(cerr[:2]))

            # ---- audio.html ----
            aerr, acerr = [], []
            pg2 = await b.new_page(viewport={'width': 1400, 'height': 1000})
            pg2.on('pageerror', lambda e: aerr.append(str(e)))

            def on_console2(m):
                if m.type == 'error' and 'Failed to load resource' not in m.text:
                    acerr.append(m.text)
            pg2.on('console', on_console2)
            print('gate url:', AUDIO_URL)
            await pg2.goto(AUDIO_URL, wait_until='domcontentloaded')
            try:
                await pg2.wait_for_function('window.__afxReady===true', timeout=45000)
            except Exception:
                chk('audio.html boots', False, 'window.__afxReady never became true in 45s')
                await b.close()
                print('\nSUMMARY', sum(R), '/', len(R))
                return 1
            await pg2.evaluate('DFMC_AFX_BANK.mute(true)')
            counts = await pg2.evaluate('[BANK.length, BGM.length, EV.length, FLOORS.length, '
                                        'Object.keys(USED).length]')
            chk('audio.html boots with all three data files',
                counts[:4] == [len(bank), len(bgm), len(ev), 120],
                '%d clips / %d beds / %d events / %d floors, %d clips used by a move or cue'
                % tuple(counts))
            # every tab renders a table, and the bank tab groups the 606
            # Scoped to each tab's HOST, not the tab: #tab-bgm also holds the floor picker's own play
            # button, and counting that as a bed is how a count check starts lying by one.
            tabs = await pg2.evaluate("""(()=>{const out={}, host={bgm:'bgmHost',events:'evHost',bank:'bankHost'};
              for(const t of ['bgm','events','bank']){
                document.querySelector('.btn.tab[data-tab="'+t+'"]').click();
                const h='#'+host[t];
                out[t]=[document.querySelectorAll(h+' table').length,
                        document.querySelectorAll(h+' tbody tr').length,
                        document.querySelectorAll(h+' button.play').length];
              }
              return out;})()""")
            chk('BGM tab: one row and one play button per bed',
                tabs['bgm'][2] == len(bgm), '%s' % (tabs['bgm'],))
            chk('EVENTS tab: one row and one play button per event',
                tabs['events'][2] == len(ev), '%s' % (tabs['events'],))
            chk('BANK tab: the 606 clips, grouped, each with a play button',
                tabs['bank'][2] == len(bank) and tabs['bank'][0] >= 9, '%s tables/rows/buttons'
                % (tabs['bank'],))
            # the filters
            filt = await pg2.evaluate("""(()=>{
              const n=()=>document.querySelectorAll('#bankHost button.play').length;
              const all=n();
              document.getElementById('hideShrill').click(); const noShrill=n();
              document.getElementById('hideClip').click();  const neither=n();
              document.getElementById('hideShrill').click(); document.getElementById('hideClip').click();
              const back=n();
              const s=document.getElementById('search'); s.value='impact';
              s.dispatchEvent(new Event('input')); const searched=n();
              s.value=''; s.dispatchEvent(new Event('input'));
              return [all, noShrill, neither, back, searched, n()];})()""")
            shrill = sum(1 for r in bank if float(r['Over3k_Pct']) >= 20)
            clipped = sum(1 for r in bank if float(r['Peak_dBFS']) > 0)
            chk('hide shrill / hide clipped / search each narrow the bank and restore',
                filt[1] == len(bank) - shrill and filt[3] == len(bank) and filt[0] == len(bank)
                and 0 < filt[4] < len(bank) and filt[5] == len(bank),
                'all %d, -shrill %d (expect %d), -both %d, restored %d, "impact" %d'
                % (filt[0], filt[1], len(bank) - shrill, filt[2], filt[3], filt[4]))
            # the fold, on the page, for all 120 floors
            # THE BED IS THE FLOOR'S ZONE BED AND NOTHING OVERRIDES IT [R D 2026-09-24]. There is no
            # boss bed, no hub bed and no title bed: a non-battle screen keeps the zone's bed, a
            # battle keeps it, and only crossing into another zone changes it.
            fold = await pg2.evaluate("""(()=>{const out=[];
              for(let f=1;f<=120;f++) out.push([f, zoneOf(f), trackForFloor(f)]);
              return out;})()""")
            zone_ids = [r['Track_ID'] for r in bgm if r['State'] == 'zone']
            wrong = []
            for f, z, tid in fold:
                want_z = ((f - 101) // 2) + 1 if f >= 101 else ((f - 1) // 10) + 1
                want = zone_ids[want_z - 1]
                if z != want_z or tid != want:
                    wrong.append('floor %d -> zone %s / %s (want %s / %s)' % (f, z, tid, want_z, want))
            chk('every floor 1-120 resolves to a bed by the Void Apex fold', not wrong,
                '%d wrong: %s' % (len(wrong), '; '.join(wrong[:3])) if wrong else
                'floors 101-120 fold onto the ten zone beds two at a time; nothing overrides a zone bed')
            chk('audio.html: no page errors', not aerr, '; '.join(aerr[:2]))
            chk('audio.html: no console errors', not acerr, '; '.join(acerr[:2]))
            await b.close()
    finally:
        if srv:
            srv.kill()

    if n_fallback:
        print('\nfell back to the placeholder synth (no AFX composition on the row): %d of %d sampled '
              'casts - %s%s' % (n_fallback, n_bank_casts + n_fallback, ', '.join(fb[:6]),
                                ' ...' if len(fb) > 6 else ''))
    for f in fails[:12]:
        print('  [!]', f)
    print('RESULT afx_gate: %d/%d checks, %d bank casts, %d fallbacks, %d wrong, %d page errors, '
          '%d console errors, %d clips + %d beds + %d cues all 200'
          % (sum(R), len(R), n_bank_casts, n_fallback, n_bad, len(perr), len(cerr),
             len(bank), len(bgm), len(ev)))
    return 0 if all(R) else 1


sys.exit(asyncio.run(main()))
