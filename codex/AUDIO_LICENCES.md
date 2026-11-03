# Audio licences — Herumon Tower

Every sound the Tower ships, its licence and where it came from. Ingested 2026-09-24 from
`dfmc-dungeon` (`docs/assets-licences.md` § Audio placeholders, § The eleven zone beds, § AFX bank);
the facts are that repo's, the files are copies. Everything ingested then is CC0, so no credit line
is *required* for it — the attributions below are recorded as a courtesy and because a pack cannot be
re-sourced from a filename. The one exception is the third pass (below, 2026-11-04): seven spell
submissions licensed CC-BY 3.0, whose credit lines are on the public `credits.html` (the page the
game's *Settings › Legal & Support › Credits* opens) and in each row's `Attribution` cell.

Per-clip provenance for the bank lives in `codex/afx_bank.csv` itself (`Licence`, `Licence_URL`,
`Attribution`, `Pack`, `Source_URL` on every row) and is rendered on `audio.html`. This page is the
pack- and track-level summary.

## The AFX bank — 895 clips, 43 packs: CC0 1.0, and seven CC-BY 3.0 spell submissions (the third pass)

`codex/afx_bank.csv` + `assets/afx/<pack>/*.ogg`. All thirty packs are CC0 1.0
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

### The second pass — 246 clips the moves needed, from OpenGameArt [2026-09-24]

`AFX-607`…`AFX-852`. The eight Kenney packs have no fire, no wind, no steam, no water, no ice, no
thunder, no bone, no stone rumble and no throat; every noise clip in `sci-fi-sounds` is a 5.00 s loop
that fits no stage budget, and `creature` was two slime clips carrying 153 wet layers between them.
These 22 OpenGameArt submissions are those gaps. Every one is CC0 1.0, read off its own node page
before the file was taken.

| Submission | Author | Clips | Licence | Source |
| --- | --- | --- | --- | --- |
| 80 CC0 creature SFX | rubberduck | 38 | CC0-1.0 | <https://opengameart.org/content/80-cc0-creature-sfx> |
| 80 CC0 creature SFX #2 | rubberduck | 35 | CC0-1.0 | <https://opengameart.org/content/80-cc0-creture-sfx-2> |
| 40 CC0 water / splash / slime SFX | rubberduck | 25 | CC0-1.0 | <https://opengameart.org/content/40-cc0-water-splash-slime-sfx> |
| 75 CC0 breaking / falling / hit SFX | rubberduck | 32 | CC0-1.0 | <https://opengameart.org/content/75-cc0-breaking-falling-hit-sfx> |
| 30 CC0 SFX loops | rubberduck | 22 | CC0-1.0 | <https://opengameart.org/content/30-cc0-sfx-loops> |
| 25 CC0 bang / firework SFX | rubberduck | 15 | CC0-1.0 | <https://opengameart.org/content/25-cc0-bang-firework-sfx> |
| 100 CC0 SFX | rubberduck | 17 | CC0-1.0 | <https://opengameart.org/content/100-cc0-sfx> |
| Fire Crackling | AntumDeluge | 1 | CC0-1.0 | <https://opengameart.org/content/fire-crackling> |
| Catching fire | themightyglider | 1 | CC0-1.0 | <https://opengameart.org/content/catching-fire> |
| Fireplace Sound loop | PagDev | 1 | CC0-1.0 | <https://opengameart.org/content/fireplace-sound-loop> |
| Flare ignition | qubodup | 1 | CC0-1.0 | <https://opengameart.org/content/flare-ignition> |
| wind1 | Luke.RUSTLTD | 5 | CC0-1.0 | <https://opengameart.org/content/wind1> |
| Rain + Long Thunder | WuxiaScrub | 1 | CC0-1.0 | <https://opengameart.org/content/rain-long-thunder> |
| Ice breaking / shattering | IgnasD | 5 | CC0-1.0 | <https://opengameart.org/content/ice-breakingshattering> |
| Ice spells | bart | 2 | CC0-1.0 | <https://opengameart.org/content/ice-spells> |
| Deep Bone Crack / Break SFX | Zane Little Music | 10 | CC0-1.0 | <https://opengameart.org/content/deep-bone-crackbreak-sfx> |
| Fleshy Bone Break / Snap SFX | Zane Little Music | 10 | CC0-1.0 | <https://opengameart.org/content/fleshy-bone-breaksnap-sfx> |
| Bones rattle | congusbongus | 10 | CC0-1.0 | <https://opengameart.org/content/bones-rattle> |
| Ghost Monster Voice Moaning and Growling | qubodup | 5 | CC0-1.0 | <https://opengameart.org/content/ghost-monster-voice-moaning-growling> |
| Different steps on wood, stone, leaves, gravel and mud | TinyWorlds | 8 | CC0-1.0 | <https://opengameart.org/content/different-steps-on-wood-stone-leaves-gravel-and-mud> |
| Sand spell | qubodup | 1 | CC0-1.0 | <https://opengameart.org/content/sand-spell> |
| Dragon Flap | VishwaJai | 1 | CC0-1.0 | <https://opengameart.org/content/dragon-flap-0> |

**What was done to them.** Nothing mixed, nothing re-titled. Two edits, both by the dungeon's
`tools/audio/afx_bank.py` through its own `ffmpeg-static`, and both recorded in the row:

- **Cut** — a clip longer than its pack's ceiling is cut to a window that long with a 120 ms
  fade-out, because `p` can only halve a clip and a 2.5 s texture cannot play inside a 1600 ms stage
  at any pitch the grammar allows. The window is in the clip's `Name`: *Wind 1 (cut 1s at 8.5s of
  60.0s)*. Where it opens matters — "Rain + Long Thunder" is 44 s of rain with the thunder at 22 s.
