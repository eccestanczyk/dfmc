# dfmc

The Herumon Tower codex: the player-facing static pages at this root (`hub.html` is the landing; `/` serves it),
their csv under `codex/`, the thumbs and images the pages load, and the game's data (`codex/*.csv`, the art) that the
client pins by commit. The team's own pages (the GDD, dev dashboard, networking / integrity / shell / stage notes,
research, review tools) live in `workflow/` and are never published (D 2026-11-03) — see `workflow/README.md`.

## Where it is served

- **https://codex.playdfmc.com/** — the codex site, since 2026-11-03 (board N5 / rulings card T70; D: "Codex goes
  to the website!"). A Cloudflare Worker with static assets and no script, `dfmc-codex`, configured by
  `wrangler.jsonc` here; a custom domain on the playdfmc.com zone. The game's Help / Privacy / Terms / Credits rows
  and the info panels' "more" links open pages here.
- **https://eccestanczyk.github.io/dfmc/** — GitHub Pages, the old host, deployed by `.github/workflows` on every push
  to `main`. It keeps serving the same tree: the dev client reads csv from it live, and old links keep working, but a
  page opened there forwards to the same path on codex.playdfmc.com (`nav.js`; `pages-redirect.js` for the few
  pages that do not load `nav.js`).
- The release client reads its data and art from the game's own R2 host at the DATA_PIN (`art.playdfmc.com`, lane
  artr2) — not from either site.

## Publishing codex.playdfmc.com

    bash tools/deploy_codex.sh              # export HEAD into _site/ (git-ignored) and deploy
    bash tools/deploy_codex.sh --dry-run    # export only: prints the file count and size

The checkout is sparse and blob-less (`codex/images`, `floors`, `_parking` are not on disk), so the script publishes a
`git archive` of the committed tree, not the working tree, minus what nobody serves (`codex/images/originals`, the
ground-plate png masters, `_parking`, `workflow`, `archive`, `tools`, `scripts`, the root `*.md` — the same filter the Pages workflow applies;
`.assetsignore` is the second copy of that list). Deploy after the push to `main`, so the two hosts carry the same
tree. The token comes from `dfmc-client/tools/cf_wrangler.sh`. Limits: 20,000 files, 25 MiB per file; the script
prints the count and refuses an oversize file. Verify: `hub.html`, a `system-*.html` page and
`creature.html?id=DFMC-001` render with their csv and thumbs; an unknown path answers `404.html`.

The release ritual (`dfmc-client/docs/release-ritual.md`, step 12) names this deploy as part of a game release
whenever the codex changed.
