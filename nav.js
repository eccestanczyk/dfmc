/* ============================================================
   HERUMON TOWER — Site Navigation (single source of truth)
   Include via <script src="nav.js"></script> on every page.
   Injects: assets/ui.css (site-wide dark-fantasy chrome),
   the ☰ menu, and the site logo. Creates a .topbar if missing.
   ============================================================ */

(function(){
  // ---- inject site-wide chrome stylesheet (idempotent) ----
  if (!document.querySelector('link[data-ht-ui]')) {
    const l = document.createElement('link');
    l.rel = 'stylesheet';
    l.href = 'assets/ui.css';
    l.setAttribute('data-ht-ui','1');
    document.head.appendChild(l);
  }

  const LINKS = [
    { href: 'hub.html',            label: 'Home' },
    { href: 'creature-codex.html', label: 'Creature Codex' },
    { href: 'type-glossary.html',  label: 'Type Glossary' },
    { href: 'floor-codex.html',    label: 'Floor Map' },
    { href: 'reliquary.html',      label: 'Reliquary' },
  { href: 'moves.html',          label: 'Moves' },
  { href: 'classes.html',        label: 'Classes' },
    { href: 'crafting.html',       label: 'Crafting' },
  { href: 'upgrading.html',      label: 'Upgrading' },
  { href: 'stat-tables.html',    label: 'Stat Tables' },
    { href: 'other-systems.html',  label: 'Other Systems' },
    { href: 'index.html',          label: 'Game Design Document' },
  ];

  const currentPage = location.pathname.split('/').pop() || 'index.html';

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
