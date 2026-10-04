# Techno Crackers — Google Cloud AI Builder Cup 2026 Execution Plan

> Prepared 2026-10-02 (Fri). Submission deadline **2026-10-18 23:59 IST** (18:29 UTC; 02:29 Oct 19 in Singapore). **Team target: 2026-10-15.** Registration is complete. The build is done from the reference pack ([docs/README.md](README.md)), not from a day-by-day plan.
>
> **Revised 2026-10-02 after the pre-development research in [RESEARCH_FINDINGS.md](RESEARCH_FINDINGS.md):**
> - Gemini 2.5 retires Oct 20, so the plan now uses Gemini 3.x on the `global` endpoint.
> - The T&C roster lock is Oct 4.
> - Only code written during the hackathon is allowed.
> - ADK 2.x replaces some APIs.
> - The vector index is now created with gcloud.
> - Spend caps are added.
>
> Legend used throughout: **[VERIFIED]** = confirmed on an official source during research · **[THIRD-PARTY]** = from a non-official source · **[UNVERIFIED]** = not found / could not confirm · **[ESTIMATE]** = our own assumption-based calculation · **[JUDGEMENT]** = strategic opinion.

---

## 0. Fact Check of the Brief (read this first)

| Claim in the brief | Status | What the sources say |
|---|---|---|
| Deadline Oct 18, 2026 | **[VERIFIED]** | Official site: "Prototype Building & Submission: September 7 – October 18, 2026". Older third-party listings say Oct 3/4; those dates are **superseded**. Hack2skill's event data gives **`2026-10-18T18:29Z` (23:59 IST)**. |
| Team roster lock | **Conflict** | The site and FAQ say registration closes Oct 11. **The official T&C says rosters lock Oct 4.** Register both members by Oct 4. |
| Code originality | **[VERIFIED]** | T&C: "Submissions must consist exclusively of fresh code and original assets created during the official hackathon timeline." |
| IP | **[VERIFIED]** | T&C grants Hack2skill a 6-month right of first refusal on an exclusive licence to the submitted materials, plus worldwide publication rights. |
| "Top 50 Grand Finale" | **[UNVERIFIED]** | Neither the official site, the themes page nor the FAQ states a number of finalists. Finalists are announced Nov 7; Demo Day is **Dec 4, 2026, Singapore**. |
| Technical Merit 40% | **[VERIFIED]** | "Technical Merit & Gen AI Implementation: 40%". |
| "Theme Alignment" | **Partly incorrect name** | The official criterion is **"Problem Alignment & Impact: 25%"**. |
| Innovation & Creativity | **[VERIFIED]** | 25%. |
| User Experience 10% | **[VERIFIED]** | "User Experience & Solution Design: 10%". |
| Deliverables: live URL, public GitHub, demo video | **[VERIFIED]** | FAQ: "a working deployed link of your prototype, a video demo under 3 minutes, the public GitHub repository of your prototype and a deck explaining your solution in detail." |
| Architecture document as a separate deliverable | **Not required, but architecture must be in the deck** | T&C: "A comprehensive presentation deck explaining the solution architecture and business case" (PDF). Video "strictly under three (3) minutes" on YouTube, Vimeo or Drive. → Put the architecture in the deck **and** in `docs/ARCHITECTURE.md`. |
| Gemini / ADK / LangChain, Cloud Run / Firebase | **[VERIFIED], with one caveat** | Must use "Google AI models (like Gemini or Gemma) or be built using agentic platforms (such as Agent Platform, Antigravity, or AI Studio)" and be "deployed on Google Cloud via Cloud Run or Firebase". **ADK and LangChain are not named** in the rules. ADK is Google's first-party kit and is part of Gemini Enterprise Agent Platform (Vertex AI was rebranded at Cloud Next 2026). → **Use ADK, not LangChain.** |
| Team of two | **[VERIFIED] allowed** | Team size is 2–4, and only 2 members travel. Every member must be a **working professional aged 21+**. Students are disqualified. |
| Can we submit both a BFSI and a Retail idea? | **No** | FAQ: "one team can only submit one solution under one problem statement/theme." |

**Other critical items**
1. **Registration & team formation closes Oct 11, 2026 [VERIFIED].** Confirm today that both members are registered on Hack2skill as one team.
2. **Inconsistency on the official themes page:** the "category specification" note says to identify the problem statement from "(Healthcare, Education, Sustainability, Accessibility, Social Good)". That list doesn't match the six actual themes and looks like leftover template text. **Ask on the organizer Discord** (and email support+aibuildercup@hack2skill.com) about: (a) the deadline timezone, (b) the category-specification format, (c) whether a separate architecture document is expected, and (d) the number of finalists.
3. **Organizer-provided GCP credits: [UNVERIFIED]**. None were found. The plan assumes your own $300 Free Trial.

---

## 1. Domain & Use-Case Strategy

### 1.1 The official theme text we must align to [VERIFIED]

- **BFSI: Intelligent Risk, Fraud & Financial Experiences.** "Build an AI-powered solution that addresses meaningful challenges across banking, financial services, insurance, or related industries… detecting and mitigating fraud or risk, automating complex processes, improving customer interactions, or delivering more personalized and informed financial experiences."
- **Retail & Commerce: Intelligent Customer and Business Experiences.** "…transforms how businesses understand, engage, and serve customers while improving operational efficiency… discovery, personalization, conversational shopping, demand planning, inventory, customer insights, or fraud."

### 1.2 Strategic read [JUDGEMENT]

- Most BFSI entries will likely be banking chatbots, KYC, or card-fraud scoring, and most Retail entries will likely be shopping assistants. **Reinsurance is a rare niche.** Your domain background is the competitive edge under *Originality & differentiation* (25%).
- The finale is in **Singapore, a major reinsurance hub for Asia**. The hackathon is **JAPAC-wide**, a region exposed to typhoons, earthquakes and floods. An Asia-Pacific catastrophe use case fits the audience.
- The 40% Technical Merit criterion explicitly rewards *"meaningful use of Gen AI… beyond a basic or superficial implementation"*. A plain RAG chatbot will look generic. **Multi-agent orchestration, structured extraction, grounding with citations, deterministic tools for the maths, and an evaluation harness** score better.

### 1.3 Three BFSI problem statements (Reinsurance)

> Industry-gap statistics below come from **vendor blogs [THIRD-PARTY]**, not independent research. Quote them in the deck as "industry reports suggest…", or replace them with figures from your own professional experience.

#### B1. CatSight — Post-Catastrophe Treaty Exposure & Wording Agent ⭐ RECOMMENDED
- **Problem:** When a typhoon or earthquake hits, a reinsurer's leadership asks within hours: *"Which treaties are hit, how deep into each layer, and does the wording (hours clause, peril exclusions, territorial scope) change the answer?"* Today this means spreadsheets, emails to cedents and manually reading treaty wordings.
- **Gap (domain hypothesis; validate from your experience):** vendor cat-model event loss estimates take time and cost money. Smaller Asian reinsurers and cedents often have no fast, explainable first-view tool that joins *event facts + portfolio + treaty wording*. Vendor sources say late data drives manual workarounds (one report: "71% of ceded reinsurance professionals" [THIRD-PARTY]).
- **Solution:** A multi-agent system that:
  1. Grounds the event in sources such as news and advisories (Google Search grounding, with citations).
  2. Matches it to treaties by peril, territory and period.
  3. Computes indicative layer losses with a **deterministic Python loss engine** (the LLM never does the arithmetic).
  4. Uses RAG over treaty wordings to flag clauses (hours clause, exclusions) with **page-level citations**.
  5. Writes a "first-view exposure flash report" for human review.
