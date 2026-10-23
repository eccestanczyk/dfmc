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

Part 3 (lane c17-gen-2, 2026-10-23) adds the trader tables (src/trader.js acquisitionPerBattle IMPORTED under node on
tools/sim_econ.mjs loadTables), the creature base stats (src/power.js coreOf/axisMult/hpFor lifted and run under node),
breeding, mutants (src/worker.js MUTANT_CHANCE and the two Codex-bonus caps), the stat-tables pools, income and quality
row, the soul-grading ladder and the prose figures that restate them.

Part 4 (lane a8-s5-c17-tail, 2026-10-23) adds the GDD's codex-file row counts, the class ultimates (ultimates.csv, on index
and classes), the move budget, Ichor, advancement and level bands, zones, encounter weights, the XP formulas and player
level, soul strength (play/app.js SOUL_STAGE_MULT), the PvP timers (src/tables.json pvp_live, src/battle_round.js
rampMult), the portal-streak table and every sentence that still restated the retired ~30 battles/h.

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


# ------------------------------------------------------------------------------------------------- engine via node
_node = {}


def node_json(key, js):
    """run an ES-module snippet under node against the client checkout and return its JSON (the engine's own code,
    imported or lifted verbatim - never re-typed). `js` console.logs one JSON line; %CLIENT% / %CODEX% are substituted."""
    if key not in _node:
        if not CLIENT:
            raise NeedClient('node: ' + key)
        import subprocess
        src = js.replace('%CLIENT%', CLIENT.replace('\\', '/')).replace('%CODEX%', CODEX.replace('\\', '/'))
        r = subprocess.run(['node', '--input-type=module', '-e', src], capture_output=True, text=True, encoding='utf-8')
        if r.returncode != 0:
            raise RuntimeError('node %s failed: %s' % (key, r.stderr[-600:]))
        _node[key] = json.loads(r.stdout.strip().splitlines()[-1])
    return _node[key]


ACQ_FLOORS = [1, 30, 60, 90, 99, 100, 101, 119, 120]


def acq(F):
    """src/trader.js acquisitionPerBattle(T, F) on tools/sim_econ.mjs loadTables(codex) - the trader's own model, imported."""
    a = node_json('acq', "import {loadTables} from 'file:///%CLIENT%/tools/sim_econ.mjs';"
                         "import {acquisitionPerBattle, TRADER_PREMIUM} from 'file:///%CLIENT%/src/trader.js';"
                         "const T = loadTables('%CODEX%'); const o = {premium: TRADER_PREMIUM};"
                         + "[%s].forEach(f => { o[f] = acquisitionPerBattle(T, f); });" % ','.join(map(str, ACQ_FLOORS))
                         + "console.log(JSON.stringify(o));")
    return a['premium'] if F == 'premium' else a[str(F)]


CUR = ['Scrap', 'Ichor', 'Dust', 'Essence', 'Ink']


def s3(x):                # three significant figures (the trader page's convention); whole numbers from 100
    if x >= 100:
        return g(jsround(x))
    d = max(0, 2 - int(math.floor(math.log10(abs(x))))) if x else 0
    return fx(x, d)


def ref_floor():
    """dfmc-client tools/statmodel.py TIER_FLOOR[10] - where the T10 grading hours are priced."""
    return int(re.search(r'TIER_FLOOR = \{[^}]*10: (\d+)\}', client_file('tools/statmodel.py')).group(1))


def gen_trader_ref():
    bph = battles_per_hour()
    a, b = acq(99), acq(119)
    out = ['<table>', '    <tr><th>Currency</th><th>Floor %d: per battle</th><th>per hour</th><th>weight (Ichor = 1)</th>'
           '<th>Floor %d: per battle</th><th>per hour</th><th>weight (Ichor = 1)</th></tr>' % (a['floor'], b['floor'])]
    for c in CUR:
        cells = []
        for x in (a, b):
            cells += [s3(x[c]), g(jsround(x[c] * bph)), '1' if c == 'Ichor' else s3(x['Ichor'] / x[c])]
        out.append('    <tr><td>%s</td>%s</tr>' % (c, ''.join('<td>%s</td>' % v for v in cells)))
    out.append('  </table>')
    out.append('  <p class="gen-note">Per hour at %d battles/h (dfmc-client <code>tools/sim_econ.mjs</code> BATTLES_PER_HOUR). '
               'Every cell is <code>acquisitionPerBattle</code> (<code>src/trader.js</code>) run under node on the current codex '
               'by <code>tools/codex_tables.py</code>.</p>' % bph)
    return '\n'.join(out)


def gen_trader_matrix(F):
    def f():
        a = acq(F)
        out = ['<table>', '    <tr><th></th>%s</tr>' % ''.join('<th>%s</th>' % c for c in CUR)]
        for r in CUR:
            out.append('    <tr><td>%s</td>%s</tr>' % (r, ''.join('<td>%s</td>' % ('&mdash;' if r == c else s3(a[r] / a[c])) for c in CUR)))
        out.append('  </table>')
        return '\n'.join(out)
    return f


def gen_trader_moves():
    a, b = acq(99), acq(119)
    w = lambda x, c: x['Ichor'] / x[c]
    return ('<p>What moves between the two: the Apex band&rsquo;s drop grades push Scrap up %s&times; per battle (floor %d gear '
            'dismantles at the 91&ndash;100 band&rsquo;s weights; the Apex band starts at Rare), Ichor %s&times; (Apex spawn mix and egg '
            'dismantles; the level term caps at 100), the enhancement currencies %s&times;. So Scrap is worth %s Ichor of time at %d and '
            '%s at %d; Dust, Essence and Ink sit at %s / %s / %s Ichor at %d and %s / %s / %s at %d; Dust and Ink are always 1:1 and '
            'Essence is ~%d%% cheaper (tags dismantle to Essence as well as Scrap).</p>') % (
        fx(b['Scrap'] / a['Scrap'], 1), a['floor'], fx(b['Ichor'] / a['Ichor'], 1), fx(b['Dust'] / a['Dust'], 1),
        fx(w(a, 'Scrap'), 1), a['floor'], fx(w(b, 'Scrap'), 1), b['floor'],
        g(jsround(w(a, 'Dust'))), g(jsround(w(a, 'Essence'))), g(jsround(w(a, 'Ink'))), a['floor'],
        g(jsround(w(b, 'Dust'))), g(jsround(w(b, 'Essence'))), g(jsround(w(b, 'Ink'))), b['floor'],
        jsround(100 * (1 - a['Dust'] / a['Essence'])))


def gen_trader_worked():
    out = ['<table>', '    <tr><th>Floor</th>%s</tr>' % ''.join('<th>%s / battle</th>' % c for c in CUR)]
    for F in (1, 30, 60, 90, 100, 101, 120):
        a = acq(F)
        out.append('    <tr><td>%d%s</td>%s</tr>' % (F, '' if a['floor'] == F else ' (boss floor: farms %d)' % a['floor'],
                                                   ''.join('<td>%s</td>' % s3(a[c]) for c in CUR)))
    out.append('  </table>')
    return '\n'.join(out)


def gen_trader_example():
    """src/trader.js traderRates (rate = perBattle(A) / perBattle(B) x (1 + premium)) and traderQuote (get = floor(pay / rate))."""
    a, p = acq(119), acq('premium')
    rate = lambda c, t: a[c] / a[t] * (1 + p)
    return ('<p>An Ichor week at the reference floor %d: 1,000 Scrap buys %s Ichor; 10 Dust buys %s Ichor (time parity would be %s Ichor '
            'per Dust; %s after the cut). A Dust week at %d: one Dust costs about %s Ichor, or %s Scrap.</p>') % (
        a['floor'], g(math.floor(1000 / rate('Scrap', 'Ichor'))), g(math.floor(10 / rate('Dust', 'Ichor'))),
        s3(a['Ichor'] / a['Dust']), s3(1 / rate('Dust', 'Ichor')), a['floor'], s3(rate('Ichor', 'Dust')),
        g(jsround(rate('Scrap', 'Dust'))))


# ------------------------------------------------------------------------------------------------- endgame income + grading hours
def gen_st_income():
    """stat-tables section 15: acquisitionPerBattle at the 91-100 band's wild floor 99 x BATTLES_PER_HOUR."""
    bph = battles_per_hour(); a = acq(99)
    hr = lambda c: g(jsround(a[c] * bph))
    return ('<h3>Endgame income (floor %d, %d battles/h)</h3>\n'
            '<table><tr><th>Currency</th><th>Rate</th><th>Main sources</th></tr>\n'
            '<tr><td>Scrap</td><td>~%s/h</td><td>Dismantling gear drops (<code>dismantle.csv</code> Gear rows; a Tag also returns Essence)</td></tr>\n'
            '<tr><td>Ichor</td><td>~%s/h</td><td>Kill Ichor (<code>round(2 &times; (1 + level/100) &times; rarity mult)</code>), egg and Rare+ gear dismantles</td></tr>\n'
            '<tr><td>Dust / Essence / Ink</td><td>~%s / %s / %s per h</td><td>Enhancement dismantles (<code>dismantle.csv</code> Gem / Rune / Scroll rows)</td></tr></table>\n'
            '<p class="gen-note"><code>acquisitionPerBattle</code> (<code>src/trader.js</code>) &times; BATTLES_PER_HOUR (<code>tools/sim_econ.mjs</code>); '
            'bosses, first wins and shop drops not counted. Generated by <code>tools/codex_tables.py</code>.</p>') % (
        a['floor'], bph, hr('Scrap'), hr('Ichor'), hr('Dust'), hr('Essence'), hr('Ink'))


def grading_totals():
    G = {(r['Category'], r['To_Grade']): r for r in rows('grading.csv') if r['Tier'] == '10'}
    cg = ce = 0.0; div = None
    for gr in grades()[1:]:
        rg, re_ = G[('Gear', gr['Grade'])], G[('Gem', gr['Grade'])]
        cg += float(rg['Cost'].split()[0]) / (float(rg['Success_Pct']) / 100)
        ce += float(re_['Cost'].split()[0]) / (float(re_['Success_Pct']) / 100)
        if gr['Grade'] == 'Divine': div = ce
    return cg, ce, div


