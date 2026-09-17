# The white-sheet tints — the token that actually lands, per sheet × element

*Measured 2026-09-17 by `tools/vfx_calibrate.py`. Do not hand-edit — re-run the tool.*

D ruled the 12 near-white sheets are kept and re-hued dark per element. The `k` token makes
that possible, but **the hue that lands is not the hue authored** — every sheet is its own mix
of white core and coloured halo, so do not write `h134` and hope for green. **Copy the token from
the row below**, verbatim, into every layer that uses that sheet at that element.

> **Re-solved 2026-09-17, after the filter order was fixed.** The first solve of this table put *none*
> of the 84 pairs over the saturation leg. That was this tool finding an engine defect rather than a
> limit of the art: `sheetFilter` emitted `brightness` **last**, a browser clamps to 8 bits between
> filter primitives, and `sepia(1)` on a white pixel returns rgb(255,255,239) — two channels already
> pinned — so every pass after it worked on a pixel whose chroma was gone. `brightness` is now emitted
> **first** on the neutral/sepia path, which moves the pixel off the ceiling before `sepia` runs. The
> tokens below are all re-measured against that chain; any older copy of this page is void.

## How to read a row

`FX-038` + `green` → write `k h120 br0.65 sat1.5`, i.e. the whole layer is
`FX-038@t s1.0 k h120 br0.65 sat1.5 d120`. The measured columns are what that token puts on the screen.

## The measurement, so a row can be audited without re-running it

- Carrier move **`M-THORNBACK-1`** (`Targets` = enemy, so the layer lands on the enemy lead), stage **S3**,
  seed **1234**, one layer at **s1.4**, no delay, no flags — the same move, seed, tile and scale for
  all 12 sheets, so the sheets are comparable to each other.
- Scrubbed **inside the layer's own `lenMs`** (fractions 0.3 / 0.5 / 0.7, brightest kept — the `ms`
  column is the frame the row was read at).
- The pixels measured are the **difference against a clean plate of the same tile**, same paused
  frame, **restricted to where the plate is dark** (max channel ≤ 0.16). That is the layer over the
  floor and not over the creature: a decile taken over the whole footprint picks the brightest
  pixels in it, and once the layer is darkened those are exactly the ones the sprite shines
  through. The mask is frozen per sheet, so two tokens are compared on the same pixels.
- Reported on the **top luminance decile** of that mask: `hue` a chroma-weighted circular mean,
  `sat` and `lum` HSL, `flat` the share at HSV value ≥ 250 and HSV saturation ≤ 0.08.
- **Target:** hue within ±18° · lum ≤ 55% · flat = 0% · sat ≥ 25%.
- The chain a `k` layer renders through is `brightness(br) sepia(1) saturate(2.4) hue-rotate(h−40)
  saturate(sat)`. `br` is the **first** primitive, so every candidate value of it costs a screenshot
  here; `sat` is the last, so that axis is ranked on pixels already shot and only the winner is re-shot.
- Element hues (client `VFXHEX`, and the same numbers as `VXHITH`): red 0°, rust 19°, bone 38°, green 134°, blue 222°, purple 272°, crimson 357°.

## The table

### FX-051 — Mending Ring

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red **MISS: lum 71%** | `k h352 br0.5 sat0.8` | 1° (want 0) | 64% | 71% | 0.0% | 542 |
| rust **MISS: lum 63%** | `k h15 br0.5 sat1.5` | 21° (want 19) | 100% | 63% | 0.0% | 542 |
| bone | `k h40 br0.55 sat1.5` | 38° (want 38) | 87% | 53% | 0.0% | 542 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 69% | 51% | 0.0% | 542 |
| blue **MISS: lum 71%** | `k h229 br0.5 sat0.8` | 227° (want 222) | 63% | 71% | 0.0% | 542 |
| purple **MISS: lum 76%** | `k h259 br0.5 sat1.5` | 267° (want 272) | 100% | 76% | 0.0% | 542 |
| crimson **MISS: lum 71%** | `k h349 br0.5 sat0.8` | 358° (want 357) | 64% | 71% | 0.0% | 542 |