- **Demo moment:** pick "Typhoon Jebi 2018". The agent timeline streams live, a map heats up, a layer-burn chart fills, and you click a citation to see the 72-hour clause highlighted.
- **Rubric fit:** Tech 5/5 · Impact 4/5 · Innovation 5/5 · UX 5/5 **[JUDGEMENT]**. **Feasibility in 16 days: medium.** There is a built-in scope-down path to B2's core (the wording RAG module is shared).

#### B2. TreatyLens — Bordereaux-vs-Treaty Compliance Auditor
- **Problem:** Cedent bordereaux (premium and claims) arrive as inconsistent Excel or PDF files. Reinsurance accountants rekey them and check them manually against treaty terms.
- **Gap [THIRD-PARTY, vendor sources]:** "Reinsurance accountants spend 40% of their time manually rekeying data". Manual error rates are quoted at "5–15%". Date-format inconsistency is cited as a persistent failure.
- **Solution:** Gemini maps messy columns to a canonical schema, extracts treaty terms into JSON, and runs a row-level rule check (risk outside the period or territory, excluded peril, sum insured above limit, premium mismatch). It produces an exception ledger with clause citations and drafts a query letter to the cedent.
- **Risk:** **Existing products** (reinsured.ai, V7 Labs, Quantiphi) already market bordereaux AI, so originality is weaker.
- **Rubric fit:** Tech 4 · Impact 4 · Innovation 3 · UX 3 **[JUDGEMENT]**. **Feasibility: high.**

#### B3. FacTriage — Multimodal Facultative Submission Triage
- **Problem:** Facultative underwriters receive email submissions with schedules of values, survey reports and site photos. Much of the effort goes to risks that end up declined.
- **Solution:** Gemini multimodal reads the PDF survey and photos (fire protection, construction, housekeeping), checks them against the underwriting appetite guide (RAG), lists missing information, scores the risk, and drafts a quote-or-decline memo with reasons.
- **Gap (domain hypothesis):** slow turnaround on submissions and inconsistent appetite application.
- **Rubric fit:** Tech 4 · Impact 4 · Innovation 3 · UX 4 **[JUDGEMENT]**. **Feasibility: high.**

### 1.4 Three Retail & Commerce problem statements

#### R1. ShelfSense — Zero-Shot Shelf Audit for Mid-Size Retailers
- **Problem:** Empty shelves and price-tag mismatches. Computer-vision vendors need custom model training, which mid-size APAC retailers can't afford.
- **Gap [THIRD-PARTY: IHL Group]:** retailers lose about 6.5% of global sales to out-of-stocks and overstock. Empty shelves alone account for about $690.9B. A 2025 field study found audits raised sales 11%.
- **Solution:** Staff photograph a shelf. Gemini multimodal detects gaps and facings and reads price labels, compares them with the planogram and price master (Firestore), and creates replenishment and re-label tasks.
- **Risk:** incumbents exist (Trax, Brain Corp). The differentiation is "no training, any store".
- **Rubric fit:** Tech 4 · Impact 4 · Innovation 3 · UX 5. **Feasibility: high.**

#### R2. FestivalPulse — Festival-Aware Demand Sensing for Multi-Store SMEs
- **Problem:** Demand around JAPAC festivals (Diwali, Lunar New Year, Ramadan/Eid, Golden Week) shifts by region and by year. SMEs plan on gut feel.
- **Solution:** BigQuery ML (ARIMA_PLUS) produces baseline forecasts. A Gemini agent adds grounded external signals (festival dates, weather, local events), explains adjustments, and drafts purchase orders that a planner approves.
- **Risk:** needs believable sales history (synthetic data), and forecast quality is hard to show in 3 minutes.
- **Rubric fit:** Tech 4 · Impact 4 · Innovation 4 · UX 4. **Feasibility: medium.**

#### R3. ReturnGuard — Explainable Returns-Fraud Triage
- **Problem:** Return fraud and abuse, such as wardrobing, empty-box returns and receipt fraud.
- **Gap [THIRD-PARTY: NRF / Appriss Retail]:** 2024 returns were $890B, with fraud and abuse at about $103B (15.14% by the Appriss method). NRF forecast $849.9B in returns for 2025, with 9% fraudulent under NRF's survey method. The two methods differ, so cite them carefully.
- **Solution:** A multimodal comparison of the customer's return photo with the catalogue image, analysis of the return-reason text, and a check of order-history patterns. It produces a risk score with a natural-language rationale and routing (auto-approve, inspect, or deny with policy citation), plus a customer-facing message.
- **Rubric fit:** Tech 4 · Impact 4 · Innovation 4 · UX 4. **Feasibility: high.**

### 1.5 Weighted scoring [JUDGEMENT] (0.40 Tech + 0.25 Impact + 0.25 Innovation + 0.10 UX)

| Idea | Tech | Impact | Innov | UX | Weighted | Feasibility (16 days) |
|---|---|---|---|---|---|---|
| **B1 CatSight** | 5 | 4 | 5 | 5 | **4.75** | Medium |
| R2 FestivalPulse | 4 | 4 | 4 | 4 | 4.00 | Medium |
| R3 ReturnGuard | 4 | 4 | 4 | 4 | 4.00 | High |
| R1 ShelfSense | 4 | 4 | 3 | 5 | 3.85 | High |
| B3 FacTriage | 4 | 4 | 3 | 4 | 3.75 | High |
| B2 TreatyLens | 4 | 4 | 3 | 3 | 3.65 | High |

**Recommendation:** submit **B1 CatSight** under BFSI. **Fallback if behind at the Oct 9 gate:** drop live Google Search grounding and ship in "replay mode" with pre-grounded historical events. If still behind, ship the wording-RAG and loss-engine core, which is still a coherent reinsurance submission. The rest of this document is written for CatSight. The same architecture pattern (ingest → embed → agents → deterministic tools → UI) carries over to any of the other five ideas.

---

## 2. Technical Architecture (CatSight)

### 2.1 High-level architecture