def gen_grading_prose(style):
    """the cumulative expected spend (gen_grading's own sum) over tools/statmodel.py Grading.piece's hours: the currency per hour
    at TIER_FLOOR[10] = acquisitionPerBattle x BATTLES_PER_HOUR."""
    def f():
        bph = battles_per_hour(); F = ref_floor(); a = acq(F) if F in ACQ_FLOORS else None
        if a is None:
            raise ValueError('ACQ_FLOORS lacks the reference floor %d' % F)
        cg, ce, div = grading_totals()
        sh, dh = a['Scrap'] * bph, a['Dust'] * bph
        if style == 'stat':
            return ('<p>One gear piece Worn&rarr;Void at T10: expected ~%s Scrap (~%s h at floor %d). One Void enhancement at T10: expected '
                    '~%s material (~%s h). The realistic endgame enhancement target is Divine (~%s material, ~%s h). Hours at %d battles/h; '
                    'model: <code>python tools/statmodel.py grids</code>, generated by <code>tools/codex_tables.py</code>.</p>') % (
                g(jsround(cg)), fx(cg / sh, 1), F, g(jsround(ce)), fx(ce / dh, 1), g(jsround(div)), fx(div / dh, 1), bph)
        vg = [r for r in rows('grading.csv') if r['Tier'] == '10' and r['Category'] == 'Gear' and r['To_Grade'] == grades()[-1]['Grade']][0]
        return ('One item Worn&rarr;Void at T10: expected ~%s Scrap &asymp; %sh at floor %d (%s Scrap/h at %d battles/h, '
                '<code>python tools/statmodel.py grids</code>). Void gate alone: expected %s.') % (
            g(jsround(cg)), fx(cg / sh, 1), F, g(jsround(sh)), bph, g(jsround(float(vg['Cost'].split()[0]) / (float(vg['Success_Pct']) / 100))))
    return f


# ------------------------------------------------------------------------------------------------- creature base stats
def power_fns():
    """src/power.js:18 STAT_SCALE and :171-173 coreOf / axisMult / hpFor, lifted verbatim and evaluated under node."""
    src = client_file('src/power.js')
    lines = []
    for pat in (r'const STAT_SCALE = [^;]+;', r'const coreOf = [^;]+;', r'const axisMult = [^;]+;', r'const hpFor = [^;]+;'):
        m = re.search(pat, src)
        if not m:
            raise ValueError('src/power.js: %s not found' % pat)
        lines.append(m.group(0))
    js = ' '.join(lines) + (" const o = {}; for (let g = 1; g <= 10; g++) o[g] = {a: coreOf(100) * axisMult(g), hp: hpFor(100, g), core: coreOf(100)};"
                            " console.log(JSON.stringify(o));")
    return node_json('power', js)


def gen_creature_base():
    P = power_fns()
    out = ['<table>', '      <tr><th>Grade</th><th>Off / Def / Utl</th><th>Speed (flat)</th><th>HP (at this Def grade)</th></tr>']
    for gr in range(1, 11):
        v = P[str(gr)]
        out.append('      <tr><td>%d</td><td>%s</td><td>%d</td><td>%s</td></tr>' % (gr, g(jsround(v['a'])), gr, g(jsround(v['hp']))))
    out.append('    </table>')
    return '\n'.join(out)


# ------------------------------------------------------------------------------------------------- level offsets
def _sgn(o):
    return ('+%d' % o) if o > 0 else ('&minus;%d' % -o if o < 0 else '0')


def gen_level_offsets():
    off = lvl_off()
    out = ['<table>', '      <tr><th>Offset from zone level</th>%s</tr>' % ''.join('<th>%s</th>' % _sgn(o) for o, _ in off),
           '      <tr><td>Spawn rate</td>%s</tr>' % ''.join('<td>%d%%</td>' % p for _, p in off), '    </table>', '']
    terms = ' + '.join('%s(%s)' % (fx(p / 100, 2), _sgn(o)) for o, p in off)
    s = sum(o * p for o, p in off) / 100
    out.append('    <div class="note note-info"><p><strong>Average preservation:</strong> &Sigma;(rate &times; offset) = %s = %s. '
               'Level offsets cancel: the mean enemy level is the zone&rsquo;s base level. What a battle at that level pays is the '
               'reference table above (expected XP of three on-level kills), not a flat multiple of the zone level. Offsets: '
               '<code>src/worker.js</code> deriveSlot <code>OFF</code>; generated by <code>tools/codex_tables.py</code>.</p></div>'
               % (terms, ('%d' % s) if s == int(s) else fx(s, 2)))
    return '\n'.join(out)


# ------------------------------------------------------------------------------------------------- breeding
RAR5 = ['C', 'UC', 'R', 'SR', 'SSR']


def ichor_kill(F, k):
    """src/trader.js:112 ichorKill / the battle credit: round(2 x (1 + min(100, F)/100) x food_rarity_mult[k])."""
    return jsround(2 * (1 + min(100, F) / 100) * json.loads(client_file('src/tables.json'))['food_rarity_mult'][k])


def gen_breed_ichor():
    bph = battles_per_hour()
    enc = {int(r['Floor']): r for r in rows('encounter_weights.csv')}
    out = ['<table>', '    <tr><th>Floor</th><th>C</th><th>UC</th><th>R</th><th>SR</th><th>SSR</th><th>Expected / battle</th><th>Ichor / hour</th></tr>']
    for F in (1, 25, 51, 75, 99, 119):
        w = {k: float(enc[F]['Weight_' + k] or 0) for k in RAR5}; tot = sum(w.values()) or 1
        per = 3 * sum(w[k] / tot * ichor_kill(F, k) for k in RAR5)
        out.append('    <tr><td class="lbl">%d</td>%s<td style="text-align:center">%s</td><td style="text-align:center">~%s</td></tr>' % (
            F, ''.join('<td style="text-align:center">%d</td>' % ichor_kill(F, k) for k in RAR5), fx(per, 1), g(jsround(per * bph / 10) * 10)))
    out.append('  </table>')
    out.append('  <p style="font-size:13px;color:var(--ink-dim)">Kill Ichor only (egg and gear dismantles are on the Shadow Trader page). '
               'Hourly figures at %d battles/h (dfmc-client <code>tools/sim_econ.mjs</code> BATTLES_PER_HOUR), rounded to 10. Deep floors still '
               'pay more &mdash; higher levels and a richer rarity mix &mdash; but the ramp is flat: floor 119 pays %s&times; floor 1. Generated by '
               '<code>tools/codex_tables.py</code> from <code>encounter_weights.csv</code> and <code>tables.json food_rarity_mult</code>.</p>' % (
                   bph, fx(_ichor_per(119, enc) / _ichor_per(1, enc), 1)))
    return '\n'.join(out)


def _ichor_per(F, enc):
    w = {k: float(enc[F]['Weight_' + k] or 0) for k in RAR5}; tot = sum(w.values()) or 1
    return 3 * sum(w[k] / tot * ichor_kill(F, k) for k in RAR5)


def gen_breed_rates():
    by = {x['Grade']: x for x in rows('breeding.csv')}
    out = ['<table>', '    <tr><th>Pair grade</th><th>Ichor / min</th><th>Minutes / egg</th><th>Ichor / egg</th><th>Drain per hour</th></tr>']
    for gr in grades():
        r = by[gr['Grade']]
        cell = lambda col: '<td style="text-align:center">%s</td>' % span('breeding.csv#Grade=%s#%s' % (gr['Grade'], col), g(int(r[col])),
                                                                          'g' if int(r[col]) >= 1000 else None)
        out.append('    <tr><td class="lbl" style="color:%s">%s</td>%s%s%s<td style="text-align:center">%s</td></tr>' % (
            GRADE_COL[gr['Grade']], gr['Grade'], cell('Ichor_Per_Min'), cell('Minutes_Per_Egg'), cell('Ichor_Per_Egg'), g(60 * int(r['Ichor_Per_Min']))))
    out.append('  </table>')
    return '\n'.join(out)


def gen_breed_egg_dismantle():
    by = {x['Grade']: x for x in rows('breeding.csv')}
    gs = [x['Grade'] for x in grades()]
    return ('<table>\n    <tr><th>Egg grade</th>%s</tr>\n    <tr><td class="lbl">Ichor</td>%s</tr>\n  </table>' % (
        ''.join('<th>%s</th>' % x for x in gs),
        ''.join('<td style="text-align:center">%s</td>' % span('breeding.csv#Grade=%s#Egg_Dismantle_Ichor' % x, by[x]['Egg_Dismantle_Ichor']) for x in gs)))


# ------------------------------------------------------------------------------------------------- mutants
def mutant_chance():
    """src/worker.js:1503 MUTANT_CHANCE (percent) and cxMutBonusOf / cxVoidBonusOf: Math.min(cap, rate x done)."""
    src = client_file('src/worker.js')
    m = re.search(r'const MUTANT_CHANCE = \{([^}]+)\}', src)
    z = re.search(r'cxMutBonusOf\(sid, realm, zc\) \{.*?return Math\.min\(([\d.]+), ([\d.]+) \* done\);', src, re.S)
    v = re.search(r'cxVoidBonusOf\(sid, realm\) \{.*?return Math\.min\(([\d.]+), ([\d.]+) \* done\);', src, re.S)
    if not (m and z and v):
        raise ValueError('src/worker.js: MUTANT_CHANCE / cxMutBonusOf / cxVoidBonusOf not found')
    ch = {k: float(x) for k, x in re.findall(r'(\w+):\s*([\d.]+)', m.group(1))}
    return ch, (float(z.group(1)), float(z.group(2))), (float(v.group(1)), float(v.group(2)))


