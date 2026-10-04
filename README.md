# CatSight

**Event-aware contract intelligence for catastrophe reinsurance.**

> When a typhoon hits, CatSight tells a reinsurer within minutes what it is likely to pay, which contract clauses change that number, and exactly where each clause says so — so disaster-hit insurers get funded faster and with fewer disputes.

Google Cloud AI Builder Cup 2026 · BFSI: Intelligent Risk, Fraud & Financial Experiences · Team Techno Crackers

---

> **🚧 Pre-build.** This repo currently contains the specification and plan. No application code yet — see [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md) for the stage order and gates.
>
> This README will be rewritten to the judge-facing `FR-DOC` specification at stage S9, with measured benchmark results, the architecture diagram and data licences.

---

## What it does

When a catastrophe strikes, CatSight replays the hazard over a reinsurer's portfolio and produces a cited flash report:

1. **Which treaties respond** — peril, territory and period matching across the portfolio
2. **What each layer pays** — gross loss, per-layer ceded, burn, exhaustion, reinstatements, our share
3. **Which clauses change that answer** — hours clauses, exclusions, territorial carve-outs, reinstatement limits, and endorsements that override the base wording
4. **Where each clause says so** — treaty, page and clause, with the quote machine-verified against the source page

Where a clause genuinely reads two ways, two agents argue the opposing readings from verified text and the deterministic engine prices both — because a clause that moves recoveries by 22% is the whole point.

## The design decision that matters

**The language model never does arithmetic.**

Every loss figure comes from deterministic, unit-tested Python with full branch coverage, validated against a hand-checked worked example. Gemini reads heterogeneous and sometimes scanned wordings, decides whether this event's timeline, perils and geography fall inside each clause, argues ambiguous readings, and writes the narrative — all with machine-checked citations. Anything it cannot verify is withheld and counted, not quietly dropped. A human approves before anything leaves.

## Architecture

Google ADK 2.x graph on Cloud Run — a linear spine, a **verification loop**, and a **parallel adversarial fan-out**:

```
event_intel → exposure_analyst → wording_checker → [verifier LOOP]
                                                        │
                                   ┌─ cedent_counsel ───┤  parallel,
                                   └─ reinsurer_counsel ─┤  blind to each other
                                                        ▼
                                                     arbiter → reporter
```

Gemini 3.5 Flash-Lite and 3.8 Flash on Agent Platform · `gemini-embedding-001` at 768 dims · Firestore vector search · Cloud Run with SSE streaming · Firebase Hosting · Cloud Storage · Secret Manager · Cloud Trace

Full detail in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Documentation

Start with [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md). Full index in [`docs/README.md`](docs/README.md).

| | |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Rules and commands for the build |
| [`docs/BUILD_PLAN.md`](docs/BUILD_PLAN.md) | Stage order, gates, target, risk register |
| [`docs/REQUIREMENTS_V2.md`](docs/REQUIREMENTS_V2.md) | Verifier, Courtroom, endorsement detective, what-if, judge mode |
| [`docs/MONEY_MOMENT.md`](docs/MONEY_MOMENT.md) | The demo's climax, derived number by number |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Agent graph, data flows, trust architecture |

## Status

| Stage | | |
|---|---|---|
| S0 | Bootstrap — live URL serving `/healthz` | ⬜ |
| S1 | Data — events, portfolio, wordings, ground truth, blind set | ⬜ |
| S2 | Core engine — loss maths, hazard *(hard gate)* | ⬜ |
| S3 | Ingestion and retrieval | ⬜ |
| S4 | Agents, API and verifier | ⬜ |
| S5 | UI demo path *(demo-path lock)* | ⬜ |
| S6 | Clause Courtroom, endorsement detective, what-if | ⬜ |
| S7 | Judge-proofing and quality | ⬜ |
| S8 | Proof pack | ⬜ |
| S9 | Story and deliverables | ⬜ |

## Data

Portfolio, cedents and treaty wordings are **entirely synthetic** — fictional companies, wordings paraphrased in the style of publicly filed contracts. Hazard data is public: NOAA IBTrACS v04r01 (cite Knapp et al. 2010, doi:10.25921/82ty-9e16), USGS ShakeMap (public domain), Natural Earth (public domain). Full attribution in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) §9.

No real employer, client or broker data is used anywhere in this project.

## Licence

Apache-2.0 `<!-- PENDING: add LICENSE file at S0 -->`

---

*Indicative first view on synthetic data. Not a catastrophe-model output. Not underwriting or claims advice. Issue-spotting only — not legal advice.*

*Jebi, Hagibis, Haiyan and Noto were real events in which people died. This project treats them as such.*