```
                        ┌──────────────────────────────────────────┐
  Reinsurance analyst   │  Firebase Hosting  (React + Vite SPA)     │
  / judge (browser) ───►│  https://<project>.web.app                │
                        └───────────────┬──────────────────────────┘
                                        │ HTTPS (REST + SSE stream), CORS
                                        ▼
                        ┌──────────────────────────────────────────┐
                        │ Cloud Run: catsight-api                   │
                        │ FastAPI + Google ADK multi-agent pipeline │
                        │ service account auth (no API keys)        │
                        └──┬──────────┬───────────┬──────────┬─────┘
                           │          │           │          │
             ┌─────────────▼──┐ ┌─────▼──────┐ ┌──▼───────┐ ┌▼──────────────────┐
             │ Gemini on Agent│ │ Firestore  │ │ Cloud    │ │ Google Search     │
             │ Platform       │ │ (native)   │ │ Storage  │ │ grounding         │
             │ (Vertex AI)    │ │ treaties,  │ │ treaty   │ │ (event facts      │
             │ 3.5 Flash-Lite │ │ exposures, │ │ PDFs,    │ │  + source URLs)   │
             │ 3.8 Flash      │ │ vectors,   │ │ uploads  │ └───────────────────┘
             │ embedding-001  │ │ analyses   │ └──────────┘
             │ (global endpt) │ └────────────┘
             └────────────────┘ └────────────┘
       Cross-cutting: Cloud Logging + Cloud Trace · Billing budget alerts · Artifact Registry · Cloud Build
```

### 2.2 Detailed data flow

```
═══════════════ FLOW A — Treaty ingestion (offline/admin, run once per document) ═══════════════

 treaty_*.pdf ──► POST /api/admin/ingest ──► Cloud Storage gs://<proj>-docs/treaties/
                                     │
                                     ├─[A1] Gemini 3.5 Flash-Lite (PDF via gs:// URI, response_schema=TreatyTerms,
                                     │      temperature 0, media_resolution medium, page_number on every field)
                                     │      → {cedent, type: CAT_XL|QS|SURPLUS, perils[], territory[],
                                     │         inception, expiry, currency, share,
                                     │         layers[{retention, limit, reinstatements, premium}],
                                     │         hours_clause{peril→hours}, exclusions[]}
                                     │      → Firestore  treaties/{treaty_id}     (+ extraction_confidence)
                                     │
                                     └─[A2] Chunk by clause/page (~400–800 tokens, keep page no. + clause heading)
                                            → gemini-embedding-001 (output_dimensionality=768,
                                              task_type=RETRIEVAL_DOCUMENT)
                                            → Firestore  treaty_chunks/{id}
                                              {treaty_id, page, clause_type, text, embedding: Vector(768)}
                                            (vector index: treaty_id ASC + embedding flat/768)

 seed_portfolio.py ──► Firestore exposures/{cedent}_{region}_{peril}  {tsi, policy_count, lob}
                       (synthetic, clearly labelled; regions = Natural Earth admin-1 codes)

═══════════════ FLOW B — Event analysis (runtime, streamed to the UI) ═══════════════

 UI: "Analyse event" (pick a replay event or type free text)
   │  POST /api/analyses {event_query | event_id}   →  text/event-stream
   ▼
 FastAPI ─► guardrails: input validation · per-IP rate limit · global daily cap (Firestore counter)
   │
   ▼  ADK Runner(root_agent = SequentialAgent "catsight_pipeline")
   │
   ├─[B1] event_intel  (LlmAgent, tool: google_search)          output_key="event"
   │      cache hit? → Firestore events/{event_id}  (replay mode = zero grounding cost)
   │      → {name, peril, start, end, duration_h, regions[{code, intensity_band}], sources[]}
   │
   ├─[B2] exposure_analyst (LlmAgent, FunctionTools)             output_key="impact"
   │      tool match_treaties(event) ──► Firestore query: peril ∈ perils, region ∈ territory,
   │                                     inception ≤ event.start ≤ expiry
   │      tool estimate_layer_losses(...) ──► DETERMINISTIC PYTHON
   │           gross_r   = TSI_r × MDR(intensity_band_r)            (published, illustrative table)
   │           gross     = Σ_r gross_r   over regions in treaty territory
   │           ceded_L   = min(max(gross − retention_L, 0), limit_L)   per layer
   │           our_loss  = ceded_L × share ;  burn% = ceded_L / limit_L
   │           reinst_prem ≈ (ceded_L / limit_L) × layer_premium   (pro-rata as to amount; simplified)
   │
   ├─[B3] wording_checker (LlmAgent, tool: search_treaty_clauses) output_key="wording_flags"
   │      per impacted treaty: Firestore find_nearest(where treaty_id==X, COSINE, limit=4)
   │      checks: hours clause vs event.duration_h (→ possible 2 loss occurrences),
   │              peril exclusions (e.g., flood excluded under windstorm?), territorial scope
   │      → flags[{treaty_id, issue, severity, citation{page, clause, quote}}]
   │
   └─[B4] reporter (LlmAgent, no tools)                           output_key="report"
          → flash report (markdown + JSON): headline, impacted treaties, layer burn,
            wording flags with citations, assumptions, "INDICATIVE — not a cat-model output"
   │
   ▼
 Firestore analyses/{id} {event, impact, flags, report, model_ids, tokens, latency_ms, created_at}
   │
   ▼  SSE events → UI: live "agent timeline" · map heat by region · impacted-treaty table ·
                       layer-burn chart · citation side panel (click → clause text + page) ·
                       "Export PDF" · "Approve / annotate" (human-in-the-loop)

═══════════════ FLOW C — Follow-up Q&A ═══════════════
 POST /api/analyses/{id}/ask {question} → load analysis from Firestore → LlmAgent with
 search_treaty_clauses + stored impact JSON → grounded answer with citations
 (stateless per request: no session-store dependency across Cloud Run instances)

═══════════════ FLOW D — Quality & ops ═══════════════
 tests/golden_set.json (15 events/questions with expected treaties, layers, clauses)
   → pytest + `adk eval` → metrics: treaty-match precision/recall, loss-engine exactness,
     citation accuracy, p50/p95 latency, tokens/analysis  → numbers go into the deck
 Cloud Logging (structured JSON) · Cloud Trace (ADK OpenTelemetry) · Budget alerts
```

### 2.3 Design decisions that earn Technical Merit points

| Decision | Why it scores |
|---|---|
| LLM orchestrates and **Python computes** (loss maths) | No hallucinated numbers. Shows "technically sound" design. |
| `response_schema` structured extraction | Reliable JSON and auditable treaty terms. |
| RAG with page/clause **citations** | Explainability, which regulated industries require. |
| Google Search grounding + **event cache / replay mode** | Real-world facts with sources, a deterministic demo for judges, and near-zero cost. |
| ADK `SequentialAgent` + `output_key` state passing | Genuine agentic workflow, not one mega-prompt. |
| Gemini via **Agent Platform (Vertex) with service account** | No API keys in code. Enterprise data terms (no training on our data). Covered by the $300 trial credit. |
| Evaluation harness with published metrics | Strong proof of "functional, technically sound". |
| Serverless (Cloud Run min 0, Firestore) + documented roadmap | "Scalability & sustainability" sub-criterion. |

