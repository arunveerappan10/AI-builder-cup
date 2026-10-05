# CatSight — build status

**As of 2026-10-06.** Branch `s2-engine` at `ea79a4b`, everything pushed.

This is a hand-off inventory: what exists, what it does, what is measured, and
what is left. It is deliberately not a pitch — where something is weaker than
it looks, that is said here rather than discovered later.

---

## 1. The one-paragraph version

The **engine, the data and the API are done and verified**; the **agent layer
does not exist yet**. You can run a complete analysis today — event, treaties
matched, layers burnt, three-party money position — on a deterministic loss
engine with no model involved, and check every number by hand. What is missing
is everything a language model contributes: clause-level wording flags, the
citation verifier's semantic half, and the Clause Courtroom. Nothing is
deployed, so there is no live URL.

| | |
|---|---|
| Backend source | **7,855 lines** across 18 modules |
| Tests | **6,828 lines**, 559 test functions → **670 cases** (parametrised) |
| Coverage | **100% statement and branch**, all 23 measured modules |
| Frontend | **1,278 lines**, typechecks clean, builds |
| Docs | 18 files |
| Deployed | **nothing** |

---

## 2. Run it right now

Nothing here costs money and nothing needs cloud access.

```bash
# Backend (Python 3.12)
cd backend
.venv/Scripts/python.exe -m pytest -q              # 670 tests
.venv/Scripts/python.exe -m uvicorn app.main:app --port 8080

# Frontend, separate terminal
cd frontend && npm install && npm run dev          # http://localhost:5173

# Or build it and let the API serve it on one origin
npm run build && cp -r dist ../backend/static
cd ../backend && STATIC_DIR=static python -m uvicorn app.main:app --port 8080

# Verify
./scripts/smoke_test.sh http://localhost:8080      # expect PASS 14  FAIL 0
```

Press **Run demo** and you get Typhoon Jebi 2018 priced against the current
book.

---

## 3. What the code contains

### 3.1 Core engine — complete, the project's foundation

| Module | Lines | What it does |
|---|---:|---|
| `tools/loss_engine.py` | 557 | FR-LOSS-1..6. Gross loss, Cat XL allocation across layers, quota share, occurrence splitting, reinstatements and reinstatement premium, scenario overrides. **All money is `Decimal`** with half-up rounding — binary float gets `7.85 − 0.525` wrong, which changes a published figure by a cent. Returns the full per-party view in one object. |
| `tools/hazard.py` | 285 | DR-4. Haversine distance, piecewise radial wind profile from RMW/R64/R50/R34, ShakeMap grid parsing with **bounds**, nearest-cell MMI sampling, quadrant means. |
| `tools/vulnerability.py` | 153 | DR-5. Emanuel (2011) wind sigmoid with Eberenz `v_half` by country, interpolated MMI→damage table, intensity banding. |

### 3.2 Data generation — complete

| Module | Lines | What it does |
|---|---:|---|
| `ingest/seed_portfolio.py` | 642 | DR-1. 8 fictional cedents (JP×4, PH×2, TW×2), 24 treaties (18 Cat XL + 6 quota share), 592 exposures. Sakura's programme is the worked example exactly: 20xs10, 30xs30, 40xs60, our share 25%/10%/0%. |
| `ingest/build_wordings.py` | 976 | DR-2. Renders 8 treaty wordings as PDFs with reportlab, plus **one rasterised endorsement page with no text layer**, and writes a 186-field answer key. |
| `ingest/wording_clauses.py` | 436 | The clause library: 10 decoy passages designed to fool a keyword extractor, 11 boilerplate clauses, 4 registers of hours-clause phrasing. |
| `ingest/build_events.py` | 619 | DR-3. Builds replay files from **real** NOAA IBTrACS tracks and USGS ShakeMap grids. 4 events: Jebi 2018, Hagibis 2019, Haiyan 2013, Noto 2024. |
| `ingest/ibtracs.py` | 173 | IBTrACS v04r01 CSV parsing, SID filtering, wind-source conversion. |
| `ingest/regions_reference.py` | 277 | 47 JP prefectures, 22 TW counties, 32 PH provinces with centroids and exposure weights. |

### 3.3 Ingestion and retrieval — complete, including live extraction

