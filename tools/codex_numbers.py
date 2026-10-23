#!/usr/bin/env python
"""codex_numbers.py - the pasted-number inventory, converter and gate (C17, dfmc-client backlog, 2026-10-23).

The codex pages quoted CSV numbers by hand ("2,290 numbers pasted into HTML across 54 pages", ruling 11.9). Every
CSV edit then left a page wrong until some lane noticed. The fix: a page cell that shows a CSV value carries
`<span data-csv="file.csv#ROW#Column">value</span>` and csv-bind.js fills it from the CSV at load. The pasted text
stays as the no-JS fallback; csv-bind marks it stale when the CSV cannot be read.

This tool finds the numbers that SHOULD be bound. It reads every static <table> on every page (scripts, styles,
comments and the Changelog / Rulings log sections are masked: those numbers are history and must not move), aligns
each row to a CSV row by its first cell (a CSV key value, or a "lo-hi" range against a *_Lo/*_Hi pair) and each column
to a CSV column (header name, or >=60% of the aligned cells agreeing in value). Each aligned numeric cell is one
inventory entry: page, line, value, csv#row#column, the CSV's value, whether they match, whether it is converted.

  python tools/codex_numbers.py                 # summary: inventoried / wrong / converted / left, per page
  python tools/codex_numbers.py --list PAGE     # every entry on one page
  python tools/codex_numbers.py --convert PAGE  # wrap every bound unconverted cell in a data-csv span (writes the CSV value)
  python tools/codex_numbers.py --refresh       # rewrite every data-csv span's fallback text to the current CSV value
  python tools/codex_numbers.py --check         # the gate: fail on a dangling data-csv ref, or on a bound unconverted
                                                # cell not in tools/codex_numbers_baseline.json
  python tools/codex_numbers.py --baseline      # rewrite the baseline (the not-yet-converted rest, per page counts)
  --site DIR  the site root (default: this file's repo)

ROW is `value` (the CSV's first column), `Col=value`, or `Lo=a&Hi=b`. data-csv-fmt (optional) is a list of tokens:
x100 (multiply), dN (N decimals), g (thousands commas), % (suffix). csv-bind.js implements the same tokens.
"""
import csv, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
args = sys.argv[1:]
if '--site' in args:
    i = args.index('--site'); SITE = args[i + 1]; del args[i:i + 2]
CODEX = os.path.join(SITE, 'codex')
BASELINE = os.path.join(SITE, 'tools', 'codex_numbers_baseline.json')
# pages that are not the codex: admin / analytics / ops consoles and the legal pages
SKIP_PAGES = {'admin-backend.html', 'analytics.html', 'feedback-pipeline.html', 'settings.html', 'privacy.html',
              'terms.html', 'delete-account.html', 'dev.html', 'credits.html', 'checklist.html', 'research.html'}
NUM = re.compile(r'(?<![\w.#&-])(-?\d{1,3}(?:,\d{3})+|-?\d+)(\.\d+)?(\s?%)?(?![\w])')


