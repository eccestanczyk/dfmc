# AFX_SPEC — the Tower's sound

The owning page for every sound Herumon Tower makes. Three data files, one grammar, one player.
`codex/VFX_SPEC.md` is its twin for the picture and the two are meant to be read together: a move's
sound is authored against that move's FX composition, not on its own.

Review page: `audio.html` (the beds, the events, the 606 clips). `vfx.html` plays a move's
composition in sync with its effect, which is the only place the two can be judged as one thing.

Ingested 2026-09-24 from `dfmc-dungeon`, which authored and measured the bank, the beds and the cue
set. Licences: `codex/AUDIO_LICENCES.md`.

## The standing rules

They are the dungeon's, they are D's, and they apply here unchanged.

1. **Nothing shrill** [R D 2026-09-14] — *"Never use annoying high pitched sounds, deeper is better
   and more comfortable."* Judged by **measurement**, never by adjective. `codex/afx_bank.csv` carries
   `Centroid_Hz`, `Over3k_Pct` and `Peak_dBFS` per clip. `Over3k_Pct >= 20` is **SHRILL**;
   `Peak_dBFS > 0` is **CLIPPED**. Pitching down (`p` negative) moves a clip's whole spectrum with it
   by `2^(p/12)`; a gain under 1 takes a clipped clip back under 0 dBFS at playback.
2. **No words.** No cue may carry a readable phrase.
3. **Nothing peaks above 0 dBFS.** Music sits far under the cues: the beds are loudness-matched in
   file and the `Gain` cell finishes the match to −29 LUFS, with nothing in music peaking above
   −3 dBFS at play.
4. **Dark fantasy / grimdark.** A sound is coherent with the creature using the move, the move's
   flavour text, and (for a bed) the zone's design. No cheerful chimes, no casino, no sci-fi laser
   reads unless pitched into a drone or rune register. Bless and heal are a low warm swell, not a
   bell. Hex and curse fall and shudder. Ward is muffled metal. Impacts are low and dry.

And the lesson the VFX run paid for [D 2026-09-17]: **a mounting gate is not proof it is right.**
`tools/afx_gate.py` proves the player was invoked with a parsed composition. It cannot hear it.

## The grammar

Columns `AFX_S1, AFX_S2, AFX_S3` on `codex/move_vfx.csv` (mirrored to `codex/moves.csv` by
`tools/sync_move_vfx.py`). ULT rows (`ULT-<LINE>-<stage>`) carry `AFX_S1` only — their stage *is* the
row. The older `AFX_Archetype*`, `AFX_Layer` and `AFX_Pitch` columns stay as the synth fallback's
taxonomy and are **not** re-authored.

A composition is layers separated by ` | `. A layer is:

```
AFX-NNN [g<gain>] [p<semitones>] [d<ms>] [n<count>] [i<ms>] [j<semitones>]
```

| token | range | default | meaning |
|---|---|---|---|
| `g` | 0.05 – 1.5 | 1 | gain multiplier on the sfx bus |
| `p` | −12 – 12 | 0 | pitch in semitones: `playbackRate = 2^(p/12)`, so it shortens or lengthens the clip too |
| `d` | 0 – 2000 | 0 | delay in ms from the cast |
| `n` | 1 – 4 | 1 | repeats |
| `i` | 30 – 600 | 90 | ms between repeats — only meaningful with `n>1` |
| `j` | 0 – 3 | 0 | random pitch jitter ± semitones, re-rolled on every play and every repeat |

A token appears at most once per layer. `p`, `d`, `n`, `i`, `j` are integers; `g` is not.

```
layer end       = d + (n-1)*i + Seconds*1000 / 2^(p/12)
composition end = max(layer end)
```

### Budgets — the same ladder as the picture

| stage | layers | max length |
|---|---|---|
| S1 | 1–2 | 900 ms |
| S2 | 1–3 | 1200 ms |
| S3 | 2–4 | 1600 ms |
| ULT | 3–5 | 2600 ms |

### The rules `tools/afx_lint.py` enforces

- **Existence and range.** Every id is in `codex/afx_bank.csv`; every token is in range; no token
  twice in a layer (a repeat is silently the last one, which is how a calibrated value gets pasted
  over an authored one and nobody sees it); `i` without `n>1` is refused as a no-op.
- **Family identity.** S2 and S3 each play S1's **first** clip id somewhere — any `g`, `p`, `d`. One
  creature's move has to stay recognisable as itself across its three stages.
- **Groups.** On a move, only `impact, material, melee, blast, arcane, machine, creature, foley,
  footstep`. `ui, coin, jingle, door` are **refused**: they are the interface, the casino, the fanfare
  and the furniture. They stay in the bank because `afx_events.csv` needs them.
- **Hygiene.** A SHRILL clip needs `p <= -3`. A CLIPPED clip needs `g <= 0.7`. The sum of `g` over
  layers whose `d` fall within 60 ms of each other is `<= 1.6` — inside that window two onsets read as
  one hit and their gains add.