def gen_mut_chance():
    ch, (zc, zr), (vc, vr) = mutant_chance()
    out = ['<table>', '    <tr><th>Egg grade</th><th>Base chance</th><th>With every zone tier (+%s%%)</th><th>With the whole Codex (+%s%%)</th></tr>'
           % (fx(zc, 2), fx(zc + vc, 2))]
    for gr in grades():
        b = ch[gr['Grade']]
        out.append('    <tr><td class="lbl" style="color:%s;font-weight:600;">%s</td><td>%s%%</td><td>%s%%</td><td>%s%%</td></tr>' % (
            GRADE_COL[gr['Grade']], gr['Grade'], fx(b, 2), fx(b + zc, 2), fx(b + zc + vc, 2)))
    out.append('  </table>')
    out.append('  <p class="gen-note">Zone tiers +%s%% each (cap +%s%%); Void lines +%s%% each (cap +%s%%): <code>src/worker.js</code> '
               'MUTANT_CHANCE, cxMutBonusOf, cxVoidBonusOf. Generated by <code>tools/codex_tables.py</code>.</p>' % (
                   fx(zr, 2), fx(zc, 2), fx(vr, 3), fx(vc, 2)))
    return '\n'.join(out)


def gen_mut_zones():
    """src/worker.js zoneCreatures: zones from floors.csv (sorted by first floor = tier), creatures by creatures.csv Floor_Found."""
    _, (zc, zr), _ = mutant_chance()
    zones = []
    for r in rows('floors.csv'):
        fn, z = int(r['Floor'] or 0), r['Zone']
        if not fn or not z:
            continue
        e = next((x for x in zones if x['zone'] == z), None)
        if not e:
            e = {'zone': z, 'lo': fn, 'hi': fn}; zones.append(e)
        e['lo'] = min(e['lo'], fn); e['hi'] = max(e['hi'], fn)
    zones.sort(key=lambda x: x['lo'])
    tier = {f: i for i, z in enumerate(zones) for f in range(z['lo'], z['hi'] + 1)}
    names = {}
    for r in rows('creatures.csv'):
        nm = (r['Name'] or '').upper()
        for f in (r.get('Floor_Found') or '').split(';'):
            t = tier.get(int(f) if f.strip().isdigit() else 0)
            if nm and t is not None:
                names.setdefault(t, set()).add(nm)
    out = ['<table>', '    <tr><th>Zone</th><th>Floors</th><th>Creatures</th><th>Tier reward</th><th>Cumulative</th></tr>']
    k = 0
    for i, z in enumerate(zones):
        if i not in names:
            continue
        k += 1
        out.append('    <tr><td class="lbl">%s</td><td>%d&ndash;%d</td><td style="text-align:center">%d</td><td style="text-align:center">+%s%%</td>'
                   '<td style="text-align:center">+%s%%</td></tr>' % (z['zone'], z['lo'], z['hi'], len(names[i]), fx(zr, 2), fx(min(zc, zr * k), 2)))
    out.append('    </table>')
    return '\n'.join(out)


# ------------------------------------------------------------------------------------------------- stat-tables pools
POOL_ATK = ['Arming Sword', 'Crude Signet', 'Crude Signet']
POOL_DEF = ['Kite Shield', 'Cowl', 'Padded Jerkin', 'Handwraps', 'Footwraps']


def pool(names, T, gi):
    return sum(item_base(n, T, gi) for n in names)


def gen_st_pools():
    G = [x['Grade'] for x in grades()]
    cols = [G.index('Worn'), G.index('Rare'), G.index('Void')]
    out = ["<div class='scroll'><table>",
           '<tr><th rowspan="2">Tier</th><th rowspan="2">Levels</th><th colspan="3">Attack pool (&Sigma; items)</th><th colspan="3">Defense pool (&Sigma; items)</th></tr>',
           '<tr><th>Worn</th><th>Rare</th><th>Void</th><th>Worn</th><th>Rare</th><th>Void</th></tr>']
    for T in range(1, 11):
        cells = [pool(POOL_ATK, T, c) for c in cols] + [pool(POOL_DEF, T, c) for c in cols]
        out.append('<tr><td>T%d</td><td>%d&ndash;%d</td>%s</tr>' % (T, 10 * T - 9, 10 * T, ''.join('<td style="text-align:center">%s</td>' % g(v) for v in cells)))
    out.append('</table></div>')
    # the example: src/power.js:416 a = ((charAtk + CHAR_CORE x coreOf(L)) x axisMult(off) x (1 + inc%)) x (1 + CHAR_RISK x ..) + CHAR_FLOOR) x clsSoulMult
    src = client_file('src/power.js')
    core_k = float(re.search(r'CHAR_CORE = ([\d.]+)', src).group(1))
    if float(re.search(r'CHAR_RISK = ([\d.]+)', src).group(1)):
        raise ValueError('src/power.js CHAR_RISK is not 0 - the example line assumes it is')
    core100 = power_fns()['1']['core']
    floor_ = jsround(25 * float(re.search(r'const STAT_SCALE = ([\d.]+)', src).group(1)))
    cls = {(r['Line_ID'], r['Stage']): r for r in rows('classes.csv')}
    a3, a2 = cls[('MAGE', '3')], cls[('MAGE', '2')]
    v = pool(POOL_ATK, 10, G.index('Void'))
    ex = lambda c: jsround((v + core_k * core100) * (3 * int(c['Grade_Attack']) + 5) / 8 + floor_)
    out.append('<p style="font-size:12px;color:#8a7a5e">Each pool is one bare loadout summed: Attack = %s; Defense = %s (each piece&rsquo;s own '
               '<code>N &times; T &times; GF</code> grid above). Example: level 100 %s (Atk %s), Void T10 bare set &rarr; (%s + %s &times; %s) &times; %s + %d = %s '
               'Attack before enhancements and ClassSoulMult; the same set on %s (Atk %s) &rarr; %s. Section 10&rsquo;s MAX numbers are a July 2026 record that this bare set already passes (see its note). '
               'Generated by <code>tools/codex_tables.py</code>.</p>' % (
                   ' + '.join(POOL_ATK), ' + '.join(POOL_DEF), a3['Name'], a3['Grade_Attack'], g(v), fx(core_k, 2), fx(core100, 1),
                   fx((3 * int(a3['Grade_Attack']) + 5) / 8, 3), floor_, g(ex(a3)), a2['Name'], a2['Grade_Attack'], g(ex(a2))))
    return '\n'.join(out)


# ------------------------------------------------------------------------------------------------- classes, souls, quality
def gen_class_stages():
    """classes.csv: every line's three stages (A / D / S) and its access - each cell a binding."""
    by = {}
    for r in rows('classes.csv'):
        by.setdefault(r['Line_ID'], {})[int(r['Stage'])] = r
    out = ['<table>', '      <tr><th>Class line</th><th>Stage 1 (A/D/S)</th><th>Stage 2 (A/D/S)</th><th>Stage 3 (A/D/S)</th><th>Access</th></tr>']
    for line, st in by.items():
        b = lambda r, c: span('classes.csv#%s#%s' % (r['Class_ID'], c), r[c])
        cells = ['%s / %s / %s' % (b(st[k], 'Grade_Attack'), b(st[k], 'Grade_Defense'), b(st[k], 'Grade_Speed')) for k in (1, 2, 3)]
        r1 = st[1]
        acc = 'Starter' if r1['Access'] == 'Starter' else 'Unlock &mdash; %s' % span('classes.csv#%s#Unlock_Cost' % r1['Class_ID'], r1['Unlock_Cost'])
        out.append('      <tr><td>%s</td>%s<td>%s</td></tr>' % (' &rarr; '.join(st[k]['Name'] for k in (1, 2, 3)), ''.join('<td>%s</td>' % c for c in cells), acc))
    out.append('    </table>')
    return '\n'.join(out)


def soul_mult(i):
    """src/power.js:188 soul grade multiplier: 1 + (1/9) x grade index (Worn 0)."""
    m = re.search(r'return 1 \+ \(1 / (\d+)\) \* i; \};', client_file('src/power.js'))
    if not m:
        raise ValueError('src/power.js: soul grade multiplier not found')
    return 1 + i / int(m.group(1))


def gen_soul_grading():
    """soul_grading.csv: per step the bundle (every currency required), Success_Pct; cumulative expected = sum(cost / p)."""
    G = [x['Grade'] for x in grades()]
    out = ['<table>', '    <tr><th>Target grade</th><th class="pct">Success</th><th class="pct">SoulMult</th><th>Bundle per try (every currency required)</th>'
           '<th>Cumulative expected Scrap / each of Dust, Essence, Ink</th></tr>']
    cs = cm = 0.0; last = None
    for r in rows('soul_grading.csv'):
        to = r['To_Grade']; p = float(r['Success_Pct']) / 100
        cs += float(r['Scrap']) / p; cm += float(r['Dust']) / p; last = (r, p)
        k = 'soul_grading.csv#To_Grade=%s#' % to
        bundle = ' &middot; '.join('%s %s' % (span(k + c, g(int(r[c])), 'g' if int(r[c]) >= 1000 else None), c)
                                   for c in ('Scrap', 'Ichor', 'Dust', 'Essence', 'Ink') if float(r[c] or 0))
        lab = '<td>%s</td>' % to if to in ('Worn', 'Common') else '<td style="color:%s">%s</td>' % (GRADE_COL[to], to)
        out.append('    <tr>%s<td class="pct">%s</td><td class="pct">&times;%s</td><td>%s</td><td>%s / %s</td></tr>' % (
            lab, span(k + 'Success_Pct', r['Success_Pct'] + '%', '%'), fx(soul_mult(G.index(to)), 2), bundle, g(jsround(cs)), g(jsround(cm))))
    out.append('  </table>')
    r, p = last
    out.append('  <div class="note">One class soul Worn&rarr;Void: expected ~%s Scrap plus ~%s each of Dust, Essence and Ink (the Void step alone is '
               '~%s Scrap, %s%% per try), drawn from four streams in parallel. It competes with gear grading (Scrap) and enhancement crafting '
               '(materials) for the same income &mdash; the deliberate terminal sink. Generated by <code>tools/codex_tables.py</code>.</div>' % (
                   g(jsround(cs)), g(jsround(cm)), g(jsround(float(r['Scrap']) / p)), r['Success_Pct']))
    return '\n'.join(out)