### FX-034 — Sanctified Circle

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h0 br0.5 sat1.5` | 3° (want 0) | 37% | 28% | 0.0% | 500 |
| rust | `k h15 br0.5 sat1.5` | 16° (want 19) | 49% | 26% | 0.0% | 500 |
| bone | `k h45 br0.65 sat1.5` | 42° (want 38) | 64% | 24% | 0.0% | 500 |
| green | `k h117 br0.65 sat1.5` | 132° (want 134) | 56% | 24% | 0.0% | 500 |
| blue | `k h225 br0.5 sat1.5` | 223° (want 222) | 41% | 29% | 0.0% | 500 |
| purple | `k h264 br0.5 sat1.5` | 270° (want 272) | 34% | 30% | 0.0% | 500 |
| crimson | `k h356 br0.5 sat1.5` | 359° (want 357) | 35% | 29% | 0.0% | 500 |

### FX-038 — Strike Flash

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red **MISS: lum 62%** | `k h352 br0.5 sat0.8` | 0° (want 0) | 42% | 62% | 0.0% | 88 |
| rust | `k h15 br0.5 sat0.8` | 19° (want 19) | 40% | 55% | 0.0% | 88 |
| bone | `k h40 br0.65 sat1.5` | 40° (want 38) | 86% | 52% | 0.0% | 88 |
| green | `k h120 br0.65 sat1.5` | 132° (want 134) | 76% | 53% | 0.0% | 88 |
| blue **MISS: lum 60%** | `k h225 br0.5 sat0.8` | 223° (want 222) | 43% | 60% | 0.0% | 88 |
| purple **MISS: lum 63%** | `k h264 br0.5 sat0.8` | 266° (want 272) | 40% | 63% | 0.0% | 88 |
| crimson **MISS: lum 62%** | `k h349 br0.5 sat0.8` | 357° (want 357) | 43% | 62% | 0.0% | 88 |

### FX-032 — Thunder Ring

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red **MISS: lum 68%** | `k h352 br0.5 sat0.8` | 1° (want 0) | 55% | 68% | 0.0% | 300 |
| rust **MISS: lum 60%** | `k h15 br0.5 sat0.8` | 20° (want 19) | 50% | 60% | 0.0% | 300 |
| bone | `k h40 br0.55 sat1.5` | 39° (want 38) | 81% | 50% | 0.0% | 300 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 67% | 49% | 0.0% | 300 |
| blue **MISS: lum 66%** | `k h225 br0.5 sat0.8` | 223° (want 222) | 55% | 66% | 0.0% | 300 |
| purple **MISS: lum 74%** | `k h261 br0.5 sat1.5` | 268° (want 272) | 94% | 74% | 0.0% | 300 |
| crimson **MISS: lum 68%** | `k h349 br0.5 sat0.8` | 358° (want 357) | 56% | 68% | 0.0% | 300 |

### FX-045 — Impact Star

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red **MISS: lum 71%** | `k h351 br0.5 sat0.8` | 360° (want 0) | 62% | 71% | 0.0% | 300 |
| rust **MISS: lum 63%** | `k h15 br0.5 sat1.5` | 21° (want 19) | 100% | 63% | 0.0% | 300 |
| bone | `k h40 br0.55 sat1.5` | 39° (want 38) | 86% | 53% | 0.0% | 300 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 69% | 51% | 0.0% | 300 |
| blue **MISS: lum 70%** | `k h229 br0.5 sat0.8` | 226° (want 222) | 62% | 70% | 0.0% | 300 |
| purple **MISS: lum 76%** | `k h260 br0.5 sat1.5` | 268° (want 272) | 100% | 76% | 0.0% | 300 |
| crimson **MISS: lum 71%** | `k h349 br0.5 sat0.8` | 358° (want 357) | 63% | 71% | 0.0% | 300 |

### FX-044 — Claw Rake

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red **MISS: lum 68%** | `k h352 br0.5 sat0.8` | 1° (want 0) | 56% | 68% | 0.0% | 542 |
| rust **MISS: lum 61%** | `k h15 br0.5 sat0.8` | 20° (want 19) | 51% | 61% | 0.0% | 542 |
| bone | `k h40 br0.55 sat1.5` | 39° (want 38) | 82% | 51% | 0.0% | 542 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 67% | 49% | 0.0% | 542 |
| blue **MISS: lum 67%** | `k h225 br0.5 sat0.8` | 223° (want 222) | 56% | 67% | 0.0% | 542 |
| purple **MISS: lum 74%** | `k h261 br0.5 sat1.5` | 268° (want 272) | 96% | 74% | 0.0% | 542 |
| crimson **MISS: lum 69%** | `k h349 br0.5 sat0.8` | 358° (want 357) | 57% | 69% | 0.0% | 542 |

### FX-043 — Spin Slash

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red **MISS: lum 71%** | `k h352 br0.5 sat0.8` | 1° (want 0) | 64% | 71% | 0.0% | 758 |
| rust **MISS: lum 63%** | `k h15 br0.5 sat1.5` | 21° (want 19) | 100% | 63% | 0.0% | 758 |
| bone | `k h40 br0.55 sat1.5` | 38° (want 38) | 87% | 53% | 0.0% | 758 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 69% | 51% | 0.0% | 758 |
| blue **MISS: lum 71%** | `k h229 br0.5 sat0.8` | 227° (want 222) | 63% | 71% | 0.0% | 758 |
| purple **MISS: lum 76%** | `k h259 br0.5 sat1.5` | 267° (want 272) | 100% | 76% | 0.0% | 758 |
| crimson **MISS: lum 71%** | `k h349 br0.5 sat0.8` | 358° (want 357) | 64% | 71% | 0.0% | 758 |

### FX-029 — Rime Bloom

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red **MISS: lum 68%** | `k h352 br0.5 sat0.8` | 1° (want 0) | 55% | 68% | 0.0% | 300 |
| rust **MISS: lum 60%** | `k h15 br0.5 sat0.8` | 20° (want 19) | 50% | 60% | 0.0% | 300 |
| bone | `k h40 br0.55 sat1.5` | 39° (want 38) | 80% | 50% | 0.0% | 300 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 67% | 49% | 0.0% | 300 |
| blue **MISS: lum 66%** | `k h225 br0.5 sat0.8` | 223° (want 222) | 55% | 66% | 0.0% | 300 |
| purple **MISS: lum 69%** | `k h263 br0.5 sat0.8` | 265° (want 272) | 53% | 69% | 0.0% | 300 |
| crimson **MISS: lum 68%** | `k h349 br0.5 sat0.8` | 358° (want 357) | 56% | 68% | 0.0% | 300 |

### FX-042 — Wide Slash

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red **MISS: lum 70%** | `k h352 br0.5 sat0.8` | 1° (want 0) | 62% | 70% | 0.0% | 542 |
| rust **MISS: lum 63%** | `k h15 br0.5 sat1.5` | 21° (want 19) | 100% | 63% | 0.0% | 542 |
| bone | `k h40 br0.55 sat1.5` | 39° (want 38) | 85% | 52% | 0.0% | 542 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 69% | 51% | 0.0% | 542 |
| blue **MISS: lum 70%** | `k h229 br0.5 sat0.8` | 227° (want 222) | 62% | 70% | 0.0% | 542 |
| purple **MISS: lum 75%** | `k h260 br0.5 sat1.5` | 268° (want 272) | 100% | 75% | 0.0% | 542 |
| crimson **MISS: lum 71%** | `k h349 br0.5 sat0.8` | 358° (want 357) | 63% | 71% | 0.0% | 542 |

### FX-036 — Cyclone Ring

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red **MISS: lum 56%** | `k h352 br0.5 sat0.8` | 360° (want 0) | 33% | 56% | 0.0% | 500 |
| rust | `k h15 br0.5 sat1.5` | 19° (want 19) | 65% | 52% | 0.0% | 500 |
| bone | `k h41 br0.65 sat1.5` | 40° (want 38) | 79% | 49% | 0.0% | 500 |
| green | `k h120 br0.75 sat1.5` | 139° (want 134) | 72% | 52% | 0.0% | 500 |
| blue **MISS: lum 55%** | `k h225 br0.5 sat0.8` | 223° (want 222) | 35% | 55% | 0.0% | 500 |
| purple **MISS: lum 57%** | `k h266 br0.5 sat0.8` | 268° (want 272) | 32% | 57% | 0.0% | 500 |
| crimson **MISS: lum 57%** | `k h349 br0.5 sat0.8` | 357° (want 357) | 34% | 57% | 0.0% | 500 |

### FX-050 — Void Bloom

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red **MISS: lum 61%** | `k h352 br0.5 sat0.8` | 0° (want 0) | 41% | 61% | 0.0% | 325 |
| rust | `k h15 br0.5 sat0.8` | 19° (want 19) | 39% | 54% | 0.0% | 325 |
| bone | `k h40 br0.65 sat1.5` | 40° (want 38) | 86% | 52% | 0.0% | 325 |
| green | `k h120 br0.65 sat1.5` | 132° (want 134) | 74% | 52% | 0.0% | 325 |
| blue **MISS: lum 60%** | `k h225 br0.5 sat0.8` | 223° (want 222) | 42% | 60% | 0.0% | 325 |
| purple **MISS: lum 62%** | `k h266 br0.5 sat0.8` | 268° (want 272) | 39% | 62% | 0.0% | 325 |
| crimson **MISS: lum 61%** | `k h349 br0.5 sat0.8` | 357° (want 357) | 42% | 61% | 0.0% | 325 |

### FX-008 — Pyre Orb I

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red **MISS: lum 71%** | `k h352 br0.5 sat0.8` | 1° (want 0) | 64% | 71% | 0.0% | 700 |
| rust **MISS: lum 63%** | `k h15 br0.5 sat1.5` | 21° (want 19) | 100% | 63% | 0.0% | 700 |
| bone | `k h40 br0.55 sat1.5` | 38° (want 38) | 87% | 53% | 0.0% | 700 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 69% | 51% | 0.0% | 700 |
| blue **MISS: lum 71%** | `k h229 br0.5 sat0.8` | 227° (want 222) | 63% | 71% | 0.0% | 700 |
| purple **MISS: lum 76%** | `k h259 br0.5 sat1.5` | 267° (want 272) | 100% | 76% | 0.0% | 700 |
| crimson **MISS: lum 71%** | `k h349 br0.5 sat0.8` | 358° (want 357) | 64% | 71% | 0.0% | 700 |

## The saturation reached, every pair

The leg that could not be met at all before the reorder. Read down a column to see how an element
fares across the sheets; the floor is 25%.

| sheet | red | rust | bone | green | blue | purple | crimson |
|---|---|---|---|---|---|---|---|
| FX-051 | 64% | 100% | 87% | 69% | 63% | 100% | 64% |
| FX-034 | 37% | 49% | 64% | 56% | 41% | 34% | 35% |
| FX-038 | 42% | 40% | 86% | 76% | 43% | 40% | 43% |
| FX-032 | 55% | 50% | 81% | 67% | 55% | 94% | 56% |
| FX-045 | 62% | 100% | 86% | 69% | 62% | 100% | 63% |
| FX-044 | 56% | 51% | 82% | 67% | 56% | 96% | 57% |
| FX-043 | 64% | 100% | 87% | 69% | 63% | 100% | 64% |
| FX-029 | 55% | 50% | 80% | 67% | 55% | 53% | 56% |
| FX-042 | 62% | 100% | 85% | 69% | 62% | 100% | 63% |
| FX-036 | 33% | 65% | 79% | 72% | 35% | 32% | 34% |
| FX-050 | 41% | 39% | 86% | 74% | 42% | 39% | 42% |
| FX-008 | 64% | 100% | 87% | 69% | 63% | 100% | 64% |

Per element, mean over the sheets solved: **red 53%**, **blue 53%**, **crimson 53%**, **green 69%**, **rust 70%**, **purple 74%**, **bone 82%**.

## What the grammar cannot reach

52 of 84 pairs miss. By leg: hue 0 · lum 52 · flat 0 · sat 0.

| sheet | element | best token | hue | want | sat | lum | flat | misses |
|---|---|---|---|---|---|---|---|---|
| FX-051 | red | `k h352 br0.5 sat0.8` | 1° | 0° | 64% | 71% | 0.0% | lum 71% |
| FX-051 | rust | `k h15 br0.5 sat1.5` | 21° | 19° | 100% | 63% | 0.0% | lum 63% |
| FX-051 | blue | `k h229 br0.5 sat0.8` | 227° | 222° | 63% | 71% | 0.0% | lum 71% |
| FX-051 | purple | `k h259 br0.5 sat1.5` | 267° | 272° | 100% | 76% | 0.0% | lum 76% |
| FX-051 | crimson | `k h349 br0.5 sat0.8` | 358° | 357° | 64% | 71% | 0.0% | lum 71% |
| FX-038 | red | `k h352 br0.5 sat0.8` | 0° | 0° | 42% | 62% | 0.0% | lum 62% |
| FX-038 | blue | `k h225 br0.5 sat0.8` | 223° | 222° | 43% | 60% | 0.0% | lum 60% |
| FX-038 | purple | `k h264 br0.5 sat0.8` | 266° | 272° | 40% | 63% | 0.0% | lum 63% |
| FX-038 | crimson | `k h349 br0.5 sat0.8` | 357° | 357° | 43% | 62% | 0.0% | lum 62% |
| FX-032 | red | `k h352 br0.5 sat0.8` | 1° | 0° | 55% | 68% | 0.0% | lum 68% |
| FX-032 | rust | `k h15 br0.5 sat0.8` | 20° | 19° | 50% | 60% | 0.0% | lum 60% |
| FX-032 | blue | `k h225 br0.5 sat0.8` | 223° | 222° | 55% | 66% | 0.0% | lum 66% |
| FX-032 | purple | `k h261 br0.5 sat1.5` | 268° | 272° | 94% | 74% | 0.0% | lum 74% |
| FX-032 | crimson | `k h349 br0.5 sat0.8` | 358° | 357° | 56% | 68% | 0.0% | lum 68% |
| FX-045 | red | `k h351 br0.5 sat0.8` | 360° | 0° | 62% | 71% | 0.0% | lum 71% |
| FX-045 | rust | `k h15 br0.5 sat1.5` | 21° | 19° | 100% | 63% | 0.0% | lum 63% |
| FX-045 | blue | `k h229 br0.5 sat0.8` | 226° | 222° | 62% | 70% | 0.0% | lum 70% |
| FX-045 | purple | `k h260 br0.5 sat1.5` | 268° | 272° | 100% | 76% | 0.0% | lum 76% |
| FX-045 | crimson | `k h349 br0.5 sat0.8` | 358° | 357° | 63% | 71% | 0.0% | lum 71% |
| FX-044 | red | `k h352 br0.5 sat0.8` | 1° | 0° | 56% | 68% | 0.0% | lum 68% |
| FX-044 | rust | `k h15 br0.5 sat0.8` | 20° | 19° | 51% | 61% | 0.0% | lum 61% |
| FX-044 | blue | `k h225 br0.5 sat0.8` | 223° | 222° | 56% | 67% | 0.0% | lum 67% |
| FX-044 | purple | `k h261 br0.5 sat1.5` | 268° | 272° | 96% | 74% | 0.0% | lum 74% |
| FX-044 | crimson | `k h349 br0.5 sat0.8` | 358° | 357° | 57% | 69% | 0.0% | lum 69% |
| FX-043 | red | `k h352 br0.5 sat0.8` | 1° | 0° | 64% | 71% | 0.0% | lum 71% |
| FX-043 | rust | `k h15 br0.5 sat1.5` | 21° | 19° | 100% | 63% | 0.0% | lum 63% |
| FX-043 | blue | `k h229 br0.5 sat0.8` | 227° | 222° | 63% | 71% | 0.0% | lum 71% |
| FX-043 | purple | `k h259 br0.5 sat1.5` | 267° | 272° | 100% | 76% | 0.0% | lum 76% |
| FX-043 | crimson | `k h349 br0.5 sat0.8` | 358° | 357° | 64% | 71% | 0.0% | lum 71% |
| FX-029 | red | `k h352 br0.5 sat0.8` | 1° | 0° | 55% | 68% | 0.0% | lum 68% |
| FX-029 | rust | `k h15 br0.5 sat0.8` | 20° | 19° | 50% | 60% | 0.0% | lum 60% |
| FX-029 | blue | `k h225 br0.5 sat0.8` | 223° | 222° | 55% | 66% | 0.0% | lum 66% |
| FX-029 | purple | `k h263 br0.5 sat0.8` | 265° | 272° | 53% | 69% | 0.0% | lum 69% |
| FX-029 | crimson | `k h349 br0.5 sat0.8` | 358° | 357° | 56% | 68% | 0.0% | lum 68% |
| FX-042 | red | `k h352 br0.5 sat0.8` | 1° | 0° | 62% | 70% | 0.0% | lum 70% |
| FX-042 | rust | `k h15 br0.5 sat1.5` | 21° | 19° | 100% | 63% | 0.0% | lum 63% |
| FX-042 | blue | `k h229 br0.5 sat0.8` | 227° | 222° | 62% | 70% | 0.0% | lum 70% |
| FX-042 | purple | `k h260 br0.5 sat1.5` | 268° | 272° | 100% | 75% | 0.0% | lum 75% |
| FX-042 | crimson | `k h349 br0.5 sat0.8` | 358° | 357° | 63% | 71% | 0.0% | lum 71% |
| FX-036 | red | `k h352 br0.5 sat0.8` | 360° | 0° | 33% | 56% | 0.0% | lum 56% |
| FX-036 | blue | `k h225 br0.5 sat0.8` | 223° | 222° | 35% | 55% | 0.0% | lum 55% |
| FX-036 | purple | `k h266 br0.5 sat0.8` | 268° | 272° | 32% | 57% | 0.0% | lum 57% |
| FX-036 | crimson | `k h349 br0.5 sat0.8` | 357° | 357° | 34% | 57% | 0.0% | lum 57% |
| FX-050 | red | `k h352 br0.5 sat0.8` | 0° | 0° | 41% | 61% | 0.0% | lum 61% |
| FX-050 | blue | `k h225 br0.5 sat0.8` | 223° | 222° | 42% | 60% | 0.0% | lum 60% |
| FX-050 | purple | `k h266 br0.5 sat0.8` | 268° | 272° | 39% | 62% | 0.0% | lum 62% |
| FX-050 | crimson | `k h349 br0.5 sat0.8` | 357° | 357° | 42% | 61% | 0.0% | lum 61% |
| FX-008 | red | `k h352 br0.5 sat0.8` | 1° | 0° | 64% | 71% | 0.0% | lum 71% |
| FX-008 | rust | `k h15 br0.5 sat1.5` | 21° | 19° | 100% | 63% | 0.0% | lum 63% |
| FX-008 | blue | `k h229 br0.5 sat0.8` | 227° | 222° | 63% | 71% | 0.0% | lum 71% |
| FX-008 | purple | `k h259 br0.5 sat1.5` | 267° | 272° | 100% | 76% | 0.0% | lum 76% |
| FX-008 | crimson | `k h349 br0.5 sat0.8` | 358° | 357° | 64% | 71% | 0.0% | lum 71% |

These are the best the shipped grammar produces on those pairs; author from them anyway,
and do not raise a lever to chase one leg without shooting it first.

### Why luminance is now the leg that fails, and what it would cost to fix

The reorder traded one leg for the other. Before it, **0 of 84** pairs met `sat`
and all met `lum`; after it, **all** meet `sat` and 52 miss `lum`.

`sepia(1)` is not a dimming matrix — its red row sums to 1.351, so it has *gain*. Darkening
before it is therefore partly undone by it, and `saturate(2.4)` then pushes the red channel
back against 255 on the sheets with the brightest cores. `br` cannot answer that, because the
grammar floors it at 0.5 and the solver is already there on every missing row. So on those
sheets `lum ≤ 55%` is not reachable by any token, exactly the way `sat ≥ 25%` was not
reachable before the reorder.

Two levers would reach it, both outside this tool and both changes to what an author may
write, so neither was taken here:

1. **lower the `br` floor** in the grammar (`RANGE` in `tools/fx_lint.py` and in the client
   parser) from 0.5. It is the direct lever and it is one number; and
2. **lower `saturate(2.4)`** in the `k` branch of `sheetFilter`. Chroma is no longer scarce —
   the rows above reach 33-100% — so there is room to spend some of it on darkness.

Both want a look at the contact sheets first: a miss of 5-15 points of lightness on a layer
that is correctly hued, fully coloured and free of flat white is a far smaller defect than
the white pop this pass set out to remove.

## The ceiling, per sheet

The highest saturation each sheet reached at any element, and the token that reached it.

| sheet | best sat reached | at | floor |
|---|---|---|---|
| FX-051 | **100%** | `k h15 br0.5 sat1.5` | 25% |
| FX-034 | **64%** | `k h45 br0.65 sat1.5` | 25% |
| FX-038 | **86%** | `k h40 br0.65 sat1.5` | 25% |
| FX-032 | **94%** | `k h261 br0.5 sat1.5` | 25% |
| FX-045 | **100%** | `k h15 br0.5 sat1.5` | 25% |
| FX-044 | **96%** | `k h261 br0.5 sat1.5` | 25% |
| FX-043 | **100%** | `k h15 br0.5 sat1.5` | 25% |
| FX-029 | **80%** | `k h40 br0.55 sat1.5` | 25% |
| FX-042 | **100%** | `k h15 br0.5 sat1.5` | 25% |
| FX-036 | **79%** | `k h41 br0.65 sat1.5` | 25% |
| FX-050 | **86%** | `k h40 br0.65 sat1.5` | 25% |
| FX-008 | **100%** | `k h15 br0.5 sat1.5` | 25% |

*A model of a renderer is not the renderer.* The first version of this page was written against a
filter table that composed the CSS matrices and clamped once at the end; a browser clamps between
primitives, and that difference was the entire "the `k` path cannot be saturated" finding. Every
number on this page is a screenshot. `python tools/vfx_calibrate.py --filter-check` renders both
orders of the chain side by side if it needs settling again.
