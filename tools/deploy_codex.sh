#!/bin/bash
# deploy_codex.sh — publish the codex site to https://codex.playdfmc.com/ (Worker `dfmc-codex`, static assets only;
# wrangler.jsonc at this repo's root). 2026-11-03, board N5 / rulings card T70; D: "Codex goes to the website!"
#
# WHY AN EXPORT, NOT THE CHECKOUT: this checkout is sparse and blob-less (codex/images, floors and _parking are not
# on disk; `git sparse-checkout list`), so wrangler pointed at the working tree would publish a codex with no art.
# `git archive` reads the committed tree and fetches the missing blobs on demand, minus the trees nobody serves
# (the same filter the GitHub Pages workflow applies: codex/images/originals and the ground-plate png masters,
# plus _parking / archive / tools / scripts). .assetsignore rides along in the export as the second filter.
#
#   bash tools/deploy_codex.sh                 export HEAD into _site/ and deploy
#   bash tools/deploy_codex.sh --dry-run       export only (prints the file count and size, deploys nothing)
#   CODEX_REF=origin/main bash tools/deploy_codex.sh      export another ref (what Pages serves is main)
#
# Deploy what is PUSHED: the Pages copy forwards to this host, so the two must carry the same tree.
# The token comes from dfmc-client/tools/cf_wrangler.sh (DFMC_CLIENT overrides the checkout path).
set -o pipefail
cd "$(dirname "$0")/.." || exit 1
REF="${CODEX_REF:-HEAD}"
CLIENT="${DFMC_CLIENT:-E:/Herumon-Tower/dfmc-client}"
SITE="$PWD/_site"
[ -f "$CLIENT/tools/cf_wrangler.sh" ] || { echo "deploy_codex: no $CLIENT/tools/cf_wrangler.sh (set DFMC_CLIENT)" >&2; exit 2; }
rm -rf "$SITE" && mkdir -p "$SITE" || exit 1
echo "deploy_codex: exporting $(git rev-parse --short "$REF") into _site/ ..."
git archive "$REF" \
  ':(exclude)codex/images/originals' ':(exclude,glob)floors/ground_plates/*.png' \
  ':(exclude)_parking' ':(exclude)archive' ':(exclude)tools' ':(exclude)scripts' ':(exclude).github' . \
  | tar -x -C "$SITE" || { echo "deploy_codex: git archive failed" >&2; exit 1; }
echo "deploy_codex: $(find "$SITE" -type f | wc -l | tr -d ' ') files, $(du -sh "$SITE" | cut -f1) (limits: 20,000 files, 25 MiB per file)"
big=$(find "$SITE" -type f -size +25M); [ -z "$big" ] || { echo "deploy_codex: over 25 MiB, cannot be served:"; echo "$big"; exit 1; }
if [ "$1" = "--dry-run" ]; then echo "deploy_codex: dry run, not deploying"; exit 0; fi
bash "$CLIENT/tools/cf_wrangler.sh" deploy --config "$PWD/wrangler.jsonc" "$@"
rc=$?
[ $rc -eq 0 ] && echo "deploy_codex: verify  curl -sI https://codex.playdfmc.com/hub.html | head -n 1"
exit $rc
