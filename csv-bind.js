/* csv-bind.js - the codex pages read their numbers from the CSVs (C17, 2026-10-23).
 *
 * A number a page quotes from a codex CSV is written
 *     <span data-csv="file.csv#ROW#Column" data-csv-fmt="g">1,365</span>
 * and this script replaces the pasted text with the CSV's current value at load. ROW is the value of the CSV's
 * first column, or Col=value pairs joined by & (Floor_Lo=110&Grade=Epic). data-csv-fmt tokens: n (the leading
 * number of a "2 Scrap" cell), x100 (multiply), dN (N decimals), g (thousands commas), % (suffix).
 * The pasted text is the fallback: when the CSV cannot be read, or the row is gone, the span keeps it and is
 * marked .csv-stale with a title saying so. tools/codex_numbers.py is the inventory, converter and gate, and
 * implements the same format tokens.
 * window.csvBind(root) re-binds spans a page renders later.
 */
(function () {
  var cache = {};
  function parse(text) {
    var rows = [], row = [], f = '', q = false, i, ch;
    text = text.replace(/^﻿/, '');
    for (i = 0; i < text.length; i++) {
      ch = text[i];
      if (q) {
        if (ch === '"') { if (text[i + 1] === '"') { f += '"'; i++; } else q = false; }
        else f += ch;
      } else if (ch === '"') q = true;
      else if (ch === ',') { row.push(f); f = ''; }
      else if (ch === '\n' || ch === '\r') {
        if (ch === '\r' && text[i + 1] === '\n') i++;
        row.push(f); f = ''; if (row.some(function (c) { return c.trim(); })) rows.push(row); row = [];
      } else f += ch;
    }
    row.push(f); if (row.some(function (c) { return c.trim(); })) rows.push(row);
    return { hdr: rows[0] || [], data: rows.slice(1) };
  }
  function load(file) {
    if (!cache[file]) {
      cache[file] = fetch('codex/' + file + '?t=' + Date.now(), { cache: 'no-store' })
        .then(function (r) { if (!r.ok) throw new Error(file + ' ' + r.status); return r.text(); })
        .then(parse);
    }
    return cache[file];
  }
  function lead(v) { var m = /^\s*(-?\d[\d,]*(?:\.\d+)?)\s*[^\d\s.,%]/.exec(v || ''); return m ? m[1] : null; }
  function num(v) { var s = String(v).replace(/,/g, '').replace(/%/g, '').trim(); return s !== '' && isFinite(+s) ? +s : null; }
  function fmt(v, spec) {
    var toks = spec ? spec.split(',').filter(Boolean) : [], dp = null, x, s, i;
    if (toks.indexOf('n') >= 0) v = lead(v) || v;
    x = num(v);
    if (x === null) return v;
    if (toks.indexOf('x100') >= 0) x *= 100;
    for (i = 0; i < toks.length; i++) if (/^d\d$/.test(toks[i])) dp = +toks[i][1];
    if (dp === null) {
      s = toks.indexOf('x100') < 0 ? String(v).trim().replace(/%$/, '').replace(/,/g, '')
        : (Math.abs(x - Math.round(x)) < 1e-9 ? String(Math.round(x)) : String(+x.toFixed(6)));
    } else s = x.toFixed(dp);
    if (toks.indexOf('g') >= 0) {
      var parts = s.split('.'), neg = parts[0][0] === '-', ip = parts[0].replace('-', '');
      if (/^\d+$/.test(ip)) ip = ip.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
      s = (neg ? '-' : '') + ip + (parts[1] ? '.' + parts[1] : '');
    }
    if (toks.indexOf('%') >= 0 || (/%\s*$/.test(v) && toks.indexOf('x100') < 0)) s += '%';
    return s;
  }
  function cell(t, row, col) {
    var ci = t.hdr.indexOf(col);
    if (ci < 0) return null;
    var want = row.split('&').map(function (p) {
      var k = p.indexOf('=');
      if (k > 0 && t.hdr.indexOf(p.slice(0, k)) >= 0) return [t.hdr.indexOf(p.slice(0, k)), p.slice(k + 1)];
      return [0, p];
    });
    var hits = t.data.filter(function (r) {
      return want.every(function (w) { return (r[w[0]] || '').trim() === w[1].trim(); });
    });
    return hits.length === 1 ? (hits[0][ci] || '') : null;
  }
  function stale(el, why) {
    el.classList.add('csv-stale');
    el.title = 'pasted value - ' + why + ' (' + el.getAttribute('data-csv') + ')';
  }
  function bind(root) {
    var els = (root || document).querySelectorAll('[data-csv]');
    return Promise.all(Array.prototype.map.call(els, function (el) {
      var ref = el.getAttribute('data-csv').split('#');
      if (ref.length !== 3) { stale(el, 'bad reference'); return null; }
      return load(ref[0]).then(function (t) {
        var v = cell(t, ref[1], ref[2]);
        if (v === null) { stale(el, 'row or column not in ' + ref[0]); return; }
        el.textContent = fmt(v, el.getAttribute('data-csv-fmt') || '');
        el.classList.remove('csv-stale'); el.classList.add('csv-live');
        el.title = 'from codex/' + ref[0];
      }, function () { stale(el, 'codex/' + ref[0] + ' could not be read'); });
    }));
  }
  var st = document.createElement('style');
  st.textContent = '.csv-stale{text-decoration:underline dotted #c0563f;cursor:help}';
  (document.head || document.documentElement).appendChild(st);
  window.csvBind = bind;
  window.csvBindFmt = fmt;
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { bind(); });
  else bind();
})();