def qm(i):
    """src/power.js:169 qmOf: 0.8 + 0.04 x (grade index + 1)."""
    m = re.search(r'const qmOf = \(grade\) => \{[^}]*return i < 0 \? 1 : ([\d.]+) \+ ([\d.]+) \* \(i \+ 1\); \};', client_file('src/power.js'))
    if not m:
        raise ValueError('src/power.js: qmOf not found')
    return float(m.group(1)) + float(m.group(2)) * (i + 1)


def gen_qm_row(lead):
    def f():
        return ''.join('<td>&times;%s</td>' % fx(qm(i), 2) for i in range(len(grades()))) if lead is None else \
            '<tr><td>%s</td>%s</tr>' % (lead, ''.join('<td>&times;%s</td>' % fx(qm(i), 2) for i in range(len(grades()))))
    return f


# ------------------------------------------------------------------------------------------------- C17 part 4 (lane a8-s5-c17-tail)
def _num(v):
    """a CSV number as the page shows it: 50.0 -> 50, 32.32 -> 32.32"""
    x = float(v)
    return ('%d' % x) if x == int(x) else ('%s' % v).rstrip('0').rstrip('.')


def _pct_span(ref, v):
    """a percent cell bound to one CSV cell: the fmt makes csv-bind render the CSV value exactly as written here"""
    x = float(v)
    return span(ref, _num(v) + '%', 'd0,%' if x == int(x) else '%')


def _runs(ns):
    """[10,20,...,100,102,...,120] -> '10, 20, &hellip; 100' and '102, 104, &hellip; 120' (arithmetic runs)"""
    ns = sorted(ns); out = []; i = 0
    while i < len(ns):
        j = i + 1
        if j < len(ns):
            d = ns[j] - ns[i]
            while j + 1 < len(ns) and ns[j + 1] - ns[j] == d:
                j += 1
            run = ns[i:j + 1]
        else:
            run = ns[i:i + 1]
        out.append(', '.join(map(str, run)) if len(run) <= 3 else '%d, %d, &hellip; %d' % (run[0], run[1], run[-1]))
        i += len(run)
    return out


def _lines():
    """creatures.csv grouped by Line_ID: {line: {stage: row}} in file order"""
    by = {}
    for r in rows('creatures.csv'):
        by.setdefault(r['Line_ID'], {})[int(r['Stage'])] = r
    return by


RARITY_ORDER = ['Common', 'Uncommon', 'Rare', 'Super Rare', 'Super Super Rare']


def gen_codex_files():
    """index.html 'Codex data': every Rows cell is len() of that CSV's data rows, every breakdown is counted from the CSV."""
    n = lambda f: len(rows(f))
    L = _lines(); nl = len(L); st = sorted({k for v in L.values() for k in v})
    fcr = rows('floor_creature_rarity.csv')
    per = {}
    for r in fcr:
        per[int(r['Floor'])] = per.get(int(r['Floor']), 0) + 1
    grp = {}
    for f, c in per.items():
        grp[c] = grp.get(c, 0) + 1
    f1 = [r['Rarity_Tier'] for r in fcr if r['Floor'] == '1']
    slots = '/'.join('%d%s' % (f1.count(t), t) for t in RAR5 if f1.count(t))
    fcr_b = ' + '.join('%d floors &times; %d slots' % (grp[c], c) for c in sorted(grp, key=lambda c: -grp[c]))
    nboss_fl = [int(r['Floor']) for r in rows('floors.csv') if r['Is_Boss'] == 'Yes']
    bfl = sorted(int(r['Floor']) for r in rows('bosses.csv'))
    it = rows('items.csv')
    cat = lambda c: [r for r in it if r['Category'] == c]
    fam = lambda c: sorted({r['Family'] for r in cat(c)})
    tiers = lambda c: len({r['Tier'] for r in cat(c)})
    ends = lambda c: (cat(c)[0]['Name'].split()[0], [r for r in cat(c) if r['Tier'] == str(max(int(x['Tier']) for x in cat(c)))][0]['Name'].split()[0])
    wp = cat('Weapon')
    items_b = ('gems (%d types &times; %d tiers: %s &rarr; %s), runes (%d&times;%d: %s &rarr; %s), scrolls (%d: %s &rarr; %s), class weapons '
               '(%d lines &times; %d hands &times; %d tiers = %d pieces, %d art identities), armour (%d slots &times; %d named pieces = %d), '
               'accessories (%d&times;%d), tags (%d&times;%d), zone keys (%d), materials (%d), eggs (%d)') % (
        len(fam('Gem')), tiers('Gem'), ends('Gem')[0], ends('Gem')[1], len(fam('Rune')), tiers('Rune'), ends('Rune')[0], ends('Rune')[1],
        tiers('Scroll'), ends('Scroll')[0], ends('Scroll')[1], len(fam('Weapon')), len({r['Slot'] for r in wp}), tiers('Weapon'), len(wp),
        len({r['Image_Path'] for r in wp}), len(fam('Armour')), tiers('Armour'), len(cat('Armour')), len(fam('Accessory')), tiers('Accessory'),
        len(fam('Tag')), tiers('Tag'), len(cat('Key')), len(cat('Material')), len(cat('Egg')))
    mv = rows('moves.csv'); mlines = [r for r in mv if r['Line_ID'] != 'CLASS']
    mper = len(mlines) // len({r['Line_ID'] for r in mlines})
    cls_row = [i + 1 for i, r in enumerate(mv) if r['Line_ID'] == 'CLASS'][0]
    bands = '/'.join(str(p) for p in sorted({int(r['Power_S3']) for r in mlines}))
    so = rows('souls.csv'); sper = len(so) // len({r['Line_ID'] for r in so})
    wins = max(int(r['Win']) for r in rows('first_win_drops.csv'))
    nz = len({r['Zone'] for r in rows('wild_quality_weights.csv')})
    D = dict(nl=nl, ns=len(st), last='%03d' % n('creatures.csv'), fcr_b=fcr_b, slots=slots, wild=len(per), nboss=len(nboss_fl),
             bruns=', then '.join(_runs(bfl)), nb=n('bosses.csv'), items_b=items_b, mper=mper, cls_row=cls_row, bands=bands, sper=sper,
             wins=wins, nz=nz)
    R = [
        ('creatures.csv', '%d<br>(%d lines &times; %d stages)' % (n('creatures.csv'), nl, len(st)),
         'Full creature roster, one row per advancement stage. Columns: <code>ID, Line_ID, Stage, Name, Type_Primary, Type_Secondary, Type_Tertiary, Background_Key, Rarity, Floor_Found, Encounter_Type, Evolves_From, Evolves_To, Evolve_Level, Grade_Attack, Grade_Defense, Grade_Utility, Grade_Speed, Description, Image_Prompt, Image_Path, Home_Zone, Art_Status, BG_Status, Option_Slots, Sync_Status</code>. IDs run <code>DFMC-001</code>&hellip;<code>DFMC-{last}</code>, assigned per line then stage (line&nbsp;k &rarr; <code>3k-2 / 3k-1 / 3k</code>). <code>Sync_Status</code> tracks game-import state (<code>not_imported</code> / <code>synced</code> / <code>needs_reimport</code>): once a creature is imported into the game, any later change to it flips it to <code>needs_reimport</code> and it&rsquo;s tagged with an amber <code>⟳</code> cue in the admin codex, so only altered creatures are re-imported rather than the whole roster.'),
        ('floors.csv', '%d' % n('floors.csv'), 'The %d floors (%d boss floors). Columns: <code>Floor, Zone, Encounter_Type, Is_Boss, Boss_Name, Primary_Type, Tier, Visual_Theme, Description, Cover_Image_Path, Wins_To_Clear</code>.' % (n('floors.csv'), len(nboss_fl))),
        ('floor_creature_rarity.csv', '%s<br>(%s)' % (g(len(fcr)), fcr_b),
         'The wild-encounter table. Each of the {wild} wild floors maps its tier-slots ({slots} on a base floor) to a <code>Creature_ID</code>. Columns: <code>Floor, Creature_ID, Rarity_Tier</code>. Stage per slot computed <strong style="color:#ede0c4">per line</strong> from each line&rsquo;s <code>Evolve_Level</code> (mixed stages per floor &mdash; see level bands below). Boss floors carry no rows &mdash; those are defined in <code>codex/bosses.csv</code>. <strong style="color:#ede0c4">Regenerate this whenever <code>creatures.csv</code> IDs change</strong> &mdash; the index joins the two by ID.'),
        ('bosses.csv', '%d<br>(1 per boss floor)' % n('bosses.csv'),
         'Zone-boss definitions, one per boss floor ({bruns}). Columns: <code>Floor, Zone, Boss_Name, Boss_Character, Active_Creature_1, Active_Creature_2, Difficulty_Index, Notes, Boss_ID, Boss_Type_Primary, Boss_Type_Secondary, Boss_Level, Boss_Quality_Grade, Grade_Attack, Grade_Defense, Grade_Utility, Grade_Speed, Move_1..4, Kit_Synergy, Description, Image_Prompt, Image_Path, Art_Status, BG_Status</code>. All {nb} bosses fully designed &mdash; humanoid boss characters with movesets borrowed from their zone&rsquo;s creature lines (S3 magnitudes, slot order: signature / secondary damage / support &times;2), 2 SR actives from the zone&rsquo;s floors; bosses carry no reserves. Rendered at <a href="bosses.html" style="color:var(--gold-bright)">bosses.html</a>.'),
        ('encounter_weights.csv', '%d' % n('encounter_weights.csv'), 'Per-floor odds of an encounter rolling into each tier; SSR/SR odds scale up over the run (see &ldquo;Encounter weights&rdquo; below).'),
        ('maptypes.csv', '%d' % n('maptypes.csv'), 'Tileset / map-restyle definitions for floor-art generation.'),
        ('items.csv', '%d' % n('items.csv'), 'Full item catalog &mdash; {items_b}. Gear tier prefixes retired &mdash; every weapon and armour tier is a distinct named piece. Columns: <code>Item_ID, Category, Family, Slot, Name, Tier, Level_Req, Effect, Flavor_Text, Image_Prompt, Image_Path, Art_Status</code>.'),
        ('moves.csv', '%d' % n('moves.csv'), 'Complete move table &mdash; {nl} lines &times; {mper} moves. Columns: Move_ID (M-{{LINE}}-{{slot}}), Line_ID, Slot, Name, Name_S1/S2/S3 (stage-progressive move names), Power_S1/S2/S3, Cooldown, Effect_S1/S2/S3, Synergy, Anti, VFX_Description. Powers use bands {bands} at S3; S2 &asymp; 80%, S1 &asymp; 60%., Targets (derived, machine-readable: union of effect-clause sides across stages &mdash; enemy / self / ally, joined with +; display text remains authoritative for counts and amounts), Level_Learned, Level_Upgrade_V2, Level_Upgrade_V3 (per-line learn/upgrade schedule derived from advancement levels). Row {cls_row} is <code>M-CLASS-STRIKE</code> (Line_ID <code>CLASS</code>, Slot 0) &mdash; the character&rsquo;s no-souls fallback; excluded from per-line invariants and schedule regeneration'),
        ('souls.csv', '%d' % n('souls.csv'), 'Soul passive table &mdash; {nl} lines &times; {sper} armor slots (Head/Chest/Gloves/Feet). Columns: Soul_ID (S-{{LINE}}-{{SLOT}}), Line_ID, Gear_Slot, Scope (Local/Personal/Team), Rarity, Effect_S3 &mdash; despite the name, the authored value is the <strong>Stage-1</strong> magnitude; stages multiply upward (S1 <code>&times;1.00</code>, S2 <code>&times;1.12</code>, S3 <code>&times;1.25</code>). Ability-slot souls (MH/OH/Acc1/Acc2) grant moves instead &mdash; see moves.csv.'),
        ('breeding.csv', '%d' % n('breeding.csv'), 'Breeding economy per pair grade. Columns: Grade_Num, Grade, Ichor_Per_Min, Minutes_Per_Egg, Ichor_Per_Egg, Egg_Dismantle_Ichor (the last keyed to egg grade, not pair grade).'),
        ('wild_quality_weights.csv', '%d' % n('wild_quality_weights.csv'), 'Zone-banded quality-grade weights for wild spawns (Worn&ndash;Void columns, {nz} zones, per-band rows). Floors 1&ndash;9 all-Worn; curve begins floor 11. Rolled once at spawn; sets the wild QM and the virtual-tag grade context.'),
        ('first_win_drops.csv', '%d' % n('first_win_drops.csv'), 'Guaranteed bonus drops for the first {wins} wild-battle wins (boss wins excluded from the counter). All grants spawn Worn T1. Selection rules: fixed Item_ID, random family, complement of win 1, or lowest-rarity enemy egg (random among ties).'),
        ('drop_rates.csv', '%d' % n('drop_rates.csv'), 'Drop roll rules &mdash; points to <code>drop_chances_by_floor.csv</code> for chances, plus family notes and the enhancement grade-band rule. Prototypes and the game read from the tables; no hardcoding.'),
        ('drop_chances_by_floor.csv', '%d' % n('drop_chances_by_floor.csv'), 'Per-kill drop chance by floor and rarity &mdash; one independent roll each for gear, enhancement, and egg. Value ladder &times;1/1.5/2.5/4/7 normalized per floor against encounter weights: each family lands exactly 10% per battle everywhere. Boss floors zeroed (no wilds).'),
        ('drop_grade_weights.csv', '%d' % n('drop_grade_weights.csv'), 'Gear-drop grade weights per floor band (%d bands; mirrors Stat &amp; Equipment Tables &sect;15). Divine, Primordial and Void never drop.' % len({(r['Floor_Lo'], r['Floor_Hi']) for r in rows('drop_grade_weights.csv')})),
        ('key_drop_rates.csv', '%d' % n('key_drop_rates.csv'), 'Per-creature boss-Key drop chances by rarity and zone, with each zone&rsquo;s <code>Key_Item_ID</code> &mdash; one expected Key per minimum-win zone journey.'),
        ('boss_loot.csv', '%d' % n('boss_loot.csv'), 'Guaranteed boss drops &mdash; one piece of equipment (grade one band ahead) and one native Stage-1 egg (rarity-weighted, Legendary-capped). Delivered on the conclusion screen.'),
        ('floor_assets.csv', '%d' % n('floor_assets.csv'), 'Level design pipeline. Per-floor: battle background prompt/path/status, parallax reference, prop assignments, map preview status (empty + populated). Decoupled from floor identity for infinite floor extension.'),
        ('prop_assets.csv', '%d' % n('prop_assets.csv'), 'Zone prop catalog &mdash; 3&ndash;4 props + 1 anchor prop per zone, with image prompts and art status.'),
    ]
    out = ['<table>', '      <tr><th>File</th><th>Rows</th><th>Contents</th></tr>']
    for f, rc, txt in R:
        out.append('      <tr><td><code>codex/%s</code></td><td>%s</td><td>%s</td></tr>' % (f, rc, txt.format(**D) if '{' in txt else txt))
    out.append('    </table>')
    out.append('    <p class="gen-note">Row counts and breakdowns counted from the CSVs by <code>tools/codex_tables.py</code> (codex-files).</p>')
    return '\n'.join(out)


