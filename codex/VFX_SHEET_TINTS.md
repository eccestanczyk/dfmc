# The sheet tints — the token that actually lands, per sheet × element

*Measured 2026-09-17 by `tools/vfx_calibrate.py`. Do not hand-edit — re-run the tool.*

D ruled the near-white sheets are kept and re-hued dark per element. The `k` token makes
that possible, but **the hue that lands is not the hue authored** — every sheet is its own mix
of white core and coloured halo, so do not write `h134` and hope for green. **Copy the token from
the row below**, verbatim, into every layer that uses that sheet at that element.

> **The table covers the WHOLE BANK since 2026-09-17, and not the 12 sheets of the white list.**
> Two findings forced that and they are the same finding. **The white list was measured on
> SHEET pixels and it does not predict the screen.** These sheets are additive-style art: the
> RGB is near-white almost everywhere and the *intensity* lives in the alpha channel, so
> "every opaque pixel is near-white" says nothing about what a player sees. Re-measured on
> composited screen pixels (`--screen-census`), FX-038 Strike Flash falls from 76% near-white
> to **0%** and FX-034 Sanctified Circle from 96% to **0%**, while FX-041 Crescent Slash, which
> was never on the list, measures **17% near-white and 14% flat white** — above four sheets that
> were. **And what those sheets actually do on screen is not go white: they go BRIGHT IN THEIR
> OWN HUE.** FX-038 reads cyan at 84% luminance, FX-039 Shard Burst cyan at 77%. A bare
> `Colored=yes` layer paints the sheet's hue, not the move's, so a purple move carrying a bare
> FX-039 renders cyan-white spikes. **Every one of the bank's 34 `Colored=yes` sheets has at
> least one element the ±90° hue clamp refuses — 121 refused pairs in all** — and on those the
> `h<element>` an author would reach for is rejected outright. `k` is the only mechanism that
> reaches them, and `k` needs a measured token. So the table is the whole bank: 48 sheets, not 12.

> **Re-solved 2026-09-17, after the filter order was fixed.** The first solve of this table put *none*
> of the 84 pairs over the saturation leg. That was this tool finding an engine defect rather than a
> limit of the art: `sheetFilter` emitted `brightness` **last**, a browser clamps to 8 bits between
> filter primitives, and `sepia(1)` on a white pixel returns rgb(255,255,239) — two channels already
> pinned — so every pass after it worked on a pixel whose chroma was gone. `brightness` is now emitted
> **first** on the neutral/sepia path, which moves the pixel off the ceiling before `sepia` runs. The
> tokens below are all re-measured against that chain; any older copy of this page is void.

> **Re-solved again 2026-09-17, after the `br` floor came down 0.5 → 0.3.** The reorder bought the
> saturation leg and lost the luminance one: that solve hit the full target on 32 of 84 pairs and
> all 52 misses were `lum ≤ 55%`, every one of them sitting on the old floor with nowhere left to
> go. The floor is one number in two places - `RANGE` in `tools/fx_lint.py` and in the client's
> `VFX_BANK` parser - and lowering it closed all 52. **161 of the 336 tokens below now carry a `br`
> under 0.5**, so this page is void against any client older than that change: an older parser
> rejects those rows outright rather than rendering them wrong.

> **`bone` re-solved 2026-09-17, and only `bone`: the saturation leg was a floor with no
> ceiling, and the solver duly spent everything it had on chroma.** That is right for an
> element that IS a colour and wrong for one that is not. `bone` had come out a vivid gold -
> 79-87% saturation on 11 of the 12 sheets, the loudest tile on its own contact sheet, and
> louder in chroma than the untinted white it was replacing. Three things make that wrong and
> they compound: `bone` is the **default** element and carries **217 of the 419 moves**, so a
> vivid gold there is a uniform gold wash over half the game; its own hex `#d8cfc0` is a light
> **neutral**; and `vxHitBone` measures **3.8%** saturation over real creature art, so the layer
> would have flashed gold while the sprite tinted near-grey. Layer and flash agreeing is the
> whole reason the element hue table and `VXHITH` share their numbers. The target now carries a
> per-element **band** (`SAT_BAND` in the tool, a table and not a branch, because a later
> element may want one): `bone` is solved to **0% ≤ sat ≤ 18%** with `lum ≤ 55%` unchanged.
> **The other six elements were not re-solved and their tokens below are the published ones,
> carried verbatim** - re-shot for the contact sheets, never re-measured.

> **One token, and no caster-scale variant — measured, 2026-09-17.** A token is solved on a TARGET
> tile at `s1.4` and a kept caster beat plays at `s0.55-0.75`, so it was put to this tool whether
> a row that holds on the enemy holds on the caster. It does. `--caster-check` re-measures a
> published token on the caster tile at s0.55 and s0.75 and on the target tile at s1.4: over 14
> sheet × element pairs × 3 scales, **hue, saturation, lightness and flat-white agree to within one
> point** — usually to the decimal. Scaling an `<img>` does not change the distribution of its
> pixel values, so a statistic taken over the layer is scale-free. **Nothing here needs a second
> column.** What DOES change with scale is what a viewer reads: at `s1.4` the rays carry the tint
> and the eye follows them; at `s0.75` the core is most of what is left, and on a banded element
> the core is by ruling near-neutral, so it reads pale. That is a consequence of the `bone` band,
> not of the scale, and it is the same at every scale — see the note below.

> **The one thing still open, and it is D's to rule: how bright `bone` may be.** Inside a
> saturation band, `br` is the ONLY lever. `saturate()` scales chroma about a pixel's own luma,
> so it cannot colour a core the band forbids from carrying chroma; `br` is the first primitive
> on the `k` path and is the only one that moves the pixel before `sepia(1)` fixes it. Shot on
> `FX-038` + `bone` on the caster tile, brightest 200 painted pixels: the published
> `k h40 br0.45 sat0.35` puts the core at **lum 49%, max value 0.57** — a pale cream star, no
> flat white by the measured definition and inside every leg of the target, but the brightest
> near-neutral thing on a near-black stage. `br0.35` takes the core to **lum 38%, max 0.44** and
> `br0.3` to **lum 33%, max 0.38**. Every one of those passes today's target, so the solver had
> no reason to go below 0.45 — its `lum ≤ 55%` leg is read on the top DECILE of the painted
> pixels, which the rays dominate, and a few hundred blown core pixels round to nothing there.
> **No threshold was invented to close this**: there is no measurement in evidence that says
> where a neutral stops being quiet and starts being white, and picking one would be taste
> shipped as a number. The candidate is one edit — `bone` at `br0.35` instead of `br0.45` — and
> the contact sheets to rule on it are beside this page.

## How to read a row

`FX-038` + `green` → write `k h120 br0.65 sat1.5`, i.e. the whole layer is
`FX-038@t s1.0 k h120 br0.65 sat1.5 d120`. The measured columns are what that token puts on the screen.

## The measurement, so a row can be audited without re-running it

- Carrier move **`M-THORNBACK-1`** (`Targets` = enemy, so the layer lands on the enemy lead), stage **S3**,
  seed **1234**, one layer at **s1.4**, no delay, no flags — the same move, seed, tile and scale for
  every sheet, so the sheets are comparable to each other.
- Scrubbed **inside the layer's own `lenMs`** (fractions 0.3 / 0.5 / 0.7, brightest kept — the `ms`
  column is the frame the row was read at).
