# CatSight — Pre-Development Research Findings

> Research date: **2026-10-02**. Five parallel research streams covered:
> - **A.** Hackathon rules
> - **B.** Google Cloud pricing and limits
> - **C.** ADK / Firestore / Gemini technical details
> - **D.** Data sources
> - **E.** Reinsurance domain and competitors
>
> Tags:
> - **[V]** = verified on an official or primary source (organizer, Google docs/source code, data publisher, regulator, court or law-firm summary, SEC filing)
> - **[3P]** = third-party or secondary source
> - **[NF]** = not found
> - **[CALC]** = our own calculation
>
> Things only a human can answer are listed in section F.

---

## ⚠️ Decision changes (read first)

| # | Finding | Impact | New decision |
|---|---|---|---|
| 1 | **Gemini 2.5 Flash and 2.5 Flash-Lite retire on Agent Platform (Vertex) on 2026-10-20** [V]. AI Studio is also limiting 2.5 to existing users [V]. | The model in the original plan would die before evaluation starts (Oct 19). | Use **`gemini-3.5-flash-lite`** (retires "July 21, 2027 or later") as the main model. Use **`gemini-3.8-flash`** for the wording reasoning step. Make the model name an env var. |
| 2 | Gemini 3.x Flash models are **not served from `us-central1`**. They are on `global` (and `us`/`eu` multi-regions) only [V]. Global is also about 10% cheaper [V]. | The original smoke test and env vars would fail. | `GOOGLE_CLOUD_LOCATION=global` for Gemini. Cloud Run stays in `us-central1`. |
| 3 | **Deadline is 2026-10-18 23:59 IST** (18:29 UTC = 02:29 Oct 19 SGT) [V, Hack2skill API]. | Removes the timezone ambiguity. | Still submit Oct 17. |
| 4 | **The official T&C says rosters lock on October 4.** The site and FAQ say Oct 11 [V]. | Possible disqualification risk. | **Finalise team registration by Oct 4.** Get written confirmation from support. |
| 5 | T&C: "**Submissions must consist exclusively of fresh code** … created during the official hackathon timeline" [V]. | Templates or code from before Sep 7 are not allowed. | Fresh repo. All commits dated after Sep 7. Open-source libraries are fine. |
| 6 | T&C grants Hack2skill a **6-month right of first refusal** on an exclusive licence to all submitted materials, and broad publication rights [V]. | IP and confidentiality. | Treat the submission as public. No employer or client material. Check your employment contract. |
| 7 | ADK is at **2.11.0** (released today). `SequentialAgent` / `ParallelAgent` are **deprecated in favour of graph `Workflow`** but still work [V]. | Design and API changes. | Pin `google-adk==2.11.0`. Try `Workflow` in the Day-6 spike. Fall back to `SequentialAgent` if needed. |
| 8 | Firebase Hosting rewrites have a **hard 60 s timeout** [V] and **don't stream SSE** [3P, Firebase engineer]. | Can't proxy agent runs through Hosting. | Confirms the plan: the frontend calls the Cloud Run URL directly, with CORS. |
| 9 | Firebase CLI has an **open bug with vector indexes** in `firestore.indexes.json` [V, firebase-tools #9385]. | Index deploy may break. | Create the vector index with **`gcloud`**. Firebase CLI deploys only the rules. |
| 10 | **Spend-cap budgets (Preview)** can **pause** Agent Platform and Cloud Run usage automatically [V]. | A real hard cost limit. | Add spend caps for Agent Platform and Cloud Run. |
| 11 | The IBTrACS BigQuery public table **stopped updating in May 2024** [3P, NOAA staff on the forum]. The CSV v04r01 is updated 3× per week [V]. | A BigQuery-only approach would miss recent events. | Preprocess the IBTrACS **CSV** offline into small per-event JSON files. |
| 12 | **Real Cat XL wordings vary: 72 / 96 / 120 / 168-hour clauses** (SEC-filed contracts) [V]. The cedent chooses the start time [V]. | Strengthens the core innovation claim. | The wording checker must *extract* the hours clause, never assume 72h. |

---

## A. Hackathon rules and submission

**Primary sources:**
- [aibuildercup.com](https://aibuildercup.com/) · [themes](https://aibuildercup.com/themes.html) · [FAQs](https://aibuildercup.com/Faqs.html) · [rewards](https://aibuildercup.com/rewards.html)
- [Official T&C (Google Doc linked from the homepage)](https://docs.google.com/document/d/e/2PACX-1vRm7ChZ6Ij9fG7uFDkxzUMpwgVeBmnQ6cMDnAIEEX84AiLBOOQ9cYbl3S5OzFBbcVb8TF55s-eVpiXb/pub)
- [Hack2skill event API](https://hack2skill.com/api/v1/event/aibuildercup2026/event-details)

### A1. Timeline [V]

| Milestone | Value |
|---|---|
| Registration end | `registrationEnd 2026-10-11T18:29Z` (Oct 11, 23:59 IST). **T&C says rosters lock Oct 4** (stale text?) |
| Submission end | `submissionEnd 2026-10-18T18:29Z` (Oct 18, 23:59 IST). See the conversion table below. |
| Evaluation | Oct 19 – Nov 6 |
| Finalists announced | Nov 7 |
| Demo Day | Dec 4, Singapore |

Submission deadline in other time zones:

| Location | Local time |
|---|---|
| Singapore | 02:29 Oct 19 |
| Tokyo | 03:29 Oct 19 |
| Sydney | 05:29 Oct 19 |

### A2. Mandatory artifacts (T&C) [V]

- a) Working deployed live URL (Cloud Run / GCP / Firebase).
- b) Video **"strictly under three (3) minutes"**, as a public YouTube, Vimeo or Google Drive link.
- c) Public GitHub repo.
- d) "A comprehensive presentation deck explaining the **solution architecture and business case**", as a PDF. Everything must be in English.
- No separate architecture document is required. **Architecture must be in the deck.** Put it in the README as well, as past winners did.

