/* ============================================================================
   GENERATED from play/app.js by tools/gen_vfx_fx.py - the client is the source of truth

   THE AFX BANK PLAYER, lifted verbatim from the client's `const AFX_BANK=(()=>{ ... })();`. The
   contract is codex/AFX_SPEC.md § The player contract. It is implemented ONCE, in play/app.js, so the
   sound a reviewer approves on vfx.html / audio.html is the sound a player hears - the same
   arrangement VFX_BANK has in vfx_fx.js, for the same reason. Do not hand-edit this copy.

     game :  AFX_BANK, inline in play/app.js
     page :  window.DFMC_AFX_BANK
   ============================================================================ */
(function (root) {
  const AFX_BANK=(()=>{
    const TOK=/^(g|p|d|n|i|j)(-?\d+(?:\.\d+)?)$/;
    const RANGE={g:[0.05,1.5],p:[-12,12],d:[0,2000],n:[1,4],i:[30,600],j:[0,3]};
    const INT={d:1,n:1,i:1};
    // groups a MOVE may use; ui / coin / jingle / door belong to the cue set and are refused on a move
    const MOVE_GROUPS={impact:1,material:1,melee:1,blast:1,arcane:1,machine:1,creature:1,foley:1,footstep:1};
    const REFUSED={ui:1,coin:1,jingle:1,door:1};
    const FADE_IN=1200, FADE_OUT=900;   // the crossfade, ms (contract)
    const num=(v,d0)=>{ const n=parseFloat(v); return (n===n)?n:d0; }; // NaN-safe: a blank cell is the default, never NaN
    const col=(row,a,b)=>{ if(row==null) return undefined; return (row[a]!==undefined)?row[a]:row[b]; }; // a raw csv row or a registered one
    /* parse(txt, bank) -> {layers:[{id,g,p,d,n,i,j}], errs:[...]}. errs non-empty = malformed; the verdicts are
       tools/afx_lint.py's, token for token, for everything a SINGLE composition can decide. The three rules that
       span cells - family identity (S2/S3 carry S1's first clip), FX/AFX timing alignment, the per-stage layer and
       length budgets - are the linter's alone: this parser is handed one cell and cannot see the others.
       bank (Id -> afx_bank.csv row) is optional; without it the clip-level checks (unknown id, group, shrill,
       clipped) are skipped and the grammar is still judged. */
    const parse=(txt,bank)=>{ const layers=[], errs=[]; if(bank===undefined) bank=BANK;
      const known=!!(bank&&Object.keys(bank).length);
      String(txt==null?'':txt).split('|').forEach(raw=>{ raw=raw.trim(); if(!raw){ errs.push('empty layer'); return; }
        const toks=raw.split(/\s+/);
        const m=/^(AFX-\d{3})$/.exec(toks[0]);
        if(!m){ errs.push('bad head token '+JSON.stringify(toks[0])+' (want AFX-NNN)'); return; }
        const aid=m[1]; const row=known?bank[aid]:null;
        if(known&&!row) errs.push('unknown clip '+aid);
        const mods={}, seen={};
        toks.slice(1).forEach(t=>{ const mm=TOK.exec(t);
          if(!mm){ errs.push('bad token '+JSON.stringify(t)+' in '+aid); return; }
          const k=mm[1], v=parseFloat(mm[2]);
          if(seen[k]){ errs.push('duplicate token '+k+' in '+aid); return; }
          seen[k]=1;
          if(!(RANGE[k][0]<=v&&v<=RANGE[k][1])) errs.push(k+mm[2]+' out of range '+RANGE[k][0]+'-'+RANGE[k][1]);
          if(INT[k]&&v!==Math.floor(v)) errs.push(k+' must be an integer');
          mods[k]=v; });
        const L={id:aid, g:(mods.g==null?1:mods.g), p:(mods.p||0), d:(mods.d||0), n:(mods.n||1), i:(mods.i==null?90:mods.i), j:(mods.j||0)};
        if(row){ const grp=String(col(row,'Group','group')||'').toLowerCase();
          if(REFUSED[grp]) errs.push(aid+' is a '+grp+' clip - the cue set owns those, a move may not use one');
          else if(grp&&!MOVE_GROUPS[grp]) errs.push(aid+' group '+JSON.stringify(grp)+' is not a move group');
          const o3=num(col(row,'Over3k_Pct','over3k'),0);
          if(o3>=20&&!(L.p<=-3)) errs.push(aid+' is SHRILL ('+o3+'% over 3 kHz) - needs p<=-3');
          const pk=num(col(row,'Peak_dBFS','peak'),-99);
          if(pk>0&&!(L.g<=0.7)) errs.push(aid+' is CLIPPED (peak '+pk+' dBFS) - needs g<=0.7'); }
        layers.push(L); });
      /* THE SIMULTANEITY BUDGET. Four layers at g1 inside one 60 ms window is four times the level of one, and
         the sum is what reaches the bus, not the loudest member. Reported once per cluster, keyed on the
         cluster's own delays, so a four-layer breach is one error and not four. */
      const said={};
      layers.forEach(a=>{ let s=0; const ds=[];
        layers.forEach(b=>{ if(Math.abs(b.d-a.d)<=60){ s+=b.g; ds.push(b.d); } });
        if(s>1.6+1e-9){ const key=ds.sort((x,y)=>x-y).join(',');
          if(!said[key]){ said[key]=1; errs.push('gain sum '+(Math.round(s*100)/100)+' across the layers within 60 ms of d'+a.d+' exceeds 1.6'); } } });
      return {layers:layers, errs:errs}; };
    // a layer's end, ms from the cast: d + (n-1)*i + Seconds*1000 / 2^(p/12). Pitching down LENGTHENS the clip.
    const layerMs=(l,bank)=>{ const row=(bank||BANK)[l.id]; if(!row) return l.d+(l.n-1)*l.i;
      const sec=num(col(row,'Seconds','seconds'),0);
      return l.d+(l.n-1)*l.i+sec*1000/Math.pow(2,l.p/12); };
    const lengthMs=(parsed,bank)=>{ const P=(typeof parsed==='string')?parse(parsed,bank):parsed;
      return ((P&&P.layers)||[]).reduce((a,l)=>Math.max(a,layerMs(l,bank)),0); };
    /* THE FOLD RULE [R D 2026-09-24]: floors 101-120 (Void Apex) reuse the ten zone beds two floors at a time,
       101-102 on zone 1, 119-120 on zone 10. The dungeon's music_zone_void is NOT used up there. Below 101 a
       zone is ten floors. This lives in the liftable block so the gate can check it on the shipped bytes. */
    const zoneFor=f=>{ f=+f||0; return f>=101?(Math.floor((f-101)/2)+1):(Math.floor((f-1)/10)+1); };

    // ---- registries and the audio graph ---------------------------------------------------------
    let BANK={}, EVENTS={}, TRACKS={}, BASE='';
    const mix={master:80, music:60, sfx:90};
    let muted=false, unlocked=false;
    let ctx=null, gMaster=null, gMusic=null, gSfx=null;
    const buf={}, pending={}, warned={}, lastCue={};
    let cur=null; // the music handle on air
    const warnOnce=msg=>{ if(warned[msg]) return; warned[msg]=1; try{ console.warn('[afx] '+msg); }catch(e){} };
    const url=f=>{ f=String(f==null?'':f).replace(/^\.?\//,''); return (/^[a-z]+:\/\//i.test(f)||!BASE)?f:(BASE+f); };
    const taper=v=>Math.pow(Math.max(0,Math.min(100,num(v,0)))/100,1.6); // (pct/100)^1.6: a slider must not spend half its travel above comfortable
    const applyMix=()=>{ if(!ctx) return;
      try{ gMaster.gain.value=muted?0:taper(mix.master); gMusic.gain.value=taper(mix.music); gSfx.gain.value=taper(mix.sfx); }catch(e){} };
    const ensure=()=>{ if(ctx) return ctx;
      try{ const AC=(typeof window!=='undefined'&&(window.AudioContext||window.webkitAudioContext))||(typeof AudioContext!=='undefined'?AudioContext:null);
        if(!AC){ warnOnce('no Web Audio in this browser'); return null; }
        ctx=new AC();
        gMaster=ctx.createGain(); gMusic=ctx.createGain(); gSfx=ctx.createGain();
        gMaster.connect(ctx.destination); gMusic.connect(gMaster); gSfx.connect(gMaster);
        applyMix(); }catch(e){ ctx=null; warnOnce('cannot open an AudioContext: '+(e&&e.message||e)); }
      return ctx; };
    /* load(rows, base, kind): afx_bank.csv, afx_events.csv or bgm.csv, told apart by their own key column so one
       call site serves all three. base is the URL prefix for File (the client ships its own copies under
       play/assets/afx|bgm, the codex page reads them from its own tree). Called again with the same kind
       REPLACES that registry - a reload must not leave a retired id addressable. */
    const load=(rows,base,kind)=>{ if(base!=null) BASE=String(base);
      const k0=kind||((rows&&rows.length)?(rows[0].Id?'bank':(rows[0].Event_ID?'events':(rows[0].Track_ID?'bgm':null))):null);
      const counts=()=>({bank:Object.keys(BANK).length, events:Object.keys(EVENTS).length, tracks:Object.keys(TRACKS).length});
      if(!k0) return counts();
      if(k0==='bank') BANK={}; else if(k0==='events') EVENTS={}; else if(k0==='bgm') TRACKS={};
      (rows||[]).forEach(r=>{ if(!r) return;
        if(k0==='bank'&&r.Id) BANK[String(r.Id)]={ id:String(r.Id), file:url(r.File), Seconds:num(r.Seconds,0), Group:String(r.Group||'').toLowerCase(),
          Over3k_Pct:num(r.Over3k_Pct,0), Peak_dBFS:num(r.Peak_dBFS,-99), Name:r.Name||'' };
        else if(k0==='events'&&r.Event_ID) EVENTS[String(r.Event_ID)]={ id:String(r.Event_ID), file:url(r.File), gain:num(r.Gain,1), retriggerMs:num(r.Retrigger_Ms,0), category:String(r.Category||'') };
        else if(k0==='bgm'&&r.Track_ID) TRACKS[String(r.Track_ID)]={ id:String(r.Track_ID), file:url(r.File), gain:num(r.Gain,1), state:String(r.State||''), zone:String(r.Zone||''), seconds:num(r.Seconds,0), title:r.Title||'' }; });
      return counts(); };
    // one decode per path, ever, and never two in flight for the same path. A miss is ONE console line, not a throw.
    const decode=path=>{ if(buf[path]) return Promise.resolve(buf[path]);
      if(pending[path]) return pending[path];
      const c=ensure(); if(!c||typeof fetch!=='function') return Promise.resolve(null);
      const p=fetch(path).then(r=>{ if(!r||!r.ok) throw new Error('HTTP '+(r&&r.status)); return r.arrayBuffer(); })
        .then(ab=>new Promise((res,rej)=>{ let out=null;
          try{ out=c.decodeAudioData(ab, b=>res(b), e=>rej(e||new Error('decode failed'))); }catch(e){ rej(e); return; }
          if(out&&typeof out.then==='function') out.then(b=>res(b), e=>rej(e)); }))
        .then(b=>{ delete pending[path]; if(b) buf[path]=b; return b||null; })
        .catch(e=>{ delete pending[path]; warnOnce('clip unavailable '+path+': '+(e&&e.message||e)); return null; });
      pending[path]=p; return p; };
    // one voice: decode (cached), then start at the scheduled time on the given bus. Returns its own stop.
    const voice=(path,gain,semis,delayMs,bus)=>{ const c=ensure(); if(!c) return ()=>{};
      const t0=c.currentTime+Math.max(0,delayMs||0)/1000; let src=null, dead=false;
      decode(path).then(b=>{ if(dead||!b) return;
        try{ src=c.createBufferSource(); src.buffer=b; src.playbackRate.value=Math.pow(2,(semis||0)/12);
          const g=c.createGain(); g.gain.value=Math.max(0,gain); src.connect(g); g.connect(bus);
          src.start(Math.max(c.currentTime,t0)); }catch(e){ warnOnce('cannot start '+path+': '+(e&&e.message||e)); } });
      return ()=>{ dead=true; if(src){ try{ src.stop(); }catch(e){} src=null; } }; };
    /* play(parsed|text, opts) -> {stop()}. opts: speed (the client's fast-forward - it scales every d and i and
       NEVER the pitch, the same rule VFX_BANK.render follows), gain (an extra multiplier), bank.
       A malformed or empty composition plays nothing and is not an error at this layer: the linter and the gate
       are where a bad cell is caught, and a battle must never fail over a data table. */
    const play=(comp,opts)=>{ opts=opts||{}; const stops=[];
      const h={ stop(){ while(stops.length){ const s=stops.pop(); try{ s(); }catch(e){} } } };
      if(muted) return h;
      const bank=opts.bank||BANK;
      const P=(typeof comp==='string')?parse(comp,bank):comp;
      if(!P||!P.layers||!P.layers.length||(P.errs&&P.errs.length)) return h;
      if(!ensure()) return h;
      const speed=(opts.speed==null?1:num(opts.speed,1))||1, og=(opts.gain==null?1:num(opts.gain,1));
      P.layers.forEach(l=>{ const row=bank[l.id]; if(!row||!row.file) return;
        for(let k=0;k<l.n;k++){
          const jit=l.j?((Math.random()*2-1)*l.j):0; // re-rolled per repeat, by the grammar
          stops.push(voice(row.file, l.g*og, l.p+jit, (l.d+k*l.i)*speed, gSfx)); } });
      return h; };
    /* cue(id, opts) -> an afx_events.csv row by Event_ID. Retrigger_Ms is a floor on how often one cue may fire,
       which is what keeps ui.click from turning a held button into a buzz. Unknown id: one console line, silence. */
    const cue=(id,opts)=>{ opts=opts||{}; if(muted||!id) return null;
      const e=EVENTS[String(id)];
      if(!e){ warnOnce('no afx_events.csv row for cue '+id); return null; }
      const now=Date.now(); const rt=(opts.retriggerMs==null?e.retriggerMs:num(opts.retriggerMs,0))||0;
      if(rt&&lastCue[e.id]&&(now-lastCue[e.id])<rt) return null;
      lastCue[e.id]=now;
      if(!ensure()) return null;
      const bus=(opts.bus==='music')?gMusic:gSfx;
      const stop=voice(e.file, e.gain*(opts.gain==null?1:num(opts.gain,1)), num(opts.p,0), num(opts.delay,0), bus);
      return { stop:stop }; };
    /* music(trackId|null, opts): crossfade to a bgm.csv track - in over FADE_IN, the outgoing one out over
       FADE_OUT, looped, the row's Gain applied on the music bus. The SAME id is a no-op, so a screen change
       that does not change the bed never restarts it; null stops. */
    const music=(id,opts)=>{ opts=opts||{};
      const outMs=(opts.fadeOut==null?FADE_OUT:num(opts.fadeOut,FADE_OUT));
      if(id!=null&&cur&&cur.id===String(id)) return cur;
      if(!ensure()) return null;
      const c=ctx;
      if(cur){ const old=cur; cur=null; old.stopped=true;
        try{ const gp=old.gain.gain; gp.cancelScheduledValues(c.currentTime); gp.setValueAtTime(gp.value,c.currentTime); gp.linearRampToValueAtTime(0,c.currentTime+outMs/1000); }catch(e){}
        setTimeout(()=>{ if(old.src){ try{ old.src.stop(); }catch(e){} old.src=null; } }, Math.round(outMs)+80); }
      if(id==null) return null;
      const row=TRACKS[String(id)];
      if(!row||!row.file){ warnOnce('no bgm.csv row for track '+id); return null; }
      const inMs=(opts.fadeIn==null?FADE_IN:num(opts.fadeIn,FADE_IN));
      let g=null; try{ g=c.createGain(); g.gain.value=0; g.connect(gMusic); }catch(e){ return null; }
      const h={ id:String(id), gain:g, src:null, stopped:false, stop(){ this.stopped=true; if(this.src){ try{ this.src.stop(); }catch(e){} this.src=null; } if(cur===this) cur=null; } };
      cur=h;
      decode(row.file).then(b=>{ if(!b||h.stopped||cur!==h) return;
        try{ const s=c.createBufferSource(); s.buffer=b; s.loop=true; s.connect(g); s.start(); h.src=s;
          g.gain.cancelScheduledValues(c.currentTime); g.gain.setValueAtTime(0,c.currentTime);
          g.gain.linearRampToValueAtTime(Math.max(0,row.gain),c.currentTime+inMs/1000); }catch(e){ warnOnce('cannot start bed '+row.file+': '+(e&&e.message||e)); } });
      return h; };
    const setMix=m=>{ if(m){ if(m.master!=null) mix.master=Math.max(0,Math.min(100,num(m.master,mix.master)));
        if(m.music!=null) mix.music=Math.max(0,Math.min(100,num(m.music,mix.music)));
        if(m.sfx!=null) mix.sfx=Math.max(0,Math.min(100,num(m.sfx,mix.sfx))); }
      applyMix(); return {master:mix.master, music:mix.music, sfx:mix.sfx}; };
    const getMix=()=>({master:mix.master, music:mix.music, sfx:mix.sfx, muted:muted,
      gain:{master:muted?0:taper(mix.master), music:taper(mix.music), sfx:taper(mix.sfx)}});
    // unlock: a browser refuses to start an AudioContext outside a gesture. Call from the first click / keydown / touchstart.
    const unlock=()=>{ const c=ensure(); if(!c) return false;
      try{ if(c.state==='suspended'&&typeof c.resume==='function') c.resume(); }catch(e){}
      unlocked=true; return true; };
    const mute=v=>{ muted=!!v; applyMix();
      if(muted&&cur){ const old=cur; cur=null; old.stopped=true; if(old.src){ try{ old.src.stop(); }catch(e){} old.src=null; } }
      return muted; };
    const trackForZone=name=>{ const ks=Object.keys(TRACKS); for(let i=0;i<ks.length;i++){ if(TRACKS[ks[i]].zone===String(name)) return TRACKS[ks[i]].id; } return null; };
    return { parse:parse, layerMs:layerMs, lengthMs:lengthMs, zoneFor:zoneFor, load:load, play:play, cue:cue,
      music:music, setMix:setMix, getMix:getMix, unlock:unlock, mute:mute, trackForZone:trackForZone,
      isMuted:()=>muted, isUnlocked:()=>unlocked, playing:()=>(cur&&cur.id)||null,
      bank:()=>BANK, events:()=>EVENTS, tracks:()=>TRACKS,
      FADE:{in:FADE_IN, out:FADE_OUT}, RANGE:RANGE, MOVE_GROUPS:MOVE_GROUPS, REFUSED:REFUSED };
  })();
  root.DFMC_AFX_BANK = AFX_BANK;
})(typeof window !== 'undefined' ? window : globalThis);
