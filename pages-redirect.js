/* pages-redirect.js — the GitHub Pages copy of the codex forwards to the game's domain.
   2026-11-03 (board N5 / rulings card T70; D: "Codex goes to the website!"): the codex is served from
   https://codex.playdfmc.com/ (a Workers static-assets site, wrangler.jsonc in this repo). GitHub Pages keeps
   serving the same tree - the dev client still reads csv from it, and old links keep working - but a page
   opened there forwards to the same path on the new host, search and hash intact
   (eccestanczyk.github.io/dfmc/creature.html?id=DFMC-001 -> codex.playdfmc.com/creature.html?id=DFMC-001).
   nav.js carries this same check for every page that loads it; this file is for the eight pages that do not
   (dev, floor-assets, pending-art, pending-crop, system-auto-pvp, system-premium-shop, system-realms,
   system-shadow-trader). Keep the two copies identical. */
(function(){
  if (location.hostname === 'eccestanczyk.github.io') {
    location.replace('https://codex.playdfmc.com' + location.pathname.replace(/^\/dfmc(?=\/|$)/, '') + location.search + location.hash);
  }
})();
