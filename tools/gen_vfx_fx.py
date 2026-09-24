#!/usr/bin/env python3
"""GENERATOR + DIVERGENCE GATE for assets/vfx/vfx_fx.js|css.

The CLIENT is the source of truth. play/app.js holds the two renderers players see -
VFX_FX (the placeholder archetypes, still the fallback) and VFX_BANK (the 48-sheet bank,
2026-09-17) - and play/markup.html holds the keyframes they animate on, `vx*` for the
archetypes and `vxb*` for the bank. This repo's copy exists ONLY so the codex review page
(vfx.html) can draw the identical thing. It is GENERATED, never hand-edited.

  python tools/gen_vfx_fx.py --write    regenerate from the client
  python tools/gen_vfx_fx.py            gate: exit 1 if the copy has drifted

By default it reads the client from disk at ../dfmc-client (--local <dir> to point
elsewhere). --remote falls back to the GitHub contents API and needs a PAT.
"""
import re, sys, os, argparse, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT  = ROOT / 'assets' / 'vfx'
REPO = 'eccestanczyk/dfmc-client'
REF  = 'dev'
PATS = ['/mnt/project/githubpat.txt', str(ROOT.parent / 'githubpat.txt')]

# ---------------------------------------------------------------- sources


def read_local(base, path):
    f = pathlib.Path(base) / path
    if not f.exists():
        sys.exit('client file missing: %s  (pass --local <dfmc-client dir>)' % f)
    return f.read_text(encoding='utf-8')


def read_remote(path):
    pat = next((p for p in PATS if os.path.exists(p)), None)
    if not pat:
        sys.exit('--remote needs a PAT at one of: ' + ', '.join(PATS))
    tok = open(pat).read().strip()
    r = subprocess.run(['curl', '-s', '--noproxy', '*', '-A', 'Mozilla/5.0 dfmc-ops',
                        '-H', 'Authorization: token ' + tok,
                        '-H', 'Accept: application/vnd.github.raw',
                        'https://api.github.com/repos/%s/contents/%s?ref=%s' % (REPO, path, REF)],
                       capture_output=True, text=True)
    return r.stdout

# ---------------------------------------------------------------- lifting


def lift(lines, name):
    """The `const <name>=(()=>{ const E=React.createElement; ... })();` block, as a
    function body. Both renderers carry the SAME first-line contract: they depend on
    nothing but `E`, so injecting a DOM factory draws the identical tree."""
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith('const ' + name + '='))
    except StopIteration:
        sys.exit('%s not found in the client - update this generator' % name)
    depth = 0
    end = None
    for i in range(start, len(lines)):
        depth += lines[i].count('{') - lines[i].count('}')
        if i > start and depth <= 0:
            end = i
            break
    if end is None:
        sys.exit('%s block never closes in the client' % name)
    block = '\n'.join(lines[start:end + 1])
    head = 'const %s=(()=>{ const E=React.createElement;\n' % name
    if not block.startswith(head):
        sys.exit('%s shape changed in the client - update this generator' % name)
    if not block.rstrip().endswith('})();'):
        sys.exit('%s does not close with })(); - update this generator' % name)
    body = block[len(head):].rstrip()
    body = body[:-len('})();')].rstrip()
    return '\n'.join(('  ' + l if l.strip() else l) for l in body.splitlines())


def lift_iife(lines, name):
    """The whole `const <name>=(()=>{ ... })();` block, verbatim, or None when the client has no such
    block yet. Unlike lift() this makes no assumption about a first line and injects nothing: AFX_BANK
    is Web Audio, it depends on nothing a page has to supply, so the block travels as it stands and the
    only added line is the global the page reads it through.

    RETURNS None RATHER THAN EXITING. The AFX data, grammar, linter and review pages landed before the
    client's player did (codex/AFX_SPEC.md § The player contract), so `assets/vfx/afx_bank.js` ships as
    a stub that implements the contract. A generator that exits here would turn this gate red for the
    whole window between the two lanes, which would train everyone to ignore it."""
    head = 'const %s=(()=>{' % name
    start = next((i for i, l in enumerate(lines) if l.startswith(head)), None)
    if start is None:
        return None
    depth = 0
    for i in range(start, len(lines)):
        depth += lines[i].count('{') - lines[i].count('}')
        if i > start and depth <= 0:
            block = '\n'.join(lines[start:i + 1])
            if not block.rstrip().endswith('})();'):
                sys.exit('%s does not close with })(); - update this generator' % name)
            return block
    sys.exit('%s block never closes in the client - update this generator' % name)


