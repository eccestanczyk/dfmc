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

> **Re-solved again 2026-09-17, after the `br` floor came down 0.5 → 0.3.** The reorder bought the
> saturation leg and lost the luminance one: that solve hit the full target on 32 of 84 pairs and
> all 52 misses were `lum ≤ 55%`, every one of them sitting on the old floor with nowhere left to
> go. The floor is one number in two places - `RANGE` in `tools/fx_lint.py` and in the client's
> `VFX_BANK` parser - and lowering it closed all 52. **57 of the 84 tokens below now carry a `br`
> under 0.5**, so this page is void against any client older than that change: an older parser
> rejects those rows outright rather than rendering them wrong.

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
| red | `k h352 br0.3 sat1.5` | 1° (want 0) | 43% | 48% | 0.0% | 542 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 65% | 52% | 0.0% | 542 |
| bone | `k h40 br0.55 sat1.5` | 38° (want 38) | 87% | 53% | 0.0% | 542 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 69% | 51% | 0.0% | 542 |
| blue | `k h229 br0.3 sat1.5` | 227° (want 222) | 44% | 48% | 0.0% | 542 |
| purple | `k h259 br0.35 sat0.95` | 261° (want 272) | 30% | 53% | 0.0% | 542 |
| crimson | `k h349 br0.3 sat1.5` | 358° (want 357) | 43% | 48% | 0.0% | 542 |

### FX-034 — Sanctified Circle

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h0 br0.45 sat1.5` | 2° (want 0) | 40% | 27% | 0.0% | 500 |
| rust | `k h15 br0.5 sat1.5` | 16° (want 19) | 49% | 26% | 0.0% | 500 |
| bone | `k h45 br0.65 sat1.5` | 42° (want 38) | 64% | 24% | 0.0% | 500 |
| green | `k h117 br0.65 sat1.5` | 132° (want 134) | 56% | 24% | 0.0% | 500 |
| blue | `k h225 br0.45 sat1.5` | 226° (want 222) | 44% | 28% | 0.0% | 500 |
| purple | `k h264 br0.5 sat1.5` | 270° (want 272) | 34% | 30% | 0.0% | 500 |
| crimson | `k h356 br0.45 sat1.5` | 358° (want 357) | 39% | 28% | 0.0% | 500 |

### FX-038 — Strike Flash

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.35 sat1.5` | 0° (want 0) | 44% | 49% | 0.0% | 88 |
| rust | `k h15 br0.45 sat1.5` | 20° (want 19) | 65% | 51% | 0.0% | 88 |
| bone | `k h40 br0.65 sat1.5` | 40° (want 38) | 86% | 52% | 0.0% | 88 |
| green | `k h120 br0.65 sat1.5` | 132° (want 134) | 76% | 53% | 0.0% | 88 |
| blue | `k h225 br0.4 sat1.4` | 223° (want 222) | 51% | 53% | 0.0% | 88 |
| purple | `k h264 br0.35 sat1.5` | 266° (want 272) | 41% | 50% | 0.0% | 88 |
| crimson | `k h349 br0.35 sat1.5` | 358° (want 357) | 45% | 49% | 0.0% | 88 |

### FX-032 — Thunder Ring

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.35 sat1.45` | 1° (want 0) | 48% | 53% | 0.0% | 300 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 62% | 50% | 0.0% | 300 |
| bone | `k h40 br0.55 sat1.5` | 39° (want 38) | 81% | 50% | 0.0% | 300 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 67% | 49% | 0.0% | 300 |
| blue | `k h225 br0.35 sat1.5` | 223° (want 222) | 50% | 51% | 0.0% | 300 |
| purple | `k h261 br0.3 sat1.5` | 263° (want 272) | 38% | 48% | 0.0% | 300 |
| crimson | `k h349 br0.35 sat1.4` | 358° (want 357) | 46% | 53% | 0.0% | 300 |

### FX-045 — Impact Star

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h351 br0.3 sat1.5` | 360° (want 0) | 43% | 48% | 0.0% | 300 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 65% | 52% | 0.0% | 300 |
| bone | `k h40 br0.55 sat1.5` | 39° (want 38) | 86% | 53% | 0.0% | 300 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 69% | 51% | 0.0% | 300 |
| blue | `k h229 br0.3 sat1.5` | 226° (want 222) | 44% | 47% | 0.0% | 300 |
| purple | `k h260 br0.3 sat1.5` | 262° (want 272) | 38% | 50% | 0.0% | 300 |
| crimson | `k h349 br0.3 sat1.5` | 358° (want 357) | 43% | 48% | 0.0% | 300 |