- The pixels measured are the **difference against a clean plate of the same tile**, same paused
  frame, **restricted to where the plate is dark** (max channel ≤ 0.16). That is the layer over the
  floor and not over the creature: a decile taken over the whole footprint picks the brightest
  pixels in it, and once the layer is darkened those are exactly the ones the sprite shines
  through. The mask is frozen per sheet, so two tokens are compared on the same pixels.
- Reported on the **top luminance decile** of that mask: `hue` a chroma-weighted circular mean,
  `sat` and `lum` HSL, `flat` the share at HSV value ≥ 250 and HSV saturation ≤ 0.08.
- **Target:** hue within ±18° · lum ≤ 55% · flat = 0% · sat ≥ 25%,
  **except where the element carries a band** — `bone` 0–18%. A banded element is solved to sit *inside*
  its band, just under the ceiling rather than at zero, because hue is a chroma-weighted mean and a
  layer with no chroma has no measurable hue to put on the element.
- The chain a `k` layer renders through is `brightness(br) sepia(1) saturate(2.4) hue-rotate(h−40)
  saturate(sat)`. `br` is the **first** primitive, so every candidate value of it costs a screenshot
  here; `sat` is the last, so that axis is ranked on pixels already shot and only the winner is re-shot.
- Element hues (client `VFXHEX`, and the same numbers as `VXHITH`): red 0°, rust 19°, bone 38°, green 134°, blue 222°, purple 272°, crimson 357°.

## The table

### FX-051 — Mending Ring

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.3 sat1.5` | 1° (want 0) | 43% | 48% | 0.0% | 542 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 65% | 52% | 0.0% | 542 |
| bone | `k h40 br0.35 sat0.35` | 39° (want 38) | 15% | 41% | 0.0% | 542 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 69% | 51% | 0.0% | 542 |
| blue | `k h229 br0.3 sat1.5` | 227° (want 222) | 44% | 48% | 0.0% | 542 |
| purple | `k h259 br0.35 sat0.95` | 261° (want 272) | 30% | 53% | 0.0% | 542 |
| crimson | `k h349 br0.3 sat1.5` | 358° (want 357) | 43% | 48% | 0.0% | 542 |

### FX-034 — Sanctified Circle

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h0 br0.45 sat1.5` | 2° (want 0) | 40% | 27% | 0.0% | 500 |
| rust | `k h15 br0.5 sat1.5` | 16° (want 19) | 49% | 26% | 0.0% | 500 |
| bone | `k h45 br0.6 sat0.45` | 34° (want 38) | 14% | 27% | 0.0% | 500 |
| green | `k h117 br0.65 sat1.5` | 132° (want 134) | 56% | 24% | 0.0% | 500 |
| blue | `k h225 br0.45 sat1.5` | 226° (want 222) | 44% | 28% | 0.0% | 500 |
| purple | `k h264 br0.5 sat1.5` | 270° (want 272) | 34% | 30% | 0.0% | 500 |
| crimson | `k h356 br0.45 sat1.5` | 358° (want 357) | 39% | 28% | 0.0% | 500 |

### FX-038 — Strike Flash

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.35 sat1.5` | 0° (want 0) | 44% | 49% | 0.0% | 88 |
| rust | `k h15 br0.45 sat1.5` | 20° (want 19) | 65% | 51% | 0.0% | 88 |
| bone | `k h40 br0.45 sat0.35` | 38° (want 38) | 15% | 45% | 0.0% | 88 |
| green | `k h120 br0.65 sat1.5` | 132° (want 134) | 76% | 53% | 0.0% | 88 |
| blue | `k h225 br0.4 sat1.4` | 223° (want 222) | 51% | 53% | 0.0% | 88 |
| purple | `k h264 br0.35 sat1.5` | 266° (want 272) | 41% | 50% | 0.0% | 88 |
| crimson | `k h349 br0.35 sat1.5` | 358° (want 357) | 45% | 49% | 0.0% | 88 |

### FX-032 — Thunder Ring

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.35 sat1.45` | 1° (want 0) | 48% | 53% | 0.0% | 300 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 62% | 50% | 0.0% | 300 |
| bone | `k h40 br0.4 sat0.35` | 38° (want 38) | 15% | 44% | 0.0% | 300 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 67% | 49% | 0.0% | 300 |
| blue | `k h225 br0.35 sat1.5` | 223° (want 222) | 50% | 51% | 0.0% | 300 |
| purple | `k h261 br0.3 sat1.5` | 263° (want 272) | 38% | 48% | 0.0% | 300 |
| crimson | `k h349 br0.35 sat1.4` | 358° (want 357) | 46% | 53% | 0.0% | 300 |

### FX-045 — Impact Star

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h351 br0.3 sat1.5` | 360° (want 0) | 43% | 48% | 0.0% | 300 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 65% | 52% | 0.0% | 300 |
| bone | `k h40 br0.4 sat0.35` | 38° (want 38) | 15% | 46% | 0.0% | 300 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 69% | 51% | 0.0% | 300 |
| blue | `k h229 br0.3 sat1.5` | 226° (want 222) | 44% | 47% | 0.0% | 300 |
| purple | `k h260 br0.3 sat1.5` | 262° (want 272) | 38% | 50% | 0.0% | 300 |
| crimson | `k h349 br0.3 sat1.5` | 358° (want 357) | 43% | 48% | 0.0% | 300 |

### FX-044 — Claw Rake

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.35 sat1.4` | 1° (want 0) | 46% | 53% | 0.0% | 542 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 62% | 50% | 0.0% | 542 |
| bone | `k h40 br0.4 sat0.35` | 38° (want 38) | 15% | 44% | 0.0% | 542 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 67% | 49% | 0.0% | 542 |
| blue | `k h225 br0.35 sat1.5` | 223° (want 222) | 51% | 52% | 0.0% | 542 |
| purple | `k h261 br0.3 sat1.5` | 263° (want 272) | 38% | 48% | 0.0% | 542 |
| crimson | `k h349 br0.35 sat1.35` | 358° (want 357) | 45% | 53% | 0.0% | 542 |

### FX-043 — Spin Slash

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.3 sat1.5` | 1° (want 0) | 43% | 48% | 0.0% | 758 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 65% | 52% | 0.0% | 758 |
| bone | `k h40 br0.35 sat0.35` | 37° (want 38) | 15% | 41% | 0.0% | 758 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 69% | 51% | 0.0% | 758 |
| blue | `k h229 br0.3 sat1.5` | 226° (want 222) | 44% | 48% | 0.0% | 758 |
| purple | `k h259 br0.3 sat1.5` | 260° (want 272) | 38% | 50% | 0.0% | 758 |
| crimson | `k h349 br0.3 sat1.5` | 358° (want 357) | 43% | 48% | 0.0% | 758 |

### FX-029 — Rime Bloom

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.35 sat1.4` | 1° (want 0) | 46% | 53% | 0.0% | 300 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 61% | 50% | 0.0% | 300 |
| bone | `k h40 br0.3 sat0.35` | 39° (want 38) | 15% | 33% | 0.0% | 300 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 67% | 49% | 0.0% | 300 |
| blue | `k h225 br0.35 sat1.5` | 223° (want 222) | 50% | 51% | 0.0% | 300 |
| purple | `k h263 br0.3 sat1.5` | 265° (want 272) | 39% | 47% | 0.0% | 300 |
| crimson | `k h349 br0.35 sat1.4` | 358° (want 357) | 46% | 53% | 0.0% | 300 |

