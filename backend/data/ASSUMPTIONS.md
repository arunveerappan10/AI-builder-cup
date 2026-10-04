# Modelling assumptions

Every assumption the engine makes, with its source and how it gets validated.
CLAUDE.md requires this file to be updated as part of the change that
introduces an assumption, not afterwards.

The UI's Methodology page (UI-9) renders from this file. Nothing here is a
result; results live in `benchmarks/results/RESULTS.md`.

**Status key** — `SOURCED` published figure, cited · `DERIVED` follows from a
sourced figure or from the spec's own arithmetic · `JUDGEMENT` our choice,
defensible but ours · `UNVERIFIED` placeholder pending validation.

---

## 1. Money and arithmetic

| # | Assumption | Status | Notes |
|---|---|---|---|
| M1 | Money is `Decimal`, not float, quantised to 6 dp | DERIVED | Binary float evaluates the split case's `7.85 - 0.525` as 7.324999999999999, which rounds to 7.32 rather than the correct 7.33. FR-LOSS acceptance requires exact matches, so float is unusable. Asserted by `test_float_arithmetic_loses_the_split_cases_tie`. |
| M2 | Money rounds **half away from zero** | JUDGEMENT | The financial convention. Python's built-in `round` is banker's rounding, which sends a true 7.325 down to 7.32. |
| M3 | Portfolio currency is USD; FX is fixed and configurable | JUDGEMENT | `JPY_PER_USD=150`, `PHP_PER_USD=56`, `TWD_PER_USD=32`. Fixed rather than dated, because the portfolio is synthetic and a moving rate would add noise without adding realism. |
| M4 | Figures are in USD millions throughout the worked example | DERIVED | From `DOMAIN_PRIMER.md` section 4. |

## 2. Reinstatements and reinstatement premium (FR-LOSS-3)

| # | Assumption | Status | Notes |
|---|---|---|---|
| R1 | `RIP = (limit eroded by that occurrence / limit) x premium x rate`, **per occurrence**, pro rata as to amount, while reinstatement capacity remains | DERIVED | Derived in `docs/MONEY_MOMENT.md` section 4.1 by working backwards from the one-event figures the primer already publishes (our RIP 0.622, net 6.82). It is the only basis that reproduces them. |
| R2 | Reinstatement applies to **partial** erosion, not only to exhaustion | DERIVED | L2 is eroded 81.33% in the one-event case and still attracts RIP of 1.22 in the primer. An exhaustion-only rule would give zero. |
| R3 | Erosion beyond available reinstatement capacity is **paid** (if aggregate cover allows) but attracts **no** RIP | JUDGEMENT | Nothing is restored, so no reinstatement premium is due. This is what makes the split case's L1 RIP 2.00 rather than 2.94. |
| R4 | Aggregate cover per layer is `limit x (1 + reinstatements)` | JUDGEMENT | Standard. Exceeding it is an error, not a silent overrun. |
| R5 | RIP is due in the one-event case even though L1 is never drawn on again | JUDGEMENT | The primer charges it, which is consistent with automatic reinstatement on loss. Some wordings do not. Flagged for a practitioner in `MONEY_MOMENT.md` section 4.5 — it changes no figure in the demo, because both readings there have subsequent exposure. |

**Explicitly rejected**, with reasons in `MONEY_MOMENT.md` section 4.3:
RIP on *aggregate* ceded (charges 1.47 reinstatements where one exists) and RIP
sized by what the *following* occurrence draws (sizes the reinstatement by the
wrong occurrence).

## 3. Occurrence splitting (FR-LOSS-5)

| # | Assumption | Status | Notes |
|---|---|---|---|
| O1 | A window opens at the first loss not yet assigned and runs for the clause's hours | JUDGEMENT | Standard wording lets the cedent elect the start but not before the first recorded loss. |
| O2 | A loss belongs to the window in which it **first occurs** | SOURCED | *UnipolSai v Covéa* (English Court of Appeal, 2024): "occur" means "first occur". |
| O3 | Windows may not overlap | SOURCED | Standard Cat XL wording. Falls out of O1 structurally. |
| O4 | Each occurrence carries its own retention | SOURCED | `DOMAIN_PRIMER.md` section 5a. |
| O5 | The 54.4 → 35.0 + 19.4 split is illustrative | JUDGEMENT | Taken from the primer as an example. In production the split derives from the event's loss timeline; whether a cedent would elect *this* placement is a judgement call flagged in `MONEY_MOMENT.md` section 4.5. |

## 4. Hazard — wind (DR-4)