### A3. Category specification [V]

The themes page text ("Healthcare, Education, Sustainability, Accessibility, Social Good") is **leftover template text**. The footer still reads "© Gen AI Academy APAC Edition". No clarification was found [NF].

Label the submission "Theme: BFSI – Intelligent Risk, Fraud & Financial Experiences" plus a one-line problem statement. Check whether the form uses a dropdown.

### A4. Data rules [V]

- No clause covers synthetic data [NF].
- T&C: participants "must not use any content protected under third party rights or subject to confidentiality obligations".
- Data security follows India's IT Act.
- → Use a synthetic portfolio and public data with licences cited.

### A5. Live URL after submission

- No rule found on keeping the URL live or on updates after submission [NF].
- Keep it live through Dec 4.
- Tag the submitted commit `submission-2026-10-18`.
- Don't change production visibly during evaluation without asking.

### A6. Credits

- None found on the official site or T&C [NF].
- One third-party site claims credits but cites no source [3P].
- In Hack2skill's sister event (Gen AI Academy APAC), credits were claimed through the **dashboard "Forms" tab** [V]. → Check the dashboard.

### A7. Tools and code

- Must be built "**primarily** using the Google Cloud tech stack" [V].
- Non-Google tools are not banned. Keep Gemini as the core reasoning engine and avoid non-Google LLMs on the main path.

### A8. IP and legal [V]

- **Right of first refusal:** Hack2skill gets 6 months of first refusal on any exclusive licence of the submitted software, code, docs, data and concepts.
- **Publication rights:** a worldwide right to publish the ideas.
- **Media:** photos and video of participants may be used for 10 years.
- **Other terms:** judges' decisions are final, prize money is subject to TDS (Indian tax withholding), and ID and employment checks can happen at any time.
- Not found [NF]: an employer-consent clause, a governing-law clause.

### A9. Prizes [V] and competition size

| Award | Prize |
|---|---|
| Winner | $10,000 |
| 1st runner-up | $7,000 |
| 2nd runner-up | $5,000 |
| Best use of Google Cloud AI tools | $2,000 |
| Most Impactful Solution | $2,000 |
| Social Choice Award | $2,000 |
| Best UI/UX | $2,000 |

- Travel and stay are covered for at most 2 members; visa costs are yours.
- **Number of finalists:** [NF].
- **Registrations:** about **19,496** (Hack2skill API counter) [V].

### A10. Judges

