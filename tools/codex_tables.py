#!/usr/bin/env python
"""codex_tables.py - the codex's COMPUTED tables, generated from the CSVs (C17 part 2, dfmc-client lane c17-gen, 2026-10-23).

csv-bind.js (part 1) binds a number a page copies from ONE CSV cell. Most of the site's numbers are not copies: they
are a formula over the CSVs (an implicit grid is round(coef x T x GF) with the grade-step floor, a levelling row is
XP_To_Next over the expected XP of an on-level battle, a cumulative grading cost is the sum of cost / success). Those
were computed once, pasted, and went wrong when a CSV moved (index.html's levelling table still divided the C1 curve
by the retired "10 x zone level" XP per battle). This tool computes each such table with the SAME formula the game
runs - every generator below cites the engine file:line it ports - and writes it between markers on its page:

    <!-- gen:NAME -->  ...generated table...  <!-- /gen:NAME -->

Cells that ARE a single CSV cell are still emitted as data-csv spans, so csv-bind.js keeps them live and
codex_numbers.py keeps checking their references. Only the computed cells are plain text, and this gate owns them.

  python tools/codex_tables.py              # summary: every block, ok / DIFFERS / no markers, numbers covered
  python tools/codex_tables.py --write [N]  # regenerate every block (or the blocks whose name or page is N)
  python tools/codex_tables.py --check      # the gate: exit 1 when a page's block differs from what the CSVs give,
                                            # or a generator's markers are missing from its page
  python tools/codex_tables.py --diff N     # the numbers that would change in block N (old -> new)
  --site DIR    the site root (default: this file's repo)
  --client DIR  the dfmc-client checkout the engine constants are read from (default $DFMC_CLIENT, then
                E:/Herumon-Tower/dfmc-client, then ../dfmc-client). A generator that needs it and cannot find it is
                SKIPPED by --check (and says so) - never guessed.

Engine constants are READ from the client, never typed here: the enemy level offsets from src/worker.js deriveSlot,
the XP penalty from src/tables.json, the battles/hour from tools/sim_econ.mjs.
"""
import csv, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
args = sys.argv[1:]


def _opt(name):
    global args
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
    return None


SITE = _opt('--site') or SITE
CLIENT = _opt('--client')
CODEX = os.path.join(SITE, 'codex')
if not CLIENT:
    for c in [os.environ.get('DFMC_CLIENT'), 'E:/Herumon-Tower/dfmc-client', os.path.join(SITE, '..', 'dfmc-client')]:
        if c and os.path.isfile(os.path.join(c, 'src', 'worker.js')):
            CLIENT = c; break


class NeedClient(Exception):
    pass


_csv = {}


def rows(f):
    if f not in _csv:
        with open(os.path.join(CODEX, f), encoding='utf-8-sig', newline='') as fh:
            _csv[f] = [r for r in csv.DictReader(fh) if any((v or '').strip() for v in r.values())]
    return _csv[f]


def client_file(rel):
    if not CLIENT or not os.path.isfile(os.path.join(CLIENT, rel)):
        raise NeedClient(rel)
    return open(os.path.join(CLIENT, rel), encoding='utf-8').read()


def jsround(x):          # Math.round: half up (Python's round() is banker's)
    return math.floor(x + 0.5)


def fx(x, d):            # JS toFixed on the decimal value (half up), not binary-float rounding
    return '%.*f' % (d, math.floor(x * 10 ** d + 0.5 + 1e-9) / 10 ** d)


def g(n):                # thousands commas
    return '{:,}'.format(int(n))


def span(ref, text, fmt=None):
    return '<span data-csv="%s"%s>%s</span>' % (ref, ' data-csv-fmt="%s"' % fmt if fmt else '', text)


GRADE_COL = {'Worn': '#c2ae8b', 'Common': '#c2ae8b', 'Uncommon': '#1eff00', 'Rare': '#0070dd', 'Epic': '#a335ee',
             'Legendary': '#ff8000', 'Abyssal': '#e5393f', 'Divine': '#00ffe0', 'Primordial': '#ff44cc', 'Void': '#a855f7'}