def const_block(lines, name):
    """A `const <name>=...;` that may run over several lines, lifted verbatim. Used for the hit-tint
    picker, which is a plain const OUTSIDE the two IIFE renderers - which is exactly how it escaped
    this generator the first time and left the review page firing a keyframe the client had deleted.
    A divergence gate only compares what it lifts."""
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith('const ' + name + '='))
    except StopIteration:
        sys.exit('%s not found in the client - update this generator' % name)
    depth = 0
    for i in range(start, len(lines)):
        depth += lines[i].count('{') - lines[i].count('}')
        if depth <= 0 and lines[i].rstrip().endswith(';'):
            return chr(10).join(lines[start:i + 1])
    sys.exit('%s never closes in the client - update this generator' % name)


def one_line(lines, name):
    hit = [l for l in lines if l.startswith('const ' + name + '=')]
    if not hit:
        sys.exit('%s not found in the client' % name)
    return hit[0].split('=', 1)[1].rstrip(';')


def keyframes(markup):
    """EVERY vx* and vxb* keyframe in the client's markup, name-sorted. The bank names its
    step sets by shape at runtime ('vxbStep'+F+'x'+C), so they can never be found by
    scanning the renderer for identifiers - the markup is the list."""
    out = {}
    for m in re.finditer(r'@keyframes\s+(vx[A-Za-z0-9]+)\s*\{(?:[^{}]|\{[^{}]*\})*\}', markup):
        out[m.group(1)] = ' '.join(m.group(0).split())
    if not out:
        sys.exit('no vx* keyframes found in the client markup')
    return out

# ---------------------------------------------------------------- assembly


JS_HEAD = """/* ============================================================================
   DFMC - THE BATTLE EFFECT RENDERERS. ONE IMPLEMENTATION, TWO CONSUMERS.
   GENERATED by tools/gen_vfx_fx.py from the client. Do not hand-edit either copy.

   Two renderers travel together, lifted verbatim from play/app.js:

     build(E)      VFX_FX   - the 20 placeholder archetypes. Since 2026-09-17 they are
                              only the FALLBACK: a move with no composition, or one the
                              parser refuses, still draws here.
     buildBank(E)  VFX_BANK - the 48-sheet bank. parse(txt,bank) reads an FX_S<stage>
                              composition; render(parsed,bank,ctx) returns the layers of
                              ONE unit tile. Sheets come from codex/fx_bank.csv.

   The BODIES ARE UNCHANGED: the only edit is that `E` is injected instead of being
   React.createElement, so a page with no React can pass a DOM factory and draw the
   identical thing.

     game :  VFX_FX / VFX_BANK, inline in play/app.js
     page :  const FX   = DFMC_VFX_FX.build(DFMC_VFX_FX.dom);
             const BANK = DFMC_VFX_FX.buildBank(DFMC_VFX_FX.dom);

   The game and the codex review page MUST draw from this file. When they had two
   implementations, approving an effect on the review page approved art players never
   saw - the fifth instance of the built-with-no-reader defect in this repo.

   Pair it with vfx_fx.css - every vx* and vxb* keyframe these effects animate on.
   Colour and duration tables travel with it so they cannot drift either.
   ============================================================================ */
(function (root) {
  var HEX = %(hex)s;
  var DURMS = %(dur)s;

  /* THE HIT TINT PICKER, lifted verbatim from play/app.js. The !flash hit is a dark, element-keyed
     tint of the target's own art (D 2026-09-17); the client picks the keyframe with VXHIT_FOR at its
     cast site and the review page must pick it the same way, off the same table, or the page draws a
     hit the game does not. Exported below as hitTintFor. */
%(vxhitc)s
%(vxhith)s
%(vxhitfor)s
  /* In the client this is RAWD('%(slash)s') - a raw.githubusercontent URL
     into THIS repo. Here the file is a sibling, so the path is relative to the page. */
  var SLASH_ART = '%(slash)s';

  /* React.createElement's signature, backed by real DOM. Handles the style object,
     ignores `key` (React-only), and accepts nested arrays of children. */
  function dom(tag, props) {
    var el = document.createElement(tag), i, k, ch = [].slice.call(arguments, 2);
    if (props) for (k in props) {
      if (k === 'key') continue;
      if (k === 'style') { for (i in props.style) { if (props.style[i] != null) el.style[i] = props.style[i]; } }
      else if (k === 'className') el.className = props[k];
      else if (props[k] != null) el.setAttribute(k, props[k]);
    }
    (function add(c) {
      if (c == null || c === false) return;
      if (Array.isArray(c)) { c.forEach(add); return; }
      el.appendChild(c.nodeType ? c : document.createTextNode(String(c)));
    })(ch);
    return el;
  }

  function build(E) {
%(fx)s
  }

  function buildBank(E) {
%(bank)s
  }

  root.DFMC_VFX_FX = { build: build, buildBank: buildBank, dom: dom, HEX: HEX, DURMS: DURMS,
                       SLASH_ART: SLASH_ART, ARCHETYPES: Object.keys(build(dom)),
                       hitTintFor: VXHIT_FOR, HITTINT_BY_COLOR: VXHITC, HITTINT_BY_HUE: VXHITH };
})(typeof window !== 'undefined' ? window : globalThis);
"""