def gen_ultimates():
    """ultimates.csv: one row per line per stage; every power / percent / duration is a binding on its cell."""
    by = {}
    for r in rows('ultimates.csv'):
        by.setdefault(r['Line_ID'], {})[int(r['Stage'])] = r
    out = ['<table>', '<tr><th>Line</th><th>S1 / S2 / S3</th><th>Effect</th></tr>']
    for line, st in by.items():
        b = lambda k, c: span('ultimates.csv#%s#%s' % (st[k]['Ult_ID'], c), st[k][c])
        tri = lambda c: ' / '.join(b(k, c) for k in (1, 2, 3))
        kind = st[1]['Kind']
        if kind == 'taunt':
            eff = ('Taunt for the round. S2 adds +%s%% Defense for the rest of the battle; S3 adds %s%% of maximum HP healed per hit taken this round.'
                   % (b(2, 'Mag_Pct'), b(3, 'Heal_Pct')))
        elif kind == 'nuke_aoe':
            eff = 'Strikes every enemy. Power %s <em>per target</em>.' % tri('Power')
        elif kind == 'nuke_single':
            eff = 'Strikes one enemy. Power %s.' % tri('Power')
        elif kind == 'retaliate':
            eff = ('Retaliation stance for the round: each hit taken answers with a %s power counter and raises Attack %s%% for the rest of the battle, '
                   'capped at +%s%%.' % (tri('Counter_Power'), tri('Stack_Pct'), tri('Stack_Cap')))
        elif kind == 'echo':
            fr = [int(st[k]['Fraction_Pct']) for k in (1, 2, 3)]
            eff = ('Echo: every support ability in the hero&rsquo;s soul slots fires at once on the whole party, the hero included &mdash; self-only and ally-type '
                   'abilities alike, and the type gate does not apply. Bonuses land at %s%% strength (a +50%% buff becomes %s) and durations are halved, '
                   'rounded up. Whole-number effects of one step round away to nothing at %s%%.' % (
                       tri('Fraction_Pct'), ' / '.join('+%d%%' % jsround(50 * f / 100) for f in fr), b(1, 'Fraction_Pct')))
        elif kind == 'vanish':
            eff = 'Untargetable by single-target moves for %s rounds.' % tri('Dur_Rounds')
        else:
            raise ValueError('ultimates.csv: no wording for Kind %s' % kind)
        names = ' / '.join(st[k]['Name'].replace("'", '&rsquo;') for k in (1, 2, 3))
        out.append('<tr><td style="color:#ede0c4">%s</td><td>%s</td><td>%s</td></tr>' % (line, names, eff))
    out.append('</table>')
    return '\n'.join(out)


