# CatSight — documentation index

Google Cloud AI Builder Cup 2026 · BFSI theme · Team Techno Crackers

---

## Reading order

| # | Doc | Purpose | Status |
|---|---|---|---|
| — | [`../CLAUDE.md`](../CLAUDE.md) | Rules and commands Claude Code follows | ✅ current |
| 1 | [`BUILD_PLAN.md`](BUILD_PLAN.md) | **Start here.** Build order, stage gates, target scenario, risk register | ✅ current |
| 2 | [`REQUIREMENTS.md`](REQUIREMENTS.md) | Base spec v1 — requirement IDs, acceptance criteria, data specs, API contract, agent specs | ✅ base pack |
| 3 | [`REQUIREMENTS_V2.md`](REQUIREMENTS_V2.md) | Addendum — verifier, Clause Courtroom, endorsement detective, what-if, judge mode, revised NFRs | ✅ current |
| 4 | [`DOMAIN_PRIMER.md`](DOMAIN_PRIMER.md) | Reinsurance terms and the worked example used as test fixtures | ✅ base pack |
| 5 | [`MONEY_MOMENT.md`](MONEY_MOMENT.md) | The demo's climax, derived number by number | ✅ current · §4 resolved |
| 6 | [`ARCHITECTURE.md`](ARCHITECTURE.md) | Agent graph, data flows, service topology, trust architecture | ✅ current |
| 7 | [`RESEARCH_FINDINGS.md`](RESEARCH_FINDINGS.md) | Verified facts, API quirks, data-source details | ✅ base pack |
| 8 | [`EXECUTION_PLAN.md`](EXECUTION_PLAN.md) | GCP setup commands, cost model, deploy procedure | ✅ base pack |
| 9 | [`BUSINESS_IMPACT.md`](BUSINESS_IMPACT.md) | Benchmarks B1–B8 and the impact model | ✅ base pack |
| — | [`SETUP.md`](SETUP.md) | How the infrastructure was built (owner reference) | ✅ base pack |
| — | [`GETTING_STARTED.md`](GETTING_STARTED.md) | Phase prompts and team roles | ✅ base pack · superseded by `BUILD_PLAN.md` for ordering |

### Deliverables (S9)

| Doc | Purpose | Status |
|---|---|---|
| [`DECK_OUTLINE.md`](DECK_OUTLINE.md) | 12-slide content source for the deck PDF | ✅ drafted · `[PENDING]` numbers |
| [`VIDEO_SCRIPT.md`](VIDEO_SCRIPT.md) | 2:45 beat sheet and voice-over | ✅ drafted · `[PENDING]` numbers |
| [`SUBMISSION_ANSWERS.md`](SUBMISSION_ANSWERS.md) | Form answers, judge Q&A, LinkedIn draft | ✅ drafted · `[PENDING]` numbers |
| `demo/` | Backup screenshots and a full-run screen recording | ⬜ S9 |

---

## Precedence

When documents disagree:

```
REQUIREMENTS_V2.md  >  REQUIREMENTS.md  >  everything else
```

`BUILD_PLAN.md` governs **order**, not content.

---

## Base pack provenance

Seven documents — `REQUIREMENTS.md`, `DOMAIN_PRIMER.md`, `RESEARCH_FINDINGS.md`, `EXECUTION_PLAN.md`, `BUSINESS_IMPACT.md`, `SETUP.md`, `GETTING_STARTED.md` — originate in the team repo (`venketraj/catsight-ai-buildercup-2026`) and were copied here **unmodified**.

They were copied rather than rewritten deliberately: they hold verified research with cited sources, the hand-checked worked example the engine's tests depend on, and the domain lead's review. Regenerating them would lose fidelity on exactly the content that is hardest to recover.

**All deltas live in `REQUIREMENTS_V2.md`**, so the base pack stays diffable against the team's version. Do not edit the seven in place — add to the addendum instead.

**S2 (the engine) depends on `DOMAIN_PRIMER.md`'s worked example** for its test fixtures. The primer is the source of truth for the one-event figures; `MONEY_MOMENT.md` §3–4 extends them to the two-occurrence split and derives the reinstatement-premium convention from them. QA-1 asserts both.

---

## Notes on this repo

- **Code lives here:** `github.com/arunveerappan10/AI-builder-cup`
- **GCP project** remains `techno-crackers-catsight`, owned by the project owner. Deploy targets, bucket names, the service account and the live URL in `EXECUTION_PLAN.md` and `SETUP.md` are unchanged — confirm with the owner that deploys from this repo are expected.
- **Do not commit** the planning PDFs (`CatSight_AI_Builder_Cup_Win_Analysis.pdf`, `CatSight_Developer_Onboarding_Guide.pdf`). The win analysis is the team's competitive strategy and this repo goes public at submission.
