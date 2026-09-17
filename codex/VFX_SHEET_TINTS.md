# The white-sheet tints — the token that actually lands, per sheet × element

*Measured 2026-09-17 by `tools/vfx_calibrate.py`. Do not hand-edit — re-run the tool.*

D ruled the 12 near-white sheets are kept and re-hued dark per element. The `k` token makes
that possible, but **the hue that lands is not the hue authored** — `sepia(1) saturate(2.4)`
clips channels at 255 before the rotation, and every sheet is its own mix of white core and
coloured halo. So do not write `h134` and hope for green. **Copy the token from the row below**,
verbatim, into every layer that uses that sheet at that element.

## How to read a row

`FX-038` + `green` → write `k h98 br0.675 sat1.5`, i.e. the whole layer is
`FX-038@t s1.0 k h98 br0.675 sat1.5 d120`. The measured columns are what that token puts on the screen.

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
- Element hues (client `VFXHEX`, and the same numbers as `VXHITH`): red 0°, rust 19°, bone 38°, green 134°, blue 222°, purple 272°, crimson 357°.

## The table

> Every row below meets **hue**, **lum** and **flat white**. Not one meets **sat ≥ 25%**,
> on any sheet at any element — that is a ceiling of the `k` path itself and it is measured,
> named and explained under *What the grammar cannot reach*. The rows are still the best the
> shipped grammar produces, so author from them.

### FX-051 — Mending Ring

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h330 br0.525 sat1.5` | 0° (want 0) | 3% | 51% | 0.0% | 542 |
| rust | `k h339 br0.55 sat1.3` | 24° (want 19) | 4% | 53% | 0.0% | 542 |
| bone | `k h353 br0.55 sat1.4` | 42° (want 38) | 7% | 52% | 0.0% | 542 |
| green | `k h99 br0.575 sat1.5` | 135° (want 134) | 10% | 53% | 0.0% | 542 |
| blue | `k h217 br0.525 sat1.5` | 225° (want 222) | 2% | 52% | 0.0% | 542 |
| purple | `k h224 br0.525 sat1.3` | 280° (want 272) | 1% | 52% | 0.0% | 542 |
| crimson | `k h330 br0.525 sat1.5` | 0° (want 357) | 3% | 51% | 0.0% | 542 |

### FX-034 — Sanctified Circle

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h348 br0.95 sat1.5` | 17° (want 0) | 5% | 36% | 0.0% | 500 |
| rust | `k h358 br0.975 sat1.5` | 34° (want 19) | 7% | 36% | 0.0% | 500 |
| bone | `k h15 br0.975 sat1.5` | 47° (want 38) | 9% | 35% | 0.0% | 500 |
| green | `k h85 br0.95 sat1.5` | 128° (want 134) | 8% | 34% | 0.0% | 500 |
| blue | `k h208 br0.95 sat1.5` | 216° (want 222) | 6% | 37% | 0.0% | 500 |
| purple | `k h240 br0.95 sat1.5` | 275° (want 272) | 6% | 37% | 0.0% | 500 |
| crimson | `k h347 br0.95 sat1.5` | 14° (want 357) | 4% | 36% | 0.0% | 500 |

### FX-038 — Strike Flash

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h330 br0.6 sat1.5` | 359° (want 0) | 6% | 53% | 0.0% | 88 |
| rust | `k h338 br0.6 sat1.5` | 24° (want 19) | 8% | 51% | 0.0% | 88 |
| bone | `k h354 br0.65 sat1.5` | 44° (want 38) | 15% | 53% | 0.0% | 88 |
| green | `k h98 br0.675 sat1.5` | 137° (want 134) | 20% | 53% | 0.0% | 88 |
| blue | `k h217 br0.575 sat1.5` | 217° (want 222) | 4% | 51% | 0.0% | 88 |
| purple | `k h225 br0.575 sat1.45` | 286° (want 272) | 3% | 52% | 0.0% | 88 |
| crimson | `k h330 br0.6 sat1.5` | 359° (want 357) | 6% | 53% | 0.0% | 88 |

### FX-032 — Thunder Ring

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h330 br0.55 sat1.5` | 2° (want 0) | 4% | 52% | 0.0% | 300 |
| rust | `k h339 br0.55 sat1.4` | 27° (want 19) | 6% | 51% | 0.0% | 300 |
| bone | `k h353 br0.575 sat1.5` | 43° (want 38) | 10% | 52% | 0.0% | 300 |
| green | `k h98 br0.6 sat1.5` | 136° (want 134) | 14% | 52% | 0.0% | 300 |
| blue | `k h217 br0.55 sat1.4` | 216° (want 222) | 3% | 53% | 0.0% | 300 |
| purple | `k h224 br0.5 sat1.5` | 278° (want 272) | 2% | 48% | 0.0% | 300 |
| crimson | `k h329 br0.55 sat1.5` | 357° (want 357) | 4% | 52% | 0.0% | 300 |

