# CatSight — Build Plan

> **Status:** approved 2026-10-04. Supersedes the dated phase plan in `REQUIREMENTS.md` §11 and the 12-day calendar in the win-readiness review. **Order and gates, not dates.**
>
> Governs *sequence*. For *content*, `REQUIREMENTS_V2.md` > `REQUIREMENTS.md`.

---

## 1. Why this plan exists

`REQUIREMENTS.md` v1 is a complete, disciplined spec — and it is precisely the plan the win-readiness review scored at **7.1 / 10**, roughly top 5–10%: *"a very good build that generalist judges may file under 'niche dashboard with RAG'."*

The gap to a title contender is not more infrastructure. The rubric puts **40% on Technical Merit & Gen-AI Implementation** and **25% on Innovation & Creativity**, and two of the nine sub-criteria score specifically *how meaningfully* and *how creatively* Gen AI is used. v1's best design decision — the LLM never does arithmetic — is correct, and it also makes the AI invisible. Four linear agents demonstrate orchestration, not reasoning.

This plan keeps every v1 requirement and designs the review's Section 8 upgrades in as **first-class architecture rather than bolt-ons**, because retrofitting a verifier loop and an adversarial fan-out onto a finished linear pipeline costs more than building the graph once.

## 2. Target

| Tier | Items | In scope |
|---|---|---|
| Base | P0–P6, all MUST requirement IDs in v1 | ✅ |
| MUST | M1 story · M2 verifier + trust panel · M3 proof pack · M4 judge-proof demo · M5 differentiation statement | ✅ |
| SHOULD | S1 **Clause Courtroom** *(signature feature)* · S2 endorsement detective · S3 what-if | ✅ |
| STRETCH | X1 pre-landfall watch · X2 A2A/MCP endpoint | Only after S7 is green |

**Scenario C** — base + MUST + SHOULD. Estimated 8.9 / 10.

Fallback is explicit and pre-agreed: **Scenario B** (base + MUST, ≈ 8.2, top 2–5%) is the minimum to secure. The S5 lock below is the mechanism that guarantees it.

### Scoring deltas this plan targets

| Criterion | Weight | v1 as written | + MUST | + MUST & SHOULD |
|---|---|---|---|---|
| Technical Merit & Gen AI | 40% | 7.5 | 8.25 | 9.0 |
| Problem Alignment & Impact | 25% | 7.0 | 8.5 | 8.75 |
| Innovation & Creativity | 25% | 6.5 | 7.5 | 8.75 |
| UX & Solution Design | 10% | 7.5 | 8.75 | 9.0 |
| **Weighted total** | | **7.1** | **8.2** | **8.9** |

Estimates are the reviewer's judgement, not official results. The working assumption for a finalist profile is ≈ 8.5+ overall with no criterion below 8.

---

## 3. Architecture delta vs v1

v1 specifies four linear agents: `event_intel → exposure_analyst → wording_checker → reporter`. This plan adds a verifier loop and an adversarial fan-out/fan-in:

```
AG-1 event_intel          google_search only · skipped in replay mode
        │
AG-2 exposure_analyst     match_treaties, estimate_layer_losses ──► loss engine [typed tool]
        │
AG-3 wording_checker      search_treaty_clauses, split_occurrence_scenario
        │
        ├──────── LOOP ────────┐
AG-5 verifier               deterministic normalised quote-match
        │                     + checker on MODEL_REASON → {supports, reason}
        │                     fail → retry once with feedback → abstain
        │                     FR-VERIFY · M2
        ▼
   ┌─ AG-6 cedent_counsel ───┐   fan-out, opposing instructions, parallel
   └─ AG-7 reinsurer_counsel ┘ ──► AG-8 arbiter (MODEL_REASON)
        │                          both readings priced by the engine
        │                          FR-COURT · S1 · signature feature
        ▼
AG-4 reporter
```

Conditional: AG-6/7/8 run only when AG-3 raises an interpretable ambiguity (an hours-clause or event-definition flag). A standard analysis skips them.

