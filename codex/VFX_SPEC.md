# Move VFX / AFX Taxonomy (locked)

Source of truth for every move's placeholder visual effect and sound: `codex/move_vfx.csv`.
One row per move, 401 rows (400 creature moves + the class fallback `M-CLASS-STRIKE`).

**The archetype assignment is LOCKED. No tool re-derives it.** Both the codex review page and
the game client read this CSV and nothing else. If an assignment is wrong, it is changed here,
in the CSV, and every consumer picks it up.

## Columns

| column | meaning |
|---|---|
| `Move_ID` | join key to `codex/moves.csv` |
| `Name` | Stage-3 move name, for reading the sheet |
| `VFX_Archetype` | the placeholder effect that plays (20 values) |
| `VFX_Color` | palette key, from the approved icon palette |
| `Target_Anchor` | where the effect plays: `self` / `target` / `ground` / `both-sides` |
| `Duration_Class` | `fast` 0.4s / `standard` 0.6s / `heavy` 0.8s |
| `VFX_Description` | the eventual bespoke effect, authored per move. Archetypes are the placeholder layer. |
| `VFX_Layer` | `impact` when the move deals damage but its archetype is a status effect - a neutral impact plays under the status effect. Empty otherwise. 78 moves. |
| `AFX_Archetype` | the placeholder sound (10 values) |
| `AFX_Layer` | `thud` wherever `VFX_Layer` is `impact`, so the hit is heard as well as seen. Empty otherwise. |
| `AFX_Pitch` | `low` Power_S3 >= 130 / `mid` 70-129 and every non-damaging move / `high` 1-69 |

## The 20 VFX archetypes (move counts)

generic_impact 152 - atk_down 41 - shield_def_up 31 - def_down 29 - heal 21 - melee_crush 17 -
atk_up 17 - melee_slash 15 - cleanse 14 - pierce_strike 12 - whip_lash 12 - charge_impact 12 -
bleed_dot 7 - projectile 6 - poison_dot 5 - speed_up 4 - burn_dot 2 - speed_down 2 - drain 1 -
curse 1

## The 10 AFX archetypes (move counts)

thud 181 - hex 73 - bless 56 - ward 31 - slash 27 - pierce 12 - wet 8 - whoosh 6 - hiss 5 -
crackle 2

Placeholder sounds are **synthesised in the browser** - there are no audio files. Each archetype
is a short recipe over an oscillator, a noise buffer and a filter, tuned by `AFX_Pitch`. Nothing
to host, nothing to license, and a change is one number.

| AFX | recipe | from VFX archetypes |
|---|---|---|
| `thud` | low sine drop 160->45 Hz + short lowpassed noise body | generic_impact, melee_crush, charge_impact |
| `slash` | fast bandpass noise sweep 3.5k->900 Hz | melee_slash, whip_lash |
| `pierce` | tight metallic triangle ping 1.6k + noise tick | pierce_strike |
| `whoosh` | noise sweep down, then a `thud` on arrival | projectile |
| `ward` | rising square 220->440 Hz, hard stop on a clunk | shield_def_up |
| `bless` | rising minor triad, sine, soft attack | heal, cleanse, atk_up, speed_up |
| `hex` | two detuned saws falling 300->110 Hz + shudder tremolo | atk_down, def_down, speed_down, curse |
| `wet` | short lowpassed noise plosive with fast decay | bleed_dot, drain |
| `hiss` | long bandpassed noise, slow decay | poison_dot |
| `crackle` | four random noise ticks over 0.4s | burn_dot |

`AFX_Pitch` shifts every recipe: `low` x0.75, `mid` x1.0, `high` x1.35.

## Palette (fixed, matches the approved icon set)

blue `#18306a` buff/heal/cleanse - purple `#3a1a56` debuff/curse - crimson `#600e12` bleed/drain -
green `#144820` poison - red `#6e1212` burn - rust `#7e3818` pierce - bone `#d8cfc0` neutral damage

## Rendering constraint

**SOLID opaque shapes only** - no soft glow, no translucent aura, no blur. Effects are drawn on a
2D canvas over the battle stage, anchored per `Target_Anchor`, and never move the stage itself
(no screen shake, no text inside the effect).

## Stage scaling

One effect per move, not per stage. Stage-1 plays at x0.85 size, Stage-2 x1.0, Stage-3 x1.2, and
the sound pitch bends the same way. **Approval is per move, not per creature-stage** - 401 review
units, not 1,203.

## Consumers

- `assets/vfx/vfx.js` - the placeholder renderer. One function per archetype, no game state.
- `assets/vfx/afx.js` - the placeholder synth. One recipe per archetype, no assets.
- `vfx.html` - the review and approval page on this site.
- The game client imports the same two modules. There is no second implementation.

## Review and approval