- **Levelled** — six packs of quiet field recordings (wind, fire, the loops, the footsteps) are
  levelled to −6 dBFS. wind1 peaks at −27, which even at the grammar's loudest `g1.5` is 20 dB under
  an impact. Headroom in the file, mix in the composition's `g`.

Not every clip of a submission is here: `Id` is `AFX-NNN`, three digits, and the client's parser pins
that width, so the bank cannot cross 999 clips and each pack came in as the clips the gap needed. And
rubberduck's creature #2 ships `human_01..08`, which nobody on that run could listen to, so under the
standing **No words** rule they are not in the bank at all.

49 of the 246 pass § Nothing shrill untouched; the rest are usable under the grammar's own hygiene
(`p <= -3` for a shrill clip, `g <= 0.7` for a clipped one), which is where most of the Kenney half
already sits.

Considered and not taken on that pass: Freesound (has a CC0 filter, but downloads need a login),
Sonniss GDC bundles (not CC0), Pixabay (its own licence, not CC0), and Fantozzi's footsteps plus
qubodup's snow and rustle sets — CC0, but shipped as .7z and there is no 7-Zip on the build machine.

Considered and refused, so nobody re-sources them: Kenney Voiceover Pack and Voiceover Pack
(Fighter) — spoken words, against the standing **No words** rule. Incompetech / Kevin MacLeod —
CC-BY 4.0, which needs a credit line this site has nowhere to put.

### The third pass — 42 recorded spells for the rune register, CC0 and CC-BY 3.0 [2026-11-04, dfmc-client lane AU2]