### Four supporting changes

1. **The loss engine gets a typed scenario entry point**, exposed as a bounded ADK function tool — hours window, occurrence split, share, retention, track offset. The Courtroom prices both readings through it, and `FR-WHATIF` reuses it at near-zero marginal cost. The LLM picks parameters; the engine computes; bounds live in the tool schema.
2. **Retrieval behind an interface** with a local JSON/numpy vector fallback beside Firestore vector search, so S2/S3 work never blocks on the index being `READY` and dev runs don't burn cloud quota.
3. **Cached instant replay is a build artifact, not a patch.** Every green run writes a precomputed SSE fixture to `data/replays/`. One mechanism closes three separate risks: cold starts during three weeks of remote judging, the daily cap being exhausted by public traffic, and a stalled stream on stage at the finale.
4. **Model config corrected.** `MODEL_MAIN` always holds the production model; cheap dev runs use an explicit `MODEL_DEV` opt-in. The onboarding guide's `.env` sets `MODEL_MAIN=gemini-3.1-flash-lite`, which would tune prompts and structured outputs on a model production never uses.

---

## 4. Known consequences

Adding agents costs latency and money. Both v1 targets need revising — honestly, up front, rather than being quietly missed. Full derivation in `REQUIREMENTS_V2.md` §6.

| | v1 target | Revised |
|---|---|---|
| Cost per analysis (NFR-4) | ≤ $0.05 | ≤ $0.05 standard · **≤ $0.08 when the Courtroom runs** |
| Latency p95 (NFR-1) | ≤ 90 s | ≤ 95 s standard · **≤ 120 s Courtroom path** |

B6 reports both figures separately. The counsel agents run on `MODEL_MAIN` and in parallel, not on `MODEL_REASON` and serially — that single choice keeps the Courtroom path affordable.

---

## 5. Stages

Dependency-ordered. Each stage ends deployable with tests green.

### S0 · Bootstrap
Clone, Python 3.12 venv, repo layout per `REQUIREMENTS.md` §3.1, FastAPI `/healthz`, Vite + React + TS calling it, `scripts/setup_gcp.sh` / `deploy.sh` / `smoke_test.sh`, `firebase.json`, `firestore.rules` (deny all), `backend/Dockerfile`, pinned `requirements.txt`, `LICENSE` (Apache-2.0), README stub.

- [ ] **Gate:** live URL serves `/healthz`; the deployed frontend calls it successfully.

### S1 · Data — DR-1..6
`build_regions.py` · `build_events.py` (**Jebi and Noto first**; Hagibis and Haiyan after) · `seed_portfolio.py` including the **exact Sakura worked-example program** (20xs10, 30xs30, 40xs60; premiums 2.0/1.5/1.0; Lion Re 25% / 10%) · `build_wordings.py` producing 8 PDFs **plus one image-only scanned endorsement page** (`FR-ENDORSE`) · `ground_truth.json` (~120 fields) + ≥ 10 decoy passages · **a 3-wording blind set, authored outside the prompt work and held out** · `data/ASSUMPTIONS.md`.

- [ ] **Gate:** Firestore holds `cedents`, `treaties`, `exposures`; `regions.geojson` ≤ 100 KB; seeds are deterministic and idempotent.

### S2 · Core engine — **hard gate**
`loss_engine.py` (QA-1) · `hazard.py` (QA-2) · `data/vulnerability.json`.

**No agent code before this passes.** Pure Python, no GCP dependency — this stage can start before cloud access is confirmed.

- [ ] **Gate:** `pytest -q` green. Worked example exact: gross **54.4** · L1 **20.0** · L2 **24.4** · L3 **0** · Lion Re loss **7.44** · our RIP **0.622** · net **≈ 6.82** · split case **29.4 / 5.0**. Full branch coverage on `loss_engine.py`.

### S3 · Ingestion and retrieval
`ingest_treaty.py` (Gemini structured output via `Part.from_uri`, temperature 0, `field_pages` on every field) · embeddings at 768 dims, L2-normalised, `task_type=RETRIEVAL_DOCUMENT` · vector index **created with gcloud** · `retrieval.py` with equality pre-filter on `treaty_id` · local vector fallback.

