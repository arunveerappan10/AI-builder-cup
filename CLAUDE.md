# CatSight: instructions for Claude Code

CatSight is a hackathon prototype for the **Google Cloud AI Builder Cup 2026** (BFSI theme: *Intelligent Risk, Fraud & Financial Experiences*). After a typhoon or earthquake in Japan, the Philippines or Taiwan, it tells a reinsurer within minutes:

- which treaties are affected;
- roughly how much each layer pays;
- which contract clauses could change that answer — and by how much.

Every claim carries a citation, and every citation is machine-verified before it is shown.

**Team:** Techno Crackers. **Theme:** BFSI. **Target: Scenario C** (see `docs/BUILD_PLAN.md` §2).

---

## Read these first (in order)

1. **[docs/BUILD_PLAN.md](docs/BUILD_PLAN.md)** — the build order, the stage gates and the current target. **Start here.**
2. **[docs/REQUIREMENTS.md](docs/REQUIREMENTS.md)** — base spec v1: requirement IDs, acceptance criteria, data specs, API contract, agent specs. Source of truth for everything it covers.
3. **[docs/REQUIREMENTS_V2.md](docs/REQUIREMENTS_V2.md)** — **addendum that overrides v1 where they conflict.** Defines the verifier, the Clause Courtroom, the endorsement detective, what-if, judge mode, and the revised latency and cost targets.
4. **[docs/DOMAIN_PRIMER.md](docs/DOMAIN_PRIMER.md)** — reinsurance terms and the **worked example used as test fixtures**.
5. **[docs/MONEY_MOMENT.md](docs/MONEY_MOMENT.md)** — the demo's climax, derived number by number. Read before implementing `FR-COURT`.
6. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — the agent graph, data flows and service topology as built.
7. **[docs/RESEARCH_FINDINGS.md](docs/RESEARCH_FINDINGS.md)** — verified facts, API quirks and data-source details. Check it before assuming how an API behaves.
8. **[docs/EXECUTION_PLAN.md](docs/EXECUTION_PLAN.md)** §2–3 — GCP setup and deploy commands.
9. **[docs/BUSINESS_IMPACT.md](docs/BUSINESS_IMPACT.md)** — benchmarks B1–B8, which the build must support.

> **Precedence when documents disagree:** `REQUIREMENTS_V2.md` > `REQUIREMENTS.md` > everything else. `BUILD_PLAN.md` governs *order*, not *content*.

---

## Hard rules (don't violate them)

### Models and auth
- `gemini-3.5-flash-lite` (`MODEL_MAIN`), `gemini-3.8-flash` (`MODEL_REASON`), `gemini-embedding-001` at **768 dims**.
- **Never use `gemini-2.5-*`** — it retires 2026-10-20.
- All model IDs come from env vars. **`MODEL_MAIN` always holds the production model.** For cheap local runs set `MODEL_DEV` and opt in explicitly; never redefine `MODEL_MAIN` in `.env`, or prompts get tuned on a model that production never uses.
- QA and benchmark harnesses **always** run against the production models.
- `GOOGLE_CLOUD_LOCATION=global` (Gemini 3.x is not served from us-central1) and `GOOGLE_GENAI_USE_ENTERPRISE=true`. Cloud Run, Firestore and GCS stay in `us-central1`.
- Service-account auth only. **No API keys.** Never commit secrets.

### Numbers and citations
- **No LLM arithmetic.** Every loss and financial number comes from deterministic Python in `backend/catsight_agent/tools/loss_engine.py`. Agents call tools and copy outputs verbatim.
- The loss engine's scenario entry point is a **typed, bounded** ADK function tool. The LLM selects parameters; the engine computes; bounds are enforced in the tool schema.
- Every wording flag cites `treaty_id`, page and clause, and the quote must verify as a normalised substring of the stored chunk.
- **An unverified flag is never displayed in the report body.** It goes to the review tray. See `FR-VERIFY`.

### Dependencies and platform
- Pin `google-adk==2.11.0`. **Python 3.12** — not 3.13 or 3.14.
- ADK 2.x: `SequentialAgent` is deprecated in favour of graph `Workflow`; `SequentialAgent` is an acceptable fallback for the linear spine but **cannot** express the verifier loop or the Courtroom fan-out.
- Built-in `google_search` must be the **only** tool on its agent (`disallow_transfer_to_parent/peers=True`).
- google-genai retries are off by default — enable `HttpRetryOptions(attempts=5, initial_delay=1)`.
- `ThinkingConfig(thinking_level=LOW)` on Gemini 3. Thinking tokens bill as output.
- Use `FallbackModel` (ADK ≥ 2.9) so 3.8 Flash fails over to 3.5 Flash-Lite.
- Tools must be idempotent — failed workflow nodes re-run on resume.