**ADK 2.x constraints to plan around** (verified 2026-10-02; see RESEARCH_FINDINGS §C):
- **Pin the version:** `google-adk==2.11.0`. Releases come out roughly weekly.
- **Search tool isolation:** built-in `google_search` excludes other tools in the same agent by default. Keep `event_intel` with only `[google_search]` and set `disallow_transfer_to_parent/peers=True`. Alternative: `AgentTool` wrapping, or `GoogleSearchTool(bypass_multi_tools_limit=True)`.
- **Schemas with tools:** `output_schema` together with tools now works natively on Gemini 3. Still validate the output with Pydantic.
- **Orchestration:** `SequentialAgent` is **deprecated in favour of graph `Workflow`** but still works. Try `Workflow(edges=[("START", a, b, c, d)])` on Day 6 and fall back to `SequentialAgent`.
- **Idempotent tools:** failed workflow nodes re-run on resume, so tools must be safe to re-run.
- **Model failover:** use `FallbackModel` (2.9+), e.g. 3.8 Flash falling back to 3.5 Flash-Lite.
- **Retries:** google-genai retries are **off by default**. Enable `HttpRetryOptions(attempts=5, initial_delay=1)`.
- **Thinking:** use `ThinkingConfig(thinking_level=LOW)` on Gemini 3. Thinking can't be turned off on Flash, and thinking tokens bill as output.
- **Streaming:** `RunConfig(streaming_mode=StreamingMode.SSE)`. The client must replace partial text with the final event, not append it. Use `fetch()` streaming, because `EventSource` is GET-only.

**Roadmap slide (scalability):**
- Pub/Sub trigger from public disaster alerts (e.g. GDACS) for auto-analysis.
- Vendor cat-model feeds via API.
- BigQuery for portfolio scale.
- Agent Engine managed runtime.
- Multi-tenant cedent portal.

### 2.4 Repository layout (public GitHub)

```
catsight/
├── backend/
│   ├── catsight_agent/          # ADK package (root_agent lives here)
│   │   ├── __init__.py          # from . import agent
│   │   ├── agent.py
│   │   └── tools/  exposure.py · loss_engine.py · retrieval.py
│   ├── app/main.py              # FastAPI: /api/analyses (SSE), /ask, /admin/ingest, /healthz
│   ├── ingest/  ingest_treaty.py · seed_portfolio.py
│   ├── data/synthetic/  treaties/*.pdf · exposures.csv · events/*.json · regions.geojson
│   ├── tests/  test_loss_engine.py · golden_set.json · test_eval.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                    # Vite + React + TS, react-leaflet, recharts
├── docs/  ARCHITECTURE.md · architecture.png · DECK.pdf · EXECUTION_PLAN.md
├── firebase.json · .firebaserc · firestore.indexes.json · firestore.rules
├── LICENSE (Apache-2.0)  ·  .gitignore  ·  README.md
```

### 2.5 Core code skeleton (backend/catsight_agent/agent.py)

```python
import os
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search
from .tools.exposure import match_treaties
from .tools.loss_engine import estimate_layer_losses
from .tools.retrieval import search_treaty_clauses

MODEL = os.getenv("MODEL_MAIN", "gemini-3.5-flash-lite")        # retires Jul 2027+
MODEL_REASON = os.getenv("MODEL_REASON", "gemini-3.8-flash")    # wording_checker only
# NOTE (ADK 2.x): SequentialAgent still works but is deprecated -> try Workflow(edges=[("START", ...)]) on Day 6.
# Add generate_content_config with HttpRetryOptions + ThinkingConfig(thinking_level=LOW) to each agent.

event_intel = LlmAgent(
    name="event_intel", model=MODEL, tools=[google_search], output_key="event",
    instruction="Identify the catastrophe in the user's request. Return ONLY JSON with keys "
                "name, peril, start, end, duration_h, regions[{code,intensity_band}], sources[].",
)
exposure_analyst = LlmAgent(
    name="exposure_analyst", model=MODEL, output_key="impact",
    tools=[match_treaties, estimate_layer_losses],
    instruction="Event: {event}. Call match_treaties, then estimate_layer_losses. "
                "Never compute numbers yourself; report tool outputs verbatim as JSON.",
)
wording_checker = LlmAgent(
    name="wording_checker", model=MODEL_REASON, output_key="wording_flags",
    tools=[search_treaty_clauses],
    instruction="For each treaty in {impact}, search its hours clause, peril exclusions and "
                "territorial scope. Compare with event duration in {event}. Cite page and clause.",
)
reporter = LlmAgent(
    name="reporter", model=MODEL, output_key="report",
    instruction="Write an indicative exposure flash report from {event}, {impact}, "
                "{wording_flags}. Every claim must carry a citation. State assumptions.",
)
root_agent = SequentialAgent(
    name="catsight_pipeline",
    sub_agents=[event_intel, exposure_analyst, wording_checker, reporter],
)
```

Retrieval tool core (Firestore vector search):

```python
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from google.cloud.firestore_v1.vector import Vector

def search_treaty_clauses(treaty_id: str, query: str) -> list[dict]:
    qvec = embed(query, task_type="RETRIEVAL_QUERY")   # gemini-embedding-001, output_dimensionality=768, L2-normalise
    docs = (db.collection("treaty_chunks")
              .where(filter=FieldFilter("treaty_id", "==", treaty_id))
              .find_nearest(vector_field="embedding", query_vector=Vector(qvec),
                            distance_measure=DistanceMeasure.COSINE, limit=4).get())
    return [{"page": d.get("page"), "clause": d.get("clause_type"), "text": d.get("text")} for d in docs]
```

---

## 3. Setup & Deployment Instructions

> **Run all `gcloud` commands in Google Cloud Shell (bash, free, pre-authenticated).** Windows PowerShell 5.1 mangles the embedded JSON quotes that some `gcloud` flags need. Use local PowerShell only for Python and npm development.

### 3.1 One-time tooling (local Windows machines)

```powershell
winget install Google.CloudSDK
winget install Python.Python.3.12
winget install OpenJS.NodeJS.LTS
npm install -g firebase-tools
gcloud auth login
gcloud auth application-default login
```

### 3.2 Project, billing, APIs (Cloud Shell)

```bash
export PROJECT_ID="techno-crackers-catsight"     # must be globally unique
export REGION="us-central1"                      # US region → Cloud Storage free tier applies
gcloud projects create $PROJECT_ID --name="CatSight"
gcloud billing accounts list                     # copy the Free Trial billing account ID
export BILLING_ACCOUNT="XXXXXX-XXXXXX-XXXXXX"
gcloud billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION

gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com aiplatform.googleapis.com firestore.googleapis.com \
  storage.googleapis.com logging.googleapis.com cloudtrace.googleapis.com \
  firebase.googleapis.com firebasehosting.googleapis.com billingbudgets.googleapis.com
```

### 3.3 Cost guardrails first (before any code)

```bash
gcloud billing budgets create --billing-account=$BILLING_ACCOUNT \
  --display-name="catsight-budget" --budget-amount=60USD \
  --threshold-rule=percent=0.25 --threshold-rule=percent=0.5 --threshold-rule=percent=0.9
```

> Budget alerts **notify only; they do not stop spending.** Hard limits come from `--max-instances`, the app's daily analysis cap (section 4.5), and **spend caps**. Spend caps are in Preview: Console → Billing → Budgets & alerts → spend cap, one each for **Agent Platform** and **Cloud Run** on this project. When a cap is hit, that service's usage pauses until you lift it. Caps count **gross** cost (credits ignored) and aren't instant, so set them at about $40 for Agent Platform and $20 for Cloud Run per month.