### FX-042 — Wide Slash

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.3 sat1.5` | 1° (want 0) | 43% | 48% | 0.0% | 542 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 64% | 52% | 0.0% | 542 |
| bone | `k h40 br0.3 sat0.35` | 38° (want 38) | 15% | 34% | 0.0% | 542 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 69% | 51% | 0.0% | 542 |
| blue | `k h229 br0.3 sat1.5` | 226° (want 222) | 44% | 47% | 0.0% | 542 |
| purple | `k h260 br0.3 sat1.5` | 262° (want 272) | 38% | 49% | 0.0% | 542 |
| crimson | `k h349 br0.3 sat1.5` | 358° (want 357) | 43% | 48% | 0.0% | 542 |

### FX-036 — Cyclone Ring

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.4 sat1.5` | 0° (want 0) | 45% | 51% | 0.0% | 500 |
| rust | `k h15 br0.5 sat1.5` | 19° (want 19) | 65% | 52% | 0.0% | 500 |
| bone | `k h41 br0.55 sat0.35` | 38° (want 38) | 15% | 51% | 0.0% | 500 |
| green | `k h120 br0.75 sat1.5` | 139° (want 134) | 72% | 52% | 0.0% | 500 |
| blue | `k h225 br0.4 sat1.5` | 223° (want 222) | 48% | 49% | 0.0% | 500 |
| purple | `k h266 br0.4 sat1.5` | 268° (want 272) | 43% | 52% | 0.0% | 500 |
| crimson | `k h349 br0.4 sat1.5` | 357° (want 357) | 46% | 51% | 0.0% | 500 |

### FX-050 — Void Bloom

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.35 sat1.5` | 0° (want 0) | 44% | 48% | 0.0% | 325 |
| rust | `k h15 br0.45 sat1.5` | 19° (want 19) | 64% | 50% | 0.0% | 325 |
| bone | `k h40 br0.45 sat0.35` | 38° (want 38) | 15% | 45% | 0.0% | 325 |
| green | `k h120 br0.65 sat1.5` | 132° (want 134) | 74% | 52% | 0.0% | 325 |
| blue | `k h225 br0.4 sat1.5` | 223° (want 222) | 54% | 53% | 0.0% | 325 |
| purple | `k h266 br0.35 sat1.5` | 268° (want 272) | 41% | 49% | 0.0% | 325 |
| crimson | `k h349 br0.35 sat1.5` | 358° (want 357) | 44% | 48% | 0.0% | 325 |

### FX-008 — Pyre Orb I

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.3 sat1.5` | 1° (want 0) | 43% | 48% | 0.0% | 700 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 65% | 52% | 0.0% | 700 |
| bone | `k h40 br0.35 sat0.35` | 38° (want 38) | 15% | 41% | 0.0% | 700 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 69% | 51% | 0.0% | 700 |
| blue | `k h229 br0.3 sat1.5` | 227° (want 222) | 44% | 48% | 0.0% | 700 |
| purple | `k h259 br0.35 sat0.95` | 261° (want 272) | 30% | 53% | 0.0% | 700 |
| crimson | `k h349 br0.3 sat1.5` | 358° (want 357) | 43% | 48% | 0.0% | 700 |

### FX-001 — Cinder Burst

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h351 br0.4 sat1.5` | 360° (want 0) | 49% | 53% | 0.0% | 300 |
| rust | `k h15 br0.5 sat1.4` | 20° (want 19) | 66% | 53% | 0.0% | 300 |
| bone | `k h40 br0.4 sat0.35` | 39° (want 38) | 15% | 38% | 0.0% | 300 |
| green | `k h120 br0.65 sat1.5` | 132° (want 134) | 71% | 50% | 0.0% | 300 |
| blue | `k h225 br0.4 sat1.5` | 223° (want 222) | 51% | 50% | 0.0% | 300 |
| purple | `k h270 br0.4 sat1.5` | 273° (want 272) | 45% | 53% | 0.0% | 300 |
| crimson | `k h345 br0.4 sat1.5` | 354° (want 357) | 51% | 53% | 0.0% | 300 |

### FX-002 — Ash Detonation

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h351 br0.6 sat1.5` | 360° (want 0) | 55% | 51% | 0.0% | 300 |
| rust | `k h15 br0.75 sat1.5` | 21° (want 19) | 73% | 51% | 0.0% | 300 |
| bone | `k h40 br0.35 sat0.35` | 38° (want 38) | 15% | 22% | 0.0% | 300 |
| green | `k h120 sat1.5` | 135° (want 134) | 76% | 49% | 0.0% | 300 |
| blue | `k h225 br0.65 sat1.5` | 222° (want 222) | 61% | 53% | 0.0% | 300 |
| purple | `k h270 br0.6 sat1.5` | 274° (want 272) | 51% | 51% | 0.0% | 300 |
| crimson | `k h345 br0.6 sat1.5` | 354° (want 357) | 56% | 51% | 0.0% | 300 |

### FX-003 — Pale Detonation

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.6 sat1.4` | 1° (want 0) | 46% | 53% | 0.0% | 700 |
| rust | `k h15 br0.7 sat1.5` | 20° (want 19) | 63% | 51% | 0.0% | 700 |
| bone | `k h40 br0.65 sat0.35` | 38° (want 38) | 15% | 42% | 0.0% | 700 |
| green | `k h120 sat1.5` | 132° (want 134) | 72% | 52% | 0.0% | 700 |
| blue | `k h225 br0.6 sat1.5` | 223° (want 222) | 50% | 52% | 0.0% | 700 |
| purple | `k h270 br0.6 sat1.35` | 273° (want 272) | 40% | 53% | 0.0% | 700 |
| crimson | `k h345 br0.6 sat1.35` | 354° (want 357) | 45% | 53% | 0.0% | 700 |

### FX-004 — Pale Plume

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.6 sat1.45` | 1° (want 0) | 47% | 53% | 0.0% | 700 |
| rust | `k h15 br0.7 sat1.5` | 20° (want 19) | 63% | 51% | 0.0% | 700 |
| bone | `k h40 br0.65 sat0.35` | 38° (want 38) | 15% | 42% | 0.0% | 700 |
| green | `k h120 sat1.5` | 132° (want 134) | 71% | 52% | 0.0% | 700 |
| blue | `k h225 br0.6 sat1.5` | 223° (want 222) | 50% | 51% | 0.0% | 700 |
| purple | `k h270 br0.6 sat1.4` | 273° (want 272) | 42% | 53% | 0.0% | 700 |
| crimson | `k h345 br0.6 sat1.4` | 354° (want 357) | 47% | 53% | 0.0% | 700 |