- [ ] **Gate:** all 8 wordings ingest; **QA-3 ≥ 95%** field accuracy against ground truth.

### S4 · Agents, API and verifier — M2
`schemas.py` · `prompts.py` · AG-1..4 · **AG-5 verifier loop** · `Workflow` graph · SSE streaming (API-4) · API-1..5.

- [ ] **Gate:** Jebi runs end-to-end locally. Every displayed flag carries a verified citation. The report header reads *"n of n displayed citations verified · k withheld"*. Both verification checks log to Cloud Trace.

### S5 · UI demo path — **DEMO-PATH LOCK**
UI-1..8 in demo-path order, plus the trust panel (UI-13).

- [ ] **Gate:** **Jebi end-to-end on the live URL in a clean incognito window.**

> This is the structural safety net. Everything after S5 is additive and individually droppable. If time or quota runs short here, stop adding features and finish S8 and S9 instead — that ships Scenario B.

### S6 · Signature Gen-AI — S1, S2, S3
`FR-COURT` Clause Courtroom (AG-6/7/8 + UI-14) · `FR-ENDORSE` endorsement detective · `FR-WHATIF` bounded what-if (UI-15).

- [ ] **Gate:** the money moment is on screen — both readings quoted and verified, both priced by the engine, both parties' positions named, and the analyst records a position that persists on the analysis document.

### S7 · Judge-proofing and quality — M4
`FR-GUARD` · cached instant replay · `FR-JUDGE` guided 60-second tour · glossary tooltips (UI-10) · WCAG AA contrast and colour-blind-safe palette, keyboard navigation, map table alternative (UI-12) · structured logging and Cloud Trace · QA-4..8 · `FR-ASK`, `FR-REVIEW`, `FR-EXPORT`.

- [ ] **Gate:** `smoke_test.sh` passes against the live URL. The cap-hit path serves a cached replay with a friendly message, never an error. Keyboard-only run of the demo path succeeds.

### S8 · Proof pack — M3
Benchmark harness B2–B7 · blind-set accuracy reported **separately** from the tuned set · **B1 manual baseline** *(human, screen-recorded)* · **B8 usability, 5 users + SUS** *(human)*.

- [ ] **Gate:** `benchmarks/results/RESULTS.md` has no "pending" cells. Every number in the deck traces to a real run.

### S9 · Story and deliverables — M1, M5
Differentiation statement (one slide + one README section) · README per FR-DOC · `ARCHITECTURE.md` + PNG diagram · `DECK_OUTLINE.md` → deck PDF · `VIDEO_SCRIPT.md` ≤ 2:45 → recorded video · `SUBMISSION_ANSWERS.md` · backup demo screenshots and full screen recording in `docs/demo/` · fictional-name web check · secret scan · data attributions · tag.

- [ ] **Gate:** README renders correctly on GitHub. Video timed under 3:00. A dry run performed as a judge, from a cold browser, with fixes applied.

### X · Stretch — only if S7 is green
`X1` pre-landfall / live watch — **confirm WeatherNext data access on day one**; if not confirmed within 48 h, build the same feature on a perturbed-track IBTrACS ensemble and show WeatherNext as roadmap. Never claim an unshipped integration. · `X2` A2A/MCP endpoint so a broker's agent can call CatSight as a tool.

---

## 6. Parallel human track

These do not block code and must start as early as their dependency allows.

| Task | Owner | Starts after |
|---|---|---|
| Domain review of the 8 wordings and one flash report | Domain lead | S1 |
| Blind set authored outside the prompt work | Someone other than the prompt author | S1 |
| **B1 manual baseline**, stopwatch per step, screen-recorded | Third member | S1 (needs only data + PDFs) |
| B8 usability, 5 users + SUS | Third member | S5 |
| Deck build from `DECK_OUTLINE.md`, video voice-over | Team | S8 |
| Fictional-name collision check | Anyone | S1 |
| Two finale presenters named; passports and Singapore visas checked | Team | Now |