### FX-045 — Impact Star

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h330 br0.525 sat1.5` | 1° (want 0) | 3% | 51% | 0.0% | 300 |
| rust | `k h339 br0.55 sat1.15` | 24° (want 19) | 4% | 53% | 0.0% | 300 |
| bone | `k h353 br0.55 sat1.5` | 44° (want 38) | 7% | 51% | 0.0% | 300 |
| green | `k h99 br0.575 sat1.5` | 137° (want 134) | 11% | 53% | 0.0% | 300 |
| blue | `k h217 br0.525 sat1.35` | 218° (want 222) | 2% | 52% | 0.0% | 300 |
| purple | `k h224 br0.525 sat1.25` | 274° (want 272) | 2% | 52% | 0.0% | 300 |
| crimson | `k h329 br0.525 sat1.5` | 358° (want 357) | 3% | 51% | 0.0% | 300 |

### FX-044 — Claw Rake

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h330 br0.55 sat1.5` | 2° (want 0) | 4% | 52% | 0.0% | 542 |
| rust | `k h339 br0.55 sat1.3` | 26° (want 19) | 6% | 51% | 0.0% | 542 |
| bone | `k h353 br0.575 sat1.5` | 43° (want 38) | 10% | 52% | 0.0% | 542 |
| green | `k h98 br0.6 sat1.5` | 136° (want 134) | 13% | 53% | 0.0% | 542 |
| blue | `k h217 br0.5 sat1.5` | 216° (want 222) | 2% | 48% | 0.0% | 542 |
| purple | `k h224 br0.525 sat1.4` | 280° (want 272) | 2% | 51% | 0.0% | 542 |
| crimson | `k h329 br0.55 sat1.5` | 357° (want 357) | 4% | 52% | 0.0% | 542 |

### FX-043 — Spin Slash

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h330 br0.525 sat1.5` | 0° (want 0) | 3% | 51% | 0.0% | 758 |
| rust | `k h339 br0.55 sat1.3` | 26° (want 19) | 4% | 53% | 0.0% | 758 |
| bone | `k h354 br0.55 sat1.5` | 44° (want 38) | 7% | 51% | 0.0% | 758 |
| green | `k h99 br0.575 sat1.5` | 136° (want 134) | 10% | 53% | 0.0% | 758 |
| blue | `k h217 br0.525 sat1.5` | 220° (want 222) | 2% | 52% | 0.0% | 758 |
| purple | `k h224 br0.525 sat1.25` | 280° (want 272) | 1% | 52% | 0.0% | 758 |
| crimson | `k h330 br0.525 sat1.5` | 0° (want 357) | 3% | 51% | 0.0% | 758 |

### FX-029 — Rime Bloom

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h330 br0.55 sat1.5` | 2° (want 0) | 5% | 53% | 0.0% | 300 |
| rust | `k h339 br0.55 sat1.2` | 25° (want 19) | 7% | 52% | 0.0% | 300 |
| bone | `k h353 br0.575 sat1.5` | 43° (want 38) | 12% | 52% | 0.0% | 300 |
| green | `k h98 br0.6 sat1.5` | 136° (want 134) | 16% | 52% | 0.0% | 300 |
| blue | `k h217 br0.525 sat1.35` | 216° (want 222) | 3% | 51% | 0.0% | 300 |
| purple | `k h224 br0.525 sat1.3` | 277° (want 272) | 2% | 51% | 0.0% | 300 |
| crimson | `k h329 br0.55 sat1.5` | 357° (want 357) | 5% | 53% | 0.0% | 300 |