### FX-005 — Ash Plume

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h353 sat1.5` | 1° (want 0) | 44% | 46% | 0.0% | 700 |
| rust | `k h15 sat1.5` | 19° (want 19) | 59% | 38% | 0.0% | 700 |
| bone | `k h45 br0.5 sat0.4` | 38° (want 38) | 15% | 17% | 0.0% | 700 |
| green | `k h120 sat1.5` | 133° (want 134) | 65% | 27% | 0.0% | 700 |
| blue | `k h225 sat1.5` | 223° (want 222) | 47% | 44% | 0.0% | 700 |
| purple | `k h270 sat1.5` | 273° (want 272) | 40% | 46% | 0.0% | 700 |
| crimson | `k h349 sat1.5` | 357° (want 357) | 44% | 46% | 0.0% | 700 |

### FX-006 — Ember Blast

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h351 br0.5 sat1.5` | 360° (want 0) | 54% | 53% | 0.0% | 300 |
| rust | `k h15 br0.6 sat1.5` | 20° (want 19) | 71% | 51% | 0.0% | 300 |
| bone | `k h40 br0.65 sat0.3` | 39° (want 38) | 15% | 49% | 0.0% | 300 |
| green | `k h120 br0.85 sat1.5` | 134° (want 134) | 77% | 51% | 0.0% | 300 |
| blue | `k h225 br0.5 sat1.5` | 223° (want 222) | 56% | 50% | 0.0% | 300 |
| purple | `k h270 br0.5 sat1.5` | 273° (want 272) | 50% | 52% | 0.0% | 300 |
| crimson | `k h345 br0.5 sat1.5` | 354° (want 357) | 56% | 53% | 0.0% | 300 |

### FX-007 — Ember Blast, Greater

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h351 br0.35 sat1.5` | 360° (want 0) | 47% | 52% | 0.0% | 300 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 61% | 47% | 0.0% | 300 |
| bone | `k h40 br0.3 sat0.35` | 39° (want 38) | 15% | 32% | 0.0% | 300 |
| green | `k h120 br0.6 sat1.5` | 132° (want 134) | 72% | 51% | 0.0% | 300 |
| blue | `k h225 br0.35 sat1.5` | 223° (want 222) | 49% | 49% | 0.0% | 300 |
| purple | `k h266 br0.35 sat1.5` | 268° (want 272) | 44% | 52% | 0.0% | 300 |
| crimson | `k h345 br0.35 sat1.5` | 354° (want 357) | 48% | 52% | 0.0% | 300 |

### FX-009 — Pyre Orb II

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h351 br0.45 sat1.5` | 360° (want 0) | 46% | 50% | 0.0% | 300 |
| rust | `k h15 br0.55 sat1.5` | 20° (want 19) | 64% | 50% | 0.0% | 300 |
| bone | `k h40 br0.3 sat0.35` | 38° (want 38) | 15% | 24% | 0.0% | 300 |
| green | `k h120 br0.8 sat1.5` | 132° (want 134) | 73% | 52% | 0.0% | 300 |
| blue | `k h225 br0.5 sat1.45` | 223° (want 222) | 53% | 53% | 0.0% | 300 |
| purple | `k h270 br0.45 sat1.5` | 273° (want 272) | 42% | 50% | 0.0% | 300 |
| crimson | `k h345 br0.45 sat1.5` | 354° (want 357) | 47% | 50% | 0.0% | 300 |

### FX-010 — Pyre Orb III

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.35 sat1.5` | 1° (want 0) | 49% | 53% | 0.0% | 700 |
| rust | `k h15 br0.3 sat1.5` | 20° (want 19) | 61% | 37% | 0.0% | 700 |
| bone | `k h40 br0.3 sat0.35` | 39° (want 38) | 15% | 33% | 0.0% | 700 |
| green | `k h120 br0.6 sat1.5` | 132° (want 134) | 75% | 53% | 0.0% | 700 |
| blue | `k h225 br0.35 sat1.5` | 223° (want 222) | 49% | 51% | 0.0% | 700 |
| purple | `k h264 br0.3 sat1.5` | 266° (want 272) | 39% | 47% | 0.0% | 700 |
| crimson | `k h349 br0.35 sat1.45` | 358° (want 357) | 47% | 53% | 0.0% | 700 |

### FX-011 — Pyre Orb IV

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h353 br0.55 sat1.5` | 1° (want 0) | 46% | 50% | 0.0% | 700 |
| rust | `k h15 br0.7 sat1.5` | 19° (want 19) | 66% | 52% | 0.0% | 700 |
| bone | `k h41 br0.75 sat0.35` | 38° (want 38) | 15% | 50% | 0.0% | 700 |
| green | `k h120 sat1.5` | 136° (want 134) | 70% | 51% | 0.0% | 700 |
| blue | `k h225 br0.6 sat1.45` | 223° (want 222) | 51% | 53% | 0.0% | 700 |
| purple | `k h270 br0.55 sat1.5` | 273° (want 272) | 42% | 51% | 0.0% | 700 |
| crimson | `k h345 br0.55 sat1.5` | 353° (want 357) | 47% | 51% | 0.0% | 700 |

### FX-012 — Standing Flame

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.35 sat1.5` | 1° (want 0) | 45% | 50% | 0.0% | 300 |
| rust | `k h15 br0.45 sat1.5` | 19° (want 19) | 68% | 53% | 0.0% | 300 |
| bone | `k h41 br0.45 sat0.35` | 39° (want 38) | 15% | 47% | 0.0% | 300 |
| green | `k h120 br0.6 sat1.5` | 132° (want 134) | 70% | 50% | 0.0% | 300 |
| blue | `k h225 br0.35 sat1.5` | 223° (want 222) | 48% | 49% | 0.0% | 300 |
| purple | `k h264 br0.35 sat1.5` | 266° (want 272) | 43% | 52% | 0.0% | 300 |
| crimson | `k h349 br0.35 sat1.5` | 358° (want 357) | 46% | 51% | 0.0% | 300 |

### FX-013 — Slender Flame

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.35 sat1.5` | 1° (want 0) | 46% | 50% | 0.0% | 500 |
| rust | `k h15 br0.45 sat1.5` | 20° (want 19) | 69% | 53% | 0.0% | 500 |
| bone | `k h40 br0.45 sat0.35` | 38° (want 38) | 15% | 47% | 0.0% | 500 |
| green | `k h120 br0.6 sat1.5` | 132° (want 134) | 71% | 50% | 0.0% | 500 |
| blue | `k h225 br0.35 sat1.5` | 223° (want 222) | 48% | 48% | 0.0% | 500 |
| purple | `k h264 br0.35 sat1.5` | 266° (want 272) | 43% | 52% | 0.0% | 500 |
| crimson | `k h349 br0.35 sat1.5` | 358° (want 357) | 47% | 51% | 0.0% | 500 |

### FX-014 — Hollow Flame

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.55 sat1.4` | 0° (want 0) | 46% | 53% | 0.0% | 1400 |
| rust | `k h15 br0.65 sat1.5` | 19° (want 19) | 65% | 51% | 0.0% | 1400 |
| bone | `k h41 br0.7 sat0.35` | 39° (want 38) | 15% | 49% | 0.0% | 1400 |
| green | `k h120 br0.9 sat1.5` | 132° (want 134) | 71% | 51% | 0.0% | 1400 |
| blue | `k h225 br0.55 sat1.5` | 223° (want 222) | 51% | 51% | 0.0% | 1400 |
| purple | `k h270 br0.55 sat1.4` | 273° (want 272) | 42% | 53% | 0.0% | 1400 |
| crimson | `k h345 br0.55 sat1.4` | 354° (want 357) | 47% | 53% | 0.0% | 1400 |

### FX-018 — Candle Smoke

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h10 br0.55 sat1.5` | 5° (want 0) | 37% | 15% | 0.0% | 300 |
| rust | `k h30 br0.7 sat1.5` | 24° (want 19) | 48% | 15% | 0.0% | 300 |
| bone | `k h50 sat0.5` | 36° (want 38) | 13% | 20% | 0.0% | 300 |
| green | `k h108 br0.55 sat1.5` | 128° (want 134) | 38% | 10% | 0.0% | 300 |
| blue | `k h210 br0.65 sat1.5` | 216° (want 222) | 52% | 17% | 0.0% | 300 |
| purple | `k h270 br0.4 sat1.5` | 268° (want 272) | 39% | 13% | 0.0% | 300 |
| crimson | `k h6 br0.6 sat1.5` | 2° (want 357) | 37% | 16% | 0.0% | 300 |

