/* ============================================================
   HERUMON TOWER — Site Navigation (single source of truth)
   Include via <script src="nav.js"></script> on every page.
   Expects a <div class="topbar"> to exist — injects the ☰ menu
   as the first child.
   ============================================================ */

(function(){
  const LINKS = [
    { href: 'hub.html',            label: 'Home' },
    { href: 'creature-codex.html', label: 'Creature Codex' },
    { href: 'floor-codex.html',    label: 'Floor Map' },
    { href: 'reliquary.html',      label: 'Reliquary' },
    { href: 'index.html?tab=equipment', label: 'Crafting' },
    { href: 'index.html',          label: 'Game Design Document' },
  ];

  const currentPage = location.pathname.split('/').pop() || 'index.html';

  function buildNav() {
    const wrap = document.createElement('div');
    wrap.className = 'site-nav';
    wrap.style.cssText = 'position:relative;z-index:20;flex-shrink:0;';

    const btn = document.createElement('button');
    btn.textContent = '☰';
    btn.style.cssText = 'font-family:Cinzel,serif;font-size:18px;background:none;border:1px solid #5c462c;color:#cfa650;padding:5px 10px;cursor:pointer;line-height:1;';
    btn.onclick = function(e) {
      e.stopPropagation();
      const m = wrap.querySelector('.site-nav-menu');
      m.style.display = m.style.display === 'flex' ? 'none' : 'flex';
    };

    const menu = document.createElement('div');
    menu.className = 'site-nav-menu';
    menu.style.cssText = 'display:none;position:absolute;top:100%;left:0;margin-top:6px;min-width:220px;background:#1e1710;border:1px solid #5c462c;box-shadow:0 8px 24px rgba(0,0,0,0.6);flex-direction:column;z-index:30;';

    LINKS.forEach(function(link, i) {
      const a = document.createElement('a');
      a.href = link.href;
      a.textContent = link.label;
      const isCurrent = currentPage === link.href;
      a.style.cssText = 'font-family:Cinzel,serif;font-size:13px;font-weight:600;letter-spacing:0.04em;text-decoration:none;padding:10px 16px;'
        + (i < LINKS.length - 1 ? 'border-bottom:1px solid #3a2c1a;' : '')
        + (isCurrent ? 'color:#cfa650;background:rgba(124,21,25,0.15);' : 'color:#c2ae8b;');
      a.onmouseenter = function(){ if(!isCurrent) this.style.color='#e6c66d'; };
      a.onmouseleave = function(){ if(!isCurrent) this.style.color='#c2ae8b'; };
      menu.appendChild(a);
    });

    wrap.appendChild(btn);
    wrap.appendChild(menu);

    // Close on outside click
    document.addEventListener('click', function(e) {
      if (!wrap.contains(e.target)) menu.style.display = 'none';
    });

    return wrap;
  }

  // Inject into topbar (first child) or create a topbar if none exists
  const topbar = document.querySelector('.topbar');
  if (topbar) {
    // Remove any old inline nav
    const old = topbar.querySelector('.site-nav');
    if (old) old.remove();
    topbar.insertBefore(buildNav(), topbar.firstChild);
  }
})();
