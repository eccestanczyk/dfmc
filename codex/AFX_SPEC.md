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
3. **Nothing peaks above 0 dBFS, and every clip shares one ceiling** [R D 2026-09-25, #993: *"Some
   sounds are way louder than the rest. They should all share a max loudness."*]. Music sits far under
   the cues: the beds are loudness-matched in file and the `Gain` cell finishes the match to −29 LUFS,
   with nothing in music peaking above −3 dBFS at play. The bank and the cues are matched **by the
   player**: `AFX_BANK.load()` derives a per-row trim from the measured `LUFS` and `Play_Peak_dBFS`
   cells — the gain that lands the clip at **−18 LUFS integrated, capped so it never peaks above
   −1 dBFS** at `g1` — and `play()` / `cue()` multiply it into the authored `g` / `Gain`. A short
   transient that cannot reach −18 LUFS under a −1 dBFS peak sits under the ceiling; nothing sits
   above it. −18 LUFS is the level the cues were already sitting near at their median and 11 LU over
   the beds; −1 dBFS is the peak margin. `tools/afx_measure.py` (client repo) writes both columns from
   a decode through the client's own decoder.
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
| `d` | 0 – 2000 | 0 | delay in ms from the cast to the clip's **hit** — its `Onset_Ms` crossing, not the file's first sample; the player starts the file that much earlier (2026-09-25, #994) |
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

  **`d` is where the hit lands, and the player makes it so** (2026-09-25, #994). The lint pins `d`; the
  hit a listener hears is the clip's own attack, `Onset_Ms` into the file, and 72 of the 208 clips a move
  plays carry more than a frame of it. `AFX_BANK.voice()` therefore starts the file early by
  `Onset_Ms / 2^(p/12)`, so the −12 dB-re-peak crossing lands on `d` and the pin above is a pin on what
  is heard. An author never compensates for a clip's lead-in in `d`. When there is no time to pre-roll —
  `d0` on a clip with lead-in — the player starts now at an offset into the lead-in (at most the onset,
  never into the hit) under a 5 ms fade. `dfmc-client/tools/afx_sync_audit.py` is the audit: every
  layer's hit against the picture beat it is authored on, before and after; `codex/afx_sync_audit.csv`
  is its table.

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
Attribution, Source_URL, Used_In, Candidate, LUFS, Play_Peak_dBFS, Onset_Ms`

`Used_In` is the dungeon's own usage record and is **not** maintained here; `audio.html` computes the
Tower's usage live from the `AFX_S*` columns and `afx_events.csv` instead.

`LUFS` and `Play_Peak_dBFS` (2026-09-25) are the Tower's own measurements, made by
`dfmc-client/tools/afx_measure.py` through the client's decoder (headless Chromium `decodeAudioData`
at 48 kHz): ITU-R BS.1770-4 integrated loudness (K-weighted, 400 ms blocks at 75 % overlap, gated at
−70 LUFS absolute and −10 LU relative; a clip shorter than one block is one block) and the sample peak
of that decode. `Peak_dBFS` stays the dungeon's in-file number — `afx_lint.py`'s CLIPPED verdict reads
it — but it differs from the decode by more than 1 dB on 611 of the 852 rows, so the player's ceiling
uses `Play_Peak_dBFS`. The player derives the trim (rule 3); nothing else reads these two.

`Onset_Ms` (2026-09-25, #994) is the clip's own attack from the same decode: the first sample whose
level reaches −12 dB re the clip's peak, in ms from the file's start. A punch is at 0–5 ms; a swell, or a
file mastered with lead-in, sits 100 ms or more in (the bank's worst in use is 255 ms). The player
pre-rolls each voice by it so an authored `d` is where the hit lands (the timing rule above);
`tools/afx_sync_audit.py` reads it against the picture.

### `codex/afx_events.csv` — everything that is not a move

`Event_ID, Category, Trigger, File, Gain, Retrigger_Ms, Notes, LUFS, Play_Peak_dBFS, Onset_Ms`

Files under `assets/afx/cues/<name>.ogg`, copied from the dungeon's authored cue set with its **tuned
`Gain` and `Retrigger_Ms`** — those levels were set against the rules above and re-tuning them here
would fork them. Since 2026-09-25 `Gain` is relative to the −18 LUFS ceiling (rule 3): the cue's clip
is trimmed to the ceiling first, then `Gain` applies, so `0.5` means 6 dB under it whatever the file
happens to hold. `LUFS` / `Play_Peak_dBFS` / `Onset_Ms` are the same measurements as on the bank, and a cue is pre-rolled by its onset like a layer. `Trigger` is the Tower's own sentence: the same recording, a different game's moment.
`Retrigger_Ms` is the minimum gap between two plays of one event; blank means no limit.

### `codex/bgm.csv` — 10 tracks

`Track_ID, State, Zone, File, Gain, LUFS, Peak_dBFS, Seconds, KB, Title, Author, Source_URL, Licence,
Notes`

Ten zone beds and nothing else. `Zone` matches `codex/floors.csv` `Zone` **exactly**; `LUFS` and
`Peak_dBFS` are measured **in file**; `Gain` is the multiplier that lands the file at −29 LUFS at play.

#### The bed is the zone's, and only a zone change moves it [R D 2026-09-24]

> *"Every non-battle screen: those should keep playing the bgm from whichever zone the player is in,
> and not change the BGM. Only going to a different zone changes it. It shouldn't restart between
> floors nor at the beginning of battle either."*

So there is **no hub bed, no boss bed and no title bed** — the three that were ingested on
2026-09-24 are removed, with their files, and the ten zone beds are the whole table. A screen is not
a bed: the hub, the shop, the codex, the inventory and the battle all keep whatever the player's
current zone is playing. Entering a floor does not restart it; entering a battle does not restart
it; only crossing into a different zone crossfades, 1200 ms in and 900 ms out.

That also means `bgm.csv` has no `State` value but `zone` and no blank `Zone` cell, and `audio.html`
resolves a floor to a bed by the fold below with nothing allowed to override it.

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

Nothing overrides it. A boss floor plays its own zone's bed like every other floor.

## The player contract — `AFX_BANK`

Implemented **once**, in the client (`play/app.js`, `const AFX_BANK=(()=>{ ... })();`), and lifted
into `assets/vfx/afx_bank.js` as `window.DFMC_AFX_BANK` by `tools/gen_vfx_fx.py` — the same
arrangement as `VFX_BANK`, for the same reason: when the game and the review page had two
implementations, approving an effect on the review page approved something players never got.

Self-contained IIFE, no React, no game state. Web Audio, one `AudioContext`, buses
`master -> music` and `master -> sfx`, decoded buffers cached by file path, decoded on first use or
by `warm()`, never more than one decode in flight per path.

```
AFX_BANK.parse(text[, bank])      -> {layers:[{id,g,p,d,n,i,j}], errs:[...]}   same verdicts as afx_lint.py
AFX_BANK.layerMs(layer[, bank])   -> one layer's end, in ms
AFX_BANK.lengthMs(parsed|text[, bank]) -> the composition's end, in ms
AFX_BANK.zoneFor(floor)           -> 1..10, by the Void Apex fold below
AFX_BANK.trackForZone(zoneName)   -> the bgm.csv Track_ID whose `Zone` cell is that name, or null
AFX_BANK.load(rows, base, kind)   -> register ONE table. `kind` is 'bank' | 'events' | 'bgm', inferred
                                     from the first row when omitted; `base` prefixes `File`.
AFX_BANK.play(parsed|text, opts)  -> handle {stop()}   opts: {speed = duration multiplier (default 1), gain, bank}
                                     every layer's HIT lands at d (+k*i) x speed: the file starts early by Onset_Ms / 2^(p/12)
AFX_BANK.warm(ids|paths)          -> decodes started. Decode a BOUNDED list ahead of its first play (the client: both
                                     kits, the ultimates and the battle cues at the battle's start). Never the bank.
AFX_BANK.isWarm(id|path)          -> true once that clip's buffer is cached
AFX_BANK.cue(id, opts)            -> play an afx_events.csv event by Event_ID, honouring Retrigger_Ms
AFX_BANK.music(trackId|null,opts) -> crossfade to a bgm.csv track (in 1200 ms, out 900 ms, looped,
                                     Gain applied). null stops. The same id is a no-op.
AFX_BANK.setMix({master,music,sfx}) / getMix()   0..100 each. music / sfx: (pct/100)^1.6 (loudness-linear);
                                     master: 0 = mute, else dB-linear -24..0 dB with a linear roll-off under 10%
AFX_BANK.normOf(lufs, peak)        -> the row trim rule 3 describes (null without a LUFS); NORM = {lufs:-18, peak:-1, masterDb:24}
AFX_BANK.unlock()                 -> resume the context on the first gesture (click/keydown/touchstart, once)
AFX_BANK.mute(bool) / isMuted() / isUnlocked() / playing()
AFX_BANK.bank() / events() / tracks()   -> the three registries. FUNCTIONS, not properties.
```

`speed` scales every `d` and every `i` — the client's fast-forward — and **never** the pitch, and
never the onset pre-roll either: the clip's attack is clip time. A missing file logs once to the
console, plays nothing, and never throws. **The first play of a clip is late unless it was warmed**:
`voice()` schedules against the clock before the decode resolves, so a cold clip starts when its
decode lands. The client warms a fight's clips at its start (`afxWarmBattle`, 2026-09-25); a page
that plays a composition on a click should `warm()` it on hover or on load.

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
| `dfmc-client/tools/afx_measure.py` | every clip, through the client's decoder: writes `LUFS`, `Play_Peak_dBFS`, `Onset_Ms` |
| `dfmc-client/tools/afx_sync_audit.py` | `Onset_Ms` + the `AFX_S*` / `FX_S*` columns: where each hit lands against its picture beat; writes `codex/afx_sync_audit.csv` |

## Changelog

- **2026-09-25 (c)** — **the hit lands on the frame: `d` is the hit, and the first cast is no longer
  cold** (#994, D: *"a lot of the sounds are out of sync with their vfx — this you should be able to fix
  easily ... You need to be able to see what the sounds actually are ... sound is data."*). Two
  mechanisms, both measured, both in the player. **(1)** The lint pins a composition's main beat to the
  picture by its `d`, and the player started the *file* at `d` — but the hit a listener hears is the
  clip's own attack. `dfmc-client/tools/afx_measure.py` now writes `Onset_Ms` (the first sample at
  −12 dB re the clip's peak, from the same headless-Chromium decode as `LUFS`): of the 208 clips a move
  plays, 72 carry an onset past one frame (41.7 ms) and 29 past 100 ms, so **487 of the 1221 authored
  compositions landed their main beat more than a frame after the picture's contact** — worst 255 ms
  (AFX-018 Creak 1 at `d0`), on every cast, invisible to a lint that reads `d` alone.
  `dfmc-client/tools/afx_sync_audit.py` is the audit and `codex/afx_sync_audit.csv` its table (every
  layer: authored `d`, onset, the picture beat it is authored on, where the hit landed, the delta before
  and after). `AFX_BANK.voice()` now pre-rolls the file by `Onset_Ms / 2^(p/12)` so the crossing lands
  at `d`; with no time to pre-roll it starts now at an offset into the lead-in, at most the onset, under
  a 5 ms fade — 337 compositions carry a `d0` layer with lead-in and take that branch. After: **0 of
  1221** main beats off by more than a frame, measured on the lifted engine over real Web Audio
  (`dfmc-client/tools/probe_00994.py`). Not one `AFX_S*` cell was re-authored: the cells were right, the
  engine read them wrong. The 330 *secondary* loud layers that sit more than a frame from any picture
  beat by authored `d` are authored tails and wind-ups, not a sync defect this data can prove — they
  belong to the "more in character" pass, which is D's question. **(2)** The first play of every clip
  in a session was late by its download + decode (`voice()` schedules before the decode resolves) —
  most casts, for a player fighting a new party each floor. `AFX_BANK.warm(ids)` decodes a bounded
  list; the client's `afxWarmBattle` (the twin of the picture's `preloadBank`, at every battle entry:
  PvE, boss, Auto PvP, competitive) warms both kits' compositions at their stage, the ultimates and the
  battle cues — 38 files in the probe's fight, never the bank. Measured on the live client through an
  80 ms route delay: the first cast fetched and landed 80+ ms late before, fetches nothing and lands at
  0.0 ms after. `assets/vfx/afx_bank.js` re-lifted. Client gate `tools/probe_00994.py`;
  `tools/probe_00983.mjs` (a) re-aimed from the file start to the hit (6/6 red on the old engine).
- **2026-09-25 (b)** — **one ceiling for every clip, and the master is a trim** (#993 first paragraph,
  D: *"Some sounds are way louder than the rest. They should all share a max loudness."*; #995, D:
  *"60% is loud and 30% is impossible to hear, seems muted. Go research how other games implement
  these sliders."*). One mechanism. `dfmc-client/tools/afx_measure.py` decoded all 852 bank clips and
  the 33 cues through the client's own decoder: at `g1` the 208 clips a move can play spanned
  **30.9 LU** (−38.5..−7.7 LUFS integrated) and the cues 26.9 LU, with peaks to +3.7 dBFS — so "60%"
  was an impact clip at −8 LUFS and "30%" was a creature clip at −35 LUFS under a `g0.4`; the slider
  was reporting the clips. The bank and the cues now carry `LUFS` and `Play_Peak_dBFS`, and the player
  trims every row to **−18 LUFS, never above −1 dBFS** (rule 3): the shipped bank at `g1` is
  −26.3..−18.0 LUFS (8.3 LU, the peak cap holding 103 short transients under the ceiling), the cues
  −22.6..−18.0 (4.6 LU); authored `g` / `Gain` cells are untouched and now read as offsets under the
  ceiling. The slider law: music / sfx keep `(pct/100)^1.6`, which is Stevens' power law — slider % is
  % of full loudness, 50% is −9.6 dB, 30% −16.7, 10% −32, and the curve the square / cube / dB-linear
  sliders of other titles approximate — but the master no longer sits on the same curve under them
  (master 10 × sfx 30 compounded to −48.7 dB): it is a bounded trim, 0 = mute, dB-linear −24..0 dB
  with a linear roll-off under 10 % (dr-lex, *Programming Volume Controls*), so master 10/30/60/80/100
  is −21.6/−16.8/−9.6/−4.8/0 dB (was −32/−16.7/−7.1/−3.1/0) and sfx 30 under any master ≥ 10 never
  lands below −38.3 dB. Neither re-encodes a file. A bus limiter for stacked layers was NOT added:
  Chromium's `DynamicsCompressorNode` carries a fixed look-ahead and #994 owns timing. The rest of
  #993 — a soft victory cue, the explosion set, per-creature cries — is asset work and waits on D.
  Client gate `tools/probe_00995.py` 14/14 (red 4/14); `tools/probe_afxbank.mjs` master pin re-aimed.
- **2026-09-25** — **Cataclysm's explosion is the beat, not a tail** (#983, D: *"low quality and out of
  sync. It plays after its effect"*). `ULT-MAGE-3 AFX_S1` opened on a punch (AFX-142) at d200 and did not
  reach an explosion clip until AFX-495 at d900 — 700 ms after the shard burst the lint pins to and 520 ms
  after the Pale Detonation at d380 — with every blast layer under g0.5, so the boom the player heard was
  a quiet tail behind a picture that had already finished. `tools/probe_00983.mjs` (client) proves the
  engine schedules each voice at exactly its authored `d` on the shipped `AFX_BANK`; the lateness was the
  authored offsets. The three MAGE stages are now one ladder on one clip: AFX-495 Explosion Crunch 000
  (peak at 1 ms, 84% of its energy under 200 Hz — measured by decoding the ogg in headless Chromium, the
  bank's own numbers do not carry an attack time) IS the d200 beat at g0.75/0.8/0.85 and p−2/−3/−4, with
  AFX-121 Impact Mining 004 (73 Hz) as the sub under it, the low-frequency body AFX-526 authored 80–90 ms
  ahead of the Pale Detonation because its onset lags that much, and the later crunch / thud on the Ember
  Blast and the ground plume. MAGE-1/2 were re-authored on the same shape so they escalate into it and do
  not fall behind their own pictures. Client, `vfx.html` and the shipped clips are untouched — every clip
  already ships under `play/assets/afx`.
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