- **Timing.** The composition's **main beat** — its first layer with `g > 0.5` — sits within ±40 ms of
  the FX composition's first `@t`/`@g`/`@b` layer (for a self or ground-on-user move with no target
  layer, its earliest layer). And a layer at `d0` on a move whose hit lands later than 100 ms must
  have `g <= 0.5`: a cast beat is quieter than the hit.

  **Those two compose, and only one reading lets them.** A quiet `d0` wind-up is exempt from the pin
  and bound by the beat rule instead; otherwise, on a move whose picture lands at d200, aligning the
  wind-up would break the pin and keeping it would break the alignment, and no composition could
  satisfy both. A composition of nothing but quiet layers pins its earliest layer.

### What the bank's own measurements mean for authoring

Worth knowing before picking a clip, because the numbers are not evenly spread:

- **All 45 `impact` clips are CLIPPED** (`Peak_dBFS` +1.8 to +2.2) and none is shrill. An impact layer
  therefore always carries `g <= 0.7`. This is not a flaw in the pool — it is Kenney's mastering — and
  the gain is the fix, not a re-encode.
- `material` is 56 clipped of 70, `footstep` 31 of 35. `arcane` is the cleanest usable group (56 of 77
  need nothing).
- 176 of the 606 are shrill and 128 of those are in `ui`/`coin`/`door`, which a move cannot use
  anyway. The shrill clips that remain are usable pitched down by three semitones or more.

### Modes

```
python tools/afx_lint.py                    # codex/move_vfx.csv: an unauthored row FAILS
python tools/afx_lint.py --allow-empty      # an unauthored row is reported and exit stays 0
python tools/afx_lint.py <lane.csv>         # Move_ID,AFX_S1,AFX_S2,AFX_S3[,AFX_Notes]
python tools/merge_afx_lanes.py <lane.csv>  # merge a lane back into move_vfx.csv, then re-lint + sync
```

`--allow-empty` exists for exactly the state this file ships in: the columns are there, the player is
there, the gate is green, and **not one row is authored yet**. Without the flag that is red, which is
correct once a lane starts filling them.

## The three CSV schemas

### `codex/afx_bank.csv` — 606 clips

Copied **verbatim** from `dfmc-dungeon play/codex/afx_bank.csv`. Same ids, same columns, and `File`
paths (`assets/afx/<pack>/<name>.ogg`) that resolve under both this repo and `dfmc-client/play/`, so
one id means one recording in all three places.

`Id, Name, Group, File, Seconds, KB, Centroid_Hz, Over3k_Pct, Peak_dBFS, Pack, Licence, Licence_URL,
Attribution, Source_URL, Used_In, Candidate`

`Used_In` is the dungeon's own usage record and is **not** maintained here; `audio.html` computes the
Tower's usage live from the `AFX_S*` columns and `afx_events.csv` instead.

### `codex/afx_events.csv` — everything that is not a move

`Event_ID, Category, Trigger, File, Gain, Retrigger_Ms, Notes`

Files under `assets/afx/cues/<name>.ogg`, copied from the dungeon's authored cue set with its **tuned
`Gain` and `Retrigger_Ms`** — those levels were set against the rules above and re-tuning them here
would fork them. `Trigger` is the Tower's own sentence: the same recording, a different game's moment.
`Retrigger_Ms` is the minimum gap between two plays of one event; blank means no limit.

### `codex/bgm.csv` — 13 tracks

`Track_ID, State, Zone, File, Gain, LUFS, Peak_dBFS, Seconds, KB, Title, Author, Source_URL, Licence,
Notes`

Ten zone beds plus `hub`, `boss` and `title`. `Zone` matches `codex/floors.csv` `Zone` **exactly** and
is blank for the three that are not zones. `LUFS` and `Peak_dBFS` are measured **in file**; `Gain` is
the multiplier that lands the file at −29 LUFS at play.

### The Void Apex fold [R D 2026-09-24]

`codex/floors.csv` has eleven zones. `bgm.csv` has ten beds. The apex does not get an eleventh:

> **Floors 101–120 reuse the zone beds two floors at a time** — 101–102 play zone 1 (Grasslands),
> 103–104 zone 2, … 119–120 zone 10.

```
zone = floor >= 101 ? ((floor - 101) // 2) + 1
                    : ((floor - 1) // 10) + 1
```

The climb is heard a second time at four times the speed, which is what the apex is. The dungeon's
`music_zone_void` bed is **not** ingested and the Tower has no eleventh bed to license.

`boss` overrides the zone bed on the 20 boss floors (10, 20 … 100, then every even floor 102–120).

## The player contract — `AFX_BANK`

Implemented **once**, in the client (`play/app.js`, `const AFX_BANK=(()=>{ ... })();`), and lifted
into `assets/vfx/afx_bank.js` as `window.DFMC_AFX_BANK` by `tools/gen_vfx_fx.py` — the same
arrangement as `VFX_BANK`, for the same reason: when the game and the review page had two
implementations, approving an effect on the review page approved something players never got.

