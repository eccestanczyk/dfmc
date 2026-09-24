/* ============================================================================
   GENERATED from play/app.js by tools/gen_vfx_fx.py - the client is the source of truth; this stub
   stands until the client lane lands

   THE AFX BANK PLAYER. ONE IMPLEMENTATION, TWO CONSUMERS - the game and this codex's review pages.
   The contract is codex/AFX_SPEC.md § The player contract, and it is implemented ONCE, in
   dfmc-client/play/app.js as `const AFX_BANK=(()=>{ ... })();`. tools/gen_vfx_fx.py lifts that block
   out of the client into this file as `window.DFMC_AFX_BANK`, exactly the way it lifts VFX_BANK into
   vfx_fx.js, and for the same reason: when the game and the review page had two implementations,
   approving an effect on the review page approved something players never got.

   WHAT THIS FILE IS RIGHT NOW. The client block does not exist yet - the AFX authoring run landed the
   data, the grammar, the linter and the pages first. So this is a STUB that implements the contract
   and nothing more, written so the review pages are real (they decode and play the actual .ogg files
   out of codex/afx_bank.csv, at the gains and pitches a composition asks for) and so the day the
   client block appears, `python tools/gen_vfx_fx.py --write` overwrites this file and nothing else has
   to change. The generator looks for the block on every run and keeps this stub, with a message, when
   it is absent - so the divergence gate does not go red before the implementation exists.

   Do not hand-author behaviour here that the client does not have. Every verdict in parse() is a
   verdict tools/afx_lint.py also reaches; if the two ever disagree, the sound a reviewer approves is
   not the sound a player hears.
   ============================================================================ */