- "Judging panel to be announced closer to the Grand Finale" [V].
- The Hack2skill platform has an **AI-evaluation admin module** (seen in the site's JavaScript). Pre-screening may be partly automated [inference]. → Make the README and deck map **explicitly** to the rubric wording.

### A11. Support [V]

- Discord: https://discord.gg/x5GRzJbKpa
- Email: support+aibuildercup@hack2skill.com
- Phone/WhatsApp: +91 98703 30830
- Online walkthrough sessions are announced on the dashboard.
- Side activity: "Prompt your jersey".

### A12. Lessons from past Hack2skill × Google Cloud winners

**Examples:**
- **Gen AI Exchange 2025:** about 270k developers, Top 100 finale, a 30-expert jury [V].
  - Winners included domain-specific agentic tools: cement-plant optimisation, PitchLense (AI startup risk analyst), and a RAG legal assistant.
  - The PitchLense README had architecture and flow diagrams, a tech-stack graphic, a YouTube demo and a custom domain [3P].
- **Gen AI Academy APAC 2026:** the #3 project was a "production-grade autonomous multi-agent" ADK + Cloud Run + MCP + AlloyDB platform [3P].
- **ADK Hackathon 2025 (Devpost):** winners were multi-agent systems (SalesShortcut, GreenOps, TradeSageAI) [V].

**Patterns:**
- Multi-agent ADK with a visible orchestration trace is now the baseline.
- Winners lead with quantified impact and a named user.
- They look production-ready: auditability, CI/CD, IAM, a clean README.
- Decks run about 10–15 slides.
- Videos: about 20 s problem, about 2 min live demo, about 20 s architecture and impact.
- **Social Choice prize:** post the build on LinkedIn.

---

## B. Google Cloud pricing and limits

**Primary sources:**
- [Agent Platform pricing](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing)
- [Model versions](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-versions)
- [Cloud Run pricing](https://cloud.google.com/run/pricing)
- [Free Trial](https://docs.cloud.google.com/free/docs/free-cloud-features)
- [Firebase Hosting + Cloud Run](https://firebase.google.com/docs/hosting/cloud-run)
- [Firestore pricing](https://cloud.google.com/firestore/pricing)
- [Spend caps](https://docs.cloud.google.com/billing/docs/how-to/budgets-spend-caps)

### B1. Gemini on Agent Platform, Standard PayGo (per 1M tokens, ≤200K context) [V]

| Model | Input (global) | Output (global) | Non-global | Endpoints | Retirement |
|---|---|---|---|---|---|
| gemini-2.5-flash | $0.30 | $2.50 | same | global + us-central1 etc. | **2026-10-20** |
| gemini-2.5-flash-lite | $0.10 | $0.40 | same | global + us-central1 etc. | **2026-10-20** |
| **gemini-3.5-flash-lite** | **$0.30** | **$2.50** | $0.33 / $2.75 | global, us, eu | July 21, 2027 or later |
| gemini-3.1-flash-lite | $0.25 | $1.50 | $0.275 / $1.65 | global, us, eu | May 7, 2027 or later |
| gemini-3.5-flash | $1.50 | $9.00 | $1.65 / $9.90 | global, us, eu | May 19, 2027 or later |
| **gemini-3.8-flash** (also 3.6, 3.7) | **$0.75** (intro to Dec 31, 2026), then $1.50 | **$3.75**, then $7.50 | $0.825 / $4.125 | global, us, eu | none announced; "short-term", ≥45 days' notice |
| gemini-embedding-001 | $0.15 | — | — | global | no sooner than May 20, 2028 |
| gemini-embedding-2 | $0.20 (text) | — | — | global, us, eu | GA, no date |

- Prices match AI Studio's paid tier at the global endpoint [V].
- **Thinking tokens are billed as output** [V]. On Gemini 3, thinking **can't be fully disabled on Flash**. Use `thinking_level=LOW` [V].
- "Starting with Gemini 3.5, **function declarations are included in the input token count**" [V]. Tool-heavy ADK agents therefore cost more input tokens.
- Only HTTP 200 responses are billed [V].

### B2. Grounding with Google Search [V]

- **Gemini 3.x:** 5,000 grounding *queries* per month free across all Gemini 3 models, then $14 per 1,000. One prompt can trigger several queries. Grounding input tokens are not charged.
- **2.x:** 1,500 grounding *prompts* per day free, then $35 per 1,000.

### B3. Quotas [V]

- Standard PayGo has no fixed per-project quota. Throughput tiers depend on 30-day spend: Flash/Flash-Lite **Tier 1 ($10–250) = 2M TPM**, and there is no RPM limit.
- A 429 means "temporary high contention". Remedies: backoff, the global endpoint, smoothing traffic.
- Throughput below $10 of spend (a new trial account) [NF]. Expect best-effort throughput early on.
- **Trial credits:** they can't pay for Gemini API in AI Studio or for partner models. Agent Platform Gemini is *not* on the exclusion list, so it's covered (inferred). The trial can't request quota increases.
- **Express mode:** a separate no-billing 90-day tier (10 RPM, 2.5 models only). Not useful to us.

### B4. Cloud Run [V]

- **Free tier (request-based billing, per billing account):** 180,000 vCPU-s, 360,000 GiB-s, 2M requests per month, 1 GiB egress (North America).
- **Tier 1 prices:**

  | Resource | Active | Idle min-instance |
  |---|---|---|
  | vCPU | $0.000024/s | $0.0000025/s |
  | Memory | $0.0000025 per GiB-s | $0.0000025 per GiB-s |
  | Requests | $0.40 per 1M | — |

- **One warm min-instance** (1 vCPU / 1 GiB) at idle rates: about **$13/month** [CALC: 0.000005 × 2.63M s].
- **Timeout:** default 300 s, up to 3600 s.
- **Streaming:** supported with no configuration needed (chunked transfer). Requests are downgraded to HTTP/1.1 at the container by default. An open SSE stream is billed as an active request.
- **`--cpu-boost`:** extra CPU during startup plus 10 s after (≤1 vCPU is boosted to 2). The boost is billed.

### B5. Firebase Hosting [V]

- **60 s hard timeout** on rewrites to Cloud Run (504 after that).
- SSE / streaming is **not supported** through rewrites [3P, Firebase engineer, 2022; no newer doc found].
- Linking billing upgrades the project to Blaze automatically.
- Dynamic responses default to `Cache-Control: private`.
- Cookies are stripped except `__session`.

### B6. Storage and databases [V]

| Service | Free | Beyond free |
|---|---|---|
| Artifact Registry | 0.5 GiB | ≈ $0.10 per GiB-month |
| Firestore (one free database per project) | 1 GiB storage, 50K reads/day, 20K writes/day, 20K deletes/day | reads $0.03, writes $0.09, deletes $0.01 per 100K |
| Cloud Storage (us-east1, us-west1, us-central1 only) | 5 GB-months, 5K Class A ops, 50K Class B ops, 100 GB egress (North America) | — |

- **Firestore vector search billing:** 1 read per batch of up to 100 kNN index entries read, plus 1 read per returned document.

### B7. Cost controls [V]

- Alert-only budgets **don't cap** spending.
- **Spend caps (Preview):**
  - What they do: they pause the chosen services until you lift the cap manually.
  - Services: Gemini API, Agent Platform, Cloud Run, and Cloud Run functions.
  - Limits: one project and one service per cap, monthly.
  - **They count gross cost (credits are ignored),** and enforcement isn't instant.
- The "disable billing via Pub/Sub" pattern exists but **shuts down all resources**. Too destructive for us.

### B8. Upgrading the trial [V]

- Upgrading keeps your unused credit, but it still expires **90 days after trial signup**.
- Resources keep running, usage beyond the credit goes on the card, and quota increases are unlocked.

---

## C. ADK, Firestore and Gemini technical details

**Primary sources:**
- [PyPI google-adk](https://pypi.org/project/google-adk/) · [ADK 2.0](https://adk.dev/2.0/)
- [Tool limitations](https://adk.dev/tools/limitations/) · [LLM agents](https://adk.dev/agents/llm-agents/) · [Graphs/Workflow](https://adk.dev/graphs/) · [Events](https://adk.dev/events/)
- [Evaluate](https://adk.dev/evaluate/) · [Traces](https://adk.dev/observability/traces/) · [Gemini models in ADK](https://adk.dev/agents/models/google-gemini/)
- [Firestore vector search](https://docs.cloud.google.com/firestore/native/docs/vector-search) · [Gemini embeddings](https://ai.google.dev/gemini-api/docs/embeddings) · [Document processing](https://ai.google.dev/gemini-api/docs/document-processing)

### C1. ADK version [V]

- `google-adk` **2.11.0** (2026-10-02). 2.0 GA was 2026-05-19.
- Releases are about weekly → **pin exact versions**.
- Requires Python ≥3.10 and `google-genai >=2.19,<3`.
- **Breaking changes to note:**
  - In 2.0, custom `_run_async_impl` overrides are ignored by `Workflow`.
  - From 2.9, `InMemorySessionService` raises `SessionNotFoundError`, and failed workflow nodes re-run on resume, so make tools **idempotent**.
  - 2.9 added `FallbackModel` for model failover.

### C2. Built-in `google_search` [V]

- Built-in tools "exclude the use of any other tools in that agent" by default.
- ADK Python escape hatch: `GoogleSearchTool(bypass_multi_tools_limit=True)`, which wraps search into a sub-agent automatically. Or use `AgentTool(agent=search_agent)` explicitly.
- Gemini 3 can combine built-in tools with function calling natively (Preview, Gemini API). Vertex support is [NF].
- **Our design:** `event_intel` has only `[google_search]` plus an `output_key`, with `disallow_transfer_to_parent/peers=True`.

### C3. `output_schema`, `output_key` and templating [V]

- ADK now supports **`output_schema` together with tools**: tools are used during the thought loop and the structure is enforced on the final output. It's native on Gemini 3; other models get an "unreliable" fallback.
- `output_key` saves the final response to state, or the parsed object if a schema is set.
- **Templating:** `{key}`, optional `{key?}`, `{artifact.name}`. Use an `InstructionProvider` when you need literal braces.
- Since 2.10, `${var}` and `\{var}` are left as written.

### C4. Orchestration and streaming [V]

- `SequentialAgent` is deprecated in favour of `Workflow`, which "cannot yet be used as an LlmAgent sub-agent". It still works.
- 2.x form: `Workflow(name="root", edges=[("START", event_intel, exposure_analyst, wording_checker, reporter)])`. `{key}` templating still works.
- **Runner:** `Runner(app_name=, agent=, session_service=, auto_create_session=False)` and `run_async(user_id=, session_id=, new_message=, run_config=RunConfig(streaming_mode=StreamingMode.SSE))`.
- **Event helpers:** `author`, `partial`, `is_final_response()`, `get_function_calls()`, `get_function_responses()`, `actions.state_delta`.
- **SSE tips:**
  - In SSE mode, partial chunks are followed by a final aggregated event, so the client should *replace* the streamed text, not append to it.
  - Use `fetch()` with a ReadableStream, since `EventSource` is GET-only.
  - Set the header `X-Accel-Buffering: no`.
- **`InMemorySessionService`** is fine for a session that lives entirely inside one request. Follow-up requests need `DatabaseSessionService` or `VertexAiSessionService`, or a stateless design (ours).

### C5. `get_fast_api_app` [V]

- Signature: `get_fast_api_app(agents_dir=, session_service_uri=, allow_origins=[... or "regex:..."], web=False, otel_to_cloud=..., auto_create_session=..., max_llm_calls=...)`.
- It exposes `/run_sse`. A custom FastAPI + Runner gives us our own request schema and filtered events. **Decision: custom FastAPI.**

### C6. Evaluation [V]

- `pip install google-adk[eval]`, then `adk eval <agent_module> <evalset.json> --config_file_path=test_config.json`.
- **Criteria and default thresholds:**

  | Criterion | Default threshold |
  |---|---|
  | `tool_trajectory_avg_score` (EXACT / IN_ORDER / ANY_ORDER) | 1.0 |
  | `response_match_score` (ROUGE-1) | 0.8 |
  | `final_response_match_v2` (LLM judge) | 0.8 |
  | `rubric_based_*` | — |
  | `hallucinations_v1` | — |
  | `safety_v1` | — |

  Also logged, with no thresholds: `token_usage_v1` and `invocation_duration_v1`.
- **pytest:** `AgentEvaluator.evaluate(agent_module=..., eval_dataset_file_path_or_dir=...)`.
- Use rubric or LLM-judge criteria for the search-grounded agent, because search results vary.

### C7. Observability [V]

- In a custom FastAPI app:

  ```python
  from google.adk.telemetry import google_cloud
  from google.adk.telemetry.setup import maybe_set_otel_providers
  maybe_set_otel_providers(otel_hooks_to_setup=[google_cloud.get_gcp_exporters(enable_cloud_tracing=True)])
  ```

  Install the `otel-gcp` extra.
- Prompt and response capture in spans is off by default (`ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS`).

### C8. Environment variables [V]

- google-genai reads both `GOOGLE_GENAI_USE_ENTERPRISE` and `GOOGLE_GENAI_USE_VERTEXAI`. **If they conflict, ENTERPRISE wins.**
- ADK logs a deprecation warning for VERTEXAI.
- Python client: `genai.Client(enterprise=True, project=..., location="global")`.

### C9. Thinking

- On Gemini 3, use `types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW)`. `thinking_budget` is accepted for backward compatibility only.
- In ADK, pass it through `BuiltInPlanner(thinking_config=...)` or `generate_content_config`. The planner wins if both are set [V].

### C10. Firestore vector search [V]

- **Equality pre-filter** with `where()` plus `find_nearest()` needs a composite index that includes the filter field.
- Whether range/inequality filters work is unclear (docs vs older blogs). **Use equality only.**
- **Limits:** max 2048 dimensions, max 1000 results, flat index only, no real-time listeners.
- `distance_result_field` and `distance_threshold` are supported.
- **Create the index with gcloud**, because of the Firebase CLI bug (#9385).

### C11. Gemini PDFs [V]

- Max **50 MB or 1000 pages** per PDF.
- On Gemini 3, tokens per page depend on `media_resolution`: low 280, **medium 560 (default, OCR quality saturates here)**, high 1120. Native text is not charged.
- On Vertex, use `Part.from_bytes` (small files) or `Part.from_uri("gs://…")`. The Files API is Gemini Developer API only.
- Use `response_schema` / `response_json_schema`. Keep schemas flat; large or deeply nested schemas may be rejected.
- **Tips:** extract one table or page range per call, temperature 0, add a `page_number` field, and validate totals in code.

### C12. Embeddings [V]

| | gemini-embedding-001 | gemini-embedding-2 |
|---|---|---|
| Price | $0.15/M | $0.20/M |
| `task_type` | ✔ (`RETRIEVAL_DOCUMENT` / `RETRIEVAL_QUERY` …) | ✘ (use text prefixes: `"task: search result \| query: …"`) |
| Default dims | 3072 (set `output_dimensionality=768`) | 3072 (set 768) |
| Normalization at <3072 | **manual** | automatic |
| Max input | 2048 tokens | 8192 tokens; multimodal |
| Batching | one input per request on Vertex [3P] | multiple `contents` are **merged into one** embedding unless each is wrapped in its own `Content` |

**Decision:** gemini-embedding-001 at 768 dims with COSINE distance. It has the longest support window, `task_type`, and the lowest price.

### C13. Retries [V]

- google-genai retries are **off by default**.
- Enable them with `types.HttpRetryOptions(attempts=5, initial_delay=1, ...)`. When enabled, the defaults retry on 408, 429 and 5xx. `Retry-After` is not honored.
- In ADK: `generate_content_config=types.GenerateContentConfig(http_options=types.HttpOptions(retry_options=...))`.

---

## D. Data sources

### D1. Typhoon tracks: NOAA IBTrACS

- **Use the CSV v04r01** ([NCEI access](https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/), updated 3× per week) [V].
  - Files: `ibtracs.WP.list.v04r01.csv` (114 MB) and `ibtracs.last3years.list.v04r01.csv` (11 MB).
  - The BigQuery table `bigquery-public-data.noaa_hurricanes.hurricanes` reportedly froze in May 2024 [3P].
- **Format:** 174 columns, uppercase headers, **row 2 is units (skip it)**.
  - Key fields: `SID, NAME, ISO_TIME, LAT, LON, USA_WIND, TOKYO_WIND, TOKYO_PRES, USA_R34/R50/R64_{NE,SE,SW,NW}, USA_RMW, LANDFALL`.
  - Units: knots and nautical miles.
  - USA winds are 1-min averages; Tokyo (JMA) winds are 10-min averages.
- **Licence:** NOAA "full and open access". Cite Knapp et al. 2010 and DOI 10.25921/82ty-9e16 [V].

| Event | SID [V] | Landfall record |
|---|---|---|
| Jebi 2018 | `2018239N11161` | 2018-09-04 03Z, 33.8N 134.6E. Tokyo 85 kt / 950 hPa. R64 NE 55 nmi. |
| Hagibis 2019 | `2019278N16165` | 2019-10-12 12Z, 35.6N 139.4E. Tokyo 70 kt / 965 hPa. R34 NE 300 nmi. |
| Haiyan 2013 | `2013306N07162` | 2013-11-08 00Z, 11.0N 124.8E. USA 165 kt. |

⚠️ **Storm names are reused** (another Jebi in 2013 and 2024, for example). Always filter by SID.

**Alternative:** [JMA best track `bst_all.zip`](https://www.jma.go.jp/jma/en/NMHS/RSMC_HP/Besttracks/bst_all.zip), 1951–2026 [V].
- Licence: Public Data License 1.0 (CC BY 4.0-compatible).
- Attribution: "Source: Japan Meteorological Agency website".

### D2. Earthquakes: USGS [V]

- **Noto 2024 = `us6000m0xl`:** Mww 7.5, 2024-01-01 07:10:09 UTC, 37.487N 137.271E, depth 10 km. ShakeMap max MMI 8.9. PAGER red.
- **Event API:** `https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=us6000m0xl&format=geojson`
- **ShakeMap files:**
  - `grid.xml` (7.6 MB): MMI/PGA grid. **Sample it at region centroids.**
  - `cont_mmi.json`: contours are *lines*, not polygons.
- **Licence:** US public domain. Credit "U.S. Geological Survey".
- PowerShell 5.1 `ConvertFrom-Json` fails on this JSON. Parse it in Python.

### D3. Other agencies

- **PAGASA:** no open machine-readable best track [NF]. Use IBTrACS for the Philippines.
- **Taiwan CWA:** open API `W-C0034-005` (Open Government Data License v1.0, free key), oriented to the current season [V].

### D4. GDACS (auto-trigger for the roadmap or a stretch goal) [V]

- **Endpoint:** `https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH?eventlist=EQ;TC&fromdate=…&todate=…&alertlevel=orange;red`
- **Response:** GeoJSON with alertlevel, severitydata and geometry URLs. HTTP 204 means no results.
- Noto = GDACS EQ 1408627 (Orange).
- **Terms:** data is provided "as is", and alerts are automatic: "should not be used for decision making without prior confirmation". **No explicit open licence** [NF]. Attribute GDACS and show the disclaimer.

### D5. Region boundaries [V]

- **[Natural Earth 10m admin-1 v5.1.1](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/): public domain.**
  - Units: JPN 47 prefectures, PHL 118 units, TWN 21 units.
  - Join keys: `iso_3166_2`, `name`, `adm0_a3`.
- **Mapshaper test** (JPN + PHL + TWN, 3 properties):

  | Version | Size |
  |---|---|
  | Raw | 623 KB |
  | `-simplify 10% keep-shapes`, precision 0.001 | 87 KB |
  | `-simplify 3%` | **55 KB** |

- **Don't use geoBoundaries.** Its JPN and TWN files are **ODbL (share-alike)**, and its PHL ADM1 is 17 regions (CC BY 3.0 IGO).

### D6. Exposure calibration

- **GIROJ prefecture CSV** (`jishin_fukyu_9_2024.csv`): earthquake-insurance policies and **sums insured by prefecture** (¥m), FY2018–2024. It is Shift-JIS encoded. [V]
  - **This is the best real TSI proxy.**
  - Licence: copyright GIROJ, with no open licence [NF]. Use it **for calibration with citation, and don't redistribute the file.**
- **e-Stat 2023 Housing and Land Survey:** 65.05M dwellings and 56.2M households. CC BY 4.0-compatible. Attribution: "出典：政府統計の総合窓口(e-Stat)". [V]
- **PSA 2020 Census (Philippines):** 28.5M housing units, by province. No licence found; cite PSA. [V]/[NF]

### D7. Vulnerability references (to justify the damage-ratio table)

- **Emanuel 2011 wind damage function:** f = vₙ³ / (1 + vₙ³), where vₙ = max(V − 25.7, 0) / (V_half − 25.7), in m/s.
- **Eberenz et al. 2021** (NHESS, CC BY 4.0) [V] calibrated V_half by region: **Philippines 76.0**, **Japan/Korea/Taiwan 190.5**.
  - Calibration basis: economic loss with 1-minute winds.
- Calculated damage ratios [CALC]:

  | 1-min wind | Philippines | Japan/Taiwan |
  |---|---|---|
  | 40 m/s | 2.3% | 0.07% |
  | 50 m/s | 10.1% | 0.3% |
  | 60 m/s | 24.1% | 0.9% |
  | 70 m/s | 40.6% | 1.9% |

  → Japan's building stock is far less vulnerable. **Use separate curves per country.** The primer's illustrative 2% (band 4, Osaka) is on the high side for Japan. Recalibrate when seeding data.
- **FEMA Hazus 6.1 earthquake manual** (public domain): repair-cost ratios by damage state. Verify table values before citing.
- **JMA shindo explanation table:** qualitative only.
- **GIROJ earthquake 被災率** (empirical claim rates by event) [V].

### D8. Event facts (citable)

**Jebi 2018**
- JMA [V]:
  - Landfall about 12:00 JST on 4 Sep in southern Tokushima; second landfall near Kobe about 14:00.
  - Kansai Airport gust 58.1 m/s. Osaka tide 329 cm (a record).
- **GIAJ [V]: 857,284 claims, ¥1,067.8bn**, the largest ever for a Japanese typhoon.
- Swiss Re: about $13bn after loss creep [3P].

**Hagibis 2019**
- Landfall just before 19:00 JST on 12 Oct, Izu Peninsula. Hakone received about 1,000 mm. [V]
- GIAJ: 264,359 claims, ¥395.9bn, as of 9 Dec 2019 [V]. Later figure: ¥582.6bn [3P].

**Haiyan 2013**
- Landfall 04:40 PHT on 8 Nov at Guiuan; 235 km/h [3P].
- Insured about $1.5bn of $12.5bn economic loss (Swiss Re sigma) [3P].

**Noto 2024**
- JMA: Mj 7.6, shindo 7 [V].
- Japan Earthquake Reinsurance: **119,913 claims, ¥108.0bn** as of 31 Mar 2026 [V].
- Moody's RMS: ¥435–870bn insured including commercial [V].

### D9. Treaty wording sources

- LMA model wordings are behind a subscription [NF for public hours-clause text].
- **SEC EDGAR has real Cat XL contracts** (public filings; *paraphrase*, don't copy):
  - **Homeowners Choice 2016:** 96h windstorm, 168h earthquake and other perils; cedent chooses the start (not before the first loss); "flood when written as such" excluded; reinstatement pro rata as to amount [V].
  - **United P&C 2014:** 120h windstorm, 168h earthquake, no overlapping periods [V].
- These are a perfect base for our 6–8 synthetic wordings, with deliberately **different hours clauses** to drive the demo.

---

## E. Reinsurance domain and competitors

### E1. Hours clauses [V/3P]

- **Classic London-style wording:**
  - 72h for windstorm/typhoon, 72h for earthquake, 168h for "any other catastrophe".
  - The **cedent chooses** when each period starts, periods **may not overlap**, and none can start before the first recorded loss.
  - A longer event can be split into several occurrences.
- Real contracts vary: **72 / 96 / 120 / 168h** [V, SEC filings].
- **UnipolSai v Covéa [2024] EWCA Civ 1110** [V]: "occur" means "first occur" for aggregation under a 168h clause.
- Swiss Re called for more precise event definitions as early as 2001 [3P].

### E2. Reinstatements [V]

- The **BRMA 41 clause family** covers pro rata as to amount and/or time, scheduled, and free reinstatements.
- Typical Cat XL: **one reinstatement at 100% additional premium, pro rata as to amount, 100% as to time**. Pro rata as to time is rare [3P].
- RIP formula (reinstatement premium) = (loss to layer ÷ limit) × layer premium. Example from a CAS paper: a 10m xs 5m layer with 400k premium and a 4m loss → **160k**.

### E3. Asia-Pacific renewals

- **1 April:** Japan (the largest Asian territory renewing then) and India [V, Guy Carpenter, 2 Apr 2026].
  - Japan property cat rates fell double digits: Gallagher Re −15 to −17.5%, Howden up to −20%, Guy Carpenter −10 to −15% [3P].
- **1 January:** Korea, Taiwan, China and Southeast Asia. Guy Carpenter APAC rate-on-line −12% [3P].
- **1 July:** Australia and New Zealand. Loss-free cat −12.5 to −17.5% [3P].
- Pitch angle: in a soft market, service (including post-event responsiveness) is how players compete.

### E4. Singapore hub [V, MAS]

- Reinsurance premiums of **S$27.6bn in 2023 (+31%), about 21% of Asia's reinsurance market**.
- **16 of the top 25 global reinsurers have their regional hub in Singapore.**
- About 150 brokers.
- 91% of APAC's 2023 economic losses (US$65bn) were uninsured.
- **MAS directory:** 22 general reinsurers, 9 composite, 4 authorised general reinsurers, 19 Lloyd's Asia Scheme members.

### E5. Post-event timeline: the gap CatSight fills

| Source | Event | First estimate | Time after event |
|---|---|---|---|
| Moody's RMS | Jebi | $3–5.5bn | ~10 days [V] |
| Moody's RMS | Hagibis | $7–11bn | ~19 days [V] |
| KCC | Noto | $6.4bn | 4 days [V] |
| Moody's RMS | Noto | $3–6bn | 11 days [V] |
| PERILS (Japan TC and flood only, **not** Japan earthquake) | — | first report | **6 weeks** [V] |
| Verisk PCS Japan (events ≥$2bn) | — | first estimate | **within 90 days** [V] |
| Munich Re public figure | Jebi | $6bn | ~3 months [3P] |

- **Jebi's loss grew from $3–5bn to about $13bn, roughly 3× the early figure** [3P, Swiss Re CFO]. Early estimates can be badly off.
- **Moody's [V] quotes:**
  - Outward reinsurance structures "might only exist in their capital model, a homegrown tool, or even in a spreadsheet".
  - Exposure managers rely on "a patchwork of multiple systems and a reliance on manual work-arounds".
- **Aon 2025 survey [V]:**
  - "**48 percent of insurers do not license catastrophe models**".
  - "**Nearly 60 percent** operate with catastrophe risk teams of **five or fewer** people".

### E6. Disputes showing that wording matters

- **Tokio Marine Europe v Novae [2014]** (Thai floods, 72h clause; the debate was 11 deductibles vs 1) [V].
- **Canterbury earthquake sequence:** successive-event allocation cases in New Zealand [V].
- **UnipolSai v Covéa [2024]** [V].
- **Jebi/Trami and Hagibis/Faxai** caused allocation difficulties [3P]. No formal dispute was found [NF].

### E7. Competitive landscape

| Player | What it does | What it doesn't do (our gap) |
|---|---|---|
| Moody's RMS (Event Response, ExposureIQ, TreatyIQ, IRP Navigator GenAI) | Footprints, then layer loss on structured treaty terms | Terms must be pre-coded as data. No evidence of reasoning over wording text with citations. Enterprise licence. |
| Verisk (Touchstone Re, PCS) | Contract modelling, industry estimates | GenAI is focused on primary underwriting |
| Aon ELEMENTS / Automated Event Response | Japan typhoon reports within 30–60 min of a forecast | Footprint and modelled loss. Broker-client service. |
| Guy Carpenter CAT-i, Gallagher Re INSIGHT | Event impact on in-force data | Tied to the broker relationship |
| EigenRisk EigenPrism | Real-time alerts plus a financial engine for treaty terms (added Swiss Re CatNet on 28 Sep 2026) | **Closest numeric competitor.** No wording RAG. |
| KCC, Reask, McKenzie Intelligence, Munich Re NATHAN, Swiss Re CatNet | Hazard data or industry-level losses | Not treaty wording |
| **Reinsured.AI** (has a Singapore office) | 25 agents including Treaty/Contract, Accumulation, Clash; its own Reinsure-8B model | **Closest threat.** Has wording extraction but no post-event layer-loss flow. |
| Cytora, Federato, Kalepa, hx, Artificial Labs, Supercede, Nomad DocChat | Underwriting, placement, generic document AI | Not post-event |
| Swiss Re (in-house wording AI), Munich Re (CatAI imagery) | Internal, used at underwriting time | Not a product |

### E8. Differentiation statement (evidence-backed)

> "Moody's and EigenRisk tell you the number *if you've already coded the treaty*. CatSight reads the wording, shows the clause that changes the number, and cites it — within hours, before vendor ranges (4–20 days), PERILS (6 weeks) or PCS (90 days) arrive. It's built for the ~48% of insurers without licensed cat models and for small cat teams."

**Topical hook [3P, must verify]:** Typhoon Dujuan made landfall in eastern Japan on **21 Sep 2026**. As of 23 Sep, no aggregate insured loss estimate had been published ([Insurance Business](https://www.insurancebusinessmag.com/asia/news/catastrophe/typhoon-dujuan-exposes-gaps-in-japans-property-insurance-cover-590853.aspx)). If confirmed and present in `ibtracs.last3years`/`ACTIVE`, it makes a strong "live" demo event.

---

## F. Open items that need a human

| # | Item | Owner | Deadline |
|---|---|---|---|
| 1 | **Register both members as one team** (the T&C roster lock says Oct 4) | Both | **Oct 4** |
| 2 | Ask on Discord or by email, and keep the written reply: Oct 4 vs Oct 11 roster lock; category label format; whether the live URL must stay up and whether we may update after Oct 18; credits | B | Oct 3 |
| 3 | Check the Hack2skill dashboard: Forms tab (credits), Resources (deck template), submission form fields and limits | B | Oct 3 |
| 4 | Check your employment contracts' IP and outside-work clauses (Hack2skill gets a right of first refusal on submitted IP) | Both | Oct 3 |
| 5 | 20-minute practitioner calls (1–2 people): how long a first view takes today, who asks for it, which clauses cause disputes | A | Oct 6 |
| 6 | Check the trial start date (Billing → Credits) and make sure it covers Dec 4 | A | Oct 2 |
| 7 | Verify Typhoon Dujuan (Sep 2026) in the IBTrACS `last3years` CSV and JMA sources | A | Oct 3 |
| 8 | Check Hazus earthquake damage-state ratio values against the manual tables before citing them | A | Oct 6 |
| 9 | Confirm in the Day-1 spike: Gemini 3.5 Flash-Lite and 3.8 Flash work on `global` from a trial project; check observed 429 rate | A | Oct 2 |