def grades():
    """grade_ladder.csv in Order, with GF. The engine's GF is 1 + 0.12 x order (src/power.js:170, play/app.js itemBase);
    the CSV column is what the server fold and the sims read - if the two ever disagree this refuses to print."""
    out = sorted(rows('grade_ladder.csv'), key=lambda r: int(r['Order']))
    for r in out:
        if abs(float(r['GF']) - (1 + 0.12 * int(r['Order']))) > 1e-9:
            raise ValueError('grade_ladder.csv GF %s for %s is not the engine 1+0.12x%s' % (r['GF'], r['Grade'], r['Order']))
    return out


# ------------------------------------------------------------------------------------------------- XP
def lvl_off():
    """src/worker.js deriveSlot: `const OFF = [[-3,3],[-2,7],...]` - the enemy level offset distribution (percent)."""
    m = re.search(r'const OFF = (\[\[[-\d, \[\]]+\]\]);', client_file('src/worker.js'))
    if not m:
        raise ValueError('src/worker.js: deriveSlot OFF table not found')
    return json.loads(m.group(1))


def battles_per_hour():
    m = re.search(r'export const BATTLES_PER_HOUR = (\d+)', client_file('tools/sim_econ.mjs'))
    return int(m.group(1))


def xp_penalty():
    return json.loads(client_file('src/tables.json'))['xp_penalty']


def xp_on_level(L):
    """Expected XP of one wild battle on floor L for a class at level L, as the server pays it:
    3 enemies (the slot + 2 extras, src/worker.js deriveExtras), each rolls its tier on encounter_weights.csv[floor]
    (deriveSlot, Weight_C..SSR) and its level floor+offset on OFF clamped 1..100 (deriveSlot), and pays
    XPCurve.csv XP_Kill_<tier>[level] (the conclusion loop, src/worker.js `const base = (TABLES.xp_kill[lvl]...`).
    On-level every enemy is within 3 levels, inside both penalty graces, so class XP = account XP here."""
    kill = {int(r['Level']): r for r in rows('XPCurve.csv')}
    enc = {int(r['Floor']): r for r in rows('encounter_weights.csv')}
    tiers = ['C', 'UC', 'R', 'SR', 'SSR']
    # a boss floor (10, 20, ...) has no wild spawns (all-zero weights): use the nearest wild floor below it
    F = min(L, max(enc))
    while F > 1 and not sum(float(enc[F]['Weight_' + t] or 0) for t in tiers):
        F -= 1
    wt = [float(enc[F]['Weight_' + t] or 0) for t in tiers]; tw = sum(wt) or 1.0
    xp = 0.0
    for ti, t in enumerate(tiers):
        for off, pct in lvl_off():
            l = max(1, min(100, L + off))
            xp += 3.0 * wt[ti] / tw * pct / 100.0 * float(kill[l]['XP_Kill_' + t] or 0)
    return xp


def battles_for_level(L):
    """battles to go from level L to L+1 on-level: XP_To_Next / expected XP per battle, rounded UP (whole battles)."""
    need = float({int(r['Level']): r for r in rows('XPCurve.csv')}[L]['XP_To_Next'] or 0)
    return int(math.ceil(need / xp_on_level(L))) if need else 0


def gen_xp_reference():
    out = ['<table>', '      <tr><th>Level</th><th>XP required</th><th>XP/battle (expected, on-level)</th><th>Battles (on-level)</th></tr>']
    cur = {int(r['Level']): r for r in rows('XPCurve.csv')}
    for L in (1, 10, 20, 30, 40, 50, 60, 66, 70, 80, 90, 99):
        need = int(cur[L]['XP_To_Next'])
        out.append('      <tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            L, span('XPCurve.csv#%d#XP_To_Next' % L, g(need), 'g' if need >= 1000 else None),
            g(jsround(xp_on_level(L))), g(battles_for_level(L))))
    out.append('    </table>')
    return '\n'.join(out)