| Module | Lines | What it does |
|---|---:|---|
| `ingest/ingest_treaty.py` | 591 | FR-INGEST-1. **Live Gemini extraction** from the PDF itself (not extracted text, so the scanned endorsement is readable), with retry/backoff, a relaxed twin schema for the API, and quarantine-not-discard on a structural failure. |
| `ingest/chunking.py` | 319 | FR-INGEST-2. Clause-aware chunking with page attribution; classification from the **heading**, not the body, because the decoys exist to exploit body matching. |
| `tools/retrieval.py` | 408 | FR-INGEST-2. `Embedder` and `VectorStore` behind protocols — deterministic/in-memory for tests, Gemini/Firestore for production. Honours C-11's equality-only pre-filter. |
| `catsight_agent/schemas.py` | 501 | Every agent contract as a strict Pydantic v2 model, plus `gemini_response_schema()` which produces the relaxed twin Gemini will actually accept. |
| `qa/extraction_accuracy.py` | 377 | QA-3/QA-4 harness. Typed comparison, per-treaty and per-source breakdowns, citation page accuracy **and** coverage reported separately. |

### 3.4 Verification — deterministic half complete

| Module | Lines | What it does |
|---|---:|---|
| `tools/verify.py` | 462 | FR-VERIFY-1 and the FR-VERIFY-3 retry/abstain loop. Normalises what `pypdf` mangles, then quote-matches **at the cited location** — treaty, then clause, then page. Catches paraphrase, wrong treaty, wrong page, wrong clause and mid-word truncation. |

FR-VERIFY-2, the semantic check, exists only as a protocol with a stub. See §6.

### 3.5 API and frontend — complete for the deterministic path

| Module | Lines | What it does |
|---|---:|---|
| `app/analysis.py` | 536 | FR-MATCH and the analysis pipeline. Conservative matching with a reason on every decision, as-if by default, SSE frame emission. |
| `app/main.py` | 363 | API-1..5, FR-GUARD's rate limit and daily cap, CORS, and static SPA serving with traversal containment. |
| `app/config.py` | 180 | Everything environment-driven. Rejects leftover `<PLACEHOLDER>` values rather than using them. |
| `frontend/src/*` | 1,278 | UI-1, 2, 4, 5, 7(partial), 10, 12, 13. One-click hero demo, three-party view, layer-burn chart with an accessible table alternative, treaties that did and did not respond. |

### 3.6 Deploy scaffolding — written, never run

`backend/Dockerfile` · `scripts/deploy.sh` · `scripts/smoke_test.sh`
(verified green against a local server) · `scripts/check_access.ps1` (21 PASS)
· `firebase.json` · `firestore.rules` (deny-all) · `LICENSE` (Apache-2.0).

---

## 4. What is measured

From `docs/RESULTS.md`, all against the live project.

| Check | Result | Bar | |
|---|---|---|---|
| QA-1 loss engine | worked example exact, incl. per-party view | — | ✅ |
| QA-2 hazard | 100% branch coverage | — | ✅ |
| **QA-3 field extraction** | **186/186 · 100.0%** | ≥95% | ✅ |
| &nbsp;&nbsp;by source | text 184/184 · **transcription 2/2** | | ✅ |
| FR-INGEST-3 validation | 8/8 ingestable, 0 quarantined | — | ✅ |
| QA-4 citation page accuracy | 135/144 · 93.8% | ≥95% | ❌ |
| QA-4 citation **coverage** | 144/186 · 77.4% | — | ❌ |
| QA-10 verifier | 40/40 corruptions withheld, **0 false withholds** | 100% / 0 | ✅ |
| Access checks | 21 PASS · 1 benign WARN · 0 FAIL | — | ✅ |
| Local smoke test | 14/14 | — | ✅ |

**Read QA-3's 100% with its caveat.** The extraction prompt went through six
revisions, each driven by the previous run's failures against *this* answer
key. The defects fixed were real and are listed in `RESULTS.md` §5, but a
score on tuned data is an upper bound. The honest sentence is *"100% on the
eight planted wordings, after six revisions against them."*

---

## 5. Requirement status

### Functional

| ID | Requirement | Status |
|---|---|---|
| FR-LOSS | Deterministic loss engine | ✅ complete |
| FR-MATCH | Treaty matching | ✅ complete |
| FR-INGEST | Wording extraction, chunking, retrieval | ✅ complete |
| FR-ENDORSE | Endorsement detective | ✅ extraction works (transcription 2/2); UI badge pending |
| FR-VERIFY | Citation verifier | 🟡 deterministic half + loop done; semantic half stubbed |
| FR-GUARD | Guardrails | 🟡 rate limit, cap, input validation done; prompt-injection guard pending (needs agents) |
| FR-EVENT | Event intelligence | 🟡 replay files done; live mode returns 501 |
| FR-WORD | Wording flags | ⬜ not started — needs AG-3 |
| FR-REPORT | Analyst report | ⬜ not started — needs AG-4 |
| FR-COURT | Clause Courtroom | ⬜ not started |
| FR-WHATIF | Bounded what-if | ⬜ engine support exists; tool and UI not wired |
| FR-JUDGE | Judge mode, tour, cached replay | ⬜ not started |
| FR-ASK | Follow-up questions | ⬜ not started |
| FR-REVIEW | Analyst review | ⬜ not started |
| FR-EXPORT | Markdown/PDF export | ⬜ not started |
| FR-DOC | Judge-facing README | 🟡 README exists; rubric mapping and diagram pending |

