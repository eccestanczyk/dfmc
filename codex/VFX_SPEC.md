# Move VFX Taxonomy (locked)

Source of truth mapping every move to a placeholder VFX archetype: codex/move_vfx.csv
Columns: Move_ID, Name, VFX_Archetype, VFX_Color, Target_Anchor, Duration_Class, VFX_Description.
Derived from Effect_S3 mechanics (first-match rules) + VFX_Description visual verbs.
The per-move VFX_Description is the eventual bespoke effect; archetypes are the placeholder layer.

20 archetypes (move counts):
generic_impact 152 · atk_down 41 · shield_def_up 31 · def_down 29 · heal 21 · melee_crush 17 ·
atk_up 17 · melee_slash 14 · cleanse 14 · pierce_strike 12 · whip_lash 12 · charge_impact 12 ·
bleed_dot 7 · projectile 6 · poison_dot 5 · speed_up 4 · burn_dot 2 · speed_down 2 · drain 1 · curse 1

Color hexes (approved icon palette):
blue #18306a (buff/heal/cleanse) · purple #3a1a56 (debuff/curse) · crimson #600e12 (bleed/drain) ·
green #144820 (poison) · red #6e1212 (burn) · rust #7e3818 (pierce) · bone #d8cfc0 (neutral damage)

Anchors: self / target / ground / both-sides. Durations: fast 0.4s / standard 0.6s / heavy 0.8s.
Constraint: SOLID opaque shapes only — no soft glow, no translucent aura, no blur.