`vfx.html` loops every move on a live battle stage and records approval per `Move_ID`.
Approvals live server-side, never in the browser, so they survive a cleared cache, a cleared
backlog, a different browser and a different device. Reading approvals is public; writing needs
the review key, pasted once per device. The backlog is separate, local, and clearing it cannot
touch an approval.

## Changelog

- **2026-09-17** - **`!shake` is declined while a window is open over the stage (#948).** Owning
  page: this one (the `!shake` row in the move-level flag table above). D, from the equipment
  screen on floor 105 with a battle resolving behind it: "when using the menu (equipment,
  inventory, soul bag, etc.) the menu shakes when menu shaking vfx occurs. feels like mini bursts
  of motion blur." The flag animates the **stage root**, and the stage root is not the battle
  scene - the scene, the HUD and every full-stage window are flat siblings under it, so a shake
  moved whatever was painted on top. Autoplay resolves battles under an open window, so every S3
  or ULT cast carrying `!shake` jolted the grid the player was reading. Nothing about the effect
  itself changes - amplitude, decay, the S3-and-ULT-only budget, the Screen Shake toggle and
  Reduce Motion are all as they were; this is one more reason to decline, asked at the moment the
  shake fires rather than when it is scheduled (an ULT arms its impact up to 2 s ahead, and a
  window opened inside that gap must be covered). A shake already in flight is allowed to finish:
  it is 150-250 ms, and cancelling a decaying translate snaps the stage. **Authors need do
  nothing** - no composition changes and no `!shake` becomes illegal. Gate
  `dfmc-client/tools/probe_948.py` 3/10 -> 10/10.

- **2026-09-17** - **`bone` is a dark neutral, not vivid gold: the calibration target gets a
  per-element saturation CEILING.** Owning pages: this one and `codex/VFX_SHEET_TINTS.md` (the 12
  `bone` tokens, rewritten by the tool). What was wrong: the entry below records the re-solve
  reaching 84/84, and the colours were right - except `bone`, which landed at HSL saturation
  **79-87 % on 11 of the 12 sheets** (FX-038: `k h40 br0.65 sat1.5`, sat 86 %, lum 52 %). On its own
  contact sheet it was the loudest tile of the eight, louder in chroma than the untinted white
  original it replaces. Three things make that wrong and they compound. **`bone` is the default
  element and carries 217 of the 419 moves**, so a vivid gold there is a uniform gold wash over half
  the game's abilities; `bone` is the "no strong element" case and has to read as restrained. Its
  own hex is `#d8cfc0`, a light **neutral** - nothing in the element table asks for gold. And the
  hit tint disagrees with the layer: **`vxHitBone` measures 3.8 % saturation over real creature
  art** (it is the dark-neutral exception the `!flash` entry below records), so a `bone` move would
  have flashed vivid gold on the layer while the sprite tinted near-grey. Layer and flash agreeing
  is the whole reason the element hue table and `VXHITH` share their numbers.

  The mechanism was structural and not a bad search: **the target's saturation leg was a floor
  (`>= 25 %`) with no ceiling**, so the solver correctly spent everything it had on chroma. That is
  right for an element that IS a colour and wrong for one that is not. The fix: `tools/vfx_calibrate.py`
  carries a **`SAT_BAND` table**, element -> (floor, ceiling) - a table and not a branch buried in
  the solver, because a later element may want one. `bone` is banded **0-18 %** with `lum <= 55 %`
  unchanged; every other element is absent from the table and keeps the bare floor with no ceiling,
  so **nothing else in the target moved**. Three things follow the band through the tool: `misses`
  and `score` take the element and weight the ceiling like the hue leg; the `sat` search axis, which
  is floored at 0.8 for an unbanded element on purpose, opens to the grammar's whole 0-1.5 for a
  banded one (it costs nothing - `sat` is the last primitive, so that axis is ranked in numpy on
  pixels already shot); and the solver aims just UNDER the ceiling rather than at zero, because hue
  is a chroma-weighted mean and a layer with no chroma has no measurable hue to put on the element.

  What it buys, measured: **`bone` re-solves on all 12 sheets to sat 13.6-15.3 %, hue 33.7-38.7 deg
  (want 38), lum 27.4-50.6 %, flat white 0.0 %** - a dim, faintly warm neutral. The table is
  **84/84** again with no leg missed on any pair. **Only `bone` was re-solved**: the tool grew a
  `--carry` that reads a published `VFX_SHEET_TINTS.md` and carries every element not being solved
  forward verbatim - re-shot on the same rig so the contact sheets stay the eight-tile comparison
  they are looked at as, never re-measured - and the other six elements' 72 published rows are
  field-identical to before, checked and not assumed. Nothing in `codex/move_vfx.csv` or
  `codex/moves.csv` changes; no client change, no engine change, no grammar change - `sat0.35` and
  `br0.3` were already legal. Judgement recorded and deliberately not acted on: **`green` reaches
  76 % on FX-038** and 56-74 % elsewhere, well above the 43-51 % of red/blue/crimson, so the element
  set does not read as one family; only **5 moves** carry `green`, so it is nearly harmless either
  way and no band was added for it.