### FX-042 — Wide Slash

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h330 br0.525 sat1.5` | 1° (want 0) | 3% | 51% | 0.0% | 542 |
| rust | `k h339 br0.55 sat1.15` | 25° (want 19) | 5% | 53% | 0.0% | 542 |
| bone | `k h353 br0.5 sat1.5` | 43° (want 38) | 8% | 47% | 0.0% | 542 |
| green | `k h98 br0.575 sat1.5` | 135° (want 134) | 11% | 52% | 0.0% | 542 |
| blue | `k h217 br0.525 sat1.25` | 218° (want 222) | 2% | 52% | 0.0% | 542 |
| purple | `k h225 br0.525` | 275° (want 272) | 2% | 52% | 0.0% | 542 |
| crimson | `k h330 br0.525 sat1.5` | 1° (want 357) | 3% | 51% | 0.0% | 542 |

### FX-036 — Cyclone Ring

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h330 br0.625 sat1.5` | 357° (want 0) | 6% | 51% | 0.0% | 500 |
| rust | `k h340 br0.65 sat1.45` | 27° (want 19) | 10% | 51% | 0.0% | 500 |
| bone | `k h354 br0.7 sat1.5` | 43° (want 38) | 17% | 52% | 0.0% | 500 |
| green | `k h98 br0.725 sat1.5` | 137° (want 134) | 22% | 52% | 0.0% | 500 |
| blue | `k h216 br0.625 sat1.45` | 214° (want 222) | 5% | 52% | 0.0% | 500 |
| purple | `k h225 br0.625 sat1.45` | 284° (want 272) | 4% | 52% | 0.0% | 500 |
| crimson | `k h330 br0.625 sat1.5` | 357° (want 357) | 6% | 51% | 0.0% | 500 |