### FX-019 — Rising Column

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h355 br0.7 sat1.5` | 2° (want 0) | 42% | 40% | 0.0% | 300 |
| rust | `k h15 br0.8 sat1.5` | 19° (want 19) | 56% | 38% | 0.0% | 300 |
| bone | `k h45 br0.9 sat0.4` | 39° (want 38) | 15% | 38% | 0.0% | 300 |
| green | `k h120 sat1.5` | 133° (want 134) | 63% | 34% | 0.0% | 300 |
| blue | `k h225 br0.7 sat1.5` | 224° (want 222) | 46% | 40% | 0.0% | 300 |
| purple | `k h270 br0.9 sat1.5` | 276° (want 272) | 39% | 50% | 0.0% | 300 |
| crimson | `k h352 br0.65 sat1.5` | 358° (want 357) | 41% | 38% | 0.0% | 300 |

### FX-020 — Wisp Smoke I

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h354 sat1.5` | 2° (want 0) | 46% | 51% | 0.0% | 300 |
| rust | `k h15 sat1.5` | 19° (want 19) | 58% | 42% | 0.0% | 300 |
| bone | `k h45 br0.65 sat0.4` | 40° (want 38) | 15% | 24% | 0.0% | 300 |
| green | `k h120 sat1.5` | 133° (want 134) | 65% | 30% | 0.0% | 300 |
| blue | `k h225 sat1.5` | 223° (want 222) | 49% | 49% | 0.0% | 300 |
| purple | `k h270 sat1.5` | 273° (want 272) | 43% | 52% | 0.0% | 300 |
| crimson | `k h351 sat1.5` | 359° (want 357) | 46% | 51% | 0.0% | 300 |

### FX-021 — Wisp Smoke II

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h355 br0.95 sat1.5` | 2° (want 0) | 43% | 45% | 0.0% | 700 |
| rust | `k h15 sat1.5` | 19° (want 19) | 57% | 40% | 0.0% | 700 |
| bone | `k h45 sat0.4` | 40° (want 38) | 15% | 35% | 0.0% | 700 |
| green | `k h120 sat1.5` | 133° (want 134) | 64% | 29% | 0.0% | 700 |
| blue | `k h225 br0.75 sat1.5` | 224° (want 222) | 46% | 36% | 0.0% | 700 |
| purple | `k h270 sat1.5` | 274° (want 272) | 39% | 48% | 0.0% | 700 |
| crimson | `k h352 br0.7 sat1.5` | 359° (want 357) | 42% | 34% | 0.0% | 700 |

### FX-022 — Wisp Smoke III

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h354 br0.9 sat1.5` | 2° (want 0) | 48% | 51% | 0.0% | 300 |
| rust | `k h15 sat1.5` | 19° (want 19) | 60% | 47% | 0.0% | 300 |
| bone | `k h45 br0.55 sat0.4` | 40° (want 38) | 15% | 23% | 0.0% | 300 |
| green | `k h120 sat1.5` | 133° (want 134) | 65% | 34% | 0.0% | 300 |
| blue | `k h225 br0.95 sat1.5` | 223° (want 222) | 52% | 52% | 0.0% | 300 |
| purple | `k h270 br0.9 sat1.5` | 273° (want 272) | 44% | 52% | 0.0% | 300 |
| crimson | `k h350 br0.9 sat1.5` | 358° (want 357) | 48% | 52% | 0.0% | 300 |

### FX-023 — Wisp Smoke IIIb

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h0 br0.75 sat1.5` | 4° (want 0) | 42% | 31% | 0.0% | 300 |
| rust | `k h21 br0.85 sat1.5` | 22° (want 19) | 56% | 29% | 0.0% | 300 |
| bone | `k h45 br0.7 sat0.45` | 33° (want 38) | 13% | 23% | 0.0% | 300 |
| green | `k h116 sat1.5` | 130° (want 134) | 57% | 26% | 0.0% | 300 |
| blue | `k h220 br0.75 sat1.5` | 221° (want 222) | 48% | 31% | 0.0% | 300 |
| purple | `k h270 br0.5 sat1.5` | 271° (want 272) | 39% | 23% | 0.0% | 300 |
| crimson | `k h0 br0.6 sat1.5` | 3° (want 357) | 41% | 26% | 0.0% | 300 |

### FX-028 — Frost Burst

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h354 br0.7 sat1.5` | 2° (want 0) | 53% | 51% | 0.0% | 500 |
| rust | `k h15 br0.75 sat1.5` | 22° (want 19) | 63% | 45% | 0.0% | 500 |
| bone | `k h45 br0.75 sat0.3` | 40° (want 38) | 15% | 44% | 0.0% | 500 |
| green | `k h120 br0.85 sat1.5` | 138° (want 134) | 69% | 38% | 0.0% | 500 |
| blue | `k h225 br0.7 sat1.5` | 220° (want 222) | 56% | 50% | 0.0% | 500 |
| purple | `k h270 br0.65 sat1.5` | 277° (want 272) | 50% | 50% | 0.0% | 500 |
| crimson | `k h351 br0.7 sat1.5` | 358° (want 357) | 53% | 52% | 0.0% | 500 |

### FX-030 — Shatterfrost

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.35 sat1.5` | 1° (want 0) | 44% | 50% | 0.0% | 500 |
| rust | `k h15 br0.45 sat1.5` | 20° (want 19) | 66% | 52% | 0.0% | 500 |
| bone | `k h40 br0.45 sat0.35` | 38° (want 38) | 15% | 46% | 0.0% | 500 |
| green | `k h120 br0.6 sat1.5` | 132° (want 134) | 68% | 50% | 0.0% | 500 |
| blue | `k h225 br0.35 sat1.5` | 223° (want 222) | 47% | 48% | 0.0% | 500 |
| purple | `k h266 br0.35 sat1.5` | 268° (want 272) | 41% | 51% | 0.0% | 500 |
| crimson | `k h345 br0.35 sat1.5` | 354° (want 357) | 45% | 50% | 0.0% | 500 |

### FX-031 — Arc Strike

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.6 sat1.5` | 0° (want 0) | 46% | 51% | 0.0% | 300 |
| rust | `k h15 br0.75 sat1.5` | 20° (want 19) | 64% | 51% | 0.0% | 300 |
| bone | `k h41 br0.8 sat0.35` | 39° (want 38) | 15% | 49% | 0.0% | 300 |
| green | `k h120 sat1.5` | 133° (want 134) | 67% | 49% | 0.0% | 300 |
| blue | `k h225 br0.65 sat1.5` | 223° (want 222) | 53% | 53% | 0.0% | 300 |
| purple | `k h270 br0.6 sat1.5` | 273° (want 272) | 42% | 51% | 0.0% | 300 |
| crimson | `k h345 br0.6 sat1.5` | 354° (want 357) | 47% | 51% | 0.0% | 300 |