def gen_moves_budget():
    """moves.csv: moves per line, the move count and the S3 power bands; DPT = Power / (1 + Cooldown) on those bands."""
    mv = [r for r in rows('moves.csv') if r['Line_ID'] != 'CLASS']
    nl = len({r['Line_ID'] for r in mv}); per = len(mv) // nl
    bands = sorted({int(r['Power_S3']) for r in mv})
    light, std, heavy, nuke = [b for b in bands if b][:4]
    dpt = lambda p, cd: g(jsround(p / (1 + cd)))
    return '\n'.join([
        '    <p>Every creature line has exactly <strong>%d fixed moves</strong> &mdash; no move customization (creature customization is Tags/equipment only). '
        'Moves persist across the 3 advancement stages, growing stronger: Stage 2 &asymp; 80%% of Stage 3 power with reduced effect magnitudes; Stage 1 &asymp; 60%% '
        'power with one effect component removed. All %d moves are catalogued in <code>codex/moves.csv</code> (%d lines &times; %d).</p>' % (per, len(mv), nl, per),
        '    <table>',
        '      <tr><th>Budget rule</th><th>Detail</th></tr>',
        '      <tr><td>Damage-per-turn proxy</td><td><code>DPT = Power / (1 + Cooldown)</code>, anchored at Standard %d @ CD0 = %s. Heavy %d @ CD2 = %s, '
        'Nuke %d @ CD3 = %s &mdash; the DPT deficit is the headroom that pays for rider effects.</td></tr>' % (std, dpt(std, 0), heavy, dpt(heavy, 2), nuke, dpt(nuke, 3)),
        '      <tr><td>Riders</td><td>%d-power carries one named debuff at CD2; %d-power carries a strong debuff or second component at CD3&ndash;4; %d-power can carry '
        'a strong effect at CD0&ndash;1; 0-power status moves carry very strong effects at CD1&ndash;4.</td></tr>' % (heavy, nuke, light),
        '      <tr><td>Buff stacking</td><td>A status is identified by the <strong>ability</strong> that applied it. Two different abilities stack and their magnitudes '
        '<strong>add</strong> (+50% and +15% is +65%); one ability never stacks with itself, and re-applying it refreshes duration and keeps the stronger magnitude. '
        'Full rules, including Synergy-clause self-inclusion and targeting: <a href="system-status-effects.html">Status Effects &amp; Buff Stacking</a>.</td></tr>',
        '      <tr><td>Named debuffs only</td><td>No generic statuses. Every buff/debuff is named and owned by one move (e.g. <em>Mothervenom</em> belongs to Echidna&rsquo;s '
        'Viper Spit). Families: Shred (&minus;Def), Sap (&minus;Off), Mire (&minus;Speed stages), named DoTs, Marks (+damage taken), and rare action-denial.</td></tr>',
        '      <tr><td>NO TYPE CHART</td><td>There is no global type-effectiveness matrix and never will be. All type interaction lives inside individual moves: '
        '<strong>Synergy</strong> clauses &mdash; a move is empowered by allied types in one of three ways: (a) an ally of a certain type <em>on the field</em> boosts the '
        'move (+20&ndash;50% band); (b) the move is stronger when it <em>targets</em> an ally of a certain type (buffs/heals, +20&ndash;50% band); or (c) the move '
        '<em>gains an added effect</em> when used on an ally of a certain type and <strong>Anti</strong> clauses (bonus vs specific target types, +30&ndash;60% band, '
        'thematically justified). Every type appears as both a synergy-giver and an anti-target.</td></tr>',
        '      <tr><td>Kit shape by stat profile</td><td>Strikers (A8&ndash;10): spam &rarr; utility-lite &rarr; Heavy CD2 &rarr; Nuke CD3&ndash;4 signature. Walls (D8&ndash;10): '
        'Def buffs, reflection, chip. Utility (U8&ndash;10): strong named debuffs/buffs, the game&rsquo;s few heals (7 healers game-wide), damage held to Light/Standard. '
        'Speed (S8&ndash;10): first-strike riders and momentum.</td></tr>',
        '      <tr><td>Speed stages</td><td>In-battle Speed buffs/debuffs are the only thing that modifies turn order. They are temporary stages (&plusmn;1, &plusmn;2), never gear.</td></tr>',
        '    </table>',
        '    <p class="gen-note">Move counts and the power bands (%s at S3) counted from <code>codex/moves.csv</code>; DPT computed on them. The cooldown anchors, rider '
        'and kit rules are design text. Generated by <code>tools/codex_tables.py</code>.</p>' % ' / '.join(map(str, bands))])


def gen_ichor():
    """index.html Ichor: the kill formula and rarity mults (src/trader.js ichorKill, src/tables.json food_rarity_mult), hourly income at
    BATTLES_PER_HOUR, and breeding.csv's dismantle and pen cells as bindings."""
    bph = battles_per_hour(); enc = {int(r['Floor']): r for r in rows('encounter_weights.csv')}
    fm = json.loads(client_file('src/tables.json'))['food_rarity_mult']
    hr = lambda F: g(jsround(_ichor_per(F, enc) * bph / 10) * 10)
    br = rows('breeding.csv'); b = lambda r, c: span('breeding.csv#%s#%s' % (r['Grade_Num'], c), g(int(float(r[c]))), 'g' if float(r[c]) >= 1000 else None)
    w, v = br[0], br[-1]
    top = max(F for F in enc if F <= 119 and sum(float(enc[F]['Weight_' + k] or 0) for k in RAR5))
    inc = _ichor_per(top, enc) * bph
    return '\n'.join([
        '    <table>',
        '      <tr><th>Source</th><th>How it yields Ichor</th></tr>',
        '      <tr><td>Combat</td><td>Per defeated enemy: <code>round(2 &times; (1 + min(100, enemyLevel) / 100) &times; RarityMult)</code> &mdash; RarityMult %s. '
        'Roughly %s Ichor/h at floor 1, %s at floor 25, %s at floor 99 (deep floors pay more: higher levels <em>and</em> richer SSR/SR encounter odds).</td></tr>' % (
            ' / '.join('%s %s' % (k, fx(fm[k], 2 if fm[k] * 10 != int(fm[k] * 10) else 1)) for k in RAR5), hr(1), hr(25), hr(99)),
        '      <tr><td>Egg dismantling</td><td>Keyed to egg grade &mdash; %s (%s &rarr; %s). Tuned against the hatch-weight matrix to always return 27&ndash;30%% of what a pen '
        'would spend breeding that grade: a refund on a bad roll, never an engine.</td></tr>' % (' / '.join(b(r, 'Egg_Dismantle_Ichor') for r in br), w['Grade'], v['Grade']),
        '    </table>',
        '    <p>Pen drain, egg duration, and Ichor-per-egg are authored per pair grade in <code>codex/breeding.csv</code> &mdash; %s %s Ichor/min / %s min / %s Ichor, up to '
        '%s %s Ichor/min / %s min / %s Ichor. A single %s pen eats %s%% of a floor-%d player&rsquo;s kill Ichor (~%s/h), and that income buys ~%s %s eggs per hour no matter '
        'how many pens are owned. Full rules: <a href="system-breeding.html" style="color:var(--gold-bright)">Breeding</a>.</p>' % (
            w['Grade'], b(w, 'Ichor_Per_Min'), b(w, 'Minutes_Per_Egg'), b(w, 'Ichor_Per_Egg'), v['Grade'], b(v, 'Ichor_Per_Min'), b(v, 'Minutes_Per_Egg'),
            b(v, 'Ichor_Per_Egg'), v['Grade'], g(jsround(float(v['Ichor_Per_Min']) * 60 / inc * 100)), top, g(jsround(inc / 10) * 10),
            fx(inc / float(v['Ichor_Per_Egg']), 1), v['Grade']),
        '    <p class="gen-note">Kill Ichor at %d battles/h (dfmc-client <code>tools/sim_econ.mjs</code> BATTLES_PER_HOUR) on <code>encounter_weights.csv</code>, rounded to 10. '
        'Generated by <code>tools/codex_tables.py</code>.</p>' % bph])


def gen_adv_bands():
    """creatures.csv: per line rarity, Stage 1 and Stage 2 Evolve_Level ranges."""
    L = _lines(); out = ['<table>', '      <tr><th>Rarity</th><th>Lines</th><th>S1 &rarr; S2</th><th>S2 &rarr; S3</th></tr>']
    for rar in RARITY_ORDER:
        ls = [v for v in L.values() if v[1]['Rarity'] == rar]
        e1 = [int(v[1]['Evolve_Level']) for v in ls]; e2 = [int(v[2]['Evolve_Level']) for v in ls]
        out.append('      <tr><td>%s</td><td>%d</td><td>Lv %d&ndash;%d</td><td>Lv %d&ndash;%d</td></tr>' % (rar, len(ls), min(e1), max(e1), min(e2), max(e2)))
    out.append('    </table>')
    return '\n'.join(out)


def gen_zones():
    """floors.csv, base tower (floors 1-100): each zone's floor range and Primary_Type."""
    z = {}
    for r in rows('floors.csv'):
        if int(r['Floor']) <= 100:
            z.setdefault(r['Zone'], []).append(r)
    out = ['<table>', '      <tr><th>Floors</th><th>Zone</th><th>Primary type(s)</th></tr>']
    for name, fl in z.items():
        types = []
        for r in fl:
            if r['Primary_Type'] and r['Primary_Type'] not in types:
                types.append(r['Primary_Type'])
        out.append('      <tr><td>%s&ndash;%s</td><td>%s</td><td>%s</td></tr>' % (fl[0]['Floor'], fl[-1]['Floor'], name, ' / '.join(types)))
    out.append('    </table>')
    return '\n'.join(out)


def gen_level_bands():
    """floor_creature_rarity.csv joined to creatures.csv: the floors (1-100) each stage actually appears on; creatures.csv line rarity split."""
    cr = {r['ID']: r for r in rows('creatures.csv')}; L = _lines()
    fl = {1: [], 2: [], 3: []}
    for r in rows('floor_creature_rarity.csv'):
        F = int(r['Floor'])
        if F <= 100:
            fl[int(cr[r['Creature_ID']]['Stage'])].append(F)
    e = lambda rar, k: [int(v[k]['Evolve_Level']) for v in L.values() if v[1]['Rarity'] == rar]
    late1 = max(RARITY_ORDER, key=lambda rar: max(e(rar, 1)))
    ab = {'Common': 'Commons', 'Uncommon': 'Uncommons', 'Rare': 'Rares', 'Super Rare': 'SR lines', 'Super Super Rare': 'SSR lines'}
    cnt = [(rar, sum(1 for v in L.values() if v[1]['Rarity'] == rar)) for rar in RARITY_ORDER]
    full = all(len(v) == 3 for v in L.values())
    return '\n'.join([
        '    <table>',
        '      <tr><th>Band (reference)</th><th>Nominal floors</th><th>Actual wild spread</th></tr>',
        '      <tr><td>Infant (Stage 1)</td><td>1&ndash;33</td><td>Floors %d&ndash;%d (%s hold S1 latest)</td></tr>' % (min(fl[1]), max(fl[1]), ab[late1]),
        '      <tr><td>Advanced (Stage 2)</td><td>34&ndash;66</td><td>Floors %d&ndash;%d (Commons reach S2 by ~%d)</td></tr>' % (min(fl[2]), max(fl[2]), min(e('Common', 1))),
        '      <tr><td>Final (Stage 3)</td><td>67&ndash;100</td><td>Floors %d&ndash;%d (Commons reach S3 by ~%d)</td></tr>' % (min(fl[3]), max(fl[3]), min(e('Common', 2))),
        '    </table>',
        '    <p style="font-size:13px;color:#c2ae8b">All %d creature lines are full 3-stage%s. Rarity (C/UC/R/SR/SSR) is a fixed property of the <em>line</em>, independent '
        'of stage, since every creature on a given floor is necessarily the same stage. %d lines split: %s. Spread counted from <code>floor_creature_rarity.csv</code> '
        '(floors 1&ndash;100) by <code>tools/codex_tables.py</code>.</p>' % (
            len(L), ' &mdash; no exceptions' if full else '', len(L), ', '.join('%d %s' % (c, r) for r, c in cnt))])


ENC_FLOORS = [1, 51, 99]