| # | Assumption | Status | Notes |
|---|---|---|---|
| W1 | Intensity at a centroid is the **maximum** over all track points | JUDGEMENT | Per DR-4. A region brushed early and struck later takes the worse of the two. |
| W2 | Radial profile is piecewise linear through RMW, R64, R50, R34, then zero | JUDGEMENT | Per DR-4. A crude but transparent substitute for a parametric wind field. |
| W3 | Quadrant radii are averaged over **reported quadrants only** | JUDGEMENT | IBTrACS writes 0 for "not reported"; averaging those in would shrink the storm. |
| W4 | Anchors whose speed is at or above the point's `vmax`, or whose radius is inside RMW, are **discarded** | JUDGEMENT | A decaying storm can report an R64 while its vmax has fallen below 64 kt. Keeping that anchor would make wind *rise* with distance. |
| W5 | A point with no usable outer radius contributes `vmax` inside RMW and zero beyond | JUDGEMENT | Conservative: the observation simply says nothing about the outer field. |
| W6 | Knots convert at 0.514444 m/s | SOURCED | Exact definition. |
| W7 | Distances are great-circle (haversine) on a sphere of radius 6371.0088 km | JUDGEMENT | IUGG mean radius. Ellipsoidal distance is unnecessary at this resolution. |
| W8 | Region geometry is reduced to a single **centroid** | JUDGEMENT | Per DR-4. Material simplification: a large prefecture is represented by one point, so a storm clipping its edge is under- or over-counted. Listed as a limitation in the README. |

## 5. Hazard — earthquake (DR-4)

| # | Assumption | Status | Notes |
|---|---|---|---|
| E1 | MMI at a centroid is the **nearest** ShakeMap grid cell | JUDGEMENT | Per DR-4. No interpolation between cells. |
| E2 | The MMI column is located by its `grid_field` declaration, not by position | DERIVED | ShakeMap products vary in field count and order; MMI sits behind PGA in the Noto product. Assuming column 3 would read PGA as intensity. |

## 6. Vulnerability — wind (DR-5)

| # | Assumption | Status | Notes |
|---|---|---|---|
| V1 | Emanuel (2011) sigmoid: `f = vn³/(1+vn³)`, `vn = max(V - 25.7, 0)/(V_half - 25.7)` | SOURCED | V in m/s, 1-minute sustained. |
| V2 | `V_half` = 190.5 m/s (JPN, TWN), 76.0 m/s (PHL) | SOURCED | Eberenz et al. 2021, CC BY 4.0. The single biggest driver of the PH/JP loss difference. |
| V3 | Per-country `calibration_factor`, default 1.0 | UNVERIFIED | Tuned in benchmark B5 and reported there. Until B5 runs, all factors are 1.0. |
| V4 | A damage ratio is capped at 1.0 after calibration | JUDGEMENT | A calibration factor must not produce a loss above the sum insured. |

## 7. Vulnerability — earthquake (DR-5)

| # | Assumption | Status | Notes |
|---|---|---|---|
| Q1 | MMI → mean damage ratio: 5 → 0, 6 → 0.5%, 7 → 2%, 8 → 6%, 9 → 15%, ≥10 → 30% | UNVERIFIED | **Illustrative.** Informed by Hazus damage-state repair ratios but not taken from them directly. `REQUIREMENTS.md` section 14.2 flags this. Must be labelled illustrative wherever displayed. |
| Q2 | Values are **interpolated linearly** between integer MMI anchors | JUDGEMENT | ShakeMap reports fractional MMI (6.7, not 7). At integer MMI the interpolated value equals the spec table exactly, so this refines the table rather than departing from it. Switchable via `interpolate: false`. |
| Q3 | Country factor 0.5 for JPN, 1.0 for TWN and PHL | UNVERIFIED | Reflects Japanese seismic building standards. Calibrated in B5. |

## 8. IBTrACS parsing (DR-3)

| # | Assumption | Status | Notes |
|---|---|---|---|
| I1 | Row 2 is a **units row** and is skipped | SOURCED | IBTrACS v04r01 format. Detected by content (unparseable `ISO_TIME`) rather than by position alone, so a file without one still parses. |
| I2 | Storms are selected by **SID**, never by NAME | SOURCED | Names repeat across basins and seasons. |
| I3 | `USA_WIND` (1-minute, kt) is preferred | SOURCED | Matches the 1-minute basis Emanuel's function expects. |
| I4 | Where `USA_WIND` is absent, `TOKYO_WIND` (10-minute) x **1.12** | JUDGEMENT | 10-minute → 1-minute conversion. A commonly used factor, but a choice; it affects JMA-only track segments. |
| I5 | Missing values are blanks, bare spaces, `NA`, `NaN`, `-999` or `-9999` — never 0 | SOURCED | A 0 radius means "reported as zero", which differs from "not reported". |
| I6 | Radii are nautical miles, converted at 1.852 km | SOURCED | Exact definition. |
| I7 | Track points with no wind reading at all are **dropped** | JUDGEMENT | The point cannot contribute to a wind field. |
| I8 | Track points with no position are **dropped** | JUDGEMENT | As above. |

## 9. Synthetic portfolio (DR-1)