### FX-033 — Storm Descent

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.45 sat1.5` | 0° (want 0) | 48% | 49% | 0.0% | 400 |
| rust | `k h15 br0.55 sat1.5` | 19° (want 19) | 66% | 49% | 0.0% | 400 |
| bone | `k h41 br0.55 sat0.35` | 39° (want 38) | 15% | 44% | 0.0% | 400 |
| green | `k h120 br0.85 sat1.5` | 136° (want 134) | 77% | 52% | 0.0% | 400 |
| blue | `k h225 br0.5 sat1.5` | 223° (want 222) | 57% | 53% | 0.0% | 400 |
| purple | `k h270 br0.45 sat1.5` | 273° (want 272) | 44% | 50% | 0.0% | 400 |
| crimson | `k h345 br0.45 sat1.5` | 354° (want 357) | 49% | 50% | 0.0% | 400 |

### FX-035 — Gale Vortex

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.4 sat1.5` | 0° (want 0) | 45% | 49% | 0.0% | 500 |
| rust | `k h15 br0.5 sat1.5` | 19° (want 19) | 63% | 49% | 0.0% | 500 |
| bone | `k h41 br0.55 sat0.35` | 39° (want 38) | 15% | 48% | 0.0% | 500 |
| green | `k h120 br0.75 sat1.5` | 134° (want 134) | 74% | 52% | 0.0% | 500 |
| blue | `k h225 br0.45 sat1.5` | 223° (want 222) | 54% | 53% | 0.0% | 500 |
| purple | `k h270 br0.4 sat1.5` | 273° (want 272) | 41% | 49% | 0.0% | 500 |
| crimson | `k h345 br0.4 sat1.5` | 354° (want 357) | 46% | 49% | 0.0% | 500 |

### FX-037 — Tempest Coil

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h354 br0.5 sat1.5` | 0° (want 0) | 47% | 44% | 0.0% | 700 |
| rust | `k h15 br0.55 sat1.5` | 19° (want 19) | 58% | 40% | 0.0% | 700 |
| bone | `k h45 br0.7 sat0.35` | 39° (want 38) | 15% | 45% | 0.0% | 700 |
| green | `k h120 br0.75 sat1.5` | 136° (want 134) | 65% | 38% | 0.0% | 700 |
| blue | `k h225 br0.5 sat1.5` | 224° (want 222) | 51% | 43% | 0.0% | 700 |
| purple | `k h270 br0.5 sat1.5` | 273° (want 272) | 45% | 45% | 0.0% | 700 |
| crimson | `k h351 br0.5 sat1.5` | 357° (want 357) | 47% | 44% | 0.0% | 700 |

### FX-039 — Shard Burst

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h351 br0.3 sat1.5` | 360° (want 0) | 43% | 41% | 0.0% | 137 |
| rust | `k h15 br0.45 sat1.5` | 20° (want 19) | 61% | 50% | 0.0% | 137 |
| bone | `k h40 br0.35 sat0.35` | 39° (want 38) | 15% | 35% | 0.0% | 137 |
| green | `k h120 br0.65 sat1.5` | 132° (want 134) | 71% | 52% | 0.0% | 137 |
| blue | `k h225 br0.4 sat1.5` | 223° (want 222) | 52% | 53% | 0.0% | 137 |
| purple | `k h270 br0.3 sat1.5` | 273° (want 272) | 39% | 41% | 0.0% | 137 |
| crimson | `k h345 br0.3 sat1.5` | 354° (want 357) | 44% | 41% | 0.0% | 137 |

### FX-040 — Ember Sphere

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.3 sat1.5` | 1° (want 0) | 43% | 48% | 0.0% | 700 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 64% | 51% | 0.0% | 700 |
| bone | `k h40 br0.4 sat0.35` | 39° (want 38) | 15% | 46% | 0.0% | 700 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 69% | 51% | 0.0% | 700 |
| blue | `k h228 br0.35 sat1.3` | 225° (want 222) | 45% | 53% | 0.0% | 700 |
| purple | `k h260 br0.3 sat1.5` | 262° (want 272) | 38% | 49% | 0.0% | 700 |
| crimson | `k h349 br0.3 sat1.5` | 358° (want 357) | 43% | 48% | 0.0% | 700 |

### FX-041 — Crescent Slash

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.3 sat1.5` | 1° (want 0) | 43% | 48% | 0.0% | 325 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 64% | 51% | 0.0% | 325 |
| bone | `k h40 br0.3 sat0.35` | 39° (want 38) | 15% | 34% | 0.0% | 325 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 68% | 51% | 0.0% | 325 |
| blue | `k h228 br0.35 sat1.3` | 225° (want 222) | 45% | 53% | 0.0% | 325 |
| purple | `k h260 br0.3 sat1.5` | 262° (want 272) | 38% | 49% | 0.0% | 325 |
| crimson | `k h349 br0.3 sat1.5` | 358° (want 357) | 43% | 48% | 0.0% | 325 |

### FX-046 — Heavy Impact

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h351 br0.65 sat1.5` | 360° (want 0) | 47% | 53% | 0.0% | 300 |
| rust | `k h15 br0.8 sat1.5` | 20° (want 19) | 66% | 52% | 0.0% | 300 |
| bone | `k h40 br0.6 sat0.35` | 38° (want 38) | 15% | 35% | 0.0% | 300 |
| green | `k h120 sat1.5` | 132° (want 134) | 66% | 47% | 0.0% | 300 |
| blue | `k h225 br0.7 sat1.35` | 223° (want 222) | 49% | 53% | 0.0% | 300 |
| purple | `k h270 br0.65 sat1.5` | 273° (want 272) | 43% | 52% | 0.0% | 300 |
| crimson | `k h345 br0.65 sat1.5` | 354° (want 357) | 49% | 53% | 0.0% | 300 |

### FX-047 — Warded Impact

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.55 sat1.5` | 0° (want 0) | 48% | 51% | 0.0% | 300 |
| rust | `k h15 br0.7 sat1.5` | 20° (want 19) | 66% | 51% | 0.0% | 300 |
| bone | `k h41 br0.65 sat0.35` | 38° (want 38) | 15% | 44% | 0.0% | 300 |
| green | `k h120 sat1.5` | 136° (want 134) | 72% | 52% | 0.0% | 300 |
| blue | `k h225 br0.6 sat1.4` | 223° (want 222) | 51% | 52% | 0.0% | 300 |
| purple | `k h270 br0.55 sat1.5` | 273° (want 272) | 45% | 51% | 0.0% | 300 |
| crimson | `k h345 br0.55 sat1.5` | 354° (want 357) | 49% | 51% | 0.0% | 300 |