def gen_enc_weights():
    """encounter_weights.csv at the first wild floor, the middle zone's first wild floor and the last base wild floor: each cell a binding."""
    out = ['<table>', '      <tr><th>Floor</th><th>Common</th><th>Uncommon</th><th>Rare</th><th>Super Rare</th><th>Super Super Rare</th></tr>']
    enc = {int(r['Floor']): r for r in rows('encounter_weights.csv')}
    for F in ENC_FLOORS:
        out.append('      <tr><td>%d</td>%s</tr>' % (F, ''.join('<td>%s</td>' % _pct_span('encounter_weights.csv#%d#Weight_%s' % (F, k), enc[F]['Weight_' + k]) for k in RAR5)))
    out.append('    </table>')
    return '\n'.join(out)


# --- system-xp
def gen_xp_formulas():
    cur = {int(r['Level']): r for r in rows('XPCurve.csv')}
    top = max(cur); poly = 66
    gr = lambda L: float(cur[L]['XP_To_Next']) / float(cur[L - 1]['XP_To_Next']) - 1
    dev = max(abs(xp_on_level(L) / (10 * L) - 1) for L in range(10, top + 1))
    lo = min(int(cur[1]['XP_Kill_' + t]) for t in RAR5)
    flat = int(cur[top]['XP_Account_Flat'])
    return '\n'.join([
        '<table>',
        '    <tr><th>Quantity</th><th>Expression</th></tr>',
        '    <tr><td class="lbl">XP required, levels 1&ndash;%d</td><td><code>10 &times; L^1.75</code></td></tr>' % poly,
        '    <tr><td class="lbl">XP required, levels %d&ndash;%d</td><td>The rows of <code>XPCurve.csv</code>: per-level growth ramps from %s%% at %d to %s%% at %d (C1, 2026-10-23)</td></tr>' % (
            poly + 1, top, fx(gr(poly + 1) * 100, 1), poly + 1, fx(gr(top - 1) * 100, 1), top - 1),
        '    <tr><td class="lbl">XP required, player level %d+</td><td><code>XPCurve.csv</code> row %d <code>XP_Account_Flat</code> = %s &mdash; flat forever (player level only; creatures and classes cap at %d)</td></tr>' % (
            top + 1, top, span('XPCurve.csv#%d#XP_Account_Flat' % top, g(flat), 'g'), top),
        '    <tr><td class="lbl">XP per kill</td><td><strong>Not a formula &mdash; a table.</strong> <code>XP_Kill_&lt;tier&gt;</code> in <code>codex/XPCurve.csv</code>, indexed by the <em>enemy&rsquo;s</em> level, '
        'on the game-wide value ladder <code>C&nbsp;1.0 / UC&nbsp;1.5 / R&nbsp;2.5 / SR&nbsp;4.0 / SSR&nbsp;7.0</code> (level&nbsp;1 floored at %s&nbsp;XP). Client <code>xpKill()</code> and server '
        '<code>TABLES.xp_kill</code> read the same %d rows; no multiplier is applied on top</td></tr>' % (span('XPCurve.csv#1#XP_Kill_C', str(lo)), len(cur)),
        '    <tr><td class="lbl">XP per battle</td><td>The sum over the battle&rsquo;s <strong>3 kills</strong>. Because <code>encounter_weights.csv</code> is tuned per floor against that same ladder, '
        'a full battle on floor&nbsp;<code>L</code> averages <code>&asymp; 10 &times; L</code> &mdash; within <strong>&plusmn;%s%%</strong> from level&nbsp;10 up (floor&nbsp;%d: %s against %s). '
        'Below level&nbsp;10 the %s-XP floor lifts it above the line</td></tr>' % (fx(dev * 100, 1), top, fx(xp_on_level(top), 1), g(10 * top), lo),
        '    <tr><td class="lbl">Battles per level</td><td><code>XP_To_Next(L) &divide; XP-per-battle(L)</code>: %s at level&nbsp;1, %s at %d, %s at %d, %s at %d. Exact per-level values in the table below</td></tr>' % (
            g(battles_for_level(1)), g(battles_for_level(poly)), poly, g(battles_for_level(poly + 1)), poly + 1, g(battles_for_level(top - 1)), top - 1),
        '  </table>',
        '  <p class="gen-note">Computed from <code>codex/XPCurve.csv</code> and the on-level battle of <code>tools/codex_tables.py</code> (xp-formulas).</p>'])


def gen_xp_player():
    cur = {int(r['Level']): r for r in rows('XPCurve.csv')}
    top = max(cur); flat = int(cur[top]['XP_Account_Flat']); prev = int(cur[top - 1]['XP_To_Next'])
    return '\n'.join([
        '<table>',
        '    <tr><th>Property</th><th>Rule</th></tr>',
        '    <tr><td class="lbl">XP source</td><td>Every point of XP the account earns, from every battle, in every realm. Player XP is never split &mdash; it is the raw total.</td></tr>',
        '    <tr><td class="lbl">Curve, levels 1&ndash;%d</td><td>Identical to the creature / class curve: the rows of <code>XPCurve.csv</code> (<code>10 &times; L^1.75</code> to 66, then the C1 ramp). '
        'There is no formula fallback: with no curve loaded the account reads level 1, as a creature does.</td></tr>' % top,
        '    <tr><td class="lbl">Curve, levels %d+</td><td><strong>Flat</strong>. Every level past %d costs <code>XP_Account_Flat</code> (row %d of <code>XPCurve.csv</code>) = <strong>%s</strong> XP: '
        'the C1 ramp continued one step past %d (+%s%% on the %s of %d&rarr;%d), then held constant. No cap; the counter never stops. It is codex data so the vanity pace can be retuned '
        'without touching the leveling model; a DATA_PIN older than the column continues the curve&rsquo;s own %d&rarr;%d growth one step instead (never a constant in the client).</td></tr>' % (
            top + 1, top, top, span('XPCurve.csv#%d#XP_Account_Flat' % top, g(flat), 'g'), top - 1, fx((flat / prev - 1) * 100, 2),
            span('XPCurve.csv#%d#XP_To_Next' % (top - 1), g(prev), 'g'), top - 1, top, top - 2, top - 1),
        '    <tr><td class="lbl">Grants</td><td>Nothing. Deliberately inert.</td></tr>',
        '  </table>'])


def gen_xp_milestone_note():
    bph = battles_per_hour()
    return ('<p style="font-size:12px;color:var(--ink-faint)">*At ~<span id="xpBph">%d</span> battles/hour on autoplay &mdash; the economy simulator&rsquo;s figure '
            '(dfmc-client <code>tools/sim_econ.mjs</code> BATTLES_PER_HOUR), about %s&nbsp;s per battle. Generated by <code>tools/codex_tables.py</code>.</p>' % (bph, fx(3600 / bph, 0)))


# --- system-equipment
def soul_stage_mults():
    """play/app.js:259 SOUL_STAGE_MULT - [0, S1, S2, S3]."""
    m = re.search(r'const SOUL_STAGE_MULT = \[([\d., ]+)\];', client_file('play/app.js'))
    if not m:
        raise ValueError('play/app.js: SOUL_STAGE_MULT not found')
    return [float(x) for x in m.group(1).split(',')]


SOUL_ROWS = ['Worn', 'Rare', 'Legendary', 'Divine', 'Void']


def gen_soul_strength():
    sm = soul_stage_mults(); G = [x['Grade'] for x in grades()]
    out = ['<table>', '    <tr><th>Creature quality grade</th><th>Stage 1</th><th>Stage 2</th><th>Stage 3</th></tr>']
    for gname in SOUL_ROWS:
        q = soul_mult(G.index(gname))
        out.append('    <tr><td class="lbl">%s &times;%s</td>%s</tr>' % (gname, fx(q, 2), ''.join('<td>&times;%s</td>' % fx(q * sm[s], 2) for s in (1, 2, 3))))
    out.append('  </table>')
    out.append('  <p class="gen-note">Stage &times; grade: <code>play/app.js</code> SOUL_STAGE_MULT &times; <code>src/power.js</code> soulMultOf (<code>1 + (1/9) &times; grade index</code>). '
               'Generated by <code>tools/codex_tables.py</code>.</p>')
    return '\n'.join(out)


# --- system-pvp
def pvp_timers():
    """src/tables.json pvp_live (round_ms, bank_ms; read by src/worker.js:2325 MM_ROUND_MS / MM_BANK_MS) and src/battle_round.js:459 rampMult."""
    pl = json.loads(client_file('src/tables.json'))['pvp_live']
    m = re.search(r'function rampMult\(round\) \{ return (.*?); \}', client_file('src/battle_round.js'))
    if not m:
        raise ValueError('src/battle_round.js: rampMult not found')
    steps = [(int(r), float(x)) for r, x in re.findall(r'round >= (\d+) \? ([\d.]+)', m.group(1))]
    return pl['round_ms'] // 1000, pl['bank_ms'] // 1000, sorted(steps)