Self-contained IIFE, no React, no game state. Web Audio, one `AudioContext`, buses
`master -> music` and `master -> sfx`, decoded buffers cached by file path, decoded on first use,
never more than one decode in flight per path.

```
AFX_BANK.parse(text[, bank])      -> {layers:[{id,g,p,d,n,i,j}], errs:[...]}   same verdicts as afx_lint.py
AFX_BANK.layerMs(layer[, bank])   -> one layer's end, in ms
AFX_BANK.lengthMs(parsed|text[, bank]) -> the composition's end, in ms
AFX_BANK.zoneFor(floor)           -> 1..10, by the Void Apex fold below
AFX_BANK.trackForZone(zoneName)   -> the bgm.csv Track_ID whose `Zone` cell is that name, or null
AFX_BANK.load(rows, base, kind)   -> register ONE table. `kind` is 'bank' | 'events' | 'bgm', inferred
                                     from the first row when omitted; `base` prefixes `File`.
AFX_BANK.play(parsed|text, opts)  -> handle {stop()}   opts: {speed = duration multiplier (default 1), gain, bank}
AFX_BANK.cue(id, opts)            -> play an afx_events.csv event by Event_ID, honouring Retrigger_Ms
AFX_BANK.music(trackId|null,opts) -> crossfade to a bgm.csv track (in 1200 ms, out 900 ms, looped,
                                     Gain applied). null stops. The same id is a no-op.
AFX_BANK.setMix({master,music,sfx}) / getMix()   0..100 each, tapered (pct/100)^1.6
AFX_BANK.unlock()                 -> resume the context on the first gesture (click/keydown/touchstart, once)
AFX_BANK.mute(bool) / isMuted() / isUnlocked() / playing()
AFX_BANK.bank() / events() / tracks()   -> the three registries. FUNCTIONS, not properties.
```

`speed` scales every `d` and every `i` — the client's fast-forward — and **never** the pitch. A
missing file logs once to the console, plays nothing, and never throws.

**Three things a consumer gets wrong exactly once**, all three found the day the real player replaced
the stub, all three on the codex side, because the stub and the client agreed on behaviour and
disagreed on spelling:

1. `load()` reads the kind off the FIRST row and **replaces** that registry. One mixed array registers
   the bank and silently drops the cues and the beds — the page looks fine and plays no music at all.
   Call it three times, once per table.
2. `bank`, `events` and `tracks` are **functions**. `Object.keys(AFX_BANK.bank)` is `[]`, which reads
   as an empty bank rather than as a mistake; that is what held `tools/afx_gate.py` at a 45-second
   timeout on `the page is not playing from the AFX bank`.
3. `play()` returns a stop handle and **no length**. Ask `lengthMs()` for the length.

**One deliberate asymmetry with the linter.** The client enforces integer `d`, `n` and `i`;
`tools/afx_lint.py` also requires integer `p` and `j`. The linter is the stricter of the two on
purpose — nothing that passes lint can surprise the player — and the table above is what an author
writes to.

## Consumers

| who | reads |
|---|---|
| the client | `AFX_BANK` inline in `play/app.js`; the three CSVs shipped under `play/codex/` |
| `vfx.html` | `assets/vfx/afx_bank.js`; plays `AFX_S<stage>` in sync with `FX_S<stage>`, falls back to the `DFMC_AFX` synth when the composition is empty |
| `audio.html` | all three CSVs: the beds with the fold, the events, the 606 clips with their metrics and flags |
| `tools/afx_lint.py` | `codex/afx_bank.csv` + the `AFX_S*` and `FX_S*` columns |
| `tools/afx_gate.py` | both pages, every `File` cell, and a sample of casts |

## Changelog

- **2026-09-24 (b)** — **the client's player landed and all 419 rows are authored.**
  `assets/vfx/afx_bank.js` is no longer a stub: `tools/gen_vfx_fx.py --write` lifts the client's real
  `AFX_BANK` block, and six authoring lanes filled every `AFX_S1..AFX_S3` cell — 173 of the 606
  clips are in use. Three codex-side fixes travelled with it, all three listed under the contract
  above, plus one in the generator itself: it compared the RAW lifted block against an indented copy,
  so its AFX check reported DIVERGED on a file it had just written. A permanently red gate is a gate
  nobody reads.
- **2026-09-24** — **the AFX bank arrives.** 606 CC0 clips, 13 music beds and 34 event cues ingested
  from `dfmc-dungeon`; this grammar, `tools/afx_lint.py`, `tools/merge_afx_lanes.py`, the
  `AFX_S1..AFX_S3` columns, a lifted-player stub to stand until the client lane landed, `audio.html`
  and `tools/afx_gate.py`. The Void Apex fold is D's ruling of the same day. `--allow-empty` is how
  the pre-authoring state stayed green; it is not needed now and must not be used to hide a gap.
