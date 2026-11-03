# workflow/ — the team's codex pages (never published)

D 2026-11-03: "This is now player facing. If we need any of the info on the site for our workflow, it should be
cleaned up and moved somewhere else." These pages left the public codex (codex.playdfmc.com and the GitHub Pages
copy) for this directory. Both publishers exclude it: `.assetsignore` + `tools/deploy_codex.sh` (codex host) and
`.github/workflows/pages.yml` (Pages). `_redirects` sends the old public URLs to `hub.html`.

Open them locally: serve the dfmc root (`python -m http.server 8000` in `E:\Herumon-Tower\dfmc`) and browse
`http://localhost:8000/workflow/<page>`. Each page carries `<base href="../">`, so its css, csv, art and links
resolve from the root exactly as before the move.

| page | what it is |
|---|---|
| index.html | the Game Design Document (codex_tables.py gen blocks) |
| dev.html | dev dashboard |
| admin-backend.html | backend, save & anti-cheat design |
| analytics.html | analytics & telemetry design |
| feedback-pipeline.html | community feedback pipeline design |
| checklist.html | implementation checklist |
| research.html | research entries (cited by tools and OPS) |
| system-networking.html | networking architecture, endpoints, trust boundary (owning page; changelog) |
| system-integrity.html | save, economy & anti-cheat (owning page; changelog) |
| system-client-shell.html | client shell & platform rendering, Taskbar mode, the Rift (owning page; changelog) |
| system-stage.html | the 1920x1080 stage and fitScale (owning page; changelog) |
| system-adventure-log.html | the retired adventure log, record only |
| crafting.html | crafting, archived |
| vfx.html, audio.html | VFX/AFX and audio review tools |
| move-icons.html | move effect icon review |
| floor-assets.html, pending-art.html, pending-crop.html | art pipeline tools |
| PIPELINE.md, ASSET_PIPELINE.md | art pipeline notes |
| changelogs/ | each player page's changelog and team notes (below) |

`dfmc-client/tools/codex_page.py` lists these as `workflow/<page>.html`; a bare name (`--changelog system-networking.html`)
still finds them.

## changelogs/ - the player pages' team notes (2026-11-04)

A player page (repo root, `tutorials/`) carries no changelog, no implementation notes and no ON DEV marker, not even
hidden: the codex is player facing (D 2026-11-03). Each player page's dated changelog (newest first, `On dev.` until
release-ritual step 12 flips it to SHIPPED IN <ver>) and the team notes that left it live in
`workflow/changelogs/<page>.html` (`tutorials/<page>` -> `changelogs/tutorials/<page>`). A change that is only on dev
leaves the player page alone; its entry carries `At release: <the page edit>` and step 12 applies it
(`dfmc-client/tools/release_sweep.py` lists them). `python tools/codex_page.py --changelog <page>` (dfmc-client) prints
the file and the shape. Each file carries `<base href="../../">`, so its links resolve from the root.