### Data
- Synthetic portfolio and wordings plus public datasets with attribution only. **Never use real employer, client or broker data.** Fictional company names only, web-checked for collisions.
- Grounded web search provides **event context only**. It never touches a number or a wording flag, and it is displayed in a separate panel.
- Retrieved document text is wrapped as data; agents are instructed to ignore instructions inside documents.

### Architecture
- The frontend calls the Cloud Run `*.run.app` URL **directly** (CORS + SSE via `fetch` streaming). No Firebase Hosting rewrite for the API — 60 s timeout, no streaming.
- Create the Firestore vector index with **gcloud**, not the Firebase CLI. Vector pre-filters are equality only.
- Retrieval sits behind an interface with a local fallback, so engine and agent work never blocks on the vector index being `READY`.
- Cost guards: `--min-instances 0 --max-instances 3`, daily analysis cap, per-IP rate limit.
- **Every green run writes a cached replay fixture.** This is load-bearing, not an optimisation — it covers cold starts during remote judging, the daily cap under public traffic, and a dead network on stage.

### Originality and compliance
- Fresh code only (competition T&C). This repo contains only work created after 2026-09-07. OSS libraries are fine.
- Show the disclaimer on every report and in the UI footer: *"Indicative first view on synthetic data. Not a catastrophe-model output. Not underwriting or claims advice."*
- Real disasters, real victims. Calm language, neutral loading text, no celebratory framing.

---

## Environment

- **Dev machine:** Windows 11, PowerShell 5.1 — no `&&`; use `;` or `if ($?) { … }`.
- **Run `gcloud` setup and deploy commands in Google Cloud Shell (bash).** PowerShell 5.1 mangles JSON quoting in some gcloud flags, such as `--field-config` for vector indexes.
- **Large public downloads** (IBTrACS CSV ≈ 114 MB, Natural Earth ≈ 40 MB) go in `backend/data/raw/` (git-ignored). Commit only small derived files: `data/events/*.json`, `regions.geojson` (≤ 100 KB).

## Commands

```bash
# backend (from backend/)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
pytest -q
adk eval catsight_agent tests/eval/pipeline.evalset.json --config_file_path=tests/eval/test_config.json

# frontend (from frontend/)
npm install
npm run dev
npm run build

# deploy (Cloud Shell)
./scripts/setup_gcp.sh      # one-time
./scripts/deploy.sh         # Cloud Run + Firebase Hosting
./scripts/smoke_test.sh     # healthz + one replay analysis against the live URL

# proof pack
python benchmarks/run_all.py --api-url <live-url> --runs 5
```

## How to work

- Follow the stage order in `docs/BUILD_PLAN.md` §5. Each stage ends **deployable, with tests passing**.
- Reference requirement IDs in commit messages: `feat(FR-LOSS-2): layer allocation`.
- One branch per stage: `git checkout -b s2-engine`.
- Write tests alongside code. **QA-1 (the loss engine reproduces the DOMAIN_PRIMER worked example) must pass before any agent code is written.**
- Record every modelling assumption in `backend/data/ASSUMPTIONS.md`.

### The S5 lock
**Stage S5 is a hard gate.** Until Jebi runs end-to-end on the live URL in a clean incognito window, no work starts on S6 (Courtroom, endorsement detective, what-if). After S5 everything is additive and individually droppable.

A half-finished Courtroom scores worse than no Courtroom. If anything slips, drop S6 and ship S0–S5 plus the M-tier items — that is still a strong submission.

### Stop and ask the human for
- GCP billing or project setup, and creating secrets (e.g. `ADMIN_TOKEN`);
- anything that publishes externally — deploys to the live URL after the submission tag, GitHub visibility changes, posts;
- any change to the figures in `docs/MONEY_MOMENT.md` §3–4 — they are asserted by QA-1 and QA-11, and the deck and video are scripted on them, so a code change that moves them means the slide is wrong, not the test;
- any decision that conflicts with `REQUIREMENTS.md` or `REQUIREMENTS_V2.md`.

## Definition of done

- The live URL's **"Run demo: Typhoon Jebi 2018"** completes end to end with streamed agent stages, map, layer chart, verified wording flags and the report.
- The Clause Courtroom prices both readings of the hours clause, and the money moment is on screen with both parties' positions.
- QA-1..12 pass. `scripts/smoke_test.sh` passes against the live URL.
- `benchmarks/results/RESULTS.md` has **no "pending" cells**.
- README meets FR-DOC. `docs/ARCHITECTURE.md`, `docs/DECK_OUTLINE.md` and `docs/VIDEO_SCRIPT.md` are current.
- Secret scan clean; data attributions present; repo tagged.