def gen_pvp_timers():
    rs, bs, steps = pvp_timers()
    xm = lambda x: ('%d' % x) if x == int(x) else ('%s' % x)
    first, last = steps[0], steps[-1]
    return '\n'.join([
        '<table>',
        '    <tr><th>Timer</th><th>Value</th><th>Rule</th></tr>',
        '    <tr><td class="lbl">Round timer (PvP)</td><td>%d s</td><td>Both players pick within it. Resolution/animation time does not count.</td></tr>' % rs,
        '    <tr><td class="lbl">Personal bank (PvP)</td><td>%d s</td><td>Drawn from only after the %d s round timer is spent, chess-clock style. Never refills during a game; resets between games of the Bo3.</td></tr>' % (bs, rs),
        '    <tr><td class="lbl">On expiry</td><td>&mdash;</td><td>The <strong>autoplay AI picks for you</strong> &mdash; the same AI that runs PvE grinding, not &ldquo;first move in the list.&rdquo; Losing time costs quality, not the game outright.</td></tr>',
        '    <tr><td class="lbl">Damage ramp (PvP)</td><td>&times;%s @ %d &rarr; &times;%s @ %d+</td><td>Replaces the 30-round hard cap and its tiebreak (2026-08-16). From round %d every hit and every lingering '
        'damage tick, both sides, is multiplied: %s from %d on and holding. A game ends only on a wipe &mdash; the ramp guarantees one, so no tiebreak is needed or exists. A hot &times;-chip beside '
        'the round counter shows the live multiplier from round %d. PvE never ramps. Replays of Competitive games ramp identically &mdash; playback must re-produce the recorded fight.</td></tr>' % (
            xm(first[1]), first[0], xm(last[1]), last[0], first[0], ', '.join('&times;%s at %d' % (xm(x), r) for r, x in steps[:-1]) + ', &times;%s' % xm(last[1]), last[0], first[0]),
        '    <tr><td class="lbl">PvE</td><td><strong>No timer</strong></td><td>Move timers are a PvP-integrity tool; against the AI there is nothing to protect and autoplay already exists for players who want speed. PvE battles instead get full crash-safe resume (below).</td></tr>',
        '  </table>',
        '  <p class="gen-note">Timers: dfmc-client <code>src/tables.json</code> <code>pvp_live</code> (read by <code>src/worker.js</code> MM_ROUND_MS / MM_BANK_MS); ramp: <code>src/battle_round.js</code> '
        '<code>rampMult</code>. Generated by <code>tools/codex_tables.py</code>.</p>'])


# --- the battles/hour prose (the retired "~30 battles/h" anchor)
def bph_txt():
    return '~%d battles/h' % battles_per_hour()


BPH_SRC = 'the economy simulator&rsquo;s figure, dfmc-client <code>tools/sim_econ.mjs</code> BATTLES_PER_HOUR'


def gen_bph_prose(tpl):
    """a sentence that restates BATTLES_PER_HOUR; {bph} is bph_txt(), {n} the bare number."""
    return lambda: tpl.format(bph=bph_txt(), n=battles_per_hour(), src=BPH_SRC)


def spawn_budget():
    return json.loads(client_file('src/tables.json'))['spawn_budget']


def gen_spawn_note():
    sb = spawn_budget(); bph = battles_per_hour()
    return ('<div class="note note-info"><p>Throughput: the refill ceiling is %d spawns/hour per floor (<code>src/tables.json</code> <code>spawn_budget</code>, %d banked) '
            '&mdash; %s&times; the %s autoplay pace (%s), so an autoplay player camping one floor rides the drip. Sustained single-floor farming is throttled at the spawner; '
            'speed builds, like everyone else, scale through floor rotation (&approx;%d per floor per pass).</p></div>' % (
                sb['per_hour'], sb['cap'], fx(sb['per_hour'] / bph, 2), bph_txt(), BPH_SRC, sb['cap']))


def gen_chase():
    """index.html 'endgame chase': gen_grading_prose's T10 Worn->Void expectation; the Void gate's p10 / p90 are the geometric
    distribution's quantiles (attempts = ln(1-q) / ln(1-p)) x the attempt cost."""
    bph = battles_per_hour(); F = ref_floor(); a = acq(F); cg, ce, div = grading_totals(); sh = a['Scrap'] * bph
    vg = [r for r in rows('grading.csv') if r['Tier'] == '10' and r['Category'] == 'Gear' and r['To_Grade'] == grades()[-1]['Grade']][0]
    c = float(vg['Cost'].split()[0]); p = float(vg['Success_Pct']) / 100
    q = lambda x: g(jsround(c * math.log(1 - x) / math.log(1 - p)))
    return '\n'.join([
        '<table>',
        '      <tr><th>One item, Worn&rarr;Void grading</th></tr>',
        '      <tr><td>Expected ~%s Scrap at T10 &asymp; %s&nbsp;h at floor %d (%s Scrap/h at %d battles/h) (Void gate alone: p10 ~%s / expected %s / p90 ~%s)</td></tr>' % (
            g(jsround(cg)), fx(cg / sh, 1), F, g(jsround(sh)), bph, q(0.1), g(jsround(c / p)), q(0.9)),
        '    </table>',
        '    <p>A marquee item taken to Void is ~%s&nbsp;h expected at floor %d, with honest odds of doubling that on a bad run. A full 12-slot Void loadout is a long, market-aggregated pursuit; '
        'Void enhancements (expected ~%s material each) are rare trade goods. Casuals buy from the market; grinders and lucky rollers supply it &mdash; that variance is what gives grade-5+ items '
        'real price discovery. Hours at %s (%s); generated by <code>tools/codex_tables.py</code>.</p>' % (fx(cg / sh, 1), F, g(jsround(ce)), bph_txt(), BPH_SRC)])


def portal_battles(n, p):
    """expected battles to string together n consecutive wins at win rate p (a loss resets the streak): (1 - p^n) / ((1 - p) p^n)."""
    return (1 - p ** n) / ((1 - p) * p ** n)


PORTAL_FLOORS = [9, 25, 55, 99]
PORTAL_P = [0.95, 0.90, 0.85, 0.80, 0.70]


def gen_portal():
    """analytics.html: floors.csv Wins_To_Clear is the streak that opens the portal; expected battles is portal_battles()."""
    fl = {int(r['Floor']): r for r in rows('floors.csv')}
    n = lambda F: int(fl[F]['Wins_To_Clear'])
    out = ['<table>', '    <tr><th>Win rate p</th>%s</tr>' % ''.join('<th>Floor %d (streak %s)</th>' % (F, n(F)) for F in PORTAL_FLOORS)]
    for i, p in enumerate(PORTAL_P):
        cells = ['~%s%s' % (g(jsround(portal_battles(n(F), p))), ' battles' if (i == 0 and j == 0) else '') for j, F in enumerate(PORTAL_FLOORS)]
        out.append('    <tr><td class="lbl">%d%%</td>%s</tr>' % (jsround(p * 100), ''.join('<td>%s</td>' % c for c in cells)))
    out.append('  </table>')
    deep = PORTAL_FLOORS[-1]; bph = battles_per_hour()
    out.append('  <p class="figcap">Expected battles to open the portal, by on-floor win rate: <code>(1 &minus; p^n) / ((1 &minus; p) p^n)</code> for a streak of n = '
               '<code>floors.csv</code> Wins_To_Clear. At %s (%s), 90%% &asymp; %s h per deep clear (floor %d); 80%% &asymp; %s h. Boss floors bypass this (always 1 battle, key-gated). '
               'Generated by <code>tools/codex_tables.py</code>.</p>' % (bph_txt(), BPH_SRC, fx(portal_battles(n(deep), 0.9) / bph, 1), deep, fx(portal_battles(n(deep), 0.8) / bph, 1)))
    return '\n'.join(out)


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
    # C17 part 3 (lane c17-gen-2, 2026-10-23)
    ('creature-base', 'index.html', gen_creature_base),
    ('level-offsets', 'index.html', gen_level_offsets),
    ('trader-ref', 'system-shadow-trader.html', gen_trader_ref),
    ('trader-m99', 'system-shadow-trader.html', gen_trader_matrix(99)),
    ('trader-m119', 'system-shadow-trader.html', gen_trader_matrix(119)),
    ('trader-moves', 'system-shadow-trader.html', gen_trader_moves),
    ('trader-worked', 'system-shadow-trader.html', gen_trader_worked),
    ('trader-example', 'system-shadow-trader.html', gen_trader_example),
    ('breed-rates', 'system-breeding.html', gen_breed_rates),
    ('breed-ichor', 'system-breeding.html', gen_breed_ichor),
    ('breed-egg-dismantle', 'system-breeding.html', gen_breed_egg_dismantle),
    ('mut-chance', 'system-mutants.html', gen_mut_chance),
    ('mut-zones', 'system-mutants.html', gen_mut_zones),
    ('st-pools', 'stat-tables.html', gen_st_pools),
    ('st-grading-prose', 'stat-tables.html', gen_grading_prose('stat')),
    ('st-income', 'stat-tables.html', gen_st_income),
    ('up-grading-prose', 'upgrading.html', gen_grading_prose('upgrading')),
    ('class-stages', 'index.html', gen_class_stages),
    ('up-soul-grading', 'upgrading.html', gen_soul_grading),
    ('up-qm-row', 'upgrading.html', gen_qm_row(None)),
    ('st-qm-row', 'stat-tables.html', gen_qm_row(None)),
    # C17 part 4 (lane a8-s5-c17-tail, 2026-10-23)
    ('codex-files', 'index.html', gen_codex_files),
    ('ultimates', 'index.html', gen_ultimates),
    ('cls-ultimates', 'classes.html', gen_ultimates),
    ('moves-budget', 'index.html', gen_moves_budget),
    ('ichor', 'index.html', gen_ichor),
    ('adv-bands', 'index.html', gen_adv_bands),
    ('zones', 'index.html', gen_zones),
    ('level-bands', 'index.html', gen_level_bands),
    ('enc-weights', 'index.html', gen_enc_weights),
    ('xp-formulas', 'system-xp.html', gen_xp_formulas),
    ('xp-player', 'system-xp.html', gen_xp_player),
    ('xp-milestone-note', 'system-xp.html', gen_xp_milestone_note),
    ('soul-strength', 'system-equipment.html', gen_soul_strength),
    ('pvp-timers', 'system-pvp.html', gen_pvp_timers),
    ('spawn-note', 'index.html', gen_spawn_note),
    ('chase', 'index.html', gen_chase),
    ('bph-realm', 'index.html', gen_bph_prose('All economy balancing is denominated in battles for this one active character ({bph} on autoplay, {src}).')),
    ('bph-econ', 'index.html', gen_bph_prose('All progression currencies flow from battles, denominated in battles ({bph} on autoplay, single active character; {src}).')),
    ('bph-integrity', 'system-integrity.html', gen_bph_prose('Rewards credited per flush are capped by elapsed real time (autoplay runs {bph}, {src}; the cap leaves headroom above it).')),
    ('bph-anchor', 'analytics.html', gen_bph_prose('The GDD already denominates the whole economy in battles ({bph} endgame, {src}).')),
    ('portal', 'analytics.html', gen_portal),
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
