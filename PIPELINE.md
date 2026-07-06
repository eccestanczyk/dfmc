# DFMC ART PIPELINE — HARD GATES (load first, every batch)

Claude MUST read this file at the start of every art batch and print the per-action
compliance line for each backlog item before reporting done. No exceptions.

## MODEL
- Generation model = `gpt-image-2-2026-04-21` ONLY. Never gpt-image-1 / 1.5.

## GENERATION METHOD (by stage)
- S2: text-to-image `/images/generations`.
- S1 & S3: `/images/edits` with the approved S2 image as visual reference + full
  descriptive prompt (fresh creature, NEVER "edit this image"). Text-to-image for
  S1/S3 is a VIOLATION.

## ART-APPROVAL GATE (credit protection)
- "Generate new option" / "Regenerate" / new S1-S3 art → place RAW art (with bg).
  DO NOT remove.bg. Cropping is PAID and runs ONLY after the art is approved.
- remove.bg happens at: "Generate new crop" (art already approved) or "Approve <opt>".

## BACKGROUND (adaptive; never strong chroma)
- Dark creature → flat WHITE bg (describe bg as white; keep lighting vivid/dark-fantasy,
  NOT "studio/high-key" → that washes out). Light creature → dark charcoal #141414.
  Mid → #808080. After white bg: white-halo despill. Green/magenta baked-in → despill.

## SLOTS (contiguous A→B→C→D→E; codex renders all five)
- New option/crop → next EMPTY slot (never skip).
- Delete → RESHUFFLE: delete A → B becomes A, C becomes B, etc. No gaps.
- Approve <X> → promote X to A, delete all other slots.

## CODEX VISIBILITY (or the image is invisible)
- Any created/moved main image → set `Image_Path = codex/images/<ID>.png` in the SAME commit.

## VERIFY (before saying done)
- Re-pull HEAD git tree (not raw CDN, not Contents API right after write).
- Print [x]/[ ] for EVERY listed backlog action + Image_Path validity.

## REGENERATE-AND-OVERWRITE = FRESH T2I ONLY (committed per D, this session)
- "Regenerate and overwrite" ALWAYS means fresh text-to-image via /images/generations from the
  (revised) prompt. NEVER pass any old/existing image as input to /images/edits for a
  regenerate-and-overwrite. Old images are never edit-inputs when D says regenerate/overwrite.
- This differs from S1/S3 "new option based off <S2>" (which DOES use the named S2 as edit ref)
  and from explicit "based off <ID>" instructions. Only regenerate/overwrite is the t2i-only rule.