def gen_xp_zones():
    bph = battles_per_hour()
    zone = {int(r['Floor']): r['Zone'] for r in rows('floors.csv')}
    out = ['<table>', '      <tr><th>Zone (10 floors each)</th><th>Levels</th><th>Battles</th><th>Zone time</th><th>Cumulative</th></tr>']
    cum = 0.0
    for z in range(1, 11):
        lo, hi = 10 * z - 9, 10 * z
        b = sum(battles_for_level(L) for L in range(lo, min(hi, 99) + 1))
        h = b / bph; cum += h
        out.append('      <tr><td>Zone %d &mdash; %s</td><td>%d&ndash;%d</td><td>%s</td><td>%.1fh</td><td>%.1fh</td></tr>'
                   % (z, zone[lo], lo, hi, g(b), h, cum))
    out.append('    </table>')
    out.append('    <p class="gen-note">Battles = the sum of the reference table&rsquo;s per-level count for each level of the zone '
               '(on-level, wild battles); hours at %d battles/h (dfmc-client <code>tools/sim_econ.mjs</code> BATTLES_PER_HOUR). '
               'Generated by <code>tools/codex_tables.py</code>.</p>' % bph)
    return '\n'.join(out)


def gen_xp_penalty():
    """system-xp.html: src/worker.js xpPenalty(diff), diff = enemy level - class level, on tables.json xp_penalty:
    linear from 0 at the grace to `floor` at `full`, either side."""
    P = xp_penalty()

    def pen(diff):
        if diff >= 0:
            if diff <= P['up_grace']: return 0.0
            if diff >= P['up_full']: return P['floor']
            return P['floor'] * (diff - P['up_grace']) / (P['up_full'] - P['up_grace'])
        d = -diff
        if d <= P['down_grace']: return 0.0
        if d >= P['down_full']: return P['floor']
        return P['floor'] * (d - P['down_grace']) / (P['down_full'] - P['down_grace'])
    faint = ' <span style="color:var(--ink-faint)">(%s)</span>'
    rws = [('On-level, or up to %d above / %d below the floor' % (P['down_grace'], P['up_grace']), 0),
           ('5 levels above the floor', -5), ('8 levels above the floor' + faint % 'measured, reference account', -8),
           ('14 levels above the floor', -14), ('19 levels above the floor', -19),
           ('%d+ levels above the floor' % P['down_full'], -P['down_full']),
           ('19 levels below the floor' + faint % 'measured, floors 97&ndash;99', 19),
           ('%d+ levels below the floor' % P['up_full'], P['up_full'])]
    out = ['  <table>', '    <tr><th>Gap</th><th>Level penalty</th><th>XP retained</th><th>Battles per level</th></tr>']
    for label, diff in rws:
        p = pen(diff); keep = 1 - p
        out.append('    <tr><td class="lbl">%s</td><td>%s</td><td>%s</td><td>&times;%s</td></tr>' % (
            label, '0' if p == 0 else fx(p, 3), '100%' if p == 0 else fx(keep * 100, 1) + '%',
            '1.00 (the table)' if p == 0 else fx(1 / keep, 1 if 1 / keep >= 10 else 2)))
    out.append('  </table>')
    return '\n'.join(out)


# ------------------------------------------------------------------------------------------------- gear grids
def item(name):
    for r in rows('items.csv'):
        if r['Name'] == name:
            return r
    raise KeyError('items.csv has no item %r' % name)


def item_base(name, T, gi):
    """play/app.js:7152 itemBase / src/power.js:196-204: the coefficient is the item's own Effect `N x T x GF`;
    round(N x T x (1 + 0.12 j)) cascading up from Worn with the grade-step floor (each grade >= the previous + 1)."""
    m = re.search(r'(\d+(?:\.\d+)?)\s*[\u00d7x]\s*T\s*[\u00d7x]\s*GF', item(name)['Effect'], re.I)
    if not m:
        raise ValueError('items.csv %s: no N x T x GF in Effect' % name)
    c = float(m.group(1)); v = 0
    for j in range(gi + 1):
        raw = jsround(c * T * float(grades()[j]['GF']))
        v = max(raw, v + 1) if j else raw
    return v


