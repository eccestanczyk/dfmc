/* ============================================================
   HERUMON TOWER - placeholder AFX synth
   Taxonomy: codex/move_vfx.csv  Spec: codex/VFX_SPEC.md
   No audio files. Every sound is synthesised at call time.
   Global: window.DFMC_AFX      (also module.exports)
   ============================================================ */
(function (root) {
  'use strict';

  var ctx = null, master = null, noiseBuf = null, vol = 0.5, muted = false;
  var PITCH = { low: 0.75, mid: 1.0, high: 1.35 };

  function ac() {
    if (!ctx) {
      var C = root.AudioContext || root.webkitAudioContext;
      if (!C) return null;
      ctx = new C();
      master = ctx.createGain();
      master.gain.value = vol;
      master.connect(ctx.destination);
    }
    if (ctx.state === 'suspended') ctx.resume();
    return ctx;
  }

  function noise() {
    if (!noiseBuf) {
      var n = ctx.sampleRate * 1.2, b = ctx.createBuffer(1, n, ctx.sampleRate), d = b.getChannelData(0);
      for (var i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
      noiseBuf = b;
    }
    var s = ctx.createBufferSource();
    s.buffer = noiseBuf; s.loop = true;
    s.playbackRate.value = 0.8 + Math.random() * 0.5;
    return s;
  }

  function env(node, t0, a, peak, d) {
    var g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, t0);
    g.gain.linearRampToValueAtTime(peak, t0 + a);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + a + d);
    node.connect(g); g.connect(master);
    return g;
  }

  function tone(type, f0, f1, t0, a, peak, d, detune) {
    var o = ctx.createOscillator();
    o.type = type;
    o.frequency.setValueAtTime(f0, t0);
    o.frequency.exponentialRampToValueAtTime(Math.max(20, f1), t0 + a + d);
    if (detune) o.detune.value = detune;
    env(o, t0, a, peak, d);
    o.start(t0); o.stop(t0 + a + d + 0.05);
    return o;
  }

  function band(kind, f0, f1, q, t0, a, peak, d) {
    var s = noise(), f = ctx.createBiquadFilter();
    f.type = kind; f.Q.value = q || 1;
    f.frequency.setValueAtTime(f0, t0);
    f.frequency.exponentialRampToValueAtTime(Math.max(30, f1), t0 + a + d);
    s.connect(f);
    env(f, t0, a, peak, d);
    s.start(t0); s.stop(t0 + a + d + 0.05);
    return s;
  }

  /* ---- 10 recipes ---------------------------------------- */
  var REC = {
    thud: function (t, k) {
      tone('sine', 160 * k, 45 * k, t, 0.004, 0.85, 0.20);
      band('lowpass', 900 * k, 180 * k, 0.8, t, 0.002, 0.42, 0.11);
    },
    slash: function (t, k) {
      band('bandpass', 3500 * k, 900 * k, 3.2, t, 0.006, 0.50, 0.15);
      tone('triangle', 900 * k, 320 * k, t + 0.01, 0.003, 0.16, 0.09);
    },
    pierce: function (t, k) {
      tone('triangle', 1600 * k, 1250 * k, t, 0.003, 0.34, 0.18);
      band('highpass', 4200 * k, 2600 * k, 1.4, t, 0.001, 0.22, 0.05);
    },
    whoosh: function (t, k) {
      band('bandpass', 2200 * k, 500 * k, 2.0, t, 0.05, 0.34, 0.26);
      REC.thud(t + 0.30, k);
    },
    ward: function (t, k) {
      tone('square', 220 * k, 440 * k, t, 0.03, 0.20, 0.20);
      tone('sine', 110 * k, 110 * k, t + 0.20, 0.004, 0.42, 0.13);
    },
    bless: function (t, k) {
      [0, 3, 7].forEach(function (semi, i) {
        var f = 330 * k * Math.pow(2, semi / 12);
        tone('sine', f, f * 1.01, t + i * 0.05, 0.05, 0.26, 0.34);
      });
    },
    hex: function (t, k) {
      tone('sawtooth', 300 * k, 110 * k, t, 0.02, 0.20, 0.36, -14);
      tone('sawtooth', 302 * k, 112 * k, t, 0.02, 0.20, 0.36, +16);
      band('lowpass', 700 * k, 220 * k, 0.7, t, 0.02, 0.16, 0.32);
    },
    wet: function (t, k) {
      band('lowpass', 1400 * k, 260 * k, 1.6, t, 0.002, 0.46, 0.09);
      tone('sine', 240 * k, 90 * k, t, 0.002, 0.24, 0.08);
    },
    hiss: function (t, k) {
      band('bandpass', 2600 * k, 1500 * k, 4.5, t, 0.06, 0.24, 0.48);
    },
    crackle: function (t, k) {
      for (var i = 0; i < 5; i++) {
        var tt = t + i * 0.075 + Math.random() * 0.03;
        band('bandpass', (1800 + Math.random() * 2200) * k, 800 * k, 6, tt, 0.001, 0.26, 0.05);
      }
    }
  };

  /* Stage lowers and thickens the sound the way it grows the picture:
     stage 1 is thinner and higher, stage 3 heavier and lower. Same recipe. */
  var STAGE_K = { 1: 1.09, 2: 1.00, 3: 0.92 };

  function play(archetype, pitch, layer, stage) {
    if (muted) return false;
    if (!ac()) return false;
    var k = (PITCH[pitch] || 1) * (STAGE_K[stage] || 1), t = ctx.currentTime + 0.001;
    if (layer && REC[layer]) REC[layer](t, k * 0.9);
    var r = REC[archetype];
    if (!r) return false;
    r(t + (layer ? 0.035 : 0), k);
    return true;
  }

  var API = {
    play: play,
    unlock: function () { ac(); },
    setVolume: function (v) { vol = v; if (master) master.gain.value = v; },
    getVolume: function () { return vol; },
    mute: function (m) { muted = !!m; },
    isMuted: function () { return muted; },
    ARCHETYPES: Object.keys(REC),
    STAGE_K: STAGE_K,
    PITCH: PITCH
  };
  root.DFMC_AFX = API;
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
})(typeof window !== 'undefined' ? window : this);
