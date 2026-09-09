/* ============================================================
   HERUMON TOWER - placeholder VFX renderer
   Taxonomy: codex/move_vfx.csv  Spec: codex/VFX_SPEC.md
   Solid opaque shapes only. No glow, no alpha wash, no blur.
   Global: window.DFMC_VFX     (also module.exports)
   ============================================================ */
(function (root) {
  'use strict';

  var DUR = { fast: 400, standard: 600, heavy: 800 };

  /* locked palette (codex/VFX_SPEC.md) */
  var BASE = {
    blue:    '#18306a', purple: '#3a1a56', crimson: '#600e12',
    green:   '#144820', red:    '#6e1212', rust:    '#7e3818',
    bone:    '#d8cfc0'
  };

  function hex2rgb(h) {
    return [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
  }
  function mix(h, t) { /* t 0..1 toward parchment white */
    var c = hex2rgb(h), w = [242, 233, 216], o = '#';
    for (var i = 0; i < 3; i++) {
      var v = Math.round(c[i] + (w[i] - c[i]) * t).toString(16);
      o += v.length < 2 ? '0' + v : v;
    }
    return o;
  }
  /* three readable tones per palette key: deep / mid / core */
  var TONE = {};
  Object.keys(BASE).forEach(function (k) {
    TONE[k] = k === 'bone'
      ? [mix(BASE[k], -0.0) , '#efe7d8', '#ffffff']
      : [BASE[k], mix(BASE[k], 0.42), mix(BASE[k], 0.78)];
  });
  TONE.bone[0] = '#8f8471';

  function rnd(seed) { var x = Math.sin(seed * 12.9898) * 43758.5453; return x - Math.floor(x); }
  function ease(p) { return 1 - Math.pow(1 - p, 3); }

  /* ---- solid primitives ---------------------------------- */
  function poly(g, pts, fill) {
    g.beginPath(); g.moveTo(pts[0][0], pts[0][1]);
    for (var i = 1; i < pts.length; i++) g.lineTo(pts[i][0], pts[i][1]);
    g.closePath(); g.fillStyle = fill; g.fill();
  }
  function shard(g, x, y, r, a, fill) {
    poly(g, [
      [x + Math.cos(a) * r, y + Math.sin(a) * r],
      [x + Math.cos(a + 2.3) * r * 0.32, y + Math.sin(a + 2.3) * r * 0.32],
      [x + Math.cos(a - 2.3) * r * 0.32, y + Math.sin(a - 2.3) * r * 0.32]
    ], fill);
  }
  function disc(g, x, y, r, fill) {
    g.beginPath(); g.arc(x, y, Math.max(0, r), 0, 6.2832); g.fillStyle = fill; g.fill();
  }
  function ring(g, x, y, r, w, fill) {
    if (r <= 0) return;
    g.beginPath(); g.arc(x, y, r, 0, 6.2832); g.arc(x, y, Math.max(0, r - w), 0, 6.2832, true);
    g.fillStyle = fill; g.fill('evenodd');
  }
  function chev(g, x, y, s, up, fill) {
    var d = up ? -1 : 1;
    poly(g, [[x, y], [x - s, y + s * 0.8 * d], [x - s * 0.55, y + s * 0.8 * d],
             [x, y + s * 0.28 * d], [x + s * 0.55, y + s * 0.8 * d], [x + s, y + s * 0.8 * d]], fill);
  }
  function crescent(g, x, y, r, a0, a1, w, fill) {
    g.beginPath(); g.arc(x, y, r, a0, a1); g.arc(x, y, Math.max(0, r - w), a1, a0, true);
    g.closePath(); g.fillStyle = fill; g.fill();
  }

  /* ---- archetypes ---------------------------------------- */
  /* each: (g, p, A, B, s, T)  p=0..1  A=source box  B=anchor box
     s=scale  T=[deep,mid,core]  boxes are {x,y,w,h} with x,y = centre */
  var FX = {

    generic_impact: function (g, p, A, B, s, T) {
      var r = 8 + 52 * ease(p) * s, k = 8;
      ring(g, B.x, B.y, r, 9 * s * (1 - p * 0.7), T[1]);
      for (var i = 0; i < k; i++) {
        var a = i / k * 6.2832 + rnd(i) * 0.6, d = r * (0.55 + rnd(i + 9) * 0.6);
        shard(g, B.x + Math.cos(a) * d, B.y + Math.sin(a) * d, (16 - 11 * p) * s, a, T[2]);
      }
      disc(g, B.x, B.y, (26 - 26 * p) * s, T[0]);
    },

    melee_slash: function (g, p, A, B, s, T) {
      var a0 = -2.5 + p * 2.6, sw = 1.5;
      crescent(g, B.x, B.y, 62 * s, a0, a0 + sw, 15 * s, T[2]);
      crescent(g, B.x, B.y, 44 * s, a0 + 0.15, a0 + sw - 0.15, 9 * s, T[1]);
      if (p > 0.5) for (var i = 0; i < 4; i++) {
        var a = a0 + sw * rnd(i);
        shard(g, B.x + Math.cos(a) * 66 * s, B.y + Math.sin(a) * 66 * s, 9 * s * (1 - p), a, T[2]);
      }
    },

    melee_crush: function (g, p, A, B, s, T) {
      var drop = p < 0.45 ? (p / 0.45) : 1, y = B.y - 70 * s + 70 * s * drop;
      poly(g, [[B.x - 26 * s, y - 34 * s], [B.x + 26 * s, y - 34 * s],
               [B.x + 16 * s, y], [B.x - 16 * s, y]], T[1]);
      if (p >= 0.45) {
        var q = (p - 0.45) / 0.55;
        ring(g, B.x, B.y + 14 * s, (10 + 60 * q) * s, 11 * s * (1 - q), T[2]);
        for (var i = 0; i < 7; i++) {
          var a = -0.3 - i / 7 * 2.5;
          shard(g, B.x + Math.cos(a) * 60 * s * q, B.y + 14 * s + Math.sin(a) * 34 * s * q,
                13 * s * (1 - q), a, T[0]);
        }
      }
    },

    charge_impact: function (g, p, A, B, s, T) {
      var dir = B.x >= A.x ? 1 : -1;
      if (p < 0.55) {
        var q = p / 0.55, x = A.x + (B.x - A.x) * q;
        poly(g, [[x + 44 * s * dir, B.y], [x - 22 * s * dir, B.y - 20 * s],
                 [x - 6 * s * dir, B.y], [x - 22 * s * dir, B.y + 20 * s]], T[1]);
      } else {
        var r = (p - 0.55) / 0.45;
        ring(g, B.x, B.y, (14 + 56 * r) * s, 13 * s * (1 - r), T[2]);
        for (var i = 0; i < 6; i++) {
          var a = i / 6 * 6.2832;
          shard(g, B.x + Math.cos(a) * 50 * s * r, B.y + Math.sin(a) * 50 * s * r, 14 * s * (1 - r), a, T[0]);
        }
      }
    },

    whip_lash: function (g, p, A, B, s, T) {
      var n = 14, pts = [], pts2 = [];
      for (var i = 0; i <= n; i++) {
        var t = i / n, ang = -2.2 + p * 3.4 + t * 1.5,
            r = 94 * s * t, w = (16 - 14 * t) * s;
        pts.push([B.x + Math.cos(ang) * r, B.y + Math.sin(ang) * r - w]);
        pts2.unshift([B.x + Math.cos(ang) * r, B.y + Math.sin(ang) * r + w]);
      }
      poly(g, pts.concat(pts2), T[2]);
    },

    pierce_strike: function (g, p, A, B, s, T) {
      var dir = B.x >= A.x ? 1 : -1, adv = -60 + 150 * ease(p);
      var x = B.x + adv * s * dir;
      poly(g, [[x + 40 * s * dir, B.y], [x, B.y - 11 * s], [x - 46 * s * dir, B.y - 6 * s],
               [x - 46 * s * dir, B.y + 6 * s], [x, B.y + 11 * s]], T[2]);
      if (p > 0.45) for (var i = 0; i < 5; i++) {
        var a = 1.2 + i * 0.5;
        shard(g, B.x + Math.cos(a) * 26 * s, B.y + Math.sin(a) * 26 * s, 10 * s * (1 - p), a, T[1]);
      }
    },

    projectile: function (g, p, A, B, s, T) {
      if (p < 0.62) {
        var q = p / 0.62, x = A.x + (B.x - A.x) * q, y = A.y + (B.y - A.y) * q - 40 * s * Math.sin(q * 3.14159);
        disc(g, x, y, 15 * s, T[2]); disc(g, x, y, 8 * s, T[0]);
        for (var i = 1; i <= 3; i++) {
          var t2 = Math.max(0, q - i * 0.06), tx = A.x + (B.x - A.x) * t2,
              ty = A.y + (B.y - A.y) * t2 - 40 * s * Math.sin(t2 * 3.14159);
          disc(g, tx, ty, (11 - i * 3) * s, T[1]);
        }
      } else {
        var r = (p - 0.62) / 0.38;
        ring(g, B.x, B.y, (12 + 48 * r) * s, 12 * s * (1 - r), T[2]);
        disc(g, B.x, B.y, 20 * s * (1 - r), T[1]);
      }
    },

    bleed_dot: function (g, p, A, B, s, T) {
      for (var i = 0; i < 11; i++) {
        var t = (p + rnd(i) * 0.7) % 1,
            x = B.x + (rnd(i + 3) - 0.5) * 76 * s,
            y = B.y - 26 * s + 88 * s * t;
        poly(g, [[x, y - 13 * s], [x + 8 * s, y + 7 * s], [x - 8 * s, y + 7 * s]], T[2]);
        disc(g, x, y + 7 * s, 7.5 * s, T[1]);
      }
    },

    poison_dot: function (g, p, A, B, s, T) {
      for (var i = 0; i < 9; i++) {
        var t = (p + rnd(i) * 0.9) % 1,
            x = B.x + (rnd(i + 5) - 0.5) * 60 * s + Math.sin(t * 6 + i) * 7 * s,
            y = B.y + 32 * s - 84 * s * t, r = (4 + rnd(i + 2) * 7) * s * (1 - t * 0.45);
        disc(g, x, y, r, i % 3 ? T[1] : T[2]);
      }
    },

    burn_dot: function (g, p, A, B, s, T) {
      for (var i = 0; i < 6; i++) {
        var ph = (p * 2 + rnd(i)) % 1, h = (34 + rnd(i + 4) * 30) * s * (0.55 + ph * 0.6),
            x = B.x + (i / 5 - 0.5) * 62 * s, y = B.y + 26 * s;
        poly(g, [[x, y - h], [x + 11 * s, y], [x - 11 * s, y]], T[1]);
        poly(g, [[x, y - h * 0.6], [x + 5 * s, y], [x - 5 * s, y]], T[2]);
      }
    },

    drain: function (g, p, A, B, s, T) {
      for (var i = 0; i < 9; i++) {
        var t = (p + i / 9) % 1,
            x = B.x + (A.x - B.x) * t, y = B.y + (A.y - B.y) * t - 46 * s * Math.sin(t * 3.14159);
        disc(g, x, y, (10 - 4 * t) * s, i % 2 ? T[2] : T[1]);
      }
    },

    heal: function (g, p, A, B, s, T) {
      for (var i = 0; i < 8; i++) {
        var t = (p + rnd(i) * 0.6) % 1, x = B.x + (rnd(i + 7) - 0.5) * 74 * s,
            y = B.y + 38 * s - 104 * s * t, k = 14 * s * (1 - t * 0.35);
        poly(g, [[x - k * 0.36, y - k], [x + k * 0.36, y - k], [x + k * 0.36, y - k * 0.36],
                 [x + k, y - k * 0.36], [x + k, y + k * 0.36], [x + k * 0.36, y + k * 0.36],
                 [x + k * 0.36, y + k], [x - k * 0.36, y + k], [x - k * 0.36, y + k * 0.36],
                 [x - k, y + k * 0.36], [x - k, y - k * 0.36], [x - k * 0.36, y - k * 0.36]], T[2]);
      }
    },

    cleanse: function (g, p, A, B, s, T) {
      var y = B.y - 60 * s + 120 * s * ease(p);
      poly(g, [[B.x - 52 * s, y], [B.x + 52 * s, y], [B.x + 40 * s, y + 13 * s], [B.x - 40 * s, y + 13 * s]], T[2]);
      ring(g, B.x, B.y, 58 * s * ease(p), 8 * s * (1 - p), T[1]);
    },

    shield_def_up: function (g, p, A, B, s, T) {
      var k = 6, r = 66 * s * (1.5 - 0.5 * ease(p));
      for (var i = 0; i < k; i++) {
        var a = i / k * 6.2832 - 1.5708, x = B.x + Math.cos(a) * r, y = B.y + Math.sin(a) * r * 0.78,
            h = 22 * s;
        poly(g, [[x, y - h], [x + h * 0.87, y - h * 0.5], [x + h * 0.87, y + h * 0.5],
                 [x, y + h], [x - h * 0.87, y + h * 0.5], [x - h * 0.87, y - h * 0.5]],
             i % 2 ? T[1] : T[2]);
      }
    },

    atk_up: function (g, p, A, B, s, T) {
      for (var i = 0; i < 5; i++) {
        var t = (p + i * 0.2) % 1;
        chev(g, B.x, B.y + 46 * s - 110 * s * t, (30 - 10 * t) * s, true, i % 2 ? T[2] : T[1]);
      }
    },

    atk_down: function (g, p, A, B, s, T) {
      for (var i = 0; i < 5; i++) {
        var t = (p + i * 0.2) % 1;
        chev(g, B.x, B.y - 56 * s + 110 * s * t, (30 - 10 * t) * s, false, i % 2 ? T[2] : T[1]);
      }
    },

    def_down: function (g, p, A, B, s, T) {
      var k = 9;
      for (var i = 0; i < k; i++) {
        var a = i / k * 6.2832 + 0.4, d = (18 + 58 * ease(p)) * s;
        shard(g, B.x + Math.cos(a) * d, B.y + Math.sin(a) * d * 0.85, (27 - 17 * p) * s, a + p * 2, i % 2 ? T[1] : T[2]);
      }
    },

    speed_up: function (g, p, A, B, s, T) {
      for (var i = 0; i < 5; i++) {
        var t = (p + rnd(i) * 0.8) % 1, y = B.y - 46 * s + i * 23 * s,
            x = B.x - 80 * s + 172 * s * t, w = 56 * s * (1 - Math.abs(t - 0.5) * 1.2);
        poly(g, [[x, y - 7 * s], [x + w, y - 3 * s], [x + w, y + 3 * s], [x, y + 7 * s]], i % 2 ? T[2] : T[1]);
      }
    },

    speed_down: function (g, p, A, B, s, T) {
      var y = B.y - 74 * s + 108 * s * ease(p), w = 26 * s;
      poly(g, [[B.x - w, y - w * 0.7], [B.x + w, y - w * 0.7], [B.x + w * 0.72, y + w * 0.8],
               [B.x - w * 0.72, y + w * 0.8]], T[1]);
      poly(g, [[B.x - w * 0.34, y - w * 1.15], [B.x + w * 0.34, y - w * 1.15],
               [B.x + w * 0.34, y - w * 0.7], [B.x - w * 0.34, y - w * 0.7]], T[2]);
      if (p > 0.82) ring(g, B.x, B.y + 30 * s, 46 * s * (p - 0.82) / 0.18, 7 * s, T[2]);
    },

    curse: function (g, p, A, B, s, T) {
      var r = 70 * s * (1 - 0.45 * ease(p)), k = 5;
      ring(g, B.x, B.y, r, 7 * s, T[1]);
      for (var i = 0; i < k; i++) {
        var a = i / k * 6.2832 + p * 2.4;
        shard(g, B.x + Math.cos(a) * r, B.y + Math.sin(a) * r, 15 * s, a + 1.57, T[2]);
      }
      if (p > 0.6) disc(g, B.x, B.y, 26 * s * (p - 0.6) / 0.4, T[0]);
    }
  };

  /* ---- engine -------------------------------------------- */
  var live = [];

  function boxOf(anchor, A, B) { return anchor === 'self' ? A : B; }

  function spawn(o) {
    var col = TONE[o.color] || TONE.bone,
        dur = DUR[o.duration] || DUR.standard,
        s = o.scale || 1;
    if (o.layer === 'impact') {
      live.push({ fn: FX.generic_impact, t0: performance.now(), dur: dur, T: TONE.bone,
                  A: o.from, B: o.to, anchor: 'target', s: s * 0.8 });
    }
    live.push({ fn: FX[o.archetype] || FX.generic_impact, t0: performance.now(),
                dur: dur, T: col, A: o.from, B: o.to, anchor: o.anchor || 'target', s: s });
  }

  function render(g, now) {
    for (var i = live.length - 1; i >= 0; i--) {
      var e = live[i], p = (now - e.t0) / e.dur;
      if (p >= 1) { live.splice(i, 1); continue; }
      var tgt = boxOf(e.anchor, e.A, e.B);
      var anchored = e.anchor === 'ground' ? { x: tgt.x, y: tgt.y + tgt.h * 0.42 } : tgt;
      g.save();
      e.fn(g, Math.max(0, p), e.A, anchored, e.s, e.T);
      g.restore();
    }
    return live.length;
  }

  function clear() { live.length = 0; }

  var API = { spawn: spawn, render: render, clear: clear, DUR: DUR, TONE: TONE,
              PALETTE: BASE, ARCHETYPES: Object.keys(FX), busy: function () { return live.length; } };
  root.DFMC_VFX = API;
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
})(typeof window !== 'undefined' ? window : this);