- **2026-09-17** - **The `br` floor comes down 0.5 -> 0.3, and the white-sheet tints re-solve
  32/84 -> 84/84.** Owning pages: this one (the grammar table, `br<f>`) and `codex/VFX_SHEET_TINTS.md`
  (the tokens themselves, rewritten by the tool). What was wrong: the filter reorder the entry below
  records bought the saturation leg of the calibration target and lost the luminance one. The solve
  that followed it hit the full target (hue +/-18 deg, lum <= 55 %, flat white 0 %, sat >= 25 %) on
  **32 of 84** sheet x element pairs, and **all 52 misses were the `lum <= 55 %` leg and nothing
  else**. The mechanism: `sepia(1)` is not a dimming matrix - its red row sums to 1.351, so it has
  gain - and on the neutral path `br` runs BEFORE it, so darkening is partly undone and
  `saturate(2.4)` then pushes the red channel back toward 255 on the sheets with the brightest
  cores. `br` is the direct answer to that and the grammar floored it at 0.5, where the solver was
  already sitting on **every one** of the 52 missing rows. The fix: `RANGE['br']` goes `(0.5, 1.6)`
  -> `(0.3, 1.6)` in `tools/fx_lint.py` AND in the client's `VFX_BANK` parser (`play/app.js`), in
  the same batch - the two have to agree or the linter accepts what the renderer rejects, which is
  the standing failure mode in this area. Both now refuse `br0.29` with the same message and accept
  `br0.3`. **This only widens what an author may write and nothing already authored changes:** of
  `codex/move_vfx.csv`'s 419 rows, 139 carry a `br` at all (286 layers of 3883), and the lowest
  value written anywhere is **0.7** - counted, not assumed. What it buys, measured: the re-solve is
  **84 of 84**, no leg missed on any pair, and **57 of the 84 published tokens now carry a `br`
  under the old floor** - so `VFX_SHEET_TINTS.md` is void against any client older than this change,
  which will reject those rows outright rather than render them wrong. `tools/vfx_calibrate.py` now
  reads its floor from `fx_lint.RANGE` instead of restating it, and its `br` ladder runs 0.30-1.00.
  Two things looked at on the contact sheets rather than on the numbers: nothing went muddy or
  vanished against the dark floor plate at the new depths (FX-034 is the darkest family at lum
  24-30 and still reads), and **the `bone` element is the one row family the target does not
  describe properly** - it solves to a fully saturated gold (sat 79-87 % on 11 of the 12 sheets)
  because the target has a saturation floor and no ceiling, while `bone`'s own hex `#d8cfc0` is a
  light neutral and its matching hit tint `vxHitBone` is deliberately a dark neutral (measured at
  3.8 % saturation). Layer and flash disagree on that element; the fix is a per-element saturation
  ceiling in the solver's target, and it is not taken here.
- **2026-09-17** - **The hit-tint family measured over real creature art; the filter order does NOT
  hurt it, and it is left alone.** Owning page: this one (the hit tint, `VXHITC` / `VXHITH` /
  `VXHIT_FOR` and the `vxRedHit` / `vxHit*` keyframes in `play/markup.html`). The whole family
  carries `sepia(1) saturate(N) hue-rotate(N) brightness(~1.0)` - the same primitive order that was
  the entire defect in `sheetFilter`. The presumption was that it bites far less because these
  filters run over creature art rather than over a white sheet, and a presumption about a filter is
  what cost this run two passes, so it was shot: 12 family members, 10 approved creature sprites
  spread across `Type_Primary`, the keyframe text lifted verbatim out of the markup and applied as
  the real animation paused on its own 12 % and 55 % stops, measured the way `vfx_calibrate.py`
  measures. Every member lands on the element it is named for - worst hue error 14.8 deg
  (`vxHitGreenSoft`), 11 of 12 inside 13 deg - at 48-100 % saturation, 22-49 % luminance and 0 %
  flat white bar `vxHitBlueSoft` at 1.1 %. The A/B on order, same numbers both sides: moving
  `brightness` to the front changes saturation by **+0.0 points on 8 of the 12**, +0.5 on
  `vxHitBoneSoft`, and at most **+4.9** (`vxHitPurple`) and +4.1 (`vxHitBlue`); luminance moves at
  most 0.8 points and hue at most 0.9 deg. On a white sheet the same reorder was worth about **40**
  points. The reason is the one predicted: `brightness(~1.0)` is not darkening anything, so there is
  no clamp to escape, and creature art already carries chroma into `sepia(1)`. **Nothing changed.**
  The two members that would gain ~4-5 points, `vxHitPurple` and `vxHitBlue`, are the only rows worth
  revisiting and only if that family is ever reopened on its own merits.
