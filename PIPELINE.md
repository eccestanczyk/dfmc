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

# ⛔ HARD RULE #0.5 — EVERY PROMPT MUST ENCODE CREATURE TYPE ⛔
# (Per D: prompts had stopped including creature types. Type_Primary and Type_Secondary
#  from creatures.csv MUST be expressed in EVERY generation/edit prompt, as concrete
#  VISUAL MOTIFS — not the bare type word (image model renders bare words poorly).
# Insert the motif clause right after the core anatomy description, before the bg/framing
#  boilerplate, phrased as: 'As a <Primary>[/<Secondary>] creature it also shows <motif>,
#  <motif2>.' Blend naturally; don't contradict the creature's own description.
# Motif lexicon (Type -> visual cue) committed below; rebuild from here each session:
#
#   Amphibian: moist glistening amphibian skin, webbed digits, a soft translucent throat sac
#   Aquatic: waterlogged fins and gill-slits, dripping brine, a bioluminescent deep-sea sheen
#   Arthropod: a hard segmented chitinous exoskeleton, jointed armored legs, twitching antennae
#   Avian: layered feathers, a hooked beak, taloned bird feet, folded or spread wings
#   Beast: thick fur or hide, a fanged predatory muzzle, clawed paws and a feral posture
#   Celestial: a faint halo of pale holy light, gilded radiant markings, an otherworldly divine glow
#   Chimera: mismatched body parts fused from several different animals, an unnatural hybrid silhouette
#   Construct: a body assembled from inert material — stone, iron or bound components — with visible joints and seams, no organic softness
#   Dragon: heavy overlapping scales, membranous draconic wings, curved horns and a reptilian sneer
#   Elemental: its body made of and wreathed in raw element — flame, stone, water or storm — with glowing elemental energy at the seams
#   Fey: an eerie ethereal glow, delicate uncanny features, drifting motes of faint fairy-light
#   Flora: living plant matter — bark, vines, leaves, blossoms or roots — growing as part of its body
#   Fungal: clustered mushroom caps, spreading spores, mottled fungal growth and mycelial threads
#   Insect: a chitinous insectoid body, compound eyes, thin multi-jointed legs and buzzing wings
#   Mollusk: a soft boneless slick body, coiling tentacles or a spiral shell, a glistening mucous sheen
#   Ooze: a semi-liquid amorphous body that sags and drips, translucent gelatinous mass, no fixed skeleton
#   Reptile: dry pebbled scales, cold slit-pupil eyes, clawed reptilian limbs
#   Serpent: a long limbless coiling serpentine body, overlapping belly scales, a flicking forked tongue
#   Spectral: a translucent semi-transparent ghostly body, edges dissolving into vapor, a cold spectral glow
#   Undead: decayed rotting flesh over exposed bone, sunken hollow eye-sockets, a desiccated grave-touched look
#   Vampiric: gaunt pale predatory features, prominent fangs, blood-red accents
#   Void: a body of light-swallowing pure black void, an unstable outline edged in faint violet, wrongness that eats the surrounding light
#   Aberration: impossible non-euclidean anatomy, too many eyes or mouths in wrong places, a maddening asymmetry
#   Demon: infernal blackened flesh, jagged horns, burning ember eyes and a cruel predatory malice
#   Eldritch: cosmic-horror features that should not exist — extra eyes, writhing appendages, an alien wrongness
#   Horror: nightmarish disturbing features, exposed sinew and wrong proportions built to unsettle
#   Parasite: parasitic growths and burrowing organisms erupting from or clinging to its body
#
# Self-check before EVERY generation call: 'Does this prompt visually encode BOTH the
#  primary and (if present) secondary type via motifs? If not -> add them before sending.'
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