def norm(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    s = s.replace('&ndash;', '-').replace('&mdash;', '-').replace('–', '-').replace('—', '-')
    s = re.sub(r'&nbsp;|&#160;', ' ', s); s = re.sub(r'&amp;', '&', s); s = re.sub(r'&[a-z]+;', '', s)
    return re.sub(r'\s+', ' ', s).strip().lower()


def hnorm(s):
    return re.sub(r'[^a-z0-9]', '', norm(s))


def fnum(s):
    try:
        return float(str(s).replace(',', '').replace('%', '').strip())
    except ValueError:
        return None


LEAD = re.compile(r'^\s*(-?\d[\d,]*(?:\.\d+)?)\s*[^\d\s.,%]')


def lead(v):
    m = LEAD.match(v or '')
    return m.group(1) if m else None


def load_csvs():
    out = {}
    for f in sorted(os.listdir(CODEX)):
        if not f.endswith('.csv'):
            continue
        with open(os.path.join(CODEX, f), encoding='utf-8-sig', newline='') as fh:
            rows = list(csv.reader(fh))
        if not rows:
            continue
        hdr = rows[0]; data = [r + [''] * (len(hdr) - len(r)) for r in rows[1:] if any(c.strip() for c in r)]
        if len(data) > 700:   # audit logs (afx_sync_audit, floor_creature_rarity): no page quotes them by row
            continue
        cols = {h: i for i, h in enumerate(hdr)}
        vidx = {}
        for h, ci in cols.items():
            d = {}
            for ri, r in enumerate(data):
                v = norm(r[ci])
                if v:
                    d.setdefault(v, set()).add(ri)
            vidx[h] = d
        numeric = [h for h in hdr if sum(1 for r in data if fnum(r[cols[h]]) is not None or lead(r[cols[h]])) >= max(1, len(data) // 2)]
        lohi = [(a, a[:-3] + '_Hi') for a in hdr if a.endswith('_Lo') and a[:-3] + '_Hi' in cols]
        out[f] = dict(hdr=hdr, cols=cols, data=data, vidx=vidx, numeric=numeric, lohi=lohi, fcache={})
    return out


def rowref(c, ri, condcols):
    """the ROW part of a data-csv ref: Col=value pairs of row ri (bare value when the one col is the first column)"""
    r = c['data'][ri]
    if len(condcols) == 1 and condcols[0] == c['hdr'][0]:
        return r[0].strip()
    return '&'.join('%s=%s' % (k, r[c['cols'][k]].strip()) for k in condcols)


def resolve(c, spec):
    """row index for a ROW spec, or None"""
    parts = spec.split('&')
    want = []
    for p in parts:
        if '=' in p and p.split('=', 1)[0] in c['cols']:
            k, v = p.split('=', 1); want.append((c['cols'][k], v))
        else:
            want.append((0, p))
    hits = [ri for ri, r in enumerate(c['data']) if all(r[ci].strip() == v.strip() for ci, v in want)]
    return hits[0] if len(hits) == 1 else None


def mask(src):
    """same-length copy with script/style/comments and the history sections blanked out"""
    m = list(src)
    def blank(a, b):
        for i in range(a, b):
            if m[i] != '\n':
                m[i] = ' '
    for x in re.finditer(r'(?is)<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->', src):
        blank(x.start(), x.end())
    for x in re.finditer(r'(?is)<h2[^>]*>\s*(changelog|rulings log|history)\b.*?</h2>', src):
        nxt = re.compile(r'(?i)<h2[\s>]').search(src, x.end())
        blank(x.start(), nxt.start() if nxt else len(src))
    return ''.join(m)


def fmt_value(v, fmt):
    toks = [t for t in fmt.split(',') if t] if fmt else []
    if 'n' in toks:
        v = lead(v) or v
    x = fnum(v)
    if x is None:
        return v
    if 'x100' in toks:
        x *= 100
    dp = None
    for t in toks:
        if re.fullmatch(r'd\d', t):
            dp = int(t[1])
    if dp is None:
        s = v.strip().rstrip('%').replace(',', '') if 'x100' not in toks else ('%d' % round(x) if abs(x - round(x)) < 1e-9 else repr(round(x, 6)))
    else:
        s = '%.*f' % (dp, x)
    if 'g' in toks:
        ip, _, fp = s.partition('.'); neg = ip.startswith('-'); ip = ip.lstrip('-')
        ip = '{:,}'.format(int(ip)) if ip.isdigit() else ip
        s = ('-' if neg else '') + ip + ('.' + fp if fp else '')
    if '%' in toks or (v.strip().endswith('%') and 'x100' not in toks):
        s += '%'
    return s


def guess_fmt(page_txt, csv_v):
    """the fmt that renders csv_v as page_txt, or None"""
    p = page_txt.strip().replace(' %', '%')
    pre = None
    if fnum(csv_v) is None:
        if not lead(csv_v):
            return None
        pre = 'n'
    if fnum(p) is None:
        return None
    pct = p.endswith('%'); grp = ',' in p.split('.')[0]
    dp = len(p.rstrip('%').split('.')[1]) if '.' in p else 0
    for mul in ([None, 'x100'] if pct else [None]):
        for d in (None, 'd%d' % dp):
            toks = [t for t in (pre, mul, d) if t]
            if grp: toks.append('g')
            if pct and not csv_v.strip().endswith('%'): toks.append('%')
            f = ','.join(toks)
            if fmt_value(csv_v, f) == p:
                return f
    return None


CELL = re.compile(r'(?is)<(t[dh])\b([^>]*)>(.*?)(?=</t[dh]>|<t[dh]\b|</tr>|<tr\b|</table>)')


def page_entries(page, csvs):
    path = os.path.join(SITE, page)
    src = open(path, encoding='utf-8').read()
    ms = mask(src)
    lines = [0] + [i + 1 for i, ch in enumerate(src) if ch == '\n']
    def lineno(off):
        lo, hi = 0, len(lines)
        while lo + 1 < hi:
            mid = (lo + hi) // 2
            if lines[mid] <= off: lo = mid
            else: hi = mid
        return lo + 1
    ents = []; dangling = []
    # converted spans anywhere in the unmasked page
    for x in re.finditer(r'data-csv="([^"]+)"(?:\s+data-csv-fmt="([^"]*)")?[^>]*>([^<]*)<', ms):
        ref, fmt, txt = x.group(1), x.group(2) or '', x.group(3)
        try:
            f, row, col = ref.split('#')
        except ValueError:
            dangling.append((lineno(x.start()), ref, 'bad ref')); continue
        c = csvs.get(f)
        ri = resolve(c, row) if c else None
        if c is None or ri is None or col not in c['cols']:
            dangling.append((lineno(x.start()), ref, 'unresolved')); continue
        cv = c['data'][ri][c['cols'][col]]
        ents.append(dict(page=page, line=lineno(x.start()), value=txt, ref=ref, fmt=fmt, csv=fmt_value(cv, fmt),
                         ok=fmt_value(cv, fmt) == txt.strip(), converted=True, off=None))
    for t in re.finditer(r'(?is)<table\b.*?</table>', ms):
        body = t.group(0); base = t.start()
        rows = []
        for r in re.finditer(r'(?is)<tr\b[^>]*>(.*?)(?=<tr\b|</table>)', body):
            cells = [(cm.group(1).lower(), cm.group(2), cm.group(3), base + r.start(1) + cm.start(3)) for cm in CELL.finditer(r.group(1))]
            if cells:
                rows.append(cells)
        if len(rows) < 2:
            continue
        hdr = None; data = []
        for cells in rows:
            if hdr is None and all(k == 'th' for k, _, _, _ in cells):
                hdr = [norm(x[2]) for x in cells]; continue
            if any('span=' in a for _, a, _, _ in cells):
                continue
            data.append(cells)
        # align: candidate lookups (csv, condition columns, per-column {table row: csv row}); then one CSV column per table column
        if len(data) < 2:
            continue
        ncol = max(len(x) for x in data)
        keys = [norm(cells[0][2]) for cells in data]
        hv = [(hdr[j] if hdr and j < len(hdr) else '') for j in range(ncol)]
        cands = []
        need = max(2, (len(data) + 1) // 2)
        for f, c in csvs.items():
            keyers = []   # (condcols, {i: set(rows)})
            for A in c['hdr']:
                hits = {}
                for i, k in enumerate(keys):
                    for kv in kvariants(k):
                        if kv in c['vidx'][A]:
                            hits[i] = c['vidx'][A][kv]; break
                if len(hits) >= need:
                    keyers.append(([A], hits))
            for lo, hi in c['lohi']:
                hits = {}
                for i, k in enumerate(keys):
                    mm = re.fullmatch(r'\D*?(\d+)\s*-\s*(\d+)\D*', k)
                    if mm:
                        s1 = c['vidx'][lo].get(mm.group(1), set()) & c['vidx'][hi].get(mm.group(2), set())
                        if s1: hits[i] = s1
                if len(hits) >= need:
                    keyers.append(([lo, hi], hits))
            if not keyers:
                continue
            smalls = [E for E in c['hdr'] if 2 <= len(c['vidx'][E]) <= 12]
            def frows(F):
                key = tuple(F)
                if key not in c['fcache']:
                    s1 = set(range(len(c['data'])))
                    for E, v in F:
                        s1 &= c['vidx'][E].get(v, set())
                    c['fcache'][key] = s1
                return c['fcache'][key]
            for condcols, hits in keyers:
                Fs = [[]] + [[(E, v)] for E in smalls if E not in condcols for v in c['vidx'][E]]
                # 1D: the row is the key (plus a filter when the key repeats)
                for F in Fs:
                    fr = frows(F); m = {}
                    for i, s1 in hits.items():
                        s2 = s1 & fr
                        if len(s2) == 1: m[i] = next(iter(s2))
                    if len(m) >= need:
                        plain = (not F and len(condcols) == 1 and len(c['vidx'][condcols[0]]) == len(c['data'])
                                 and bool(set(re.findall(r'[a-z]+', hv[0])) & set(condcols[0].lower().split('_'))))
                        cands.append((f, condcols + [E for E, _ in F], {j: m for j in range(1, ncol)}, False, plain))
                        if not F and len(m) == len(hits): break
                # 2D: the column header is a second key (grade x tier grids)
                if hdr:
                    for B in c['hdr']:
                        if B in condcols: continue
                        hb = {}
                        for j in range(1, ncol):
                            for kv in kvariants(hv[j]):
                                if kv in c['vidx'][B]:
                                    hb[j] = c['vidx'][B][kv]; break
                        if len(hb) < 2: continue
                        for F in Fs:
                            fr = frows(F); per = {}; n = 0
                            for j, sb in hb.items():
                                m = {}
                                for i, s1 in hits.items():
                                    s2 = s1 & sb & fr
                                    if len(s2) == 1: m[i] = next(iter(s2))
                                if m: per[j] = m; n += len(m)
                            if n >= 4:
                                cands.append((f, condcols + [B] + [E for E, _ in F], per, True, False))
        if not cands:
            continue
        for j in range(1, ncol):
            cells_j = {i: norm(data[i][j][2]) for i in range(len(data)) if j < len(data[i])}
            tot_num = sum(1 for t in cells_j.values() if NUM.fullmatch(t))
            if tot_num == 0:
                continue
            hname = hnorm(hv[j])
            choice = None
            ident = sum(1 for i, t in cells_j.items() if NUM.fullmatch(t) and fnum(t) is not None and
                        any(fnum(kv) == fnum(t) for kv in kvariants(keys[i]) if fnum(kv) is not None))
            if ident >= 0.8 * tot_num:   # the column repeats the row key (grade 1..10 -> 1..10): nothing to bind
                continue
            for f, conds, per, twod, plain in cands:
                m = per.get(j)
                if not m: continue
                c = csvs[f]
                for V in c['numeric']:
                    if V in conds: continue
                    good = 0; near = 0; tot = 0; same = 0; fmts = {}
                    for i, ri in m.items():
                        txt = cells_j.get(i, '')
                        if not NUM.fullmatch(txt): continue
                        tot += 1
                        r = c['data'][ri]; cv = r[c['cols'][V]]
                        cvn = fnum(cv) if fnum(cv) is not None else fnum(lead(cv) or '')
                        if cvn is not None and any(cvn == fnum(r[c['cols'][k]]) for k in conds): same += 1
                        g = guess_fmt(txt, cv)
                        if g is not None:
                            good += 1; fmts[g] = fmts.get(g, 0) + 1
                        elif is_near(txt, cv):
                            near += 1
                    if not good or same >= 0.8 * tot: continue
                    named = (not twod) and hname and hname == hnorm(V.replace('_', ' '))
                    if not (named or (good >= 3 and good >= 0.6 * tot) or (good >= 2 and good == tot)
                            or (plain and good >= 2 and good + near >= 0.5 * tot and good + near >= 4)):
                        continue
                    score = (1000 if named else 0) + good * 10 + near * 3 - len(conds) - (2 if twod else 0)
                    if choice is None or score > choice[0]:
                        choice = (score, f, conds, m, V, max(fmts, key=fmts.get))
            if not choice:
                continue
            _, f, conds, m, V, fmt = choice; c = csvs[f]
            for i, ri in m.items():
                k, a, inner, off = data[i][j]
                if 'data-csv=' in inner:
                    continue
                txt = cells_j.get(i, '')
                if not NUM.fullmatch(txt):
                    continue
                row = rowref(c, ri, conds)
                if resolve(c, row) != ri:
                    continue
                cv = c['data'][ri][c['cols'][V]]
                cf = guess_fmt(txt, cv)
                if cf is None:
                    cf = shape_fmt(txt, fmt)
                want = fmt_value(cv, cf)
                ents.append(dict(page=page, line=lineno(off), value=txt, ref='%s#%s#%s' % (f, row, V),
                                 fmt=cf, csv=want, ok=want == txt.replace(' %', '%'), converted=False, off=off, inner=inner))
    return src, ents, dangling


def is_near(txt, cv):
    a = fnum(txt); b = fnum(cv) if fnum(cv) is not None else fnum(lead(cv) or '')
    if a is None or b is None:
        return False
    for x in (b, b * 100):
        if x and abs(a - x) <= 0.35 * abs(x):
            return True
    return False


def shape_fmt(txt, colfmt):
    """the fmt a drifted cell keeps: the column's multiplier / unit-strip, the page's decimals, grouping and % sign"""
    toks = [t for t in colfmt.split(',') if t in ('n', 'x100')]
    p = txt.replace(' %', '%')
    if '.' in p:
        toks.append('d%d' % len(p.rstrip('%').split('.')[1]))
    elif 'x100' in toks:
        toks.append('d0')
    if ',' in p.split('.')[0]:
        toks.append('g')
    if p.endswith('%') and '%' in colfmt.split(','):
        toks.append('%')
    return ','.join(toks)


def kvariants(k):
    out = [k]
    k2 = re.sub(r'^(floor|f|level|lv|lvl|grade|tier|t|zone|rung|win|pen|slot)\s*(?=\d)', '', k); out.append(k2)
    if k2:
        out.append(re.split(r'[\s(/:]', k2)[0])
    k3 = re.split(r'\s[(-]|\s\d', k)[0]
    out.append(k3)
    return [x for x in dict.fromkeys(out) if x]


def pages():
    return sorted(p for p in os.listdir(SITE) if p.endswith('.html') and p not in SKIP_PAGES)


def convert(page, csvs, refresh_only=False):
    src, ents, _ = page_entries(page, csvs)
    out = src; n = 0
    if not refresh_only:
        for e in sorted([e for e in ents if not e['converted']], key=lambda e: -e['off']):
            inner = e['inner']
            # wrap the one number in the cell's text (outside any tag)
            hit = None
            for s in re.finditer(r'(?:^|>)([^<]+)', inner):
                mm = NUM.search(s.group(1))
                if mm and s.group(1).strip():
                    hit = (s.start(1) + mm.start(), s.start(1) + mm.end()); break
            if not hit:
                continue
            a, b = e['off'] + hit[0], e['off'] + hit[1]
            fa = ' data-csv-fmt="%s"' % e['fmt'] if e['fmt'] else ''
            out = out[:a] + '<span data-csv="%s"%s>%s</span>' % (e['ref'], fa, e['csv']) + out[b:]
            n += 1
    # refresh every span's fallback to the current CSV value
    def rep(x):
        ref, fmt = x.group(2), x.group(4) or ''
        f, row, col = ref.split('#'); c = csvs.get(f); ri = resolve(c, row) if c else None
        if c is None or ri is None or col not in c['cols']:
            return x.group(0)
        return x.group(1) + fmt_value(c['data'][ri][c['cols'][col]], fmt) + '<'
    out2 = re.sub(r'(<span data-csv="([^"]+)"( data-csv-fmt="([^"]*)")?>)[^<]*<', rep, out)
    if 'data-csv=' in out2 and 'csv-bind.js' not in out2:
        k = out2.find('<script src="nav.js"></script>')
        tag = '<script src="csv-bind.js"></script>'
        out2 = out2[:k] + tag + '\n' + out2[k:] if k >= 0 else out2.replace('</body>', tag + '\n</body>', 1)
    if out2 != src:
        with open(os.path.join(SITE, page), 'w', encoding='utf-8', newline='') as fh:
            fh.write(out2)
    return n, out2 != src


def main():
    csvs = load_csvs()
    if '--convert' in args:
        for p in args[args.index('--convert') + 1:]:
            n, ch = convert(p, csvs); print('%s: %d converted' % (p, n))
        return 0
    if '--refresh' in args:
        for p in pages():
            _, ch = convert(p, csvs, refresh_only=True)
            if ch: print('refreshed', p)
        return 0
    per = {}; dang = []; allents = []
    for p in pages():
        _, ents, d = page_entries(p, csvs)
        allents += ents; dang += [(p,) + x for x in d]
        per[p] = dict(n=len(ents), wrong=sum(not e['ok'] for e in ents), conv=sum(e['converted'] for e in ents),
                      left=sum(not e['converted'] for e in ents), wrong_left=sum(not e['ok'] and not e['converted'] for e in ents))
    if '--list' in args:
        pg = args[args.index('--list') + 1]
        for e in allents:
            if e['page'] == pg:
                print('%s:%d\t%s\t%s\tcsv=%s\t%s%s' % (pg, e['line'], e['value'], e['ref'], e['csv'], 'ok' if e['ok'] else 'WRONG', ' conv' if e['converted'] else ''))
        return 0
    if '--json' in args:
        print(json.dumps([{k: v for k, v in e.items() if k not in ('off', 'inner')} for e in allents], indent=1)); return 0
    left = {p: v['left'] for p, v in per.items() if v['left']}
    if '--baseline' in args:
        with open(BASELINE, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(dict(note='C17: bound-but-unconverted table numbers per page; only the count may fall. '
                                'Convert with tools/codex_numbers.py --convert PAGE, then --baseline.', left=left), fh, indent=1, sort_keys=True)
            fh.write('\n')
        print('baseline: %d pages, %d numbers' % (len(left), sum(left.values()))); return 0
    tot = {k: sum(v[k] for v in per.values()) for k in ('n', 'wrong', 'conv', 'left', 'wrong_left')}
    if '--check' in args:
        base = json.load(open(BASELINE, encoding='utf-8'))['left'] if os.path.exists(BASELINE) else {}
        bad = ['%s: %d bound numbers pasted, baseline %d (convert: tools/codex_numbers.py --convert %s)' % (p, n, base.get(p, 0), p)
               for p, n in sorted(left.items()) if n > base.get(p, 0)]
        bad += ['%s:%d dangling data-csv="%s" (%s)' % d for d in dang]
        if bad:
            print('codex_numbers: FAIL\n  ' + '\n  '.join(bad[:40])); return 1
        print('codex_numbers: PASS - %d bound, %d converted, %d left (baseline), %d dangling' % (tot['n'], tot['conv'], tot['left'], len(dang)))
        return 0
    for p, v in sorted(per.items(), key=lambda x: -x[1]['n']):
        if v['n']:
            print('%5d bound %4d wrong %4d conv %4d left  %s' % (v['n'], v['wrong'], v['conv'], v['left'], p))
    print('TOTAL inventoried %(n)d, wrong %(wrong)d, converted %(conv)d, left %(left)d (wrong among left %(wrong_left)d)' % tot)
    if dang:
        print('dangling:', len(dang))
    return 0


if __name__ == '__main__':
    sys.exit(main())