- **2026-09-17** - **The filter order was the whole defect: `brightness` is emitted FIRST on the
  neutral/sepia path.** What was wrong: `VFX_BANK.sheetFilter` built its chain hue ops ->
  `saturate` -> `brightness`, so a `k` layer was handed
  `sepia(1) saturate(2.4) hue-rotate(h-40) brightness(br)`. **A browser clamps its 8-bit buffer
  BETWEEN filter primitives**, and `sepia(1)` on a white pixel returns rgb(255,255,239) - two
  channels already pinned at 255 - so `saturate` and `hue-rotate` were working on a pixel whose
  chroma had already been thrown away, and darkening it last could not give the chroma back. That
  is why the entry below reports 0 of 84 pairs reaching `sat >= 25 %`, why the measured ceiling was
  20 %, and why `k h0` read gold instead of red. **The fix is the order, not a bigger multiplier and
  not new art:** on the neutral path only - the `Colored` = no branch and any layer carrying `k` -
  `brightness` is pushed onto the chain before `sepia(1)`, which moves the pixel off the ceiling
  first. Measured in a browser on a literal white div: `sepia(1) saturate(2.4) hue-rotate(60deg)
  brightness(.7)` is rgb(157,178,163), HSL saturation **12 %**; `brightness(.5) sepia(1)
  saturate(2.4) hue-rotate(60deg)` is rgb(102,179,76), **40 %**; `brightness(.4) sepia(1)
  saturate(3) hue-rotate(-40deg)` is rgb(211,102,85), hue 8, **59 %**. On the real FX-038 sheet
  `k h134 br0.5` goes 14 % -> 47 % saturation and `k h0 br0.5` goes hue 44 (gold) -> hue 8 (red).
  **The coloured path is deliberately unchanged** (`Colored` = yes without `k`, still
  `hue-rotate` -> `saturate` -> `brightness`): those sheets carry their own chroma, no `sepia` pass
  clamps them, and reordering there would change the look of rows that are fine. `saturate(2.4)` is
  unchanged and so are the grammar's `br` (0.5-1.6) and `sat` (0-1.5) ranges - the reorder is worth
  about 40 points of saturation where those levers are worth about 7, so **neither of the two
  engine changes the entry below proposed was made**. `tools/fx_lint.py` validates tokens and models
  no chain, so it does not move; `tools/vfx_calibrate.py` does, because `br` is no longer a post-pass
  it can apply in numpy - it is now a browser axis, and its `--filter-check` renders both orders side
  by side. **`codex/VFX_SHEET_TINTS.md` is re-solved against the new chain and every older copy of it
  is void:** all 84 pairs now meet `sat` (33-100 %, was 0 of 84) and hue and flat white, and **32 of
  84 meet all four legs**; the 52 that miss all miss `lum <= 55 %` and only that, because `sepia(1)`
  has gain (its red row sums to 1.351) so darkening before it is partly undone, and `br` is floored
  at 0.5 by the grammar. That trade - and the two levers that would close it, a lower `br` floor or a
  smaller `saturate(2.4)` - is written up on that page; neither is taken without D looking at the
  contact sheets (`local-only/vfxshots/tints/tint_FX0NN.png`). No row of `move_vfx.csv` or
  `moves.csv` is touched. Owning pages: this spec and `codex/VFX_SHEET_TINTS.md`.

- **2026-09-17** - **The 12 white sheets are calibrated per element - and the target's saturation
  leg is proved unreachable inside the grammar.** `k` makes a white sheet colourable, but the hue
  that LANDS is not the hue authored, so each sheet needs its own token per element rather than the
  element's hue written straight. `tools/vfx_calibrate.py` measures them: one carrier move
  (`M-THORNBACK-1`, `Targets` = enemy), one seed, one tile, one scale for all 12 so they are
  comparable; the composition is a page-level `FX_S3` override, so **no row of `move_vfx.csv` or
  `moves.csv` is touched**; the scrub lands inside the layer's own `lenMs`; the pixels are the
  difference against a clean plate of the same paused frame, restricted to where that plate is dark
  - the layer over the floor and not over the creature, which is the second way to measure the
  sprite instead of the effect - and the four numbers are read on the top luminance decile. The 84
  rows are **`codex/VFX_SHEET_TINTS.md`**, which is what the six authoring lanes copy from; the
  proof sheets are `local-only/vfxshots/tints/tint_FX0NN.png`.
  **What the run found:** all 84 pairs meet hue (+/-18 deg), lum (<= 55 %) and flat white (0 %), and
  **not one meets `sat >= 25 %`**. The measured ceiling is 23 % (FX-050 at green) down to 9 %
  (FX-034), and purple and blue average 2-3 % across all 12 - the `k` chain leaves a white pixel a
  pale warm yellow, and rotating that to the cool half of the wheel crosses the achromatic axis.
  The cause is not the art: `saturate(2.4)` is too small a multiplier to open up the chroma
  `sepia(1)` leaves. `tools/vfx_calibrate.py --filter-check` renders the chain on a literal white
  div beside the CSS spec matrices - they agree to the last level - and shows that the second
  filter table in `dfmc-client/docs/vfx-pass2-recipes-2026-09-17.md`, the table the 25 % floor was
  set from, composed the three matrices and clamped ONCE at the end. A browser clamps its 8-bit
  buffer BETWEEN filter passes, and the clamp right after `sepia(1)` is what throws the chroma
  away: `sepia(1) saturate(2.4) hue-rotate(60deg) brightness(.7)` renders rgb(157,178,163), HSL
  saturation 12 %, where that table records rgb(142,178,106), HSL saturation 32 % - about 3x out.
  **So a desaturated twin is not the answer to any of the 12** - the chroma is lost in the filter,
  not in the sheet - and the fix is one number, either `saturate(2.4)` -> `saturate(4)` in the `k`
  branch of `sheetFilter` (25.8 % reachable) or the grammar's `sat` ceiling 1.5 -> 2.5 (25.6 %).
  Neither was made here: both are engine/grammar changes and each needs its own review.
  Owning pages: this spec and `codex/VFX_SHEET_TINTS.md`.

