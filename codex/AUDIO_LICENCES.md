# Audio licences — Herumon Tower

Every sound the Tower ships, its licence and where it came from. Ingested 2026-09-24 from
`dfmc-dungeon` (`docs/assets-licences.md` § Audio placeholders, § The eleven zone beds, § AFX bank);
the facts are that repo's, the files are copies. Nothing here is CC-BY, so no credit line is
*required* — the attributions below are recorded as a courtesy and because a pack cannot be
re-sourced from a filename.

Per-clip provenance for the bank lives in `codex/afx_bank.csv` itself (`Licence`, `Licence_URL`,
`Attribution`, `Pack`, `Source_URL` on every row) and is rendered on `audio.html`. This page is the
pack- and track-level summary.

## The AFX bank — 606 clips, Kenney, every pack CC0 1.0

`codex/afx_bank.csv` + `assets/afx/<pack>/*.ogg`. All eight packs are CC0 1.0
(<https://creativecommons.org/publicdomain/zero/1.0/>): no attribution, no fee, commercial use and
redistribution both allowed — redistribution matters because this site is served publicly.

| Pack | Clips | Licence | Source |
| --- | --- | --- | --- |
| Kenney Impact Sounds | 130 | CC0-1.0 | <https://kenney.nl/assets/impact-sounds> |
| Kenney Interface Sounds | 100 | CC0-1.0 | <https://kenney.nl/assets/interface-sounds> |
| Kenney Music Jingles | 85 | CC0-1.0 | <https://kenney.nl/assets/music-jingles> |
| Kenney Sci-fi Sounds | 73 | CC0-1.0 | <https://kenney.nl/assets/sci-fi-sounds> |
| Kenney Digital Audio | 62 | CC0-1.0 | <https://kenney.nl/assets/digital-audio> |
| Kenney Casino Audio | 54 | CC0-1.0 | <https://kenney.nl/assets/casino-audio> |
| Kenney RPG Audio | 51 | CC0-1.0 | <https://kenney.nl/assets/rpg-audio> |
| Kenney UI Audio | 51 | CC0-1.0 | <https://kenney.nl/assets/ui-audio> |

Considered and refused, so nobody re-sources them: Kenney Voiceover Pack and Voiceover Pack
(Fighter) — spoken words, against the standing **No words** rule. Incompetech / Kevin MacLeod —
CC-BY 4.0, which needs a credit line this site has nowhere to put.

## The music beds — 13 tracks, OpenGameArt, every one CC0 1.0

`codex/bgm.csv` + `assets/bgm/<slug>.ogg`. One work per zone, by its own author: the CC0
dedication was read off each OpenGameArt node page's own licence field
(`creativecommons.org/publicdomain/zero/1.0` and nothing else) before the file was taken. Each bed
is cut to a 60–120 s seamless loop, low-passed per zone and loudness-matched in file, with the
`Gain` cell finishing the match to −29 LUFS at play. The uncut originals are ~136 MB and are not
committed to any repo; `dfmc-dungeon tools/audio/zone-beds.mjs --fetch` re-downloads them.

| Track | Plays on | Title | Author | Licence | Source |
| --- | --- | --- | --- | --- | --- |
| `grasslands` | Grasslands | Sunset Plains | yoiyami | CC0-1.0 | <https://opengameart.org/content/sunset-plains> |
| `tidal` | Tidal Shallows | The Seeing Pool | umplix | CC0-1.0 | <https://opengameart.org/content/the-seeing-pool> |
| `desert` | Desert Plains | Desert Loop | iamoneabe | CC0-1.0 | <https://opengameart.org/content/desert-loop> |
| `thicket` | Swarm Thicket | Creepy Forest (F) | haeldb | CC0-1.0 | <https://opengameart.org/content/creepy-forest-f> |
| `crag` | The Crag | White Limestone | bobjt | CC0-1.0 | <https://opengameart.org/content/white-limestone> |
| `peaks` | Storm Peaks | rain and thunders | mikhog | CC0-1.0 | <https://opengameart.org/content/rain-and-thunders> |
| `bog` | Sunken Bog | Swamp Environment Audio | lokif | CC0-1.0 | <https://opengameart.org/content/swamp-environment-audio> |
| `undercave` | Underwater Cave | Nautilus | poinl | CC0-1.0 | <https://opengameart.org/content/nautilus> |
| `gemstone` | Gemstone Cave | Crystal Cave | pro-sensory | CC0-1.0 | <https://opengameart.org/content/crystal-cave> |
| `hellscape` | Flaming Hellscape | The 9th Circle | joth | CC0-1.0 | <https://opengameart.org/content/the-9th-circle> |
| `hub` | The hub | Medieval: The Bard's Tale | RandomMind | CC0-1.0 | <https://opengameart.org/content/medieval-the-bards-tale> |
| `boss` | Boss floors | Heavy Boss Battle 1 | MintoDog | CC0-1.0 | <https://opengameart.org/content/heavy-boss-battle-1> |
| `title` | The title screen | Dark Cavern Ambient | Paul Wortmann | CC0-1.0 | <https://opengameart.org/content/dark-cavern-ambient> |

`music_zone_void` (tozan, "Manaos Drones") exists in the dungeon and is **not** ingested: the Void
Apex folds onto the ten zone beds two floors at a time [R D 2026-09-24], so the Tower has no
eleventh bed to license. Also auditioned and CC0, rejected with the reason: neonarkade "Ends of the
Earth" — cuts between sections; springyspringo "Watch The Sand" — dual-licensed CC-BY 3.0 + CC0
where a CC0-only pick was available.

## The event cues — 33 files

`codex/afx_events.csv` + `assets/afx/cues/*.ogg`, copied unchanged from the dungeon's authored cue
set with their tuned `Gain` and `Retrigger_Ms`. Each is either a CC0 Kenney clip or synthesised for
the project (no third-party licence at all).

| Cue file | Dungeon cue | Origin |
| --- | --- | --- |
| `boss_arrive.ogg` | `boss.arrive` | Kenney "sci-fi-sounds" spaceEngineLow_000.ogg (CC0) |
| `boss_victory.ogg` | `boss.fell` | Synthesised for this project (no third-party licence) |
| `combat_death_enemy.ogg` | `combat.death_enemy` | Kenney "impact-sounds" impactSoft_heavy_000.ogg (CC0) |
| `combat_death_player.ogg` | `combat.death_player` | Kenney "sci-fi-sounds" lowFrequency_explosion_000.ogg (CC0) |
| `combat_hit.ogg` | `combat.hit` | Kenney "impact-sounds" impactPunch_medium_000.ogg (CC0) |
| `combat_hurt.ogg` | `combat.hurt` | Kenney "impact-sounds" impactPunch_heavy_000.ogg (CC0) |
| `craft_fail.ogg` | `craft.fail` | Kenney "rpg-audio" metalPot3.ogg (CC0) |
| `craft_feed.ogg` | `craft.feed` | Kenney "rpg-audio" chop.ogg (CC0) |
| `craft_success.ogg` | `craft.success` | Kenney "rpg-audio" metalPot1.ogg (CC0) |
| `egg_dismantle.ogg` | `egg.dismantle` | Kenney "impact-sounds" impactGlass_heavy_000.ogg (CC0) |
| `egg_hatch.ogg` | `egg.hatch` | Kenney "impact-sounds" impactGlass_light_000.ogg (CC0) |
| `egg_lay.ogg` | `egg.lay` | Kenney "rpg-audio" bookPlace1.ogg (CC0) |
| `floor_arrive.ogg` | `floor.arrive` | Kenney "sci-fi-sounds" doorOpen_000.ogg (CC0) |
| `floor_gate_open.ogg` | `floor.gate_open` | Kenney "rpg-audio" doorOpen_2.ogg (CC0) |
| `floor_gear_drop.ogg` | `floor.gear_drop` | Kenney "rpg-audio" dropLeather.ogg (CC0) |
| `floor_item.ogg` | `floor.item` | Kenney "rpg-audio" handleSmallLeather.ogg (CC0) |
| `hub_bank.ogg` | `hub.bank` | Kenney "rpg-audio" handleCoins2.ogg (CC0) |
| `hub_devour.ogg` | `hub.devour` | Kenney "sci-fi-sounds" slime_001.ogg (CC0) |
| `hub_revive.ogg` | `hub.revive` | Kenney "music-jingles" jingles_STEEL03.ogg (CC0) |
| `move_stairs.ogg` | `move.stairs` | Kenney "rpg-audio" doorClose_1.ogg (CC0) |
| `pen_start.ogg` | `pen.start` | Kenney "interface-sounds" toggle_001.ogg (CC0) |
| `pen_stop.ogg` | `pen.stop` | Kenney "interface-sounds" toggle_002.ogg (CC0) |
| `progress_advance.ogg` | `progress.advance` | Synthesised, tools/audio/advance-cue.mjs (CC0) |
| `progress_level_up.ogg` | `progress.level_up` | Kenney "music-jingles" jingles_PIZZI00.ogg (CC0) |
| `status_apply.ogg` | `status.apply` | Kenney "interface-sounds" glass_001.ogg (CC0) |
| `status_bleed.ogg` | `status.bleed` | Kenney "impact-sounds" impactSoft_medium_003.ogg (CC0) |
| `town_enter.ogg` | `town.enter` | Kenney "music-jingles" jingles_PIZZI09.ogg (CC0) |
| `ui_click.ogg` | `ui.click` | Synthesised by tools/audio/ui-cues.mjs (no source file; deterministic, rebuildable). |
| `ui_close.ogg` | `ui.close` | Synthesised by tools/audio/ui-cues.mjs (no source file; deterministic, rebuildable). |
| `ui_deny.ogg` | `ui.deny` | Synthesised by tools/audio/ui-cues.mjs (no source file; deterministic, rebuildable). |
| `ui_open.ogg` | `ui.open` | Synthesised by tools/audio/ui-cues.mjs (no source file; deterministic, rebuildable). |
| `ui_select.ogg` | `ui.select` | Synthesised by tools/audio/ui-cues.mjs (no source file; deterministic, rebuildable). |
| `ui_toast.ogg` | `ui.toast` | Synthesised by tools/audio/ui-cues.mjs (no source file; deterministic, rebuildable). |

The six `ui_*` cues are synthesised by the dungeon's `tools/audio/ui-cues.mjs` and replace a Kenney
UI/interface pick that breached **Nothing shrill** on every row — which is also why the bank's
`ui`, `coin`, `jingle` and `door` groups are refused on a move composition (`codex/AFX_SPEC.md`).

## Replacing a sound

Overwrite the file in place and re-measure. The bank's `Centroid_Hz`, `Over3k_Pct` and `Peak_dBFS`
columns are what `tools/afx_lint.py` judges **Nothing shrill** by, so a swapped clip with stale
metrics is a lie the linter will believe. Paid or AI-generated audio (Suno, ElevenLabs SFX) is a
roadmap tail item, not a placeholder path.