### 3.4 Data stores and identity

```bash
gcloud firestore databases create --location=$REGION --type=firestore-native
gcloud storage buckets create gs://$PROJECT_ID-docs --location=$REGION --uniform-bucket-level-access

gcloud iam service-accounts create catsight-run --display-name="CatSight Cloud Run SA"
export SA="catsight-run@$PROJECT_ID.iam.gserviceaccount.com"
for ROLE in roles/aiplatform.user roles/datastore.user roles/storage.objectAdmin \
            roles/logging.logWriter roles/cloudtrace.agent; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA" --role=$ROLE --condition=None
done
```

Vector index: **create it with `gcloud`** (command below). Firebase CLI has an open bug (firebase-tools #9385) that breaks vector-index reconcile. The JSON below is kept for reference only. **Don't** deploy `firestore:indexes` through Firebase CLI.

```json
{
  "indexes": [{
    "collectionGroup": "treaty_chunks",
    "queryScope": "COLLECTION",
    "fields": [
      { "fieldPath": "treaty_id", "order": "ASCENDING" },
      { "fieldPath": "embedding", "vectorConfig": { "dimension": 768, "flat": {} } }
    ]
  }],
  "fieldOverrides": []
}
```

`firestore.rules`: deny all client access. The backend uses its service account, so rules don't apply to it.

```
rules_version = '2';
service cloud.firestore { match /databases/{db}/documents { match /{doc=**} { allow read, write: if false; } } }
```

**Index command to run** (Cloud Shell). Pre-filtering must use **equality** filters only:

```bash
gcloud firestore indexes composite create --collection-group=treaty_chunks \
  --query-scope=COLLECTION --field-config=order=ASCENDING,field-path=treaty_id \
  --field-config='field-path=embedding,vector-config={"dimension":"768","flat":"{}"}' \
  --database="(default)"
```

### 3.5 Gemini smoke test (local, after `gcloud auth application-default login`)

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install "google-adk[eval,otel-gcp]==2.11.0" google-cloud-firestore google-cloud-storage fastapi "uvicorn[standard]" pydantic
python -c "from google import genai; c=genai.Client(enterprise=True, project='techno-crackers-catsight', location='global'); [print(m, c.models.generate_content(model=m, contents='ping').text[:40]) for m in ('gemini-3.5-flash-lite','gemini-3.8-flash')]"
```

Gemini 3.x Flash models are served **only from `global` (or the `us`/`eu` multi-regions), not `us-central1`** [VERIFIED]. Global is also about 10% cheaper. If `enterprise=True` isn't accepted by your installed google-genai, use `vertexai=True`.

### 3.6 Backend container and Cloud Run deploy

`backend/Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8080
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
```

Deploy (Cloud Shell, from `backend/`):

```bash
gcloud run deploy catsight-api --source . --region $REGION \
  --service-account $SA --allow-unauthenticated \
  --cpu 1 --memory 1Gi --concurrency 20 --timeout 300 \
  --min-instances 0 --max-instances 3 --cpu-boost \
  --set-env-vars GOOGLE_GENAI_USE_ENTERPRISE=true,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=global,MODEL_MAIN=gemini-3.5-flash-lite,MODEL_REASON=gemini-3.8-flash,DAILY_ANALYSIS_CAP=300,ALLOWED_ORIGINS=https://$PROJECT_ID.web.app
```

- `GOOGLE_GENAI_USE_ENTERPRISE` is current. `GOOGLE_GENAI_USE_VERTEXAI` is deprecated, and ENTERPRISE wins if both are set [VERIFIED].
- `GOOGLE_CLOUD_LOCATION=global` applies to Gemini calls. Cloud Run itself still runs in `$REGION` (us-central1), and Firestore and Cloud Storage stay in us-central1.
- Optional dev shortcut: `adk deploy cloud_run --project=$PROJECT_ID --region=$REGION --with_ui ./catsight_agent` deploys ADK's dev UI for internal testing. **Judges should see the custom UI, not this one.**

Keep Artifact Registry under its 0.5 GB free tier by deleting old images. Save this as `cleanup.json`:

```json
[{"name":"keep-recent","action":{"type":"Keep"},"mostRecentVersions":{"keepCount":3}},
 {"name":"delete-old","action":{"type":"Delete"},"condition":{"olderThan":"7d"}}]
```

```bash
gcloud artifacts repositories set-cleanup-policies cloud-run-source-deploy \
  --location=$REGION --policy=cleanup.json
```

### 3.7 Frontend on Firebase Hosting

```bash
firebase login
firebase projects:addfirebase $PROJECT_ID
firebase use $PROJECT_ID
cd frontend && npm create vite@latest . -- --template react-ts && npm install
npm install react-leaflet leaflet recharts
echo "VITE_API_BASE=$(gcloud run services describe catsight-api --region $REGION --format='value(status.url)')" > .env.production
npm run build && cd ..
firebase deploy --only hosting,firestore:rules     # vector index is created via gcloud (§3.4)
```

`firebase.json`:

```json
{
  "hosting": {
    "public": "frontend/dist",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [{ "source": "**", "destination": "/index.html" }]
  },
  "firestore": { "rules": "firestore.rules" }
}
```

**Why the frontend calls the Cloud Run URL directly (with CORS) instead of a Hosting → Cloud Run rewrite:** Hosting rewrites have a **hard 60-second timeout** (504 after that) [VERIFIED]. They also **don't stream SSE** [THIRD-PARTY, Firebase engineer]. Agent runs can exceed 60 s and stream, so the browser talks to `*.run.app` directly.

### 3.8 Safe updates during evaluation (Oct 19 – Nov 6)

Never break the URL the judges have. Deploy changes as a tagged, no-traffic revision and test it first:

```bash
gcloud run deploy catsight-api --source . --no-traffic --tag dev
gcloud run services update-traffic catsight-api --to-latest   # only after testing the dev URL
```

---

## 4. Financial Model — Free Tier vs Paid

### 4.1 Free allowances [VERIFIED unless noted]

| Service | Free allowance | Paid rate beyond it |
|---|---|---|
| **$300 Free Trial** | $300 credit, **90 days**, only for accounts that have **never** been paying GCP, Maps or Firebase users. Resources **stop** when credit or time runs out without upgrading. 30-day grace to recover. **Cannot request quota increases.** | — |
| ⚠️ Trial credit **excludes** | **"Gemini API in AI Studio"** charges and partner model-as-a-service. → **Call Gemini through Agent Platform / Vertex AI**, which the credit covers. | — |
| Cloud Run (request-based) | 2M requests/month, 360,000 GiB-seconds/month; 180,000 vCPU-seconds/month **[THIRD-PARTY, consistent with the Cloud Run pricing page]** | $0.000024 /vCPU-s, $0.0000025 /GiB-s, $0.40 /M requests (Tier-1 regions) **[THIRD-PARTY]** |
| Firestore | 1 GiB storage, 50K reads, 20K writes, 20K deletes **per day** | Per-operation pricing **[check the pricing page]** |
| Cloud Storage | 5 GB-months (**US regions only**), 5K Class A, 50K Class B operations | — |
| Cloud Build | 2,500 build-minutes/month | — |
| Artifact Registry | 0.5 GB/month | Small per-GB charge **[rate UNVERIFIED]** |
| Cloud Logging | 50 GiB/project/month | — |
| Secret Manager | 6 active versions, 10K accesses | (not needed: service-account auth) |
| Firebase Hosting | 10 GB storage, 360 MB/day transfer (Spark quotas) | Blaze pay-as-you-go beyond that |
| ~~Gemini 2.5 Flash / Flash-Lite~~ | — | **Retire on Agent Platform 2026-10-20. Don't use.** |
| **Gemini 3.5 Flash-Lite** (main) | No free tier on Agent Platform | **$0.30 in / $2.50 out** per 1M tokens (global endpoint) |
| **Gemini 3.8 Flash** (wording reasoning) | No free tier on Agent Platform | **$0.75 / $3.75** introductory through 2026-12-31, then $1.50 / $7.50 |
| Gemini 3.1 Flash-Lite (dev / cheap fallback) | — | $0.25 / $1.50 |
| gemini-embedding-001 | — | $0.15 per 1M tokens |
| Google Search grounding (Gemini 3.x) | **5,000 queries/month free** across Gemini 3 models | $14 per 1,000 queries |

> Prices verified on the Agent Platform pricing page on 2026-10-02 at the **global** endpoint. Non-global endpoints are about 10% higher. They match AI Studio paid prices. **Thinking tokens bill as output, and Gemini 3.5+ counts function declarations as input tokens.**

### 4.2 Unit cost per analysis [ESTIMATE]

Assumptions: about 7 model calls per analysis (4 agents plus tool-call turns), about 28K input and **6K output** tokens in total. Output is higher than before because thinking can't be fully disabled on Gemini 3 Flash; use `thinking_level=LOW`.

| Model mix | Input cost | Output cost | **Per analysis** |
|---|---|---|---|
| All 3.1 Flash-Lite (dev) | 28K × $0.25/M = $0.0070 | 6K × $1.50/M = $0.0090 | **≈ $0.016** |
| All 3.5 Flash-Lite | 28K × $0.30/M = $0.0084 | 6K × $2.50/M = $0.0150 | **≈ $0.023** |
| All 3.8 Flash (intro price) | 28K × $0.75/M = $0.0210 | 6K × $3.75/M = $0.0225 | **≈ $0.044** |
| **Production mix** (3.5 Flash-Lite, with wording_checker on 3.8 Flash ≈ 25% of tokens) | | | **≈ $0.028** |

Cloud Run compute per analysis: about 30 s × 1 vCPU = 30 vCPU-s. The free 180K vCPU-s covers **about 6,000 analyses/month** even with no request overlap. Concurrency 20 stretches that further.

### 4.3 Budget across the whole competition [ESTIMATE]

| Phase | Volume assumption | Gemini | Cloud Run / Firestore / Storage / Build / Hosting | Total credit used |
|---|---|---|---|---|
| Dev (Oct 2–17) | 2 people × 14 days × ~80 runs ≈ 2,200 runs (mostly 3.1 Flash-Lite) + ingestion + embeddings | $35–60 | $0 (within free tier) | **$35–60** |
| Evaluation (Oct 19 – Nov 6) | 100–500 judge runs on the production mix, replay mode cached | $3–14 | $0 | **$3–14** |
| Finale prep and Demo Day (Dec 4) | ~300 runs; optional min-instances=1 for the finale week (~$3) | ~$8 | ~$3 | **≈ $11** |
| Search grounding | Cached per event; 5,000 free queries/month on Gemini 3 | ≈ $0 | — | **≈ $0** |
| **Total** | | | | **≈ $50–85 of $300 → $0 cash** |

### 4.4 Scenarios

| Scenario | Cash cost | Notes |
|---|---|---|
| **A. Trial active, Gemini via Agent Platform (recommended)** | **$0** | About $50–85 of credit used. Upgrading keeps the remaining credit but **doesn't extend** the 90-day expiry [VERIFIED]. **Check your trial start date** (Billing → Credits). Trial activated Oct 2 ends about **Dec 31**, covering evaluation and the Dec 4 finale. Trial activated ~Sep 7 ends about **Dec 6**: too close. Upgrade to a paid account before expiry, or the live URL stops. |
| **B. Not trial-eligible** | **≈ $0–5** | Use the **AI Studio free tier** for Gemini 3.5 Flash-Lite and 3.8 Flash (API key in Secret Manager). 2.5 models are limited to existing users. **Search grounding is "Not available" on the 3.x free tier**, so use replay mode only. Run Cloud Run, Firestore and Hosting inside free tiers; a billing account is still required. Risks: rate limits that may cause 429s during judging (free-tier limits are not published statically; see aistudio.google.com/rate-limit), and free-tier data "used to improve our products". **Synthetic data only.** |
| **C. Abuse / runaway worst case (with caps)** | Bounded | max-instances 3 pegged 24/7 ≈ 3 × 86,400 × $0.0000265 ≈ **$6.9/day**. Gemini at a 300/day cap × $0.028 ≈ **$8.4/day**. Budget alerts fire at $15, $30 and $54. **Spend caps** pause Agent Platform and Cloud Run at the monthly limit. |

### 4.5 Cost-control rules (implement them, don't just document them)

1. `--min-instances 0` and `--max-instances 3`. Use `--cpu-boost` for faster cold starts.
2. A Firestore `usage/{yyyy-mm-dd}` counter enforces `DAILY_ANALYSIS_CAP`. When the cap is hit, the UI offers cached replay results.
3. Per-IP rate limit (e.g. 20 analyses per hour).
4. Use 3.1 Flash-Lite for dev, 3.5 Flash-Lite for production, and 3.8 Flash only for `wording_checker`. Set `thinking_level=LOW`.
4b. Set spend caps (Preview) on Agent Platform and Cloud Run (section 3.3).
5. Cache grounded events and use replay mode as the default "Try a demo" path.
6. Artifact Registry cleanup policy (section 3.6). Delete unused buckets and images after the competition.

---

## 5. Build Approach (replaces the day-by-day plan)

> **Changed 2026-10-02:** the team works on several projects at once, so there is **no fixed daily schedule**. Development is done by a Claude Code session using this reference pack:
> - [`/CLAUDE.md`](../CLAUDE.md)
> - [`REQUIREMENTS.md`](REQUIREMENTS.md): the build spec, with requirement IDs and acceptance criteria
> - [`BUSINESS_IMPACT.md`](BUSINESS_IMPACT.md)
> - [`RESEARCH_FINDINGS.md`](RESEARCH_FINDINGS.md)
> - [`DOMAIN_PRIMER.md`](DOMAIN_PRIMER.md)
>
> **Team target: submit by Oct 15, 2026** (official deadline Oct 18, 23:59 IST). Registration is complete.

**Build phases.** Each phase ends in a deployable state. The order is set in REQUIREMENTS.md §11.

| Phase | Outcome | Exit check |
|---|---|---|
| P0 Foundations | GCP project, budget + spend caps, hello-world on Cloud Run + Firebase Hosting, fresh public repo | Live URL loads |
| P1 Data | Synthetic portfolio, treaty wordings (PDF), event replay files, region GeoJSON | Seed script loads Firestore |
| P2 Core engine | Treaty extraction, chunk + embed + vector index, deterministic loss engine with unit tests | `pytest` green; worked example matches |
| P3 Agents | ADK pipeline (event_intel → exposure_analyst → wording_checker → reporter) + SSE API | End-to-end run on Jebi replay |
| P4 UI | Event picker, agent timeline, map, treaty table, layer chart, citation panel, export | Full demo flow in browser |
| P5 Quality | Hardening, eval harness, benchmarks B1–B7, observability | Benchmark table filled |
| P6 Deliverables | README, architecture doc, deck, video, submission | Everything on the REQUIREMENTS §12 checklist ✔ |

**Human-only tasks** (not delegable to Claude Code): GCP billing and trial check, Discord questions, practitioner interviews, the manual benchmark run (B1), video recording and voice-over, the submission form.

<details><summary>Original day-by-day plan (superseded, kept for reference)</summary>

| Day | Date | Member A (Backend / Data / AI) | Member B (Frontend / Deploy) | Joint gate |
|---|---|---|---|---|
| D1 | **Fri Oct 2** | Create GCP project, billing, APIs, **budget + spend caps**. Check trial start date. Gemini smoke test on **`global`** with 3.5 Flash-Lite and 3.8 Flash. | **Fresh** public GitHub repo (no pre-Sep-7 code), monorepo scaffold, LICENSE, `.gitignore`. Deploy a hello-world FastAPI to Cloud Run and a Vite app to Hosting → **live URL on Day 1**. | Confirm Hack2skill team registration (**T&C roster lock Oct 4**). Lock the idea. Post Discord questions. Check employment-contract IP terms. |
| D2 | Sat Oct 3 | Firestore schema. `seed_portfolio.py`: ~30 synthetic treaties (CAT XL multi-layer, QS) and exposures across JP/PH/TW admin-1 regions, **scaled to GIROJ prefecture sums insured** (calibration only; don't commit GIROJ files). Preprocess the **IBTrACS v04r01 WP CSV** into per-event JSON (filter by SID; skip the units row). | Wireframes. App shell, routing, design tokens. Map with **Natural Earth 10m admin-1** cut to JPN/PHL/TWN, simplified with mapshaper to about 55–87 KB. | Check Dashboard Forms/Resources for credits, a deck template and form fields. |
| D3 | Sun Oct 4 | Write 6–8 synthetic treaty wordings as PDFs, **paraphrased from public SEC-filed Cat XL contracts**, with deliberately different hours clauses (72 / 96 / 120 / 168h), exclusions, territory and reinstatements. Structured extraction with `response_schema` from `gs://` URIs. | Portfolio pages (treaty list and detail with extracted terms). Upload UI. | **Roster lock (T&C) today.** |
| D4 | Mon Oct 5 | Chunking, embeddings (768-dim), vector index, `search_treaty_clauses`. Retrieval tests. | Deploy script / Cloud Build trigger, env config, CORS, error states, `/healthz`. | |
| D5 | Tue Oct 6 | Deterministic `loss_engine.py` (country-specific damage curves based on Emanuel/Eberenz; Japan far flatter than the Philippines) and `match_treaties`, with **hand-calculated unit tests** (DOMAIN_PRIMER §8). Practitioner calls. | Event analysis page layout: event picker, impacted-treaty table, layer-burn chart (Recharts). | |
| D6 | Wed Oct 7 | ADK 2.x: try `Workflow` graph (fall back to `SequentialAgent`). `event_intel` (search grounding only + event cache) and `exposure_analyst`. Retries, `thinking_level=LOW`. Test with `adk web`. | SSE client and live **agent timeline** component (shows each agent step as it runs). | |
| D7 | Thu Oct 8 | `wording_checker` and `reporter`. Citation JSON contract. Stateless `/ask` follow-up endpoint. | Citation side panel (click → clause text and page). Map heat by intensity and exposure. | |
| D8 | **Fri Oct 9** | Integration fixes. | Integration fixes. | **🚦 GATE: end-to-end MVP on the live URL.** If not working, switch to replay-only mode (section 1.5 fallback). |
| D9 | Sat Oct 10 | Replay mode: cache Jebi 2018 (`2018239N11161`), Hagibis 2019 (`2019278N16165`), Haiyan 2013 (`2013306N07162`), and Noto 2024 (USGS `us6000m0xl`, ShakeMap `grid.xml` sampled at region centroids). Golden set (15 cases) + planted-clause ground truth. `pytest` + `adk eval`. | PDF/Markdown report export. Accessibility pass. Responsive layout. **Benchmark B1: timed manual control run** (BUSINESS_IMPACT §3.2). | |
| D10 | Sun Oct 11 | Hardening: retries, timeouts, Pydantic validation, prompt-injection guard, daily cap and rate limit. **Benchmarks B3–B5** (accuracy, wording flags, back-test against GIAJ/JER). | Structured logging, Cloud Trace, one-click **"Try a demo event"**. `docs/ARCHITECTURE.md` + diagram. | |
| D11 | Mon Oct 12 | Fix user-test findings. Cost-per-analysis and latency stats from logs (B2, B6). | README. Deck v1 (incl. impact and benchmark slides). Video script. | User test with 2–3 outsiders (ideally one insurance colleague). |
| D12 | **Tue Oct 13** | Final benchmark table into the deck. Freeze prompts. | Record the video (target 2:45). Edit and add captions. | **🧊 FEATURE FREEZE.** (Bordereaux stretch dropped.) |
| D13 | Wed Oct 14 | Repo hygiene: secret scan, remove dead code, pin requirements. | Deck final (PDF). Incognito and mobile test of the live URL. | Full dry run of the submission form. |
| D14 | **Thu Oct 15** | — | — | **📤 SUBMIT** (live URL, public repo, video < 3 min, deck, BFSI). Tag `submission-2026-10-15`. |
| D15–D17 | Oct 16–18 | Buffer only. **No production deploys.** | Buffer only. LinkedIn post. | Official deadline Oct 18, 23:59 IST. |
| After | Oct 19 → Dec 4 | Keep prod untouched. Watch budget and logs weekly. | Same. | Upgrade billing before trial expiry if needed. Prepare finale demo if shortlisted (Nov 7). |

</details>

---

## 6. Rubric Alignment Matrix

| Criterion (weight) [VERIFIED wording] | How CatSight answers it | Evidence we show judges |
|---|---|---|
| **Technical Merit & Gen AI Implementation (40%)**: "meaningful use of Gen AI… contributes directly to solving the problem"; "functional, technically sound"; "scalability & sustainability" | 4-agent ADK pipeline. Structured extraction. Firestore vector RAG with citations. Search grounding. Deterministic loss engine (no LLM maths). Eval harness. Serverless and cost-capped. | Live URL. Architecture slide. Eval-metrics slide (precision/recall, citation accuracy, latency, cost per analysis). Repo tests. |
| **Problem Alignment & Impact (25%)**: "addresses the chosen problem statement"; "clear and meaningful value" | Maps directly to the BFSI text "detecting and mitigating… risk, automating complex processes". Turns a multi-day manual first view into minutes (state this as **our hypothesis**, not a sourced fact). | Problem slide in the voice of a reinsurance practitioner (your experience). Before/after workflow. JAPAC cat context. |
| **Innovation & Creativity (25%)**: "fresh perspective… differentiation"; "beyond a basic or superficial implementation" | A rare reinsurance niche. Fuses live event intelligence, treaty-wording reasoning (hours-clause vs event duration) and layer maths. | Demo moment: hours-clause flag with a highlighted citation. A "why not just ChatGPT?" slide. |
| **User Experience & Solution Design (10%)**: "intuitive… accessible"; "components work together cohesively" | One-click demo event. Streaming agent timeline. Map, table and chart. Citation panel. Human approval step. Accessibility pass. | Video. Fresh-browser test. |

### Mandatory deliverables checklist

- [ ] **Working deployed link** (Firebase Hosting URL; backend on Cloud Run). Tested in incognito and on mobile.
- [ ] **Public GitHub repository**: README, setup steps, architecture, license, no secrets.
- [ ] **Video demo strictly under 3 minutes** (T&C), as a public YouTube, Vimeo or Drive link. Prefer YouTube (unlisted or public). Aim for **2:45**. English.
- [ ] **Deck (PDF)** "explaining the solution architecture and business case" (T&C), including the architecture diagram and data flow. Use the Hack2skill template if one is on the dashboard. Map each slide explicitly to the rubric wording, since pre-screening may be partly AI-assisted.
- [ ] Git tag `submission-2026-10-18` on the submitted commit. Data licences and attributions in the README (NOAA IBTrACS DOI, USGS, Natural Earth, JMA if used, GIROJ/e-Stat citations).
- [ ] Post the build on LinkedIn (Social Choice Award).
- [ ] **Category specification:** "BFSI: Intelligent Risk, Fraud & Financial Experiences" (confirm the format with the organizers; see section 0).
- [ ] Architecture document: `docs/ARCHITECTURE.md` + PNG (not explicitly required; included defensively).

### Video storyboard (2:45)

| Time | Scene |
|---|---|
| 0:00–0:20 | Hook: "A typhoon just made landfall. The CRO asks: what's our exposure?" Today: spreadsheets and days. |
| 0:20–0:35 | CatSight one-liner and the BFSI theme. |
| 0:35–2:00 | Live demo: pick Typhoon Jebi → agent timeline → map → impacted treaties → layer burn → click the hours-clause citation → follow-up question "Which layers exhaust?" |
| 2:00–2:25 | Architecture in 20 seconds, plus eval metrics and cost per analysis. |
| 2:25–2:45 | Impact, roadmap, live URL and repo on the end card. |

### Deck outline (10–12 slides)

1. Title and team
2. Problem (practitioner voice)
3. Who suffers and the gap
4. Solution
5. Demo screenshots
6. Architecture
7. Agent workflow
8. Responsible AI (citations, deterministic maths, human-in-the-loop, synthetic data)
9. Evaluation results
10. Cost and scalability
11. Roadmap
12. Theme alignment

---

## 7. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Trial not available (account previously paid) | Scenario B (AI Studio free tier + free tiers, synthetic data only). |
| Gemini 429s during judging (trial cannot request quota increases) | Retry with backoff, replay-mode cache, and Flash-Lite fallback. |
| Judges unfamiliar with reinsurance | 20-second plain-English framing in the video. Glossary tooltip in the UI. |
| Loss numbers look like an actual cat model | "INDICATIVE — illustrative damage ratios" label. Assumptions panel. |
| Scope overrun | Oct 9 gate, replay-only fallback, Oct 15 freeze. |
| Real client data leakage | **Synthetic data only.** No employer or client documents in the repo or prompts. |
| Deadline timezone unknown | Submit Oct 17. |
| Trial expires before Dec 4 finale | Check the start date Day 1. Upgrade billing before expiry. |

---

## 8. Still Unverified / Unavailable

Updated after the 2026-10-02 research. Full details and the human-action list are in [RESEARCH_FINDINGS.md](RESEARCH_FINDINGS.md) §F.

1. Number of finalists ("Top 50" not found). About 19.5k registrants.
2. ~~Deadline timezone~~ → **resolved: 23:59 IST Oct 18.**
3. Category-specification format (official text is leftover template). Ask the organizers.
4. ~~Standalone architecture document~~ → **resolved: not required; architecture must be in the deck.**
5. Organizer-provided GCP credits. Check the dashboard Forms tab.
6. ~~Agent Platform vs AI Studio prices~~ → **resolved: identical at the global endpoint.**
7. Throughput for brand-new trial accounts below $10 spend (expect best-effort; handle 429s).
8. Roster lock: Oct 4 (T&C) vs Oct 11 (site). Register by Oct 4.
9. Live-URL availability and updates after submission: not specified.
10. Industry-gap statistics are from vendor or trade sources. The domain section now has stronger primary sources (MAS, Aon survey, Moody's, PERILS, Verisk PCS, SEC filings).

## Sources

- Official: [aibuildercup.com](https://aibuildercup.com/) · [Themes & judging](https://aibuildercup.com/themes.html) · [FAQs](https://aibuildercup.com/Faqs.html)
- Google Cloud: [Free Trial & Free Tier](https://docs.cloud.google.com/free/docs/free-cloud-features) · [Cloud Run pricing](https://cloud.google.com/run/pricing) · [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing) · [Gemini rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) · [ADK Cloud Run deploy](https://adk.dev/deploy/cloud-run/) · [Firestore vector search](https://docs.cloud.google.com/firestore/docs/vector-search) · [Firebase pricing](https://firebase.google.com/pricing) · [Gemini embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- Context: [Gemini Enterprise Agent Platform rebrand (HPCwire)](https://www.hpcwire.com/aiwire/2026/04/23/google-unveils-gemini-enterprise-agent-platform/) · [Deadline change noted (GitHub PR)](https://github.com/williamlabdev/context-rail/pull/9)
- Industry (third-party): [V7 Labs bordereaux guide](https://www.v7labs.com/blog/insurance-bordereaux-guide) · [reinsured.ai bordereaux guide](https://www.reinsured.ai/resources/guides/bordereaux-automation-guide) · [NRF 2025 Returns Landscape](https://nrf.com/research/2025-retail-returns-landscape) · [IHL inventory distortion](https://www.ihlservices.com/news/analyst-corner/2025/09/retail-inventory-crisis-persists-despite-172-billion-in-improvements/) · [Retail Insight Network on IHL](https://www.retail-insight-network.com/features/how-overstock-stockouts-and-returns-cost-retail-1-75tn/)