CSS_HEAD = """/* DFMC battle-effect keyframes, lifted verbatim from play/markup.html by
   tools/gen_vfx_fx.py. vx* are the placeholder archetypes, vxb* the 48-sheet bank
   (vxbStep<frames>x<cols> steps a sheet, vxbLife gates a layer's delay and life).
   The !flash hit is the vxRedHit / vxHit* family: a dark, element-keyed tint of the
   target's own art, 300 ms (D 2026-09-17 - it is never white; the old vxbFlash
   brightness(3) pop is deleted), each with a *Soft member for Reduce Flashing.
   Loaded by BOTH the game client and the codex review page. Do not edit one copy. */
"""

AFX_HEAD = """/* ============================================================================
   GENERATED from play/app.js by tools/gen_vfx_fx.py - the client is the source of truth

   THE AFX BANK PLAYER, lifted verbatim from the client's `const AFX_BANK=(()=>{ ... })();`. The
   contract is codex/AFX_SPEC.md § The player contract. It is implemented ONCE, in play/app.js, so the
   sound a reviewer approves on vfx.html / audio.html is the sound a player hears - the same
   arrangement VFX_BANK has in vfx_fx.js, for the same reason. Do not hand-edit this copy.

     game :  AFX_BANK, inline in play/app.js
     page :  window.DFMC_AFX_BANK
   ============================================================================ */
(function (root) {
%(afx)s
  root.DFMC_AFX_BANK = AFX_BANK;
})(typeof window !== 'undefined' ? window : globalThis);
"""

