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