(function (root) {
  'use strict';

  /* ---- the grammar (codex/AFX_SPEC.md § The grammar) ---------------------------------------- */
  var TOK = /^(g|p|d|n|i|j)(-?\d+(?:\.\d+)?)$/;
  var RANGE = { g: [0.05, 1.5], p: [-12, 12], d: [0, 2000], n: [1, 4], i: [30, 600], j: [0, 3] };
  var INT = { p: 1, d: 1, n: 1, i: 1, j: 1 };
  var DEF = { g: 1, p: 0, d: 0, n: 1, i: 90, j: 0 };
  var MOVE_GROUPS = ['impact', 'material', 'melee', 'blast', 'arcane', 'machine', 'creature', 'foley', 'footstep'];
  var REFUSED = ['ui', 'coin', 'jingle', 'door'];
  var SHRILL_OVER3K = 20, SHRILL_MAX_P = -3, CLIP_MAX_G = 0.7;

  /* ---- state ------------------------------------------------------------------------------- */
  var ctx = null, gMaster = null, gMusic = null, gSfx = null;
  var mix = { master: 70, music: 60, sfx: 80 }, muted = false;
  var BANK = {}, EVENTS = {}, TRACKS = {}, BASE = '';
  var buffers = {}, inflight = {}, warned = {};
  var lastCue = {}, music = { id: null, src: null, gain: null };

  function taper(pct) { return Math.pow(Math.max(0, Math.min(100, pct)) / 100, 1.6); }

  function ac() {
    if (!ctx) {
      var C = root.AudioContext || root.webkitAudioContext;
      if (!C) return null;
      ctx = new C();
      gMaster = ctx.createGain(); gMusic = ctx.createGain(); gSfx = ctx.createGain();
      gMusic.connect(gMaster); gSfx.connect(gMaster); gMaster.connect(ctx.destination);
      applyMix();
    }
    return ctx;
  }
  function applyMix() {
    if (!gMaster) return;
    gMaster.gain.value = muted ? 0 : taper(mix.master);
    gMusic.gain.value = taper(mix.music);
    gSfx.gain.value = taper(mix.sfx);
  }

  /* One decode per path, ever, and never two in flight for the same path. A missing file is logged
     ONCE and then plays nothing - a review page that casts 1200 times must not print 1200 lines. */
  function buffer(file) {
    if (buffers[file]) return Promise.resolve(buffers[file]);
    if (inflight[file]) return inflight[file];
    var c = ac();
    if (!c) return Promise.resolve(null);
    var p = fetch(BASE + file).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.arrayBuffer();
    }).then(function (ab) {
      return new Promise(function (res, rej) { c.decodeAudioData(ab, res, rej); });
    }).then(function (buf) {
      buffers[file] = buf; delete inflight[file]; return buf;
    }).catch(function (e) {
      delete inflight[file];
      if (!warned[file]) { warned[file] = 1; try { console.warn('[afx] cannot play ' + file + ': ' + e.message); } catch (x) {} }
      return null;
    });
    return (inflight[file] = p);
  }

  /* ---- parse ------------------------------------------------------------------------------- */
  function parse(text) {
    var layers = [], errs = [], parts = String(text == null ? '' : text).split('|'), i, k;
    for (i = 0; i < parts.length; i++) {
      var raw = parts[i].trim();
      if (!raw) { errs.push('empty layer'); continue; }
      var toks = raw.split(/\s+/);
      if (!/^AFX-\d{3}$/.test(toks[0])) { errs.push('bad head token "' + toks[0] + '" (want AFX-NNN)'); continue; }
      var id = toks[0], row = BANK[id], mods = {}, seen = {};
      if (!row) errs.push('unknown clip ' + id);
      for (k = 1; k < toks.length; k++) {
        var m = TOK.exec(toks[k]);
        if (!m) { errs.push('bad token "' + toks[k] + '" in ' + id); continue; }
        var key = m[1], v = parseFloat(m[2]);
        if (seen[key]) errs.push(id + ' writes ' + key + ' twice - the last one silently wins');
        seen[key] = 1;
        if (v < RANGE[key][0] || v > RANGE[key][1])
          errs.push(id + ' ' + key + m[2] + ' out of range ' + RANGE[key][0] + '..' + RANGE[key][1]);
        if (INT[key] && v !== Math.round(v)) errs.push(id + ' ' + key + ' must be an integer');
        mods[key] = v;
      }
      if (mods.i != null && !(mods.n > 1)) errs.push(id + ' has i without n>1 - nothing to space');
      if (row) {
        var over3k = parseFloat(row.Over3k_Pct), peak = parseFloat(row.Peak_dBFS);
        if (over3k >= SHRILL_OVER3K && (mods.p == null || mods.p > SHRILL_MAX_P))
          errs.push(id + ' is SHRILL (' + over3k + '% above 3 kHz) and needs p<=' + SHRILL_MAX_P);
        if (peak > 0 && (mods.g == null || mods.g > CLIP_MAX_G))
          errs.push(id + ' is CLIPPED (peak ' + peak + ' dBFS) and needs g<=' + CLIP_MAX_G);
        if (REFUSED.indexOf(row.Group) >= 0)
          errs.push(id + ' is a ' + row.Group + ' clip - refused on a move');
        else if (MOVE_GROUPS.indexOf(row.Group) < 0)
          errs.push(id + ' is group "' + row.Group + '", which is not a move group');
      }
      var L = { id: id };
      for (k in DEF) L[k] = (mods[k] == null ? DEF[k] : mods[k]);
      layers.push(L);
    }
    return { layers: layers, errs: errs };
  }

  function rate(p) { return Math.pow(2, p / 12); }

  function layerEnd(L, bank) {
    var row = (bank || BANK)[L.id];
    var secs = row ? parseFloat(row.Seconds) : 0;
    return L.d + (L.n - 1) * L.i + (secs * 1000) / rate(L.p);
  }
  function lengthMs(parsed, bank) {
    var ls = (parsed && parsed.layers) || [], out = 0, i;
    for (i = 0; i < ls.length; i++) out = Math.max(out, layerEnd(ls[i], bank));
    return out;
  }

  /* ---- load -------------------------------------------------------------------------------- */
  /* Takes afx_bank.csv rows, afx_events.csv rows or bgm.csv rows - the row's own key column says
     which, so a page can hand over all three without three entry points. */
  function load(rows, base) {
    if (base != null) BASE = base;
    (rows || []).forEach(function (r) {
      if (r.Id) BANK[r.Id] = r;
      else if (r.Event_ID) EVENTS[r.Event_ID] = { file: r.File, gain: parseFloat(r.Gain) || 1,
                                                 retriggerMs: parseInt(r.Retrigger_Ms, 10) || 0, row: r };
      else if (r.Track_ID) TRACKS[r.Track_ID] = { file: r.File, gain: parseFloat(r.Gain) || 1, row: r };
    });
    return { clips: Object.keys(BANK).length, events: Object.keys(EVENTS).length, tracks: Object.keys(TRACKS).length };
  }

  /* ---- play -------------------------------------------------------------------------------- */
  /* speed scales every d and every i - the client's fast-forward - and NEVER the pitch. */
  function play(comp, opts) {
    opts = opts || {};
    var parsed = (comp && comp.layers) ? comp : parse(comp);
    var speed = opts.speed > 0 ? opts.speed : 1;
    var gain = opts.gain == null ? 1 : opts.gain;
    var c = ac(), nodes = [], timers = [], dead = false;
    if (!c || !parsed.layers.length) return { stop: function () {}, parsed: parsed, lenMs: lengthMs(parsed) };
    if (c.state === 'suspended') c.resume();

    parsed.layers.forEach(function (L) {
      var row = BANK[L.id];
      if (!row) return;
      for (var k = 0; k < L.n; k++) {
        (function (rep) {
          var at = (L.d + rep * L.i) / speed;
          var t = setTimeout(function () {
            if (dead) return;
            buffer(row.File).then(function (buf) {
              if (dead || !buf) return;
              var s = c.createBufferSource(), g = c.createGain();
              s.buffer = buf;
              /* j is re-rolled on every play AND every repeat, so a volley never sounds copy-pasted. */
              var jit = L.j ? (Math.random() * 2 - 1) * L.j : 0;
              s.playbackRate.value = rate(L.p + jit);
              g.gain.value = L.g * gain;
              s.connect(g); g.connect(gSfx);
              s.start();
              nodes.push(s);
            });
          }, at);
          timers.push(t);
        })(k);
      }
    });
    return {
      parsed: parsed, lenMs: lengthMs(parsed) / speed,
      stop: function () {
        dead = true;
        timers.forEach(clearTimeout);
        nodes.forEach(function (s) { try { s.stop(); } catch (e) {} });
      }
    };
  }

  /* ---- cue --------------------------------------------------------------------------------- */
  function cue(id, opts) {
    opts = opts || {};
    var e = EVENTS[id];
    if (!e) {
      if (!warned['ev:' + id]) { warned['ev:' + id] = 1; try { console.warn('[afx] no such event: ' + id); } catch (x) {} }
      return { stop: function () {} };
    }
    var now = Date.now();
    if (e.retriggerMs && lastCue[id] && now - lastCue[id] < e.retriggerMs) return { stop: function () {} };
    lastCue[id] = now;
    var c = ac(), stopped = false, src = null;
    if (!c) return { stop: function () {} };
    if (c.state === 'suspended') c.resume();
    buffer(e.file).then(function (buf) {
      if (stopped || !buf) return;
      var s = c.createBufferSource(), g = c.createGain();
      s.buffer = buf; g.gain.value = e.gain * (opts.gain == null ? 1 : opts.gain);
      s.connect(g); g.connect(gSfx); s.start(); src = s;
    });
    return { stop: function () { stopped = true; try { src && src.stop(); } catch (x) {} } };
  }

  /* ---- music ------------------------------------------------------------------------------- */
  var FADE_IN = 1.2, FADE_OUT = 0.9;
  function musicPlay(trackId, opts) {
    opts = opts || {};
    if (trackId === music.id) return;                 /* the same bed is a no-op, not a restart */
    var c = ac();
    if (!c) return;
    if (c.state === 'suspended') c.resume();
    if (music.src) {
      var oldSrc = music.src, oldGain = music.gain, t0 = c.currentTime;
      try {
        oldGain.gain.cancelScheduledValues(t0);
        oldGain.gain.setValueAtTime(oldGain.gain.value, t0);
        oldGain.gain.linearRampToValueAtTime(0.0001, t0 + FADE_OUT);
      } catch (e) {}
      setTimeout(function () { try { oldSrc.stop(); } catch (e) {} }, FADE_OUT * 1000 + 60);
      music.src = null; music.gain = null;
    }
    music.id = trackId || null;
    if (!trackId) return;
    var tr = TRACKS[trackId];
    if (!tr) {
      if (!warned['tr:' + trackId]) { warned['tr:' + trackId] = 1; try { console.warn('[afx] no such track: ' + trackId); } catch (x) {} }
      return;
    }
    buffer(tr.file).then(function (buf) {
      if (!buf || music.id !== trackId) return;
      var s = c.createBufferSource(), g = c.createGain(), t = c.currentTime;
      s.buffer = buf; s.loop = true;
      var target = tr.gain * (opts.gain == null ? 1 : opts.gain);
      g.gain.setValueAtTime(0.0001, t);
      g.gain.linearRampToValueAtTime(target, t + FADE_IN);
      s.connect(g); g.connect(gMusic); s.start();
      music.src = s; music.gain = g;
    });
  }

  /* ---- the Void Apex fold (codex/AFX_SPEC.md, R D 2026-09-24) ------------------------------- */
  /* Floors 101-120 reuse the ten zone beds two floors at a time: the climb heard a second time at
     four times the speed, which is what the apex is. There is no eleventh bed. */
  function zoneForFloor(floor) {
    var f = Math.max(1, Math.min(120, Math.round(+floor || 1)));
    return f >= 101 ? Math.floor((f - 101) / 2) + 1 : Math.floor((f - 1) / 10) + 1;
  }
  function trackForFloor(floor, isBoss) {
    if (isBoss && TRACKS.boss) return 'boss';
    var n = zoneForFloor(floor), zones = Object.keys(TRACKS).filter(function (k) {
      return TRACKS[k].row && TRACKS[k].row.State === 'zone';
    });
    return zones[n - 1] || null;
  }

  root.DFMC_AFX_BANK = {
    parse: parse, lengthMs: lengthMs, load: load, play: play, cue: cue, music: musicPlay,
    setMix: function (m) { if (m) { for (var k in m) if (mix[k] != null && m[k] != null) mix[k] = +m[k]; } applyMix(); },
    getMix: function () { return { master: mix.master, music: mix.music, sfx: mix.sfx }; },
    unlock: function () { var c = ac(); if (c && c.state === 'suspended') c.resume(); },
    mute: function (m) { muted = !!m; applyMix(); },
    isMuted: function () { return muted; },
    zoneForFloor: zoneForFloor, trackForFloor: trackForFloor,
    bank: BANK, events: EVENTS, tracks: TRACKS,
    STUB: true
  };
})(typeof window !== 'undefined' ? window : globalThis);