### FX-048 — Piercing Bolt

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.35 sat1.5` | 1° (want 0) | 46% | 51% | 0.0% | 500 |
| rust | `k h15 br0.45 sat1.35` | 20° (want 19) | 62% | 53% | 0.0% | 500 |
| bone | `k h40 br0.35 sat0.35` | 39° (want 38) | 15% | 37% | 0.0% | 500 |
| green | `k h120 br0.6 sat1.5` | 132° (want 134) | 70% | 51% | 0.0% | 500 |
| blue | `k h225 br0.35 sat1.5` | 223° (want 222) | 48% | 49% | 0.0% | 500 |
| purple | `k h266 br0.35 sat1.5` | 268° (want 272) | 42% | 52% | 0.0% | 500 |
| crimson | `k h345 br0.35 sat1.5` | 354° (want 357) | 47% | 51% | 0.0% | 500 |

### FX-049 — Water Shard

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h351 br0.4 sat1.5` | 0° (want 0) | 47% | 52% | 0.0% | 542 |
| rust | `k h15 br0.5 sat1.5` | 20° (want 19) | 68% | 52% | 0.0% | 542 |
| bone | `k h40 br0.4 sat0.35` | 39° (want 38) | 15% | 37% | 0.0% | 542 |
| green | `k h120 br0.7 sat1.5` | 132° (want 134) | 75% | 53% | 0.0% | 542 |
| blue | `k h225 br0.4 sat1.5` | 223° (want 222) | 50% | 50% | 0.0% | 542 |
| purple | `k h270 br0.4 sat1.5` | 273° (want 272) | 44% | 52% | 0.0% | 542 |
| crimson | `k h345 br0.4 sat1.5` | 354° (want 357) | 49% | 52% | 0.0% | 542 |

### FX-052 — Cure Ring

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.35 sat1.4` | 1° (want 0) | 46% | 53% | 0.0% | 542 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 61% | 50% | 0.0% | 542 |
| bone | `k h40 br0.3 sat0.35` | 39° (want 38) | 15% | 33% | 0.0% | 542 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 67% | 49% | 0.0% | 542 |
| blue | `k h225 br0.35 sat1.5` | 223° (want 222) | 50% | 52% | 0.0% | 542 |
| purple | `k h263 br0.3 sat1.5` | 265° (want 272) | 39% | 47% | 0.0% | 542 |
| crimson | `k h349 br0.35 sat1.35` | 358° (want 357) | 44% | 53% | 0.0% | 542 |

### FX-053 — Radiant Burst

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.35 sat1.5` | 1° (want 0) | 44% | 50% | 0.0% | 500 |
| rust | `k h15 br0.45 sat1.5` | 20° (want 19) | 66% | 52% | 0.0% | 500 |
| bone | `k h40 br0.45 sat0.35` | 38° (want 38) | 15% | 46% | 0.0% | 500 |
| green | `k h120 br0.6 sat1.5` | 132° (want 134) | 68% | 50% | 0.0% | 500 |
| blue | `k h225 br0.35 sat1.5` | 223° (want 222) | 47% | 48% | 0.0% | 500 |
| purple | `k h266 br0.35 sat1.5` | 268° (want 272) | 41% | 51% | 0.0% | 500 |
| crimson | `k h345 br0.35 sat1.5` | 354° (want 357) | 45% | 50% | 0.0% | 500 |

### FX-054 — Empowerment

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.5 sat1.5` | 1° (want 0) | 47% | 52% | 0.0% | 325 |
| rust | `k h15 br0.6 sat1.5` | 19° (want 19) | 64% | 51% | 0.0% | 325 |
| bone | `k h41 br0.65 sat0.35` | 39° (want 38) | 15% | 49% | 0.0% | 325 |
| green | `k h120 br0.85 sat1.5` | 132° (want 134) | 72% | 52% | 0.0% | 325 |
| blue | `k h225 br0.5 sat1.5` | 223° (want 222) | 49% | 50% | 0.0% | 325 |
| purple | `k h270 br0.5 sat1.5` | 273° (want 272) | 44% | 52% | 0.0% | 325 |
| crimson | `k h345 br0.5 sat1.5` | 354° (want 357) | 49% | 53% | 0.0% | 325 |

### FX-055 — Hex Motes

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h351 br0.45 sat1.5` | 360° (want 0) | 50% | 52% | 0.0% | 325 |
| rust | `k h15 br0.55 sat1.5` | 20° (want 19) | 69% | 52% | 0.0% | 325 |
| bone | `k h40 br0.3 sat0.35` | 38° (want 38) | 15% | 25% | 0.0% | 325 |
| green | `k h120 br0.75 sat1.5` | 132° (want 134) | 74% | 51% | 0.0% | 325 |
| blue | `k h225 br0.45 sat1.5` | 223° (want 222) | 52% | 50% | 0.0% | 325 |
| purple | `k h270 br0.45 sat1.5` | 273° (want 272) | 46% | 52% | 0.0% | 325 |
| crimson | `k h345 br0.45 sat1.5` | 354° (want 357) | 52% | 53% | 0.0% | 325 |

## The saturation reached, every pair

The leg that could not be met at all before the reorder. Read down a column to see how an element
fares across the sheets; the floor is 25% for an unbanded element, and bone is capped at 18%.

**Read the banded columns downwards, not across:** a banded element is deliberately the
quietest column on the page and is not competing with the rest.

| sheet | red | rust | bone | green | blue | purple | crimson |
|---|---|---|---|---|---|---|---|
| FX-051 | 43% | 65% | 15% | 69% | 44% | 30% | 43% |
| FX-034 | 40% | 49% | 14% | 56% | 44% | 34% | 39% |
| FX-038 | 44% | 65% | 15% | 76% | 51% | 41% | 45% |
| FX-032 | 48% | 62% | 15% | 67% | 50% | 38% | 46% |
| FX-045 | 43% | 65% | 15% | 69% | 44% | 38% | 43% |
| FX-044 | 46% | 62% | 15% | 67% | 51% | 38% | 45% |
| FX-043 | 43% | 65% | 15% | 69% | 44% | 38% | 43% |
| FX-029 | 46% | 61% | 15% | 67% | 50% | 39% | 46% |
| FX-042 | 43% | 64% | 15% | 69% | 44% | 38% | 43% |
| FX-036 | 45% | 65% | 15% | 72% | 48% | 43% | 46% |
| FX-050 | 44% | 64% | 15% | 74% | 54% | 41% | 44% |
| FX-008 | 43% | 65% | 15% | 69% | 44% | 30% | 43% |
| FX-001 | 49% | 66% | 15% | 71% | 51% | 45% | 51% |
| FX-002 | 55% | 73% | 15% | 76% | 61% | 51% | 56% |
| FX-003 | 46% | 63% | 15% | 72% | 50% | 40% | 45% |
| FX-004 | 47% | 63% | 15% | 71% | 50% | 42% | 47% |
| FX-005 | 44% | 59% | 15% | 65% | 47% | 40% | 44% |
| FX-006 | 54% | 71% | 15% | 77% | 56% | 50% | 56% |
| FX-007 | 47% | 61% | 15% | 72% | 49% | 44% | 48% |
| FX-009 | 46% | 64% | 15% | 73% | 53% | 42% | 47% |
| FX-010 | 49% | 61% | 15% | 75% | 49% | 39% | 47% |
| FX-011 | 46% | 66% | 15% | 70% | 51% | 42% | 47% |
| FX-012 | 45% | 68% | 15% | 70% | 48% | 43% | 46% |
| FX-013 | 46% | 69% | 15% | 71% | 48% | 43% | 47% |
| FX-014 | 46% | 65% | 15% | 71% | 51% | 42% | 47% |
| FX-018 | 37% | 48% | 13% | 38% | 52% | 39% | 37% |
| FX-019 | 42% | 56% | 15% | 63% | 46% | 39% | 41% |
| FX-020 | 46% | 58% | 15% | 65% | 49% | 43% | 46% |
| FX-021 | 43% | 57% | 15% | 64% | 46% | 39% | 42% |
| FX-022 | 48% | 60% | 15% | 65% | 52% | 44% | 48% |
| FX-023 | 42% | 56% | 13% | 57% | 48% | 39% | 41% |
| FX-028 | 53% | 63% | 15% | 69% | 56% | 50% | 53% |
| FX-030 | 44% | 66% | 15% | 68% | 47% | 41% | 45% |
| FX-031 | 46% | 64% | 15% | 67% | 53% | 42% | 47% |
| FX-033 | 48% | 66% | 15% | 77% | 57% | 44% | 49% |
| FX-035 | 45% | 63% | 15% | 74% | 54% | 41% | 46% |
| FX-037 | 47% | 58% | 15% | 65% | 51% | 45% | 47% |
| FX-039 | 43% | 61% | 15% | 71% | 52% | 39% | 44% |
| FX-040 | 43% | 64% | 15% | 69% | 45% | 38% | 43% |
| FX-041 | 43% | 64% | 15% | 68% | 45% | 38% | 43% |
| FX-046 | 47% | 66% | 15% | 66% | 49% | 43% | 49% |
| FX-047 | 48% | 66% | 15% | 72% | 51% | 45% | 49% |
| FX-048 | 46% | 62% | 15% | 70% | 48% | 42% | 47% |
| FX-049 | 47% | 68% | 15% | 75% | 50% | 44% | 49% |
| FX-052 | 46% | 61% | 15% | 67% | 50% | 39% | 44% |
| FX-053 | 44% | 66% | 15% | 68% | 47% | 41% | 45% |
| FX-054 | 47% | 64% | 15% | 72% | 49% | 44% | 49% |
| FX-055 | 50% | 69% | 15% | 74% | 52% | 46% | 52% |

