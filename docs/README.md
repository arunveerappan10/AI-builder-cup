# CatSight — documentation index

Google Cloud AI Builder Cup 2026 · BFSI theme · Team Techno Crackers

---

## Reading order

| # | Doc | Purpose | Status |
|---|---|---|---|
| — | [`../CLAUDE.md`](../CLAUDE.md) | Rules and commands Claude Code follows | ✅ current |
| 1 | [`BUILD_PLAN.md`](BUILD_PLAN.md) | **Start here.** Build order, stage gates, target scenario, risk register | ✅ current |
| 2 | [`REQUIREMENTS.md`](REQUIREMENTS.md) | Base spec v1 — requirement IDs, acceptance criteria, data specs, API contract, agent specs | ⚠️ **not yet in this repo** |
| 3 | [`REQUIREMENTS_V2.md`](REQUIREMENTS_V2.md) | Addendum — verifier, Clause Courtroom, endorsement detective, what-if, judge mode, revised NFRs | ✅ current |
| 4 | [`DOMAIN_PRIMER.md`](DOMAIN_PRIMER.md) | Reinsurance terms and the worked example used as test fixtures | ⚠️ **not yet in this repo** |
| 5 | [`MONEY_MOMENT.md`](MONEY_MOMENT.md) | The demo's climax, derived number by number | ✅ current · **§4 needs domain lead** |
| 6 | [`ARCHITECTURE.md`](ARCHITECTURE.md) | Agent graph, data flows, service topology, trust architecture | ✅ current |
| 7 | [`RESEARCH_FINDINGS.md`](RESEARCH_FINDINGS.md) | Verified facts, API quirks, data-source details | ⚠️ **not yet in this repo** |
| 8 | [`EXECUTION_PLAN.md`](EXECUTION_PLAN.md) | GCP setup commands, cost model, deploy procedure | ⚠️ **not yet in this repo** |
| 9 | [`BUSINESS_IMPACT.md`](BUSINESS_IMPACT.md) | Benchmarks B1–B8 and the impact model | ⚠️ **not yet in this repo** |
| — | [`SETUP.md`](SETUP.md) | How the infrastructure was built (owner reference) | ⚠️ **not yet in this repo** |
| — | [`GETTING_STARTED.md`](GETTING_STARTED.md) | Phase prompts and team roles | ⚠️ **not yet in this repo** |

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

## ⚠️ Base pack still to be brought across

Six documents are referenced throughout but are **not yet in this repo**: `REQUIREMENTS.md`, `DOMAIN_PRIMER.md`, `RESEARCH_FINDINGS.md`, `EXECUTION_PLAN.md`, `BUSINESS_IMPACT.md`, `SETUP.md`, `GETTING_STARTED.md`.

They exist in the team repo (`venketraj/catsight-ai-buildercup-2026`) and should be **copied, not rewritten** — they hold verified research, cited sources, the hand-checked worked example that the engine's tests depend on, and the domain lead's review. Regenerating them would lose fidelity on exactly the content that is hardest to recover.

```bash
# from a clone of the team repo, into this repo
cp <team-repo>/docs/REQUIREMENTS.md      docs/
cp <team-repo>/docs/DOMAIN_PRIMER.md     docs/
cp <team-repo>/docs/RESEARCH_FINDINGS.md docs/
cp <team-repo>/docs/EXECUTION_PLAN.md    docs/
cp <team-repo>/docs/BUSINESS_IMPACT.md   docs/
cp <team-repo>/docs/SETUP.md             docs/
cp <team-repo>/docs/GETTING_STARTED.md   docs/
```

**S2 (the engine) depends on `DOMAIN_PRIMER.md`'s worked example** for its test fixtures — the reference figures are reproduced in `MONEY_MOMENT.md` §3, but the primer is the source of truth and the domain lead's sign-off target.

---

## Notes on this repo

- **Code lives here:** `github.com/arunveerappan10/AI-builder-cup`
- **GCP project** remains `techno-crackers-catsight`, owned by the project owner. Deploy targets, bucket names, the service account and the live URL in `EXECUTION_PLAN.md` and `SETUP.md` are unchanged — confirm with the owner that deploys from this repo are expected.
- **Do not commit** the planning PDFs (`CatSight_AI_Builder_Cup_Win_Analysis.pdf`, `CatSight_Developer_Onboarding_Guide.pdf`). The win analysis is the team's competitive strategy and this repo goes public at submission.