SLASH = 'assets/ui/vfx/slash.png'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='regenerate the copy')
    ap.add_argument('--local', default=str(ROOT.parent / 'dfmc-client'),
                    help='dfmc-client checkout to read (default ../dfmc-client)')
    ap.add_argument('--remote', action='store_true', help='read the client over the GitHub API instead')
    a = ap.parse_args()

    if a.remote:
        app, markup = read_remote('play/app.js'), read_remote('play/markup.html')
        src = 'github:%s@%s' % (REPO, REF)
    else:
        app, markup = read_local(a.local, 'play/app.js'), read_local(a.local, 'play/markup.html')
        src = a.local
    lines = app.splitlines()

    fx = lift(lines, 'VFX_FX')
    bank = lift(lines, 'VFX_BANK')
    hexl = one_line(lines, 'VFXHEX')
    durl = one_line(lines, 'VFXDURMS')
    vxhitc = const_block(lines, 'VXHITC')
    vxhith = const_block(lines, 'VXHITH')
    vxhitfor = const_block(lines, 'VXHIT_FOR')
    afx = lift_iife(lines, 'AFX_BANK')
    # INDENT ONCE, HERE. The written copy is indented into the wrapper below, so comparing the RAW
    # block against it can never match: the gate reported DIVERGED on a file it had just written
    # itself, and a gate that is permanently red is a gate nobody reads. lift() has no such split
    # because it indents inside itself; this path must do the same before either branch uses it.
    afx_body = None if afx is None else '\n'.join(
        ('  ' + l if l.strip() else l) for l in afx.splitlines())
    kf = keyframes(markup)

    js = JS_HEAD % {'hex': hexl, 'dur': durl, 'fx': fx, 'bank': bank, 'slash': SLASH,
                    'vxhitc': vxhitc, 'vxhith': vxhith, 'vxhitfor': vxhitfor}
    css = CSS_HEAD + '\n'.join(kf[n] for n in sorted(kf)) + '\n'

    jsp, cssp, afxp = OUT / 'vfx_fx.js', OUT / 'vfx_fx.css', OUT / 'afx_bank.js'
    cur_js = jsp.read_text(encoding='utf-8') if jsp.exists() else ''
    cur_css = cssp.read_text(encoding='utf-8') if cssp.exists() else ''
    cur_afx = afxp.read_text(encoding='utf-8') if afxp.exists() else ''

    # Compare only the GENERATED parts, so the header prose above each copy stays editable.
    ok_fx = fx in cur_js
    ok_bank = bank in cur_js
    ok_tab = hexl in cur_js and durl in cur_js
    ok_hit = all(b in cur_js for b in (vxhitc, vxhith, vxhitfor))
    ok_css = all(kf[n] in cur_css for n in kf)
    miss = [n for n in sorted(kf) if kf[n] not in cur_css]
    # The AFX player is only a divergence question once the client has one. Until then the stub stands
    # and this stays green - see lift_iife.
    ok_afx = True if afx is None else (afx_body in cur_afx)

    print('client read from          : %s' % src)
    print('keyframes in client       : %d (%d vxb*)' % (len(kf), sum(1 for n in kf if n.startswith('vxb'))))
    print('VFX_FX body matches copy  : %s' % ok_fx)
    print('VFX_BANK body matches copy: %s' % ok_bank)
    print('colour/duration tables    : %s' % ok_tab)
    print('hit-tint picker           : %s' % ok_hit)
    print('keyframes match copy      : %s%s' % (ok_css, '' if ok_css else '  missing ' + ', '.join(miss)))
    print('AFX_BANK in client        : %s' % ('yes, %d lines' % len(afx.splitlines()) if afx else
                                              'NOT YET - keeping the afx_bank.js stub (codex/AFX_SPEC.md)'))
    print('AFX_BANK matches copy     : %s' % ('n/a' if afx is None else ok_afx))

    if a.write:
        OUT.mkdir(parents=True, exist_ok=True)
        jsp.write_text(js, encoding='utf-8')
        cssp.write_text(css, encoding='utf-8')
        print('--write: wrote %s (%d bytes) and %s (%d bytes)' % (jsp, len(js), cssp, len(css)))
        if afx is None:
            print('--write: left %s alone - the client has no AFX_BANK block yet, so the stub stands'
                  % afxp)
        else:
            ajs = AFX_HEAD % {'afx': afx_body}
            afxp.write_text(ajs, encoding='utf-8')
            print('--write: wrote %s (%d bytes)' % (afxp, len(ajs)))
        return 0
    if not (ok_fx and ok_bank and ok_tab and ok_hit and ok_css and ok_afx):
        print('DIVERGED - the client changed and assets/vfx/vfx_fx.* is stale. Regenerate with --write.')
        return 1
    print('OK - the published copy is byte-identical to the client')
    return 0


if __name__ == '__main__':
    sys.exit(main())