### FX-044 — Claw Rake

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.35 sat1.4` | 1° (want 0) | 46% | 53% | 0.0% | 542 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 62% | 50% | 0.0% | 542 |
| bone | `k h40 br0.55 sat1.5` | 39° (want 38) | 82% | 51% | 0.0% | 542 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 67% | 49% | 0.0% | 542 |
| blue | `k h225 br0.35 sat1.5` | 223° (want 222) | 51% | 52% | 0.0% | 542 |
| purple | `k h261 br0.3 sat1.5` | 263° (want 272) | 38% | 48% | 0.0% | 542 |
| crimson | `k h349 br0.35 sat1.35` | 358° (want 357) | 45% | 53% | 0.0% | 542 |

### FX-043 — Spin Slash

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.3 sat1.5` | 1° (want 0) | 43% | 48% | 0.0% | 758 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 65% | 52% | 0.0% | 758 |
| bone | `k h40 br0.55 sat1.5` | 38° (want 38) | 87% | 53% | 0.0% | 758 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 69% | 51% | 0.0% | 758 |
| blue | `k h229 br0.3 sat1.5` | 226° (want 222) | 44% | 48% | 0.0% | 758 |
| purple | `k h259 br0.3 sat1.5` | 260° (want 272) | 38% | 50% | 0.0% | 758 |
| crimson | `k h349 br0.3 sat1.5` | 358° (want 357) | 43% | 48% | 0.0% | 758 |

### FX-029 — Rime Bloom

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.35 sat1.4` | 1° (want 0) | 46% | 53% | 0.0% | 300 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 61% | 50% | 0.0% | 300 |
| bone | `k h40 br0.55 sat1.5` | 39° (want 38) | 80% | 50% | 0.0% | 300 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 67% | 49% | 0.0% | 300 |
| blue | `k h225 br0.35 sat1.5` | 223° (want 222) | 50% | 51% | 0.0% | 300 |
| purple | `k h263 br0.3 sat1.5` | 265° (want 272) | 39% | 47% | 0.0% | 300 |
| crimson | `k h349 br0.35 sat1.4` | 358° (want 357) | 46% | 53% | 0.0% | 300 |

### FX-042 — Wide Slash

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.3 sat1.5` | 1° (want 0) | 43% | 48% | 0.0% | 542 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 64% | 52% | 0.0% | 542 |
| bone | `k h40 br0.55 sat1.5` | 39° (want 38) | 85% | 52% | 0.0% | 542 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 69% | 51% | 0.0% | 542 |
| blue | `k h229 br0.3 sat1.5` | 226° (want 222) | 44% | 47% | 0.0% | 542 |
| purple | `k h260 br0.3 sat1.5` | 262° (want 272) | 38% | 49% | 0.0% | 542 |
| crimson | `k h349 br0.3 sat1.5` | 358° (want 357) | 43% | 48% | 0.0% | 542 |

### FX-036 — Cyclone Ring

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.4 sat1.5` | 0° (want 0) | 45% | 51% | 0.0% | 500 |
| rust | `k h15 br0.5 sat1.5` | 19° (want 19) | 65% | 52% | 0.0% | 500 |
| bone | `k h41 br0.65 sat1.5` | 40° (want 38) | 79% | 49% | 0.0% | 500 |
| green | `k h120 br0.75 sat1.5` | 139° (want 134) | 72% | 52% | 0.0% | 500 |
| blue | `k h225 br0.4 sat1.5` | 223° (want 222) | 48% | 49% | 0.0% | 500 |
| purple | `k h266 br0.4 sat1.5` | 268° (want 272) | 43% | 52% | 0.0% | 500 |
| crimson | `k h349 br0.4 sat1.5` | 357° (want 357) | 46% | 51% | 0.0% | 500 |

### FX-050 — Void Bloom

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.35 sat1.5` | 0° (want 0) | 44% | 48% | 0.0% | 325 |
| rust | `k h15 br0.45 sat1.5` | 19° (want 19) | 64% | 50% | 0.0% | 325 |
| bone | `k h40 br0.65 sat1.5` | 40° (want 38) | 86% | 52% | 0.0% | 325 |
| green | `k h120 br0.65 sat1.5` | 132° (want 134) | 74% | 52% | 0.0% | 325 |
| blue | `k h225 br0.4 sat1.5` | 223° (want 222) | 54% | 53% | 0.0% | 325 |
| purple | `k h266 br0.35 sat1.5` | 268° (want 272) | 41% | 49% | 0.0% | 325 |
| crimson | `k h349 br0.35 sat1.5` | 358° (want 357) | 44% | 48% | 0.0% | 325 |