**B1 is on the critical path for the Impact score.** Every effort-saving claim in the deck depends on it, and it needs a human with a stopwatch — it cannot be compressed by building faster.

---

## 7. Open decisions

| # | Decision | Status |
|---|---|---|
| 1 | Build location and git remote — this repo, `main` with per-stage branches | ✅ resolved: `github.com/arunveerappan10/AI-builder-cup` |
| 2 | `gcloud` and `firebase-tools` are not installed locally; GCP access unverified; `gemini-3.5-flash-lite` / `gemini-3.8-flash` not yet confirmed to resolve on the project | ⏳ **open** — **placeholders in use**, see below. S1 and S2 proceed locally meanwhile |
| 3 | Python 3.12 required; only 3.14 is installed | ⏳ **open** |
| 4 | Money-moment framing — reinstatement-premium basis and L1 reinstatement sufficiency | ⏳ **open** — needs domain lead, see `MONEY_MOMENT.md` §4 |
| 5 | GCP project remains `techno-crackers-catsight` (owned by the project owner) while code lives in this repo | ⏳ confirm |

### Placeholder convention (decision 2)

Until GCP details arrive, **every environment-specific value is a `<PLACEHOLDER>` in exactly two files**:

- `backend/.env.example` — project ID, bucket, CORS origins, admin token, model IDs, feature switches
- `frontend/.env.example` — the Cloud Run service URL (which only exists after the first deploy)

**No project ID, bucket name, service-account email or URL may be hardcoded anywhere else in the codebase.** Scripts and application code read them from the environment, so swapping in real values later is a one-file edit per side with no code search. `scripts/setup_gcp.sh` and `deploy.sh` take the project ID from the environment too.

This also keeps the public repo clean: the live URL and project identifiers appear only in a git-ignored `.env`, never in committed source.

---

## 8. Risk register

Carried from the win-readiness review, with the mitigation each stage owns.

| Level | Risk | Mitigated by |
|---|---|---|
| HIGH | Differentiation never stated → judges assume a re-implementation | S9 · M5 |
| HIGH | Gen-AI reasoning not showcased → under-scores two sub-criteria in the 40% and 25% blocks | S4 verifier · S6 Courtroom |
| HIGH | Proof arrives late or shows "pending" | S8, with B1 started at S1 |
| HIGH | Scope versus runway; half-finished features cost more than missing ones | **The S5 lock** |
| MED | Answer-key bias — the team writes both the wordings and the ground truth | S1 blind set, authored outside the prompt work, reported separately |
| MED | Dev/prod model mismatch | `MODEL_MAIN` / `MODEL_DEV` split; QA always on production models |
| MED | Cold start and latency for remote judges | S7 cached replay; `min-instances=1` for the judging window, with owner approval |
| MED | Public traffic exhausts the daily cap and shows judges an error | S7 — anonymous visitors get cached replays at no LLM cost |
| MED | Grounded web snippets leaking into a "verified" report | Separate Event-context panel; never in numbers or flags |
| MED | Celebratory framing of events that killed people | Calm language, neutral loading text, one respectful acknowledgement |
| LOW | Fictional name collides with a real company | S1 web check |
| LOW | Secrets or personal details in public git history | S9 secret scan |

---

## 9. Never cut

`FR-LOSS` · `FR-WORD` with citations · `FR-VERIFY` · UI-1..7 · QA-1, QA-3, QA-4 · the deliverables in S9.

**Cut order if forced** (bottom up): X2 → X1 → `FR-WHATIF` → `FR-ENDORSE` → live mode → PDF export → `FR-ASK` → Taiwan coverage → Hagibis and Haiyan replays → **`FR-COURT`**.

`FR-COURT` is last to be cut because it is the single clearest piece of evidence for non-superficial Gen AI — and first to be cut if it cannot be finished *well*, because a half-built Courtroom is worse than none.
