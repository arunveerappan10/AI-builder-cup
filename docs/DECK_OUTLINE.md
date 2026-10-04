# CatSight — Deck outline

> 12 slides, exported to **PDF**. A human builds the slides (Google Slides or PowerPoint, Hack2skill template if provided); this document is the content source.
>
> **Every number comes from `benchmarks/results/RESULTS.md`.** `[PENDING]` markers must be resolved before export — a slide with an invented number is worse than a slide without one.
>
> Design: clean financial-services tone. Colour-blind-safe palette, consistent with the product. One architecture diagram, reused everywhere.

---

## Slide 1 · Title and the one-sentence pitch

**CatSight** — *event-aware contract intelligence for catastrophe reinsurance*

> "When a typhoon hits, CatSight tells a reinsurer within minutes what it is likely to pay, which contract clauses change that number, and exactly where each clause says so — so disaster-hit insurers get funded faster and with fewer disputes."

Team Techno Crackers · BFSI: Intelligent Risk, Fraud & Financial Experiences · live URL · repo · video

---

## Slide 2 · The morning after a typhoon

The persona, not the product. A catastrophe analyst at a mid-size reinsurer, the morning after landfall, with a CFO who needs a defensible number by noon.

- Early market estimates for Jebi: ~$2.3–5.5bn within days → ~$15bn a year later
- S&P called it a reminder of how uncertain early loss estimates are
- Overlapping Trami claims weeks later were a major driver

**Takeaway:** the first number matters, it is hard, and it moves.

---

## Slide 3 · Why it is hard today

The six-step workflow, and where the time goes:

| Step | Today | Pain |
|---|---|---|
| Event intelligence | Licensed modeller feeds | Expensive; describes the market, not your contracts |
| Exposure overlay | Cat modelling / exposure tools | Specialist time, batch runs under pressure |
| Contract application | Analysts in spreadsheets | Error-prone when rushed |
| **Wording check** | Underwriting, claims and legal re-read PDFs | **Slow; endorsements get missed; disputes surface months later** |
| Reporting | Flash estimates to board, rating agencies | Must be fast *and* defensible |

Context: 48% of insurers don't license cat models; ~60% have cat teams of five or fewer. Treaty structures often "only exist in a spreadsheet."

---

## Slide 4 · What exists vs what is new — M5

**The differentiation statement. This slide exists because judges who know the market will otherwise assume a re-implementation.**

| Category | Examples | What they do well | Where they stop |
|---|---|---|---|
| Cat-model event response | Moody's RMS, Verisk (+ MIS) | Hazard footprints, near-real-time intelligence, portfolio overlays | At the hazard and the modelled loss — not *your* treaty wording |
| AI treaty-wording review | Nomad Doc Chat, V7 Go, custom builds | Clause extraction, page-level citations | Static documents — not driven by an event's timeline and footprint, not tied to layer maths |
| Generic LLM over PDFs | Chat with uploaded contracts | Fast answers | Numbers unverifiable, no deterministic maths, no audit trail |
| **CatSight** | — | **event × exposure × layers × wording** | **The join is the product** |

> "To our knowledge, event-response products stop at the hazard and the modelled loss, and AI wording tools stop at the document. CatSight is the join."

**Say "to our knowledge." Position as complementary** — CatSight can consume a vendor footprint instead of IBTrACS or ShakeMap.

*Honest framing: reading treaties with AI, overlaying a storm, and computing layer losses are each established. What is new is event-specific clause applicability — time windows, peril definitions, territory, endorsements — fused with deterministic layer maths, and the money at stake when a clause reads two ways.*

---

## Slide 5 · CatSight in one picture

The architecture diagram from `docs/ARCHITECTURE.md` §1. Nothing else on the slide.

---

## Slide 6 · The product

Three or four real screenshots: the streaming agent timeline, the choropleth map with the layer chart, a verified wording flag with the citation panel open on the treaty page.

Caption: **"Gemini reads. Tested code calculates."**

---

## Slide 7 · The money moment — one clause, one number

**The slide the deck is built around.** Figures from `docs/MONEY_MOMENT.md` §3, confirmed against a real run.

The hours clause — the definition of "one event":

| | One event | Two events | Move |
|---|---|---|---|
| Total ceded | $44.4M | $34.4M | **−$10.0M · −22.5%** |
| Cedent retention | $10.0M | $20.0M | doubles |
| Our net | $6.82M | [PENDING §4.1] | **worse under the split** |

Then the reveal: **our share is concentrated in Layer 1, so the reading that saves the treaty $10M costs us more.** The cedent argues one event. We argue two. We are not arguing about the same pot.

Evidence that the question is real: *UnipolSai v Covéa* (English Court of Appeal, 2024) turned on how a 168-hour clause works.

*Labelled: issue-spotting, not legal advice.*

---

## Slide 8 · Trust architecture

Why a finance team can let an LLM near a loss report:

- **The LLM never calculates.** Every number from tested deterministic Python, full branch coverage.
- **Every wording claim is cited** — treaty, page, clause.
- **Every citation is machine-verified** — normalised quote-match, then a semantic check; one retry, then abstain.
- **Unverifiable claims are withheld, visibly** — `"n of n verified · k withheld"` in the report header.
- **Grounded web search touches event context only** — never a number, never a flag.
- **A human approves** before anything leaves.
- **Synthetic contracts, fictional cedents, public hazard data with attribution.**

---

## Slide 9 · Results — the proof pack

| Metric | Result | Method |
|---|---|---|
| Time to a defensible first estimate | [PENDING B1 vs B2] | Manual run, stopwatch, screen-recorded, vs CatSight |
| Loss-maths correctness | [PENDING QA-1] | Worked example, exact match on every reference figure |
| Extraction accuracy | [PENDING B3] | 8 wordings vs ground truth |
| **Extraction, blind set** | **[PENDING B3-blind]** | **3 wordings authored outside the build team** |
| Flag recall / precision | [PENDING B4] | Planted features + decoys |
| Citation verification | [PENDING]% displayed · [PENDING] withheld | Verifier counts |
| Latency p50 / p95 | [PENDING B2] | Live URL, 5 runs × 4 events |
| Cost per analysis | [PENDING B6] | Token logs × list price |
| Back-test vs actuals | [PENDING B5] | Market-level proxy vs GIAJ / JER, calibrate on one event, test on the other |
| Usability (SUS) | [PENDING B8] (n=5) | System Usability Scale |

**Report the blind-set number next to the tuned number, including if it is worse.** Report known misses.

---

## Slide 10 · Google Cloud architecture

The same diagram, annotated by service:

Gemini 3.5 Flash-Lite and 3.8 Flash on Agent Platform (global) · **ADK 2.x graph Workflow — verification loop + parallel fan-out** · Firestore vector search, `gemini-embedding-001` at 768 dims · Cloud Run with SSE streaming · Firebase Hosting · Cloud Storage · Secret Manager · Cloud Trace · Cloud Build

Call out the two things that are not generic: **the verifier loop** and **the adversarial fan-out/fan-in**. Those are the ADK features a rules engine cannot replicate.

---

## Slide 11 · Impact and scale

**Who pays, who benefits.** Reinsurance recoveries are what let primary insurers pay households and small businesses at scale after a disaster. Faster, less-disputed recoveries mean faster claim payments.

- Global insured nat-cat losses ≈ $107bn in 2025, against ≈ $220bn economic
- Asia carried ≈ 30% of global economic catastrophe losses but only ≈ 5% of insured losses — only ~8% of its ≈ $65bn 2025 losses were insured
- The global protection gap reached $424bn
- Public risk pools such as SEADRIF (eight participating countries including Japan, the Philippines and Singapore) administer exactly this kind of cover

**Do not overclaim: CatSight is decision support, not a payout engine.**

**Scale:** stateless Cloud Run, scale-to-zero, Firestore serverless. Roadmap — real treaty-pack ingestion, multi-tenancy, Pub/Sub triggers from public alerts, vendor footprint feeds, A2A/MCP so a broker's agent can call CatSight as a tool, loss-development tracking as advices arrive.

---

## Slide 12 · Team, ask, next steps

Team Techno Crackers — the domain lead (reinsurance), the lead builder, the proof-and-story owner.

**Next steps:** pilot on an anonymised treaty pack · pre-landfall mode on forecast tracks · public risk-pool mode with parametric triggers.

Live URL · repo · video · *Indicative first view on synthetic data. Not a catastrophe-model output. Not underwriting or claims advice.*

---

## Rubric mapping

Include as an appendix slide or in the README. Judges should not have to hunt.

| Criterion | Weight | Where it is evidenced |
|---|---|---|
| **Technical Merit & Gen AI** | 40% | Slides 5, 8, 10 — ADK graph with a verification loop and adversarial fan-out; deterministic engine with full branch coverage; machine-verified citations; `adk eval`; Cloud Trace; cost caps |
| **Problem Alignment & Impact** | 25% | Slides 2, 3, 9, 11 — direct BFSI theme fit (intelligent risk + automating a complex process); measured time saving; protection-gap bridge |
| **Innovation & Creativity** | 25% | Slides 4, 7 — the event × exposure × layers × wording join; the Clause Courtroom; the endorsement detective |
| **UX & Solution Design** | 10% | Slide 6 — one-click demo, streaming stages, citation panel, glossary, guided tour, WCAG AA, colour-blind-safe palette |

---

## Build checklist

- [ ] Every `[PENDING]` resolved from `RESULTS.md` — **no invented numbers**
- [ ] `MONEY_MOMENT.md` §4 signed off before slide 7 is final
- [ ] Screenshots from the **live URL**, no localhost chrome
- [ ] Fictional names only, web-checked
- [ ] Disclaimer on slides 7, 9 and 12
- [ ] Exported to PDF and attached to the submission
- [ ] Readable at thumbnail size — judges skim first