### FX-008 — Pyre Orb I

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h352 br0.3 sat1.5` | 1° (want 0) | 43% | 48% | 0.0% | 700 |
| rust | `k h15 br0.4 sat1.5` | 20° (want 19) | 65% | 52% | 0.0% | 700 |
| bone | `k h40 br0.55 sat1.5` | 38° (want 38) | 87% | 53% | 0.0% | 700 |
| green | `k h120 br0.55 sat1.5` | 132° (want 134) | 69% | 51% | 0.0% | 700 |
| blue | `k h229 br0.3 sat1.5` | 227° (want 222) | 44% | 48% | 0.0% | 700 |
| purple | `k h259 br0.35 sat0.95` | 261° (want 272) | 30% | 53% | 0.0% | 700 |
| crimson | `k h349 br0.3 sat1.5` | 358° (want 357) | 43% | 48% | 0.0% | 700 |

## The saturation reached, every pair

The leg that could not be met at all before the reorder. Read down a column to see how an element
fares across the sheets; the floor is 25%.

| sheet | red | rust | bone | green | blue | purple | crimson |
|---|---|---|---|---|---|---|---|
| FX-051 | 43% | 65% | 87% | 69% | 44% | 30% | 43% |
| FX-034 | 40% | 49% | 64% | 56% | 44% | 34% | 39% |
| FX-038 | 44% | 65% | 86% | 76% | 51% | 41% | 45% |
| FX-032 | 48% | 62% | 81% | 67% | 50% | 38% | 46% |
| FX-045 | 43% | 65% | 86% | 69% | 44% | 38% | 43% |
| FX-044 | 46% | 62% | 82% | 67% | 51% | 38% | 45% |
| FX-043 | 43% | 65% | 87% | 69% | 44% | 38% | 43% |
| FX-029 | 46% | 61% | 80% | 67% | 50% | 39% | 46% |
| FX-042 | 43% | 64% | 85% | 69% | 44% | 38% | 43% |
| FX-036 | 45% | 65% | 79% | 72% | 48% | 43% | 46% |
| FX-050 | 44% | 64% | 86% | 74% | 54% | 41% | 44% |
| FX-008 | 43% | 65% | 87% | 69% | 44% | 30% | 43% |

Per element, mean over the sheets solved: **purple 37%**, **crimson 44%**, **red 44%**, **blue 47%**, **rust 63%**, **green 69%**, **bone 82%**.

## What the grammar cannot reach

**Nothing.** All 84 sheet × element pairs hit the target inside `h` 0-359, `br` 0.3-1.6,
`sat` 0-1.5 — hue on the element, lum ≤ 55%, no flat white, sat ≥ 25%. No desaturated twin is
needed for any of the sheets, no new art, and neither engine lever the first solve proposed
(raising `saturate(2.4)`, or lifting the `sat` ceiling) was required: each was worth about 7
points of saturation where the filter reorder was worth about 40.

## The ceiling, per sheet

The highest saturation each sheet reached at any element, and the token that reached it.

| sheet | best sat reached | at | floor |
|---|---|---|---|
| FX-051 | **87%** | `k h40 br0.55 sat1.5` | 25% |
| FX-034 | **64%** | `k h45 br0.65 sat1.5` | 25% |
| FX-038 | **86%** | `k h40 br0.65 sat1.5` | 25% |
| FX-032 | **81%** | `k h40 br0.55 sat1.5` | 25% |
| FX-045 | **86%** | `k h40 br0.55 sat1.5` | 25% |
| FX-044 | **82%** | `k h40 br0.55 sat1.5` | 25% |
| FX-043 | **87%** | `k h40 br0.55 sat1.5` | 25% |
| FX-029 | **80%** | `k h40 br0.55 sat1.5` | 25% |
| FX-042 | **85%** | `k h40 br0.55 sat1.5` | 25% |
| FX-036 | **79%** | `k h41 br0.65 sat1.5` | 25% |
| FX-050 | **86%** | `k h40 br0.65 sat1.5` | 25% |
| FX-008 | **87%** | `k h40 br0.55 sat1.5` | 25% |

*A model of a renderer is not the renderer.* The first version of this page was written against a
filter table that composed the CSS matrices and clamped once at the end; a browser clamps between
primitives, and that difference was the entire "the `k` path cannot be saturated" finding. Every
number on this page is a screenshot. `python tools/vfx_calibrate.py --filter-check` renders both
orders of the chain side by side if it needs settling again.