### Agents — none built

| ID | Agent | Status |
|---|---|---|
| AG-1..AG-4 | event_intel, exposure_analyst, wording_analyst, reporter | ⬜ |
| AG-5 | verifier | 🟡 logic built and tested; not wired as an ADK loop |
| AG-6..AG-8 | cedent_counsel, reinsurer_counsel, arbiter | ⬜ |

`google-adk==2.11.0` is installed and verified: `google.adk.workflow` exports
`Workflow`, `Node`, `Edge(route=...)`, `JoinNode`, `START`, `RetryConfig` and
`max_concurrency`. The AG-5 cycle and the AG-6/7 fan-in are both expressible,
so the `SequentialAgent` fallback stays a fallback.

### API

| ID | Endpoint | Status |
|---|---|---|
| API-1 | `GET /healthz` | ✅ |
| API-2 | `GET /api/events` | ✅ |
| API-3 | `GET /api/treaties[/{id}]` | ✅ (no signed PDF URL yet) |
| API-4 | `POST /api/analyses` (SSE) | ✅ deterministic frames |
| API-5 | `GET /api/analyses/{id}` | ✅ recomputed, not stored |
| API-6..9 | ask, review, export, admin ingest | ⬜ |

### UI

| ID | Screen | Status |
|---|---|---|
| UI-1 | Landing + one-click hero | ✅ |
| UI-2 | Agent timeline | 🟡 stage chips; no per-agent detail |
| UI-4 | Impacted treaties | ✅ |
| UI-5 | Layer burn chart | ✅ + accessible table (UI-12) |
| UI-7 | Report tab | 🟡 three-party panel; no prose report |
| UI-10 | Glossary tooltips | ✅ 10 terms |
| UI-12 | Accessibility | 🟡 AA contrast, focus rings, reduced motion, table alternative; no keyboard-only run tested |
| UI-13 | Trust panel | ✅ states honestly that no wording claims are shown |
| UI-3, 6, 8, 9, 11, 14, 15, 16 | map, flags, portfolio, methodology, states, Courtroom, what-if, tour | ⬜ |

### Tests

QA-1 ✅ · QA-2 ✅ · QA-3 ✅ · QA-4 ❌ below bar · QA-5 ⬜ (needs agents) ·
QA-6 ✅ · QA-7 🟡 (typecheck + build; no component tests) · QA-8 ⬜ (needs a
deploy) · QA-9 ⬜ · QA-10 ✅ · QA-11 ⬜ · QA-12 🟡 extraction verified, badge
pending · QA-13 ⬜

---

## 6. What is pending

### 6.1 Blocked on spending money

Vertex AI Gemini has **no free tier**; every token is billed. A full analysis
costs roughly $0.05. Note the project bills to
`subbulakshmik1945@gmail.com`'s account, not to the repo owner's.

- **S4 — the agent graph.** AG-1..4, `prompts.py`, the AG-5 loop wired as a
  real ADK cycle, FR-VERIFY-2 against `MODEL_REASON`, agent SSE frames.
- **S6 — the Clause Courtroom.** AG-6/7 in parallel, AG-8 arbiter, both
  readings priced by the engine.
- **Firestore seed and the vector index.** `write_firestore()` is written and
  tested against a fake client but has never run live. Within free tier, but
  unverified.
- **Deploy to Cloud Run.** Free-tier eligible except Artifact Registry, whose
  0.5 GB allowance a Python image may exceed (~$0.10/GB/month).

### 6.2 Blocked on a human

- **The blind set (Y9) — the single biggest credibility gap.** Three wordings
  with planted issues, authored by someone who has not seen the extraction
  prompt. Without it, QA-3's 100% cannot support a general claim.
- **B1 manual baseline.** An analyst doing this by hand, stopwatched and
  screen-recorded. Every "faster than" claim depends on it.
- **B8 usability.** 5 users + SUS.
- **Domain review** of the 8 wordings by a practitioner.
- **Two finale presenters** named, and Singapore visas.

### 6.3 Buildable now, for free