| # | Assumption | Status | Notes |
|---|---|---|---|
| X1 | Region exposure weights are **approximate resident populations**, not GIROJ sums insured or e-Stat dwelling counts | JUDGEMENT | DR-1 asks for the latter two; we do not hold those datasets. Populations are public general knowledge and give a plausible distribution. The portfolio is synthetic by rule (C-8), so nothing downstream claims these are real exposure. Replacing them is a one-table change. **Benchmark B5 must not be run on these weights** — it uses a market-level proxy, which is a separate input. |
| X2 | All **22** ISO 3166-2:TW entries are carried | DERIVED | DR-1 says "21 counties/cities"; ISO lists 22. Carrying all 22 rather than dropping one to hit a number. |
| X3 | `TSI_PER_WEIGHT_USD_M = 15,000` | JUDGEMENT | Makes the synthetic Japanese market about **US$18.7tn** of sum insured — the right order for Japan, whose real insured value is order US$20–30tn — and puts Sakura at 14% share on about US$2.6tn. A round number chosen for that realism. |
| X4 | Market shares are **explicit per cedent**, not drawn from the seed | JUDGEMENT | A cedent's size is structural. If it moved with the seed, the demo's headline figures would move with it. Sakura is pinned at 14%. |
| X5 | The modelled Jebi gross loss for Sakura lands at **54.45** against the worked example's 54.40 | DERIVED | Falls out of X3 and X4 rather than being fitted. It is what lets the live demo reproduce the documented figures, and it is asserted by `test_the_jebi_replay_reproduces_the_worked_example_gross`. If `build_events.py`'s real IBTrACS track moves it, re-derive X3 once rather than loosening the test. |
| X6 | **The model under-predicts Jebi's actual market loss by roughly 25x** | UNVERIFIED | Jebi's paid claims were about ¥1,068bn (~US$9.5bn). The curve gives a market-wide damage ratio of ~0.00024 against a reality of ~0.0003–0.0005 — so the curve is roughly right at market level, but the modelled footprint only reaches 16 regions at low ratios, while real losses were broader and driven partly by flood and surge the model does not carry. **This is a B5 finding to report honestly, not something to tune away in the portfolio.** The lever is `calibration_factor` (V3), and it stays at 1.0 until B5 derives it. |
| X7 | Programmes are sized against a **reference major-event loss**, not against sum insured | JUDGEMENT | DR-1 asks for retentions "plausible relative to TSI", but a Cat XL is bought against a return-period loss. Sakura retains 10.0 of a 54.4 event — 18.4% of the event, and 0.0004% of its TSI, which is entirely normal for a cat cover. Every filler programme attaches in the same 15–35% band, so the book is internally coherent. |
| X8 | Each cedent's reference loss scales linearly with its sum insured from Sakura's | JUDGEMENT | Ignores that a Philippine book is far more wind-vulnerable than a Japanese one at the same wind speed. It only has to make the filler book's structure sensible, and it keeps the generator free of any dependency on the vulnerability curves. |
| X9 | Philippine earthquake penetration is **25%** of wind | JUDGEMENT | Reflects thin EQ take-up. Illustrative. |
| X10 | Region **centroids** are approximate, to about a tenth of a degree | JUDGEMENT | Committed so the hazard chain is testable and the demo runs without the ~40 MB Natural Earth download. `build_regions.py` recomputes them from Natural Earth 10m admin-1 polygons; a recomputed centroid more than ~50 km away is a reconciliation failure worth investigating. |

## 10. Data sources and licences (DR-6)

| Source | Use | Licence |
|---|---|---|
| NOAA **IBTrACS** v04r01 WP | Typhoon tracks | Cite Knapp et al. 2010, doi:10.25921/82ty-9e16 |
| **USGS** ShakeMap | Earthquake MMI | Public domain — credit U.S. Geological Survey |
| **Natural Earth** 10m admin-1 | Region geometry and centroids | Public domain |
| **JMA** | Event facts | "Source: Japan Meteorological Agency website" |
| **e-Stat** | Dwelling counts for exposure calibration | 出典：政府統計の総合窓口(e-Stat) |
| **GIROJ / GIAJ / JER** | Calibration and B5 back-test references | Cited only, not redistributed |
| **Eberenz et al. 2021** | Wind `V_half` by country | CC BY 4.0 |
| SEC EDGAR contracts | Style reference for wordings only — paraphrased, never copied | — |

Portfolio, cedents and treaty wordings are **entirely synthetic**. Events are
real, and the referenced market losses are real; those are used for
credibility and the B5 back-test only, **never as model inputs**.

## 11. Outstanding — to validate, not blocking

1. `calibration_factor` (V3) and the EQ country factors (Q3) are 1.0 / 0.5 placeholders until B5 runs. Calibrate on one event, test on the other, and report misses honestly.
2. The EQ MMI table (Q1) should be checked against published Hazus repair ratios before it is cited as anything but illustrative.
3. The 10-minute to 1-minute wind factor (I4) deserves a source rather than convention.
4. Centroid representation (W8) is the largest structural simplification in the hazard chain. Quantify its effect on at least one event before claiming regional accuracy.
5. Baseline manual-effort figures are hypotheses until the B1 run.
6. The portfolio exposure weights (X1) should be rebuilt on GIROJ and e-Stat figures before any claim about regional accuracy is made.
7. X6 is the single most important honest disclosure in the proof pack: report the under-prediction and the calibration separately.