- **2026-09-17** - **The scale ladder is cut to 0.7 / 0.85 / 1.0 / 1.35.** D, answering the pass-2
  artifact's Q1: "a harder cut (0.7 / 0.85 / 1.0 / 1.35)" - S1 / S2 / S3 / ULT. What was wrong: `s`
  is a fraction of the 380 px unit TILE and a creature's opaque art is only ~85 % of that tile, so
  `s1.0` already draws the effect at ~118 % of the body; the authored rows were running at 124 /
  137 / 165 / 246 percent of it and the effect had become the subject. `tools/fx_lint.py` moves its
  S1 primary-scale band from **0.8-1.2 to 0.55-0.85**, centred on D's 0.7; the monotonic
  `S1 -> S2 -> S3` growth checks are unchanged, and so is `BUDGET` (layer counts and ms per stage) -
  D ruled on scale, not on how many sheets or how long they play. **This deliberately puts all 401
  non-ULT rows of `codex/move_vfx.csv` outside the band**: the linter now fails every one of them,
  which is the point - it is the gate the six authoring lanes re-author against, not a regression.
  No row is changed by this entry. Owning pages: this spec and `vfx.html`.

- **2026-09-17** - **`k`: the neutral colourise path, picked per LAYER.** The renderer had two
  colourise paths chosen by the sheet's `Colored` column - `hue-rotate(h - sheetHue)` for `yes`,
  `sepia(1) saturate(2.4) hue-rotate(h - 40)` for `no`. What was wrong: **`hue-rotate` on a white
  pixel returns white** (it moves chroma, and white has none), verified against the spec's own
  colour matrices, so FX-038 Strike Flash (76 % near-white, 175 uses) and FX-032 Thunder Ring (70 %,
  27 uses) are both `Colored=yes` and **no `h` an author has ever written has moved them**. The
  sepia path does colour white, because `sepia(1)` gives the pixel chroma first. `Colored` is a
  column on the SHEET, so flipping FX-038 to `no` would change all 175 of its uses at once, and
  FX-055 Hex Motes could never be red in one move and green in another. The fix is one bare layer
  token, **`k`** (like `f` / `m` / `z`, no argument): take the neutral path for this layer whatever
  the sheet says. The **+/-90 hue clamp is skipped when `k` is present** - the clamp exists to stop a
  coloured sheet being rotated far off its own hue into mud, and `sepia(1)` has already discarded
  that hue; it is unchanged for every layer without `k`. `k` on a sheet that is already `Colored=no`
  is a **no-op, not an error**. It is also what the two "desaturated twin" follow-ups wanted:
  FX-055 reaches clean poison green through `k` where the clamp only reached a muddy hue 85 at
  luminance 27, so **no new sheets are needed**. Pair `k` with `br0.6-0.8`: `k` alone colours the
  white core but leaves it at 80-96 % luminance, still a flash. Both parsers move together -
  `VFX_BANK.parse` / `sheetFilter` in the client's `play/app.js` and `tools/fx_lint.py`, which is
  the reference. No composition changes; the token is inert until a lane writes it. Owning pages:
  this spec and `vfx.html`.