def rune_pct(name, T, gi):
    """play/app.js:7142 runePct: the item's own Effect `a% + b% x (g-1) + c% x T`, gi = grade order (Worn 0), toFixed(1)."""
    m = re.search(r'([\d.]+)%\s*\+\s*([\d.]+)%\s*[\u00d7x]\s*\(g\s*[\u2212-]\s*1\)\s*\+\s*([\d.]+)%\s*[\u00d7x]\s*T',
                  item(name)['Effect'], re.I)
    if not m:
        raise ValueError('items.csv %s: no rune curve in Effect' % name)
    return '%.1f%%' % (float(m.group(1)) + float(m.group(2)) * gi + float(m.group(3)) * T)


def grid(fn, sub):
    th = ''.join('<th>T%d%s</th>' % (T, '<br><span style="font-weight:400;font-size:10px;color:#8a7a5e">%d–%d</span>'
                                          % (10 * T - 9, 10 * T) if sub else '') for T in range(1, 11))
    out = "<div class='scroll'><table><tr><th>Grade \\ Tier</th>" + th + '</tr>'
    for gi, gr in enumerate(grades()):
        out += '<tr><td style="color:%s;white-space:nowrap">%s</td>' % (GRADE_COL.get(gr['Grade'], '#c2ae8b'), gr['Grade'])
        out += ''.join('<td style="text-align:center">%s</td>' % fn(T, gi) for T in range(1, 11)) + '</tr>'
    return out + '</table></div>'


def flat_grid(name, sub=True):
    return lambda: grid(lambda T, gi: item_base(name, T, gi), sub)


def rune_grid(name):
    return lambda: grid(lambda T, gi: rune_pct(name, T, gi), True)


# ------------------------------------------------------------------------------------------------- grading
def gen_grading(style):
    """grading.csv at T10: Gear (Scrap) and Gem (Dust - the enhancement families share one ladder). Expected spend per
    step = Cost / Success (no pity, failure consumes the currency, tools/statmodel.py Grading.ladder); cumulative =
    the running sum from Worn, rounded once at the end."""
    G = {(r['Category'], r['To_Grade']): r for r in rows('grading.csv') if r['Tier'] == '10'}
    up = style == 'upgrading'
    out = ['<table>' if not up else '  <table>']
    out.append(('    <tr><th>Target grade</th><th class="pct">Success</th><th>Gear @T10 (Scrap/try)</th><th>Gear cumulative expected @T10</th>'
                '<th>Enh. @T10 (material/try)</th><th>Enh. cumulative expected @T10</th></tr>') if up else
               ('<tr><th>Into grade</th><th>Success</th><th>Gear cost (Scrap) @T10</th><th>Gear expected cumulative</th>'
                '<th>Enhancement cost (material) @T10</th><th>Enh. expected cumulative</th></tr>'))
    cg = ce = 0.0
    for gr in grades()[1:]:
        to = gr['Grade']; rg, re_ = G[('Gear', to)], G[('Gem', to)]
        ng, ne = float(rg['Cost'].split()[0]), float(re_['Cost'].split()[0])
        cg += ng / (float(rg['Success_Pct']) / 100); ce += ne / (float(re_['Success_Pct']) / 100)
        sp = rg['Success_Pct']
        lab = ('<td style="color:%s">%s</td>' % (GRADE_COL[to], to)) if up and to not in ('Worn', 'Common') else '<td>%s</td>' % to
        cells = [span('grading.csv#To_Grade=%s&Category=Gear&Tier=10#Success_Pct' % to, sp + '%', '%'),
                 span('grading.csv#To_Grade=%s&Category=Gear&Tier=10#Cost' % to, g(ng), 'n'), g(jsround(cg)),
                 span('grading.csv#To_Grade=%s&Category=Gem&Tier=10#Cost' % to, g(ne), 'n'), g(jsround(ce))]
        if up:
            out.append('    <tr>%s<td class="pct">%s</td>%s</tr>' % (lab, cells[0], ''.join('<td>%s</td>' % c for c in cells[1:])))
        else:
            out.append('<tr>%s%s</tr>' % (lab, ''.join('<td>%s</td>' % c for c in cells)))
    out.append('  </table>' if up else '</table>')
    return ('\n' if up else '').join(out)