`AFX-854`…`AFX-895`, group `arcane`. D (chat, 2026-11-04): *"a lot of our AFX for Tower is not very
good"* — after lane AU took the voices off, the worst left was the Kenney Digital Audio chiptune set
standing in as the rune register (488 move layers). The Dungeon had nothing newer to give (its bank
is this bank), so these 13 OpenGameArt submissions were sourced for it, each licence read off its own
node page before the file was taken (raw downloads and the node pages kept in
`E:\Herumon-Tower\local-only\afx-src\oga-<slug>\`). D's order allows CC-BY where a credit line is all
it asks; nothing NC, ND, SA or GPL-only was taken (*Spell 4 (fire)* and *3 Heal Spells* are
multi-licensed and taken under their CC-BY 3.0 option; HaelDB's *Spell sounds* under its CC0 option).

| Submission | Author | Clips | Licence | Source | Credit line (CC-BY) |
| --- | --- | --- | --- | --- | --- |
| Spell sounds | HaelDB | 9 | CC0-1.0 | <https://opengameart.org/content/spell-sounds> | - |
| Magic Spell SFX | JaggedStone | 7 | CC0-1.0 | <https://opengameart.org/content/magic-spell-sfx> | - |
| RPG Sound Pack | artisticdude | 3 | CC0-1.0 | <https://opengameart.org/content/rpg-sound-pack> | - |
| Teleport Spell | Ogrebane | 2 | CC0-1.0 | <https://opengameart.org/content/teleport-spell> | - |
| Freeze Spell | artisticdude | 2 | CC0-1.0 | <https://opengameart.org/content/freeze-spell-0> | - |
| Earth Element Magic Spell | qubodup | 1 | CC0-1.0 | <https://opengameart.org/content/earth-element-magic-spell> | - |
| Fantasy Sound Effects Library | Little Robot Sound Factory | 5 | CC-BY-3.0 | <https://opengameart.org/content/fantasy-sound-effects-library> | "Fantasy Sound Effects Library" by Little Robot Sound Factory - www.littlerobotsoundfactory.com (https://opengameart.org/content/fantasy-sound-effects-library), CC-BY 3.0; trimmed, filtered and level-matched |
| 3 Heal Spells | DoKashiteru | 3 | CC-BY-3.0 | <https://opengameart.org/content/3-heal-spells> | "3 Heal Spells" by DoKashiteru (https://opengameart.org/content/3-heal-spells), CC-BY 3.0; trimmed, filtered and level-matched |
| Magic SFX Sample | ViRiX | 3 | CC-BY-3.0 | <https://opengameart.org/content/magic-sfx-sample> | "Magic SFX Sample" by ViRiX (https://opengameart.org/content/magic-sfx-sample), CC-BY 3.0; trimmed, filtered and level-matched |
| Magic Shield | spookymodem | 2 | CC-BY-3.0 | <https://opengameart.org/content/magic-shield> | "Magic Shield" by spookymodem (https://opengameart.org/content/magic-shield), CC-BY 3.0; trimmed, filtered and level-matched |
| Magic Smite | spookymodem | 2 | CC-BY-3.0 | <https://opengameart.org/content/magic-smite> | "Magic Smite" by spookymodem (https://opengameart.org/content/magic-smite), CC-BY 3.0; trimmed, filtered and level-matched |
| Torch Fire Spell | spookymodem | 2 | CC-BY-3.0 | <https://opengameart.org/content/torch-fire-spell> | "Torch Fire Spell" by spookymodem (https://opengameart.org/content/torch-fire-spell), CC-BY 3.0; trimmed, filtered and level-matched |
| Spell 4 (fire) | bart | 1 | CC-BY-3.0 | <https://opengameart.org/content/spell-4-fire> | "Spell 4 (fire)" by bart (https://opengameart.org/content/spell-4-fire), CC-BY 3.0; trimmed, filtered and level-matched |

**What was done to them** (ffmpeg-static from the Dungeon checkout + numpy, by path; nothing in the
download folders was executed): a high-pass at 60-130 Hz (the sub rumble a phone speaker turns into
distortion, the #993 lesson), a low-pass at 4-4.5 kHz on the four sources that measured shrill
(`Over3k_Pct >= 20`: Healing Full, Magic Shield, Spell_00, freeze; *Trap Snap* stays at 22 % and plays
under the grammar's `p <= -3` hygiene), a cut to a window of 0.5-1.45 s that starts at the clip's own onset (or the take
named in `Name`), a squared fade-out, then a gain to −18 LUFS integrated capped at −1 dBFS sample peak
(6 % headroom for the Vorbis encode), mono 48 kHz Vorbis q4. Most sources gave a long cut (S2 / S3 /
ultimate) and a short one (≤ 850 ms, because a W6 swap must fit S1's 900 ms budget too).

Considered and not taken: qubodup's *Time Magic*, *Spell Sounds Starter Pack* (CC-BY-SA / GPL);
*Replenish Life Force*, *Wisdom Magic*, *Energy Drain*, *Ghost breath* (built from a human voice —
lane AU took every voice off the abilities); *3 dark magic spells*, *Ice & Electricity Magic*,
*Growth Spell*, *Fire & Evil Spell* (7z only, no 7-Zip on the build machine); the shrill
(`Over3k_Pct` 50-99 %) *Misc 02*, *Ice attack 2*, *Spell_01*, *electricspell*, *magical 5-7* and the
sub booms (centroid under 90 Hz) *Fire impact 1*, *Spell_02*, *Spell_04*.

## The music beds — 10 zone tracks (OpenGameArt, every one CC0 1.0) and one synthesized boss bed

`codex/bgm.csv` + `assets/bgm/<slug>.ogg`. **Ten tracks, one per zone, and no others** — the `hub`,
`boss` and `title` beds ingested on 2026-09-24 were removed the same day under D's ruling that the
bed belongs to the zone and only a zone change moves it (`AFX_SPEC.md` § The bed is the zone's), and
their three files are not in this repo. One work per zone, by its own author: the CC0
dedication was read off each OpenGameArt node page's own licence field
(`creativecommons.org/publicdomain/zero/1.0` and nothing else) before the file was taken. Each bed
is cut to a 60–120 s seamless loop, low-passed per zone and loudness-matched in file, with the
`Gain` cell finishing the match to −29 LUFS at play. The uncut originals are ~136 MB and are not
committed to any repo; `dfmc-dungeon tools/audio/zone-beds.mjs --fetch` re-downloads them.

**Since 2026-10-01 (#1041, D: *"Need a boss battle song"*) there is one bed that is not a zone's:**
`boss.wav`, `State=boss`, blank `Zone`. It is synthesized from numbers by dfmc-client
`tools/afx_boss_bgm.py` (seed 1041; D minor, 150 BPM, 16 bars, seamless by construction) the way the
creature cries are - no third-party work in it, so nothing to licence and nothing to credit. WAV rather
than OGG because the dev machine has no Vorbis / Opus encoder (16-bit mono, 24 kHz, 1.2 MB, under the
beds' 8 kHz line). The client plays it for exactly as long as a boss fight is on; every other screen
keeps the zone rule above.

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
| `hub_devour.ogg` | `hub.devour` | Since 2026-10-01 (#1035): bank clip AFX-615 "Eat 02", 80 CC0 creature SFX (OpenGameArt, CC0). Was Kenney "sci-fi-sounds" slime_001.ogg (CC0), the 4.7 s gurgle D heard as water |
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