Per element, mean over the sheets solved: **bone 15%**, **purple 41%**, **red 46%**, **crimson 46%**, **blue 50%**, **rust 63%**, **green 69%**.

## What the grammar cannot reach

**Nothing.** All 336 sheet × element pairs hit the target inside `h` 0-359, `br` 0.3-1.6,
`sat` 0-1.5 — hue on the element, lum ≤ 55%, no flat white, sat ≥ 25%. No desaturated twin is
needed for any of the sheets, no new art, and neither engine lever the first solve proposed
(raising `saturate(2.4)`, or lifting the `sat` ceiling) was required: each was worth about 7
points of saturation where the filter reorder was worth about 40.

## The highest saturation each sheet can reach

The most chroma any element got out of each sheet, and the token that got it. Not to be confused
with the per-element **ceiling** above: this is what the art allows, that is what a ruling permits.

| sheet | best sat reached | at | floor |
|---|---|---|---|
| FX-051 | **69%** | `k h120 br0.55 sat1.5` | 25% |
| FX-034 | **56%** | `k h117 br0.65 sat1.5` | 25% |
| FX-038 | **76%** | `k h120 br0.65 sat1.5` | 25% |
| FX-032 | **67%** | `k h120 br0.55 sat1.5` | 25% |
| FX-045 | **69%** | `k h120 br0.55 sat1.5` | 25% |
| FX-044 | **67%** | `k h120 br0.55 sat1.5` | 25% |
| FX-043 | **69%** | `k h120 br0.55 sat1.5` | 25% |
| FX-029 | **67%** | `k h120 br0.55 sat1.5` | 25% |
| FX-042 | **69%** | `k h120 br0.55 sat1.5` | 25% |
| FX-036 | **72%** | `k h120 br0.75 sat1.5` | 25% |
| FX-050 | **74%** | `k h120 br0.65 sat1.5` | 25% |
| FX-008 | **69%** | `k h120 br0.55 sat1.5` | 25% |
| FX-001 | **71%** | `k h120 br0.65 sat1.5` | 25% |
| FX-002 | **76%** | `k h120 sat1.5` | 25% |
| FX-003 | **72%** | `k h120 sat1.5` | 25% |
| FX-004 | **71%** | `k h120 sat1.5` | 25% |
| FX-005 | **65%** | `k h120 sat1.5` | 25% |
| FX-006 | **77%** | `k h120 br0.85 sat1.5` | 25% |
| FX-007 | **72%** | `k h120 br0.6 sat1.5` | 25% |
| FX-009 | **73%** | `k h120 br0.8 sat1.5` | 25% |
| FX-010 | **75%** | `k h120 br0.6 sat1.5` | 25% |
| FX-011 | **70%** | `k h120 sat1.5` | 25% |
| FX-012 | **70%** | `k h120 br0.6 sat1.5` | 25% |
| FX-013 | **71%** | `k h120 br0.6 sat1.5` | 25% |
| FX-014 | **71%** | `k h120 br0.9 sat1.5` | 25% |
| FX-018 | **52%** | `k h210 br0.65 sat1.5` | 25% |
| FX-019 | **63%** | `k h120 sat1.5` | 25% |
| FX-020 | **65%** | `k h120 sat1.5` | 25% |
| FX-021 | **64%** | `k h120 sat1.5` | 25% |
| FX-022 | **65%** | `k h120 sat1.5` | 25% |
| FX-023 | **57%** | `k h116 sat1.5` | 25% |
| FX-028 | **69%** | `k h120 br0.85 sat1.5` | 25% |
| FX-030 | **68%** | `k h120 br0.6 sat1.5` | 25% |
| FX-031 | **67%** | `k h120 sat1.5` | 25% |
| FX-033 | **77%** | `k h120 br0.85 sat1.5` | 25% |
| FX-035 | **74%** | `k h120 br0.75 sat1.5` | 25% |
| FX-037 | **65%** | `k h120 br0.75 sat1.5` | 25% |
| FX-039 | **71%** | `k h120 br0.65 sat1.5` | 25% |
| FX-040 | **69%** | `k h120 br0.55 sat1.5` | 25% |
| FX-041 | **68%** | `k h120 br0.55 sat1.5` | 25% |
| FX-046 | **66%** | `k h120 sat1.5` | 25% |
| FX-047 | **72%** | `k h120 sat1.5` | 25% |
| FX-048 | **70%** | `k h120 br0.6 sat1.5` | 25% |
| FX-049 | **75%** | `k h120 br0.7 sat1.5` | 25% |
| FX-052 | **67%** | `k h120 br0.55 sat1.5` | 25% |
| FX-053 | **68%** | `k h120 br0.6 sat1.5` | 25% |
| FX-054 | **72%** | `k h120 br0.85 sat1.5` | 25% |
| FX-055 | **74%** | `k h120 br0.75 sat1.5` | 25% |

*A model of a renderer is not the renderer.* The first version of this page was written against a
filter table that composed the CSS matrices and clamped once at the end; a browser clamps between
primitives, and that difference was the entire "the `k` path cannot be saturated" finding. Every
number on this page is a screenshot. `python tools/vfx_calibrate.py --filter-check` renders both
orders of the chain side by side if it needs settling again.
