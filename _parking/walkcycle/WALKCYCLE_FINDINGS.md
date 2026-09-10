# WALK CYCLE / SPRITE SHEET — FINDINGS, 2026-09-10

Everything here is measured, not guessed. Read before spending another cent.

## THE BEST ASSET SO FAR
`assassin_25_v4.png` — 12-frame walk sheet, 6x2, clean native alpha, no weapons,
upright posture, cloak locked. Produced by `sheet_v4.py` in ONE call, ~$0.35.
`walk_v4_sheet.png` is the registered strip. `assassin_25_v1.png` is the earlier
run D called "very close" — v4 is v1 plus three prompt lines and nothing else.

## THE RECIPE THAT WORKS — do not redesign it
- Endpoint `/v1/images/edits`, TWO images with EXPLICIT ROLES.
- IMAGE 1 = pose reference, a 6x2 grid of 12 Muybridge frames in the SAME layout and
  reading order as the sheet being asked for. `muy_grid_6x2.png` (plate 546 side row).
- IMAGE 2 = character + art style reference. `assassin1.png` (codex/images/classes).
- Model `gpt-image-2.5-sunburst-2026-09-08`, size `2304x1536`, quality `xhigh`,
  `background=transparent`, `output_format=png`.
- Say outright: "the twelve cells are TWELVE DIFFERENT POSES - do not average them".
- Say what NOT to take from the plate: not the person, not the nudity, not the lighting,
  not the grid backdrop, not the frame numbers.

## WHAT IS PROVEN TO FAIL
1. **PER-FRAME GENERATION IS A DEAD END.** 24 calls across two attempts, ~$5, unusable.
   Asking for "a character in a pose" makes the model paint a PICTURE — fog, mist and a
   ground shadow get baked into the alpha at 55-78% frame coverage, opaque, not keyable.
   An explicit no-fog/no-haze/no-shadow/no-atmosphere clause did NOT remove it.
   Scale also drifts 105px vs 17px on a sheet, even with head and foot positions pinned.
   Asking for "a sprite sheet" makes the model produce an ARTIFACT, and that comes back clean.
2. **PROMPT LANGUAGE CANNOT FORCE LEG ALTERNATION.** A long block telling it cells 1-6 are
   the near leg leading and 7-12 the far leg made the result WORSE than saying nothing (v3).
   Deleted. Do not re-add it.
3. **The 20-frame Muybridge plate is a trap** — it is rear + profile split, ~10 side frames.
   Fewer usable poses, not more.
4. **The high-res plate did not help enough to matter.** Plate 1 at 9575px (cells 500x936
   native, 4x the reference detail) produced v2/v3. v1/v4 off the low-res plate 546 read better.

## STILL OPEN
- **Full cycle / leg identity.** The model does not track which leg leads, so the loop reads
  as one step repeated rather than two. UNTESTED IDEA, and it is the cheap one: paint a
  coloured marker on the forward leg in each of the 12 plate cells and re-run the SAME
  whole-sheet call. Fix the REFERENCE, not the prompt. One call.
- **Vertical bob.** Hip height varies ~2.6% across frames; a real walk drops on contact and
  rises on passing. Not present in any run. Probably needs the same reference-side fix.
- **More than 12 frames.** Muybridge shot 12. More means generating in-betweens (one extra
  sheet call, this sheet as reference, halfway poses) — untested.
- **Cloak drift.** Reduced by the lock line, not eliminated.

## REGISTRATION — arithmetic, not prompting. `reg.py`
The model will not hold scale or position; fix it after the fact.
- Normalise on BODY HEIGHT (head to lowest foot), never the bounding box — bbox scaling
  shrinks the wide-stride frames.
- Anchor horizontally on the HEAD/SHOULDER centroid (top 35% of the silhouette), never the
  bbox centre, which drifts with the legs.
- Plant the lowest foot on a fixed baseline at 94% of cell height.
- Size the cell from the WIDEST transformed frame + 10% margin. This is what stopped the feet
  being clipped. There is an edge-touch check; it must report nothing.
- Result on v4: head wanders ~2px, feet ~3px across all 12 frames.

## MEASURE, DO NOT EYEBALL
- stride = horizontal extent of the silhouette in the bottom 12% of the figure.
- hip proxy = (mean y of silhouette - top) / height. Flat across frames = no weight.
- Two local minima in the stride sequence = two passing poses = a full cycle.
- Luminance-based "which leg is nearer" DOES NOT WORK — signal was 1-5 points out of 45 and
  flipped 6 times in 12 frames. Noise. Do not build on it.

## COST / RULES
- ~$6 burned in this session, most of it on the two per-frame runs that produced nothing.
- **ANY PROMPT CHANGE GETS TESTED ON ONE FRAME OR ONE SHEET BEFORE A FULL RUN.**
- A sheet call is ~$0.35 and ~2-3 min. Twelve per-frame calls are ~$2.50 and ~10 min.

## MODEL / ACCESS
- `gpt-image-2.5-flare` and `-sunburst` (+ dated `-2026-09-08` snapshots) are LIVE on the key.
  Nothing newer exists. Sunburst is the precision tier; use it for this work.
- Quality ladder: low | medium | high | xhigh | max. `xhigh` produced the best-read sheets;
  `max` was not visibly better and costs more.
- Sizes are now arbitrary — both dimensions divisible by 16, aspect between 1:3 and 3:1,
  hard max 3840x2160. The old three-size limit is gone (it is also gone on gpt-image-2).
- 2.5 has NATIVE ALPHA. `background=transparent` works and the whole cut.py keying tier is
  no longer needed for new art. This is the single biggest change from the old pipeline.
- Two gates had to be cleared for access, and BOTH were needed: org Individual verification
  (ID check, D did it) AND the per-project model allowlist under project limits. A new
  project starts with the same allowlist restriction.
- The key lives in `/mnt/project/ImgGenFlow.txt`. Never ask D for it.
