/* ============================================================
   HERUMON TOWER — Site Navigation (single source of truth)
   Include via <script src="nav.js"></script> on every page.
   Injects: assets/ui.css (site-wide dark-fantasy chrome),
   the ☰ menu, and the site logo. Creates a .topbar if absent.
   ============================================================ */

(function(){
  // ---- the GitHub Pages copy forwards to the game's domain (2026-11-03, board N5 / card T70; D: "Codex goes to
  // the website!") ---- the codex is served from https://codex.playdfmc.com/ (wrangler.jsonc, tools/deploy_codex.sh).
  // Pages keeps serving the tree (the dev client reads csv from it; old links keep working) but a page opened there
  // goes to the same path on the new host, search and hash intact. pages-redirect.js is this same check for the
  // eight pages that do not load nav.js - keep the two identical.
  if (location.hostname === 'eccestanczyk.github.io') {
    location.replace('https://codex.playdfmc.com' + location.pathname.replace(/^\/dfmc(?=\/|$)/, '') + location.search + location.hash);
    return;
  }

  // ---- workflow sections stay off the public page (D 2026-11-03: "This is now player facing") ----
  // The rules pages carry the team's changelog and implementation notes; tools/codex_page.py and the bug lanes read
  // them from the source. A visitor never sees them; ?admin=1 (admin.js) shows them. Same block in pages-redirect.js.
  function hideWorkflowSections(){
    if (/\/workflow\//.test(location.pathname)) return;   // the team's own pages show everything
    try { if (localStorage.getItem('dfmc_admin') === '1') return; } catch (e) {}
    document.querySelectorAll('h2,h3').forEach(function(h){
      if (!/^\s*(changelog|implementation notes)\b/i.test(h.textContent)) return;
      var lvl = +h.tagName[1], n = h.nextElementSibling;
      h.style.display = 'none';
      while (n && !(/^H[1-6]$/.test(n.tagName) && +n.tagName[1] <= lvl)) { n.style.display = 'none'; n = n.nextElementSibling; }
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', hideWorkflowSections); else hideWorkflowSections();

  // ---- always-fresh content ----
  // GitHub Pages serves everything with `cache-control: max-age=600` and gives
  // us no way to change that, so the browser happily shows a 10-minute-stale
  // codex. This service worker is network-first, so edits appear on reload.
  // `updateViaCache:'none'` keeps sw.js itself out of the HTTP cache.
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function(){
      navigator.serviceWorker.register('sw.js', { updateViaCache: 'none' })
        .then(function(reg){ reg.update(); })
        .catch(function(){ /* non-fatal: site works without it */ });
    });
  }

  // ---- inject site-wide chrome stylesheet (idempotent) ----
  if (!document.querySelector('link[data-ht-ui]')) {
    const l = document.createElement('link');
    l.rel = 'stylesheet';
    l.href = 'assets/ui.css?v=2';
    l.setAttribute('data-ht-ui','1');
    document.head.appendChild(l);
  }

  // Player pages only (D 2026-11-03: the codex is player facing). The workflow pages live in workflow/, unpublished.
  const LINKS = [
    { href: 'hub.html',            label: 'Home' },
    { href: 'tutorials/index.html', label: 'Tutorials' },
    { href: 'creature-codex.html', label: 'Creature Codex' },
    { href: 'type-glossary.html',  label: 'Type Glossary' },
    { href: 'floor-codex.html',    label: 'Floor Map' },
    { href: 'bosses.html',         label: 'Bosses' },
    { href: 'reliquary.html',      label: 'Reliquary' },
    { href: 'eggs.html',           label: 'Eggs' },
  { href: 'classes.html',        label: 'Classes' },
  { href: 'upgrading.html',      label: 'Upgrading' },
  { href: 'stat-tables.html',    label: 'Stat Tables' },
  { href: 'droptables.html',     label: 'Droptables' },
    { href: 'other-systems.html',  label: 'Other Systems' },
  ];

  const currentPage = location.pathname.split('/').pop() || 'hub.html';

  function buildNav() {
    const wrap = document.createElement('div');
    wrap.className = 'site-nav';

    const btn = document.createElement('button');
    btn.textContent = '☰';
    btn.setAttribute('aria-label','Site menu');
    btn.onclick = function(e) {
      e.stopPropagation();
      const m = wrap.querySelector('.site-nav-menu');
      m.style.display = m.style.display === 'flex' ? 'none' : 'flex';
    };

    const menu = document.createElement('div');
    menu.className = 'site-nav-menu';

    LINKS.forEach(function(link) {
      const a = document.createElement('a');
      a.href = link.href;
      a.textContent = link.label;
      if (currentPage === link.href) a.className = 'current';
      menu.appendChild(a);
    });

    wrap.appendChild(btn);
    wrap.appendChild(menu);

    document.addEventListener('click', function(e) {
      if (!wrap.contains(e.target)) menu.style.display = 'none';
    });

    return wrap;
  }

  // ---- topbar: use existing or create one ----
  let topbar = document.querySelector('.topbar');
  if (!topbar) {
    topbar = document.createElement('div');
    topbar.className = 'topbar';
    const h1 = document.createElement('h1');
    h1.textContent = (document.title.split('—')[0] || 'HERUMON TOWER').trim();
    topbar.appendChild(h1);
    document.body.insertBefore(topbar, document.body.firstChild);
  }

  const old = topbar.querySelector('.site-nav');
  if (old) old.remove();
  topbar.insertBefore(buildNav(), topbar.firstChild);

  // ---- site logo — right side, links home ----
  if (!topbar.querySelector('.site-logo')) {
    const logoLink = document.createElement('a');
    logoLink.href = 'hub.html';
    logoLink.className = 'site-logo';
    const logoImg = document.createElement('img');
    logoImg.src = 'assets/logo.png';
    logoImg.alt = 'Herumon Tower';
    logoLink.appendChild(logoImg);
    topbar.appendChild(logoLink);
  }
})();
