/* pages-redirect.js — the GitHub Pages copy of the codex forwards to the game's domain.
   2026-11-03 (board N5 / rulings card T70; D: "Codex goes to the website!"): the codex is served from
   https://codex.playdfmc.com/ (a Workers static-assets site, wrangler.jsonc in this repo). GitHub Pages keeps
   serving the same tree - the dev client still reads csv from it, and old links keep working - but a page
   opened there forwards to the same path on the new host, search and hash intact
   (eccestanczyk.github.io/dfmc/creature.html?id=DFMC-001 -> codex.playdfmc.com/creature.html?id=DFMC-001).
   nav.js carries this same check for every page that loads it; this file is for the pages that do not
   (system-auto-pvp, system-premium-shop, system-realms, system-shadow-trader, the index.html stub; dev,
   floor-assets, pending-art and pending-crop moved to workflow/, unpublished, D 2026-11-03). Keep the two copies identical. */
(function(){
  if (location.hostname === 'eccestanczyk.github.io') {
    location.replace('https://codex.playdfmc.com' + location.pathname.replace(/^\/dfmc(?=\/|$)/, '') + location.search + location.hash);
    return;
  }

  // ---- workflow sections stay off the public page (D 2026-11-03: "This is now player facing") ----
  // The rules pages carry the team's changelog and implementation notes; tools/codex_page.py and the bug lanes read
  // them from the source. A visitor never sees them; ?admin=1 (admin.js) shows them. Same block in nav.js.
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
})();
