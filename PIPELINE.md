# ⛔ HARD RULE #0 — REGENERATE / OVERWRITE = FRESH TEXT-TO-IMAGE, NO IMAGE INPUT ⛔
# (Reaffirmed by D multiple times. A prior session VIOLATED this on DFMC-045 by routing a
#  regenerate through /images/edits. Do not repeat.)
#
# When D says "regenerate", "regenerate and overwrite", "regen fresh", "redo from prompt",
# or any regeneration of an EXISTING creature's OWN stage:
#   -> ALWAYS /images/generations (text-to-image). NEVER /images/edits.
#   -> NEVER pass ANY existing image as input, reference, or edit base. Not the old version,
#      not a sibling stage, nothing. Prompt text only.
#   -> If the stored Image_Prompt is edit-style ("the very same creature shown in the
#      reference image", "reference image", "make a X version"), REWRITE it into a fully
#      self-contained descriptive t2i prompt BEFORE generating, and save the rewrite to CSV.
#
# The /images/edits endpoint with an image reference is ONLY for:
#   - Building a NEW stage (S1 or S3) from an APPROVED S2, i.e. "new s1/s3 based off <S2>".
#   - An explicit "based off <specific ID>" instruction from D.
# Regenerating a creature's own art is NEVER one of these. When in doubt: t2i, no image.
#
# Self-check before EVERY generation call: "Is this a regenerate/overwrite of an existing
# creature's own stage? If yes and I am about to call /images/edits or attach any image -> STOP,
# switch to /images/generations with prompt only."
#

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