# ------------------------------------------------------------------------------------------------- registry
GENS = [
    # (name, page, generator)
    ('xp-reference', 'index.html', gen_xp_reference),
    ('xp-zones', 'index.html', gen_xp_zones),
    ('mainhand-grid', 'index.html', flat_grid('Arming Sword', sub=False)),
    ('st-mainhand-grid', 'stat-tables.html', flat_grid('Arming Sword')),
    ('st-armour-grid', 'stat-tables.html', flat_grid('Cowl')),
    ('st-signet-grid', 'stat-tables.html', flat_grid('Crude Signet')),
    ('st-relic-grid', 'stat-tables.html', flat_grid('Crude Relic')),
    ('st-fang-grid', 'stat-tables.html', flat_grid('Crude Fang')),
    ('st-gem-grid', 'stat-tables.html', flat_grid('Rough Garnet')),
    ('st-rune-grid', 'stat-tables.html', rune_grid('Faded Rune of Ruin')),
    ('st-grading', 'stat-tables.html', lambda: gen_grading('stat')),
    ('up-grading', 'upgrading.html', lambda: gen_grading('upgrading')),
    ('xp-penalty', 'system-xp.html', gen_xp_penalty),
]

NUMRE = re.compile(r'-?\d[\d,]*(?:\.\d+)?')


def numbers(html):
    txt = re.sub(r'<[^>]+>', ' ', re.sub(r'<th.*?</th>', ' ', html, flags=re.S))
    return [x.replace(',', '') for x in NUMRE.findall(txt)]


def block_re(name):
    return re.compile(r'(<!-- gen:%s -->)(.*?)(<!-- /gen:%s -->)' % (re.escape(name), re.escape(name)), re.S)


def run(mode, sel=None):
    pages, bad, cov, wrong, skipped, done = {}, [], 0, 0, [], 0
    for name, page, fn in GENS:
        if sel and sel not in (name, page):
            continue
        path = os.path.join(SITE, page)
        if page not in pages:
            pages[page] = open(path, encoding='utf-8').read()
        src = pages[page]
        m = block_re(name).search(src)
        if not m:
            bad.append('%s: no <!-- gen:%s --> markers' % (page, name)); print('  NO MARKERS  %-18s %s' % (name, page)); continue
        try:
            new = fn()
        except NeedClient as e:
            skipped.append(name); print('  SKIPPED     %-18s %s (needs the dfmc-client checkout: %s)' % (name, page, e)); continue
        old = m.group(2).strip('\n')
        on, nn = numbers(old), numbers(new)
        diff = sum(1 for a, b in zip(on, nn) if a != b) + abs(len(on) - len(nn))
        cov += len(nn); done += 1
        if old.strip() == new.strip():
            print('  ok          %-18s %-18s %4d numbers' % (name, page, len(nn)))
            continue
        wrong += diff
        print('  DIFFERS     %-18s %-18s %4d numbers, %d differ' % (name, page, len(nn), diff))
        if mode == 'diff':
            for i, (a, b) in enumerate(zip(on, nn)):
                if a != b: print('      #%d %s -> %s' % (i, a, b))
        if mode == 'write':
            pages[page] = src[:m.start(2)] + '\n' + new + '\n' + src[m.end(2):]
        else:
            bad.append('%s: block %s differs from the CSVs (%d numbers) - python tools/codex_tables.py --write %s' % (page, name, diff, name))
    if mode == 'write':
        for page, src in pages.items():
            with open(os.path.join(SITE, page), 'w', encoding='utf-8', newline='') as fh:
                fh.write(src)
    print('TABLES %d generated, %d numbers covered, %d %s, %d skipped' % (
        done, cov, wrong, 'rewritten' if mode == 'write' else 'differ', len(skipped)))
    return bad


def main():
    if '--write' in args:
        i = args.index('--write'); sel = args[i + 1] if len(args) > i + 1 else None
        run('write', sel); return 0
    if '--diff' in args:
        run('diff', args[args.index('--diff') + 1]); return 0
    bad = run('check')
    if '--check' in args:
        for b in bad:
            print('FAIL ' + b)
        print('RESULT codex_tables: %s' % ('FAIL (%d)' % len(bad) if bad else 'ok'))
        return 1 if bad else 0
    return 0


if __name__ == '__main__':
    sys.exit(main())
