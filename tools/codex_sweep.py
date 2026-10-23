"""codex_sweep.py - C17 part 3 (dfmc-client lane c17-gen-2, 2026-10-23): what is still pasted.

Counts, per page, the numbers in table cells that are neither inside a <!-- gen:NAME --> block (tools/codex_tables.py)
nor a data-csv span (csv-bind.js / tools/codex_numbers.py). Changelogs, <code>, <pre>, <script> and headers are skipped.
Not a gate: many such numbers are not game data (hosting costs, screen sizes, research, credits). It is the worklist.
A dated historical record (a table of what was measured on a past date, deliberately not live) is wrapped in
    <!-- dated:NAME --> ... <!-- /dated:NAME -->
and skipped like a gen block; the page states the date above it. Use it only for records, never to hide live numbers
(C17 part 4, dfmc-client lane a8-s5-c17-tail, 2026-10-23).
  python tools/codex_sweep.py [SITE]
"""
import glob, os, re, sys
SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NUM = re.compile(r'(?<![\w#.-])\d[\d,]*(?:\.\d+)?%?')
tot = 0; rows = []
for p in sorted(glob.glob(os.path.join(SITE, '*.html'))):
    s = open(p, encoding='utf-8').read()
    s = re.split(r'<h2[^>]*>\s*Changelog', s)[0]
    s = re.sub(r'<!-- gen:([\w-]+) -->.*?<!-- /gen:\1 -->', ' ', s, flags=re.S)
    s = re.sub(r'<!-- dated:([\w-]+) -->.*?<!-- /dated:\1 -->', ' ', s, flags=re.S)
    s = re.sub(r'<(script|style|code|pre)\b.*?</\1>', ' ', s, flags=re.S)
    s = re.sub(r'<span data-csv=[^>]*>[^<]*</span>', ' ', s)
    s = re.sub(r'<th\b.*?</th>', ' ', s, flags=re.S)
    cells = re.findall(r'<td\b[^>]*>(.*?)</td>', s, flags=re.S)
    n = 0; ex = []
    for c in cells:
        t = re.sub(r'<[^>]+>', ' ', c)
        t = re.sub(r'&\w+;', ' ', t)
        f = NUM.findall(t)
        n += len(f)
        if f and len(ex) < 4: ex.append(t.strip()[:50])
    if n:
        rows.append((n, os.path.basename(p), ex)); tot += n
for n, p, ex in sorted(rows, reverse=True):
    print('%5d  %-34s %s' % (n, p, ' | '.join(ex)))
print('TOTAL', tot, 'numbers in unbound table cells on', len(rows), 'pages')
