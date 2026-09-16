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
| `h<deg>` | **absolute** target hue 0-359 (0 red, 30 orange, 50 gold, 120 green, 180 cyan, 210 blue, 270 violet, 300 magenta, 330 rose). The renderer rotates from the sheet's own hue (`Hue` in fx_bank.csv) so `h120` means green on any sheet; on an uncoloured sheet (`Colored` = no) it colourises the mid-tones and keeps the white core white | sheet's own colour |
| `sat<f>` | saturation multiplier, 0-1.5 (never above 1.5; the research rule is "never above the source") | 1 |
| `br<f>` | brightness multiplier 0.5-1.6 | 1 |
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
| `!flash` | white hit-flash on every target sprite at the impact, 50 ms. Damaging moves only |
| `!shake` | stage shake, 4 px decaying over 150 ms. **S3 and ULT only**; honours the Screen Shake and Reduce Motion settings |
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
| primary layer scale (first layer of S1, the same sheet at S2/S3) | 0.8-1.2 | >= S1 | >= S2 | any |
| `!shake` | no | no | allowed | allowed |
| first `@t` layer delay | <= 200 ms | | | |

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
neutral untinted. Stay within +/-90 deg of a sheet's own hue unless the sheet is uncoloured; prefer the
family's own sheet over a re-hued stranger.

**Low VFX / Battery Saver / Reduce Motion:** only the first layer plays, at 0.75x length; flags are off.

### Consumers

- `dfmc-client/play/app.js` `VFX_BANK` - parses the columns and draws the layers as stepped sprite-sheet
  animations over the unit tile; the sheets ship inside the client at `play/assets/fx/bank/`.
- `dfmc/vfx.html` + `assets/vfx/vfx_fx.js` - the review page draws the same thing from the same columns.
- `tools/fx_lint.py` - the authoring gate: grammar, ids, budgets, family identity. Exit 0 or nothing ships.
- `tools/sync_move_vfx.py` - copies the VFX/AFX/FX columns from `move_vfx.csv` onto `moves.csv` by Move_ID.