### FX-050 — Void Bloom

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h330 br0.575 sat1.5` | 358° (want 0) | 7% | 51% | 0.0% | 325 |
| rust | `k h340 br0.6 sat1.45` | 26° (want 19) | 11% | 51% | 0.0% | 325 |
| bone | `k h355 br0.65 sat1.5` | 44° (want 38) | 18% | 52% | 0.0% | 325 |
| green | `k h98 br0.675 sat1.5` | 136° (want 134) | 23% | 52% | 0.0% | 325 |
| blue | `k h217 br0.575 sat1.5` | 216° (want 222) | 4% | 52% | 0.0% | 325 |
| purple | `k h225 br0.575 sat1.4` | 283° (want 272) | 4% | 52% | 0.0% | 325 |
| crimson | `k h330 br0.575 sat1.5` | 358° (want 357) | 7% | 51% | 0.0% | 325 |

### FX-008 — Pyre Orb I

| element | token to write | hue | sat | lum | flat | ms |
|---|---|---|---|---|---|---|
| red | `k h330 br0.525 sat1.5` | 0° (want 0) | 3% | 51% | 0.0% | 700 |
| rust | `k h339 br0.55 sat1.3` | 24° (want 19) | 4% | 53% | 0.0% | 700 |
| bone | `k h353 br0.55 sat1.5` | 42° (want 38) | 7% | 52% | 0.0% | 700 |
| green | `k h99 br0.575 sat1.5` | 135° (want 134) | 10% | 53% | 0.0% | 700 |
| blue | `k h217 br0.525 sat1.5` | 225° (want 222) | 2% | 52% | 0.0% | 700 |
| purple | `k h224 br0.525 sat1.3` | 280° (want 272) | 1% | 52% | 0.0% | 700 |
| crimson | `k h330 br0.525 sat1.5` | 0° (want 357) | 3% | 51% | 0.0% | 700 |

## What the grammar cannot reach

84 of 84 pairs miss. By leg: hue 0 · lum 0 · flat 0 · **sat 84**.

**No pair misses hue, lum or flat white.** The whole miss is one leg.

### The saturation actually reached, every pair

Read down a column to see how far an element is from 25%.

| sheet | red | rust | bone | green | blue | purple | crimson |
|---|---|---|---|---|---|---|---|
| FX-051 | 3% | 4% | 7% | 10% | 2% | 1% | 3% |
| FX-034 | 5% | 7% | 9% | 8% | 6% | 6% | 4% |
| FX-038 | 6% | 8% | 15% | 20% | 4% | 3% | 6% |
| FX-032 | 4% | 6% | 10% | 14% | 3% | 2% | 4% |
| FX-045 | 3% | 4% | 7% | 11% | 2% | 2% | 3% |
| FX-044 | 4% | 6% | 10% | 13% | 2% | 2% | 4% |
| FX-043 | 3% | 4% | 7% | 10% | 2% | 1% | 3% |
| FX-029 | 5% | 7% | 12% | 16% | 3% | 2% | 5% |
| FX-042 | 3% | 5% | 8% | 11% | 2% | 2% | 3% |
| FX-036 | 6% | 10% | 17% | 22% | 5% | 4% | 6% |
| FX-050 | 7% | 11% | 18% | 23% | 4% | 4% | 7% |
| FX-008 | 3% | 4% | 7% | 10% | 2% | 1% | 3% |

Per element, mean over the 12 sheets: **purple 2%**, **blue 3%**, **crimson 4%**, **red 4%**, **rust 6%**, **bone 11%**, **green 14%**.
The cool half of the wheel is the worse half: the `k` chain leaves a white pixel a pale
warm yellow, and rotating that to blue or purple crosses the achromatic axis, so there is
almost no chroma left to darken. `purple` and `blue` are the elements a white sheet cannot carry.

**The saturation floor is not a near miss on a few sheets — it is the whole `k` path.**
The measured ceiling per sheet is the HSL saturation the layer keeps once it is dark enough
to satisfy `lum ≤ 55%` (below mid-lightness, HSL saturation stops falling with `br`, so this
is a true ceiling and not an artefact of how far it was darkened):

| sheet | best sat reachable | at | needed |
|---|---|---|---|
| FX-051 | **10%** | `k h99 br0.575 sat1.5` | 25% |
| FX-034 | **9%** | `k h15 br0.975 sat1.5` | 25% |
| FX-038 | **20%** | `k h98 br0.675 sat1.5` | 25% |
| FX-032 | **14%** | `k h98 br0.6 sat1.5` | 25% |
| FX-045 | **11%** | `k h99 br0.575 sat1.5` | 25% |
| FX-044 | **13%** | `k h98 br0.6 sat1.5` | 25% |
| FX-043 | **10%** | `k h99 br0.575 sat1.5` | 25% |
| FX-029 | **16%** | `k h98 br0.6 sat1.5` | 25% |
| FX-042 | **11%** | `k h98 br0.575 sat1.5` | 25% |
| FX-036 | **22%** | `k h98 br0.725 sat1.5` | 25% |
| FX-050 | **23%** | `k h98 br0.675 sat1.5` | 25% |
| FX-008 | **10%** | `k h99 br0.575 sat1.5` | 25% |

The cause is arithmetic, and it is checkable with `--filter-check`: run a literal white pixel
through the `k` chain in a browser and `sepia(1) saturate(2.4) hue-rotate(60deg)` returns
**rgb(224,255,233)** — chroma 0.12 — and with `brightness(0.7)` **rgb(157,178,163)**, which is
HSL saturation **12%**. The second filter table in
`dfmc-client/docs/vfx-pass2-recipes-2026-09-17.md` reports that same filter as rgb(142,178,106),
HSL saturation 32%. The browser does not render that. **The ≥25% leg of the target was set from
a table that overstates the `k` path's chroma by about 3x**, so no token inside `h` 0-359,
`br` 0.5-1.6, `sat` 0-1.5 can meet it on any of the 12 sheets.

What the rows above DO deliver is the other three legs, which are D's words: the hue lands on
the element, the layer is dark, and the flat white is gone. What they do not deliver is a
strongly coloured dark — they read as tinted greys.

### So: are desaturated twins the answer? No.

A twin sheet would not help. The chroma is not lost in the sheet, it is lost in the filter:
`sepia(1)` gives a white pixel only chroma 0.06 and `saturate(2.4)` is too small a multiplier
to open it up. The two cheap fixes both live outside this tool, and both are one number:

1. **raise the multiplier in the `k` branch of `sheetFilter`** (`assets/vfx/vfx_fx.js` and
   the client's own copy in `play/app.js`). Swept over the whole hue circle on a white pixel,
   with `br` taken to whatever puts it at `lum 55%`: `saturate(2.4)` tops out at **14.5%**,
   `saturate(3)` at 18.5%, **`saturate(4)` at 25.8%** — the first value that clears the floor —
   and `saturate(5)` at 33.9%; or
2. **raise the `sat` ceiling in the grammar** (`RANGE` in `tools/fx_lint.py` and in the
   parser). Same sweep, engine left alone: `sat1.5` tops out at **14.5%**, `sat2` at 19.8%,
   **`sat2.5` at 25.6%**, `sat3` at 31.9%. This is the same multiplication, moved from the
   engine to the author — and it keeps the choice per layer.

Either is one number. Both would let the tokens above be re-solved by re-running this tool;
nothing else about the method or the page would change.

Both are engine/grammar changes with their own review, so neither was made here. Until one of
them lands, **the tokens above are the darkest, most coloured, flat-white-free version of each
sheet the shipped grammar can produce** — and they are still a large improvement on the white.