- **2026-09-17** - **A killing blow now plays on the thing it killed.** D, on the pass-2 artifact:
  "Some of the abilities are playing ONLY on the caster." Neither the data nor the renderer was at
  fault - the census through `vfx.html` found 0 compositions asking for a target layer that is not
  mounted, and 0 non-`self` moves painting no target-side layer. The client's act playback pushes
  the **post-act** units into state in the same patch as the act, so on the first frame of a lethal
  cast the target already sits at `hp:0`; the battle scene gated the whole composition - and the
  `!flash` hit tint, and the hit reaction - on the unit being alive, so a target that this act
  killed drew nothing while the caster played normally. The composition is now gated on the tile
  **owning the act** (its caster, or a unit named in the act's targets) rather than on HP. A unit
  that was already dead *before* the act is never named by it and still draws nothing. Authoring is
  unaffected - no composition changes, no budget changes. Owning pages: this spec and `vfx.html`.

- **2026-09-17** - **`!flash` is a dark element tint, not a white flash.** D's ruling: "Models can
  still flash, just not plain white. Dark colors are fine. For instance a damage flash dark red
  flashing the target art reads great. Probably the same for dark green when it's poison." The
  mechanism is unchanged - the flag still rides the target's tint wrapper at the impact - but the
  50 ms `brightness(3)` blowout (`vxbFlash` / `vxbFlashSoft`, both deleted) gives way to the 300 ms
  `sepia(1) saturate(..) hue-rotate(..)` recolour `vxRedHit` has fired for `melee_slash` since
  before the bank, generalised into one keyframe per `VFX_Color`: `vxRedHit` (red/crimson),
  `vxHitRust`, `vxHitGreen`, `vxHitBlue`, `vxHitPurple`, `vxHitBone`, each with a `*Soft` member
  for the Reduce Flashing setting (same hue, lower saturation - never a brightness change).
  `hue-rotate` is the element's hue in `VFXHEX` minus 40, because `sepia(1)` lands every sprite at
  hue 40. **`bone` is the exception**: it is the majority colour (217 moves) and `#d8cfc0` is light,
  so its keyframe is a dark neutral - no hue rotation, `saturate(0.22)`, `brightness(0.58)`.
  The element comes from the composition first, the row second: the `h` of the first target-side
  layer (`@t`/`@g`/`@b`) when one is authored, else the move row's `VFX_Color`; a numeric `h` snaps
  to the nearest element by circular hue distance and anything unknown falls to bone's dark neutral.
  Nothing in `move_vfx.csv` changes - no re-authoring is needed for this. Owning pages: this spec
  and `vfx.html`.

- **2026-09-17** - **The 48-sheet VFX bank replaces the placeholder archetypes.** Three columns
  per move - `FX_S1`, `FX_S2`, `FX_S3` on `codex/move_vfx.csv`, mirrored onto `codex/moves.csv`
  by `tools/sync_move_vfx.py`; the 18 class ultimates are rows `ULT-<LINE>-<stage>` and carry
  only `FX_S1`. Manifest `codex/fx_bank.csv`, sheets `assets/fx/bank/*.webp`. The grammar and the
  budgets are in *Bank compositions* above; `tools/fx_lint.py` is the reference parser and the
  authoring gate. The renderer is `VFX_BANK` in the client's `play/app.js`, animating the `vxb*`
  keyframes in `play/markup.html`; `tools/gen_vfx_fx.py --write` lifts it - with `VFX_FX` and every
  `vx*`/`vxb*` keyframe - into `assets/vfx/vfx_fx.js|css`, so the codex review page `vfx.html`
  casts through `DFMC_VFX_FX.buildBank(E)` and the archetype columns are only its fallback.
  `tools/vfx_bank_gate.py` walks all 1221 casts (401 moves x 3 stages + 18 ultimates) on that page.
  Owning pages: this spec and `vfx.html`.
- **2026-09-10** - AFX taxonomy added: four columns (`VFX_Layer`, `AFX_Archetype`, `AFX_Layer`,
  `AFX_Pitch`), 10 sound archetypes, browser-synthesised placeholders. `M-CLASS-STRIKE` added as
  row 401 (it was missing from the mapping). Damage-carrying status moves now layer a neutral
  impact under the status effect - 78 moves. Owning pages: this spec and `vfx.html`.
- **2026-07-15** - 20-archetype VFX taxonomy locked for all 400 moves, derived from `Effect_S3`
  mechanics and the `VFX_Description` visual verbs.

## Per-stage renditions (2026-09-10)

A move keeps ONE archetype at every stage. What improves when it advances is the rendition,
not the identity: the renderer takes the stage (1-3) and escalates scale, layer count and
duration, and for audio the pitch and body.

`VFX_Archetype_S2`, `VFX_Archetype_S3`, `AFX_Archetype_S2`, `AFX_Archetype_S3` are SPARSE
overrides for the few moves that genuinely become a different effect when they advance.
**Blank or absent means inherit the base.** Read them defensively. Do not author three
archetypes per move.

## Keying

`Move_ID` is the key. Never a name: names are display strings, they differ per stage, and a
lookup keyed on the base name misses at stages 1 and 2 (the live defect found 2026-09-10).
A miss must fail loudly - never fall back to `generic_impact` silently.

## Bank compositions (2026-09-17) - the placeholder layer is retired

The 48 CC0 sprite-sheet effects of the VFX bank (`codex/fx_bank.csv`, sheets in `assets/fx/bank/`,
gallery at https://playdfmc.com/dungeon-dev/vfx.html, wiki page *VFX bank*) replace the solid-shape
placeholder archetypes for every move. **The archetype columns stay** as the neutral fallback for an
id-less move and as the AFX key; they no longer decide what a player sees.

Three new columns on `codex/move_vfx.csv` (mirrored onto `codex/moves.csv` by `tools/sync_move_vfx.py`
so the review page reads the same thing): **`FX_S1`, `FX_S2`, `FX_S3`** - one composition per stage,
authored per move. The 18 class ultimates are rows `ULT-<LINE>-<stage>` (their stage is the row, so only
`FX_S1` is filled and read). `M-CLASS-STRIKE` is one row with three stages like a creature move.

The rules that drove the authoring are in `dfmc-client/docs/vfx-research-2026-09-17.md` (§ Rules for the
Herumon Tower bank run); the numbers below are the ones the linter (`tools/fx_lint.py`) enforces.

### Grammar

A composition is **layers separated by `|`**. A layer is **tokens separated by spaces**; the first token is
the sheet and its anchor, the rest are optional modifiers in any order.

```
FX-041@t f s1.2 v1.5 | FX-038@t d160 s0.8 | FX-054@u v2 h50 | !flash
```

| token | meaning | default |
|---|---|---|
| `FX-NNN@u` | play on the **user's** tile, centred on the sprite | - |
| `FX-NNN@t` | play on **every target's** tile, centred on the sprite | - |
| `FX-NNN@g` | play at the **target's feet**: bottom-anchored, drawn behind the sprite, squashed to 50 % height (a ring in fake perspective) | - |
| `FX-NNN@ug` | same, at the user's feet | - |
| `FX-NNN@b` | play on user AND every target (one layer, two tiles) | - |
| `s<f>` | scale. 1.0 = the sheet's frame is as wide as the unit tile (the 128 px sprite box) | 1.0 |
| `v<f>` | playback speed multiplier over the base 24 fps (`v2` plays a 24-frame sheet in 500 ms) | 1.0 |
| `d<ms>` | start delay from the cast, in ms | 0 |
| `n<int>` | loop the sheet n times | 1 |
| `h<deg>` | **absolute** target hue 0-359 (0 red, 30 orange, 50 gold, 120 green, 180 cyan, 210 blue, 270 violet, 300 magenta, 330 rose). The renderer rotates from the sheet's own hue (`Hue` in fx_bank.csv) so `h120` means green on any sheet; on an uncoloured sheet (`Colored` = no) the pixel is given chroma by `sepia(1)` first, so `h` colours the white core too - and the hue that LANDS is not the hue authored on a near-white sheet, so **copy the token from `codex/VFX_SHEET_TINTS.md`** rather than writing the element's hue | sheet's own colour |
| `k` | **keyed**: force the neutral colourise path for THIS layer whatever the sheet's `Colored` says - `brightness(br) sepia(1) saturate(2.4) hue-rotate(h-40) saturate(sat)` instead of `hue-rotate(h - sheetHue) saturate(sat) brightness(br)`. Needed on a near-white sheet: **`hue-rotate` on a white pixel returns white** (it moves chroma and white has none), so no `h` moves FX-038 or FX-032 without it. **`br` is applied FIRST on this path and is not optional** - see the 2026-09-17 filter-order entry; without it `sepia(1)` clamps the white core at 255 and the layer stays a pale flash whatever `h` and `sat` say. The +/-90 hue clamp is **skipped** with `k` - `sepia(1)` has already discarded the sheet's own hue, so the clamp has nothing to protect. `k` on a sheet that is already `Colored` = no is a **no-op, not an error** | off |
| `sat<f>` | saturation multiplier, 0-1.5 (never above 1.5; the research rule is "never above the source") | 1 |
| `br<f>` | brightness multiplier 0.3-1.6. **The floor was 0.5 until 2026-09-17**; it was lowered because on the `k` path `br` is the FIRST primitive and 52 of the 84 calibrated sheet x element pairs sat on the old floor and still could not reach `lum <= 55%` | 1 |
| `a<f>` | opacity 0.2-1 | 1 |
| `f` | **directional**: flip horizontally when the attacker is on the right side of the stage. Put it on every slash, rake, bolt, arc and travel sheet; never on bursts, rings, blooms, motes | off |
| `m` | mirror always (independent of `f`) | off |
| `r<deg>` | rotate the layer | 0 |
| `x<pct>` | horizontal offset in % of the tile, **positive = toward the target** (flips with side) | 0 |
| `y<pct>` | vertical offset in % of the tile, positive = down | 0 |
| `z` | draw behind the sprite | in front |
| `w<pct>` | squash: height as % of the natural height (ground rings, floor pools) | 100 (50 for `@g`/`@ug`) |

Move-level flags are pseudo-layers, once per composition, anywhere in the list - **each flag is its own `|` segment** (`... | !flash | !shake`):

| flag | meaning |
|---|---|
| `!flash` | hit tint: every target sprite is recoloured a **dark, saturated** version of its own art at the impact, 300 ms, keyed to the element. Damaging moves only. Never white (D 2026-09-17) |
| `!shake` | stage shake, 4 px decaying over 150 ms. **S3 and ULT only**; honours the Screen Shake and Reduce Motion settings, and **is declined while a window is open over the stage** (#948, 2026-09-17) |
| `!stop` | hit-stop: the target freezes 100/150/200 ms (S1/S2/S3), 250 ms ULT, at the impact |

**Timing.** `t=0` is the cast. The renderer's existing hit reaction (lunge, hit shudder, damage number) is
untouched; the **first `@t` layer is the impact** and must start by **200 ms** (`d` <= 200) so it lands with
the number. Layers on the user (`@u`) are the cast beat and start at `d0`. On a `both-sides` move the user-side
beat starts at least 100 ms AFTER the first target layer.

**Length** of a layer = `d + frames / (24 * v) * n * 1000` ms. The composition's length is its longest layer.

### Budgets the linter enforces

| | S1 | S2 | S3 | ULT |
|---|---|---|---|---|
| layers (sheets, flags not counted) | 1-2 | 2-3 | 3-4 | 4-5 |
| length, ms (max over layers) | <= 700 | <= 900 | <= 1200 | <= 2000 |
| primary layer scale (first layer of S1, the same sheet at S2/S3) | 0.55-0.85 | >= S1 | >= S2 | any |
| `!shake` | no | no | allowed | allowed |
| first `@t` layer delay | <= 200 ms | | | |

**The scale ladder (D, 2026-09-17).** The primary layer's `s` grows **0.7 / 0.85 / 1.0 / 1.35** across
S1 / S2 / S3 / ULT. The linter pins the S1 rung (0.55-0.85) and the two growth checks; S2 and S3 are held only
by `>=` so a family may spread its rungs, but 0.85 / 1.0 is the shape to author toward.

The reason the ladder is this low: **`s` is a fraction of the 380 px unit TILE, not of the creature.** A
creature's opaque art fills about **85 %** of that tile, so `s1.0` already draws the effect at ~**118 %** of
the body it is meant to sit on. The rows authored before this ruling ran at 124 / 137 / 165 / 246 percent of
the body - the effect was the subject and the creature was behind it. At the new ladder S1 reads at ~82 % of
the body, ULT at ~159 %, and the ULT is the only stage that should ever swallow the sprite.

**Family identity.** Every sheet used at S1 is used again at S2, and every sheet at S2 again at S3. A stage
ADDS (a second sheet, a user-side cast beat, a ground ring, a flag) and GROWS (scale, hue intensity, `n`); it
never swaps the primary. The move names evolve the same way (Snout Butt -> Skullplate Ram -> Skullplate
Onslaught) and the effect must read as one family across the three.

**Anchor follows `Target_Anchor`**, which since 2026-09-17 is derived from the move's `Targets`: `self` -> `self`; `enemy`, `ally`, `enemy+ally` -> `target` (the ally IS the target of a heal); `enemy+self`, `self+enemy`, `ally+self` -> `both-sides` (55 rows were re-aimed; they had been anchored by the placeholder's convenience). `self` moves use only `@u`/`@ug`; `target` moves use `@t`/`@g`, plus a
`@u` cast beat from S2 on; `both-sides` (the drains) hit the target first and answer on the user.

**Colour follows the move, not the creature.** The palette per element (research rule 12) is: fire orange/red
(h20-35), ice cyan/blue (h190-215), lightning violet-white (h240-260), wind green-grey (h100-165), water blue
(h195-210), holy gold (h45-60), heal gold/soft green (h50-120), dark violet-magenta (h280-320), poison green
(h95-130), bleed crimson (h340-359), buff-up gold (h40-55), debuff-down violet (h270-290), physical /
neutral untinted. Stay within +/-90 deg of a sheet's own hue unless the sheet is uncoloured **or the layer
carries `k`** (which discards that hue before the rotation, so the clamp does not apply); prefer the
family's own sheet over a re-hued stranger.

**Low VFX / Battery Saver / Reduce Motion:** only the first layer plays, at 0.75x length; flags are off.

### Consumers

- `dfmc-client/play/app.js` `VFX_BANK` - parses the columns and draws the layers as stepped sprite-sheet
  animations over the unit tile; the sheets ship inside the client at `play/assets/fx/bank/`.
- `dfmc/vfx.html` + `assets/vfx/vfx_fx.js` - the review page draws the same thing from the same columns.
- `tools/fx_lint.py` - the authoring gate: grammar, ids, budgets, family identity. Exit 0 or nothing ships.
- `tools/sync_move_vfx.py` - copies the VFX/AFX/FX columns from `move_vfx.csv` onto `moves.csv` by Move_ID.