- `regions.geojson` for the map (UI-3) — the last unticked S1 gate item.
- UI-8 portfolio, UI-9 methodology, UI-11 states, UI-16 guided tour.
- QA-7 frontend component tests.
- FR-EXPORT markdown export.
- Rubric mapping table and architecture PNG for FR-DOC.
- Cached replay fixtures (FR-JUDGE-2) from the deterministic pipeline.

---

## 7. Honest disclosures

Carried from `backend/data/ASSUMPTIONS.md`. These belong in any write-up.

| Ref | What |
|---|---|
| **G9** | QA-3's 100% is on data the prompt was tuned against, over six revisions. Upper bound, not expectation. |
| **Y9** | The eight wordings are a structural holdout, **not a blind set**. |
| **VF7** | QA-10 covers the deterministic half only. Every `semantic_pass` in the suite comes from a stub, so FR-VERIFY-2 is unmeasured. |
| **R11** | Partly closed. `GeminiEmbedder` runs live (768-dim, correct ranking), but no recall or precision figure over the corpus exists. Margins vary 8× by query phrasing: `"loss occurrence"` separates a decoy by 0.145, `"hours clause"` by 0.018. |
| **X6** | The model under-predicts Jebi's actual market loss. Report the gap; do not tune it away. `calibration_factor` stays 1.0 until B5. |
| **Market size** | The synthetic Japanese market is ~US$2.5tn against a real insured value of order US$20–30tn — about 10× light. Deliberate: `TSI_PER_WEIGHT_USD_M` was set so the demo reproduces the worked example and the programme burns partially. |
| **Hours clause** | **It cannot bite on any replay event.** Jebi is 9h; the shortest clause in the book is 72h. The one-occurrence-vs-two comparison is not reachable from real data as configured. See §9. |
| **G7** | `temperature=0` is not determinism — two runs over identical PDFs disagreed. QA-11 wants 5 identical runs; unmeasured. |
| **G8** | Quota looks exactly like inaccuracy. One run scored 33.9% from pure 429 throttling. |

---

## 8. Decisions already made

Recorded so nobody re-opens them without new information.

| # | Decision |
|---|---|
| 1 | Repo is `github.com/arunveerappan10/AI-builder-cup`, private, `main` + per-stage branches. |
| 2 | GCP project `techno-crackers-catsight`; Firestore `(default)` Native, us-central1; models at `location=global`. |
| 3 | Python 3.12.10 in `backend/.venv`. |
| 4 | Reinstatement premium is pro rata as to amount, **per occurrence**, on the limit eroded by that occurrence while capacity remains — derived from the primer's own published figures. |
| 5 | **Serve the frontend from Cloud Run, not Firebase Hosting.** One deploy, one origin, no CORS to misconfigure, and no dependency on a Firebase terms acceptance only the project owner can complete. |
| 6 | ADK 2.x graph `Workflow` confirmed real; Scenario B stays a fallback. |
| 7 | Replay matching is **as-if by default** — a historical event on the current book. The period test applies only when `as_if=false`. |
| 8 | Strict Pydantic models are the contract; Gemini gets a relaxed twin. FR-INGEST-3's validation is load-bearing, not decorative. |
| 9 | `response_schema` gets **lists and typed objects, never open-ended maps** — the one shape the model will not populate. |

---

## 9. Open questions needing an answer

1. **Spend or not.** Vertex has no free tier. Either accept ~cents per run and
   build S4/S6, or ship the deterministic demo only and drop the Gen-AI
   differentiator the contest scores. *(Options also include the AI Studio free
   tier, which is not Vertex.)*
2. **Where the money moment comes from**, given the hours clause cannot bite:
   - **Noto's aftershock sequence** — a real earthquake sequence spans days, so
     a 72h clause genuinely applies. `ASSUMPTIONS` Z4 already flags this as
     undecided. Needs extra ShakeMaps; USGS is free.
   - **An explicit as-if scenario** — FR-WHATIF-1 sanctions `occurrences: 1–3`
     as a bounded parameter, clearly labelled as a scenario.
3. **Deploy now or later.** Deploying early gets a live URL, which is the
   structural safety net S5 exists to provide; everything after it is
   individually droppable.
4. **QA-4's shortfall.** Citation coverage is 77.4% where C-7 wants every claim
   cited. Fix by prompt, or by refusing to report a field with no provenance?

---

## 10. Suggested order from here

1. **Deploy the deterministic demo** → a live URL exists, S5's gate is met, and
   there is something to submit whatever happens next. *(Needs spend approval.)*
2. **S4 agents** → wording flags with verified citations. The largest remaining
   build and the M2 milestone.
3. **S6 Courtroom** → the differentiator, gated behind S5 by the plan's own
   lock.
4. **In parallel, free:** the blind set (human), B1 baseline (human), map,
   methodology page, export, rubric mapping.
