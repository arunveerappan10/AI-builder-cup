# CatSight — Requirements v2 (addendum)

> **This document overrides `REQUIREMENTS.md` v1 where the two conflict.** Everything v1 specifies and v2 does not mention stands unchanged.
>
> v2 adds the upgrades that move the two Gen-AI sub-criteria inside the 40% and 25% rubric blocks, and revises the latency and cost targets that the added agents make unachievable as written.
>
> Requirement IDs here are stable and continue v1's numbering. Reference them in commits and tests.
> **MUST** = required for submission · **SHOULD** = strongly desired · **MAY** = stretch.

---

## 1. New functional requirements

### FR-VERIFY · Citation verifier and trust panel (MUST · M2)

v1's `FR-WORD-5` already requires that an unverifiable quote causes the flag to be dropped. That rule is correct and invisible. `FR-VERIFY` turns it into a measurable, visible feature.

- **FR-VERIFY-1 · Deterministic match.** For every candidate flag, normalise the quote and the stored chunk text (casefold, collapse whitespace, strip punctuation that PDF extraction mangles, normalise Unicode quotes and dashes) and assert the quote is a substring of the chunk. This check runs first, in code, at no model cost.
- **FR-VERIFY-2 · Semantic check.** Call `MODEL_REASON` with the quote, the surrounding chunk and the asserted issue, using `response_schema` to return `{supports: bool, reason: str}`. Batch all of an analysis's candidate flags into as few calls as the context allows.
- **FR-VERIFY-3 · Loop and abstain.** Wire AG-5 as an ADK loop. On failure of either check, the wording agent retries **once** with the checker's `reason` as feedback. On a second failure the flag **abstains**: it is withheld from the report body and placed in a review tray with the reason shown.
- **FR-VERIFY-4 · Counts and display.** Every displayed flag renders a badge `verified · {treaty_id}, p. {page}, cl. {clause_no}`. The report header renders `"{n} of {n} displayed citations verified · {k} withheld"`. Both counts persist on the analysis document and are reported in `RESULTS.md`.
- **Guardrail.** An unverified flag is **never** rendered in the report body. Both checks log to Cloud Trace with the analysis ID.
- **Acceptance:** on the 8 wordings and the blind set, 100% of displayed flags pass both checks; withheld flags are counted, not silently dropped. **QA-10.**

### FR-COURT · Clause Courtroom (SHOULD · S1 · signature feature)

Adversarial interpretation of the single most material ambiguous clause — typically the hours clause or the loss-occurrence definition.

- **FR-COURT-1 · Trigger.** Runs when AG-3 raises a flag of `issue_type ∈ {HOURS, PERIOD}` with `severity = HIGH`, or an exclusion flag whose applicability depends on an event fact. Picks the single flag with the largest engine-priced delta. If no flag qualifies, the Courtroom is skipped and the UI says so — it is never faked.
- **FR-COURT-2 · Fan-out.** Two `LlmAgent`s run **in parallel** on `MODEL_MAIN` with opposing instructions: AG-6 `cedent_counsel` argues the reading favouring the cedent, AG-7 `reinsurer_counsel` the reading favouring the reinsurer. Each returns `response_schema`:
  ```
  {reading: str, quoted_text: str, citation: {treaty_id, page, clause_no},
   scenario: {occurrences: int, hours_window: int, window_starts: [iso8601]},
   argument_md: str}
  ```
- **FR-COURT-3 · Verified or dropped.** Each side's `quoted_text` passes through `FR-VERIFY`. **A side that cannot cite verified text is dropped from the debate** and the UI states that it was dropped and why. The Courtroom never shows an unsupported argument.
- **FR-COURT-4 · Pricing.** Each side's `scenario` goes to the loss engine through the typed tool in `FR-WHATIF-1`. The engine returns the full result set for both readings — total ceded, per-layer ceded, cedent retention, our loss, our RIP, our net. `money_at_stake` is computed in Python as the signed difference **per party**, never by the LLM.
- **FR-COURT-5 · Arbiter and position.** AG-8 `arbiter` on `MODEL_REASON` summarises the dispute risk, cites the case-law consideration where relevant (`UnipolSai v Covéa`, 2024: "occur" means "first occur"), and names which reading each party would advance and why. It **does not decide.** The analyst records a position (`cedent_reading` | `reinsurer_reading` | `unresolved`) with an optional note, persisted to `analyses.courtroom.position`.
- **Persistence.** `analyses.courtroom = {flag_ref, sides[], priced_outcomes{}, money_at_stake{}, arbiter_md, position, decided_at}`.
- **Guardrails.** Labelled **issue-spotting, not legal advice**. The human decides. Both sides must cite verified text or be dropped. The arbiter is instructed never to state a number not present in the engine output.
- **Acceptance:** on the Jebi/Sakura hours-clause case the Courtroom produces both readings, both verified, both priced, with `money_at_stake` matching `MONEY_MOMENT.md` §3 exactly — total ceded 44.4 → 34.4, cedent retention 10.0 → 20.0, our net 6.82 → 7.33 — and the per-party preferences of §4.4 reproduced. **QA-11.**

### FR-LOSS-3 clarified (overrides v1)

v1 gives `RIP = (ceded / limit) × premium × rate` without stating that `ceded` is **per occurrence**. Applied to aggregate ceded in a multi-occurrence scenario it charges for more reinstatements than the treaty provides (1.47 against 1 available in the worked example). Restated:

> For each occurrence, in chronological order: `RIP += (limit eroded by that occurrence / limit) × premium × rate`, pro rata as to amount, **while reinstatement capacity remains**. Cumulative reinstated amount is capped at `count × limit`; aggregate cover is capped at `limit × (1 + count)`. Erosion beyond available reinstatement capacity is still paid if aggregate cover allows, but generates **no** RIP — nothing is restored.

Reinstatement applies to **partial erosion**, not only to exhaustion. Derivation from the primer's published one-event figures in `MONEY_MOMENT.md` §4.1. QA-1 asserts both the one-event total (our RIP 0.622, net 6.82) and the split (our RIP 0.525, net 7.33).

The engine returns the **per-party** view — cedent net cost, market net, our net — because the per-party divergence is the demo's payload, not a derived nicety.

### FR-ENDORSE · Endorsement detective (SHOULD · S2)

- **FR-ENDORSE-1 · Data.** One wording gains a **scanned, image-only endorsement page** — stamped and signed in appearance, carrying no text layer — that changes a material term (the hours window or the territorial scope) relative to the base wording. Built in `build_wordings.py`; the planted change is added to `ground_truth.json` and to the blind set.
- **FR-ENDORSE-2 · Extraction.** `ingest_treaty.py` extracts it with Gemini's native PDF and image understanding at medium media resolution. The transcription is **stored** as a chunk with `clause_type` and a flag `source="transcription"`, so `FR-VERIFY` can quote-match against it.
- **FR-ENDORSE-3 · Override and display.** When an endorsement contradicts the base wording, the effective term is the endorsement's, the treaty record retains both with provenance, and the flag reads **"endorsement overrides base wording"** citing the scanned page.
- **Guardrail.** Transcription-based verification is badged **distinctly** from text-layer verification — `verified against transcription`. A judge must be able to tell the two apart.
- **Acceptance:** the planted endorsement change is extracted correctly, the override is flagged, and the citation resolves to the scanned page. **QA-12.**

### FR-WHATIF · Bounded scenario tool (SHOULD · S3)

- **FR-WHATIF-1 · The tool.** The loss engine's scenario entry point is exposed as a typed ADK function tool with **bounded** parameters, enforced in the schema:

  | Parameter | Type | Bounds |
  |---|---|---|
  | `hours_window` | int | ∈ {24, 48, 72, 96, 120, 168, 240} |
  | `occurrences` | int | 1–3 |
  | `window_starts` | list[iso8601] | within `event.start − 24h` .. `event.end + 24h`; windows must not overlap |
  | `our_share_override` | float | 0.0–1.0, optional |
  | `retention_override` | float | ≥ 0, ≤ 10 × base retention, optional |
  | `track_offset_km` | float | −200..200, optional |

- **FR-WHATIF-2 · Routing.** `FR-ASK` questions that imply a scenario route to this tool. The LLM selects parameters only; out-of-bounds values are rejected by the schema, not clamped silently.
- **FR-WHATIF-3 · Display.** The layer chart shows the delta against the base analysis. Scenario runs are labelled as scenarios and never overwrite the base analysis.
- **Guardrail.** The engine computes; the LLM chooses parameters. Every scenario result carries the parameters that produced it.
- **Acceptance:** "What if the hours clause were 168 hours?" and "Shift the track 30 km east" both re-run and show a correct delta. Out-of-bounds parameters are refused with a clear message.

### FR-JUDGE · Judge mode (MUST · M4)

Judges open the live URL themselves, unaccompanied, over a three-week window.

- **FR-JUDGE-1 · Guided tour.** A dismissible 60-second guided tour on first visit, pointing at the timeline, the map, the layer chart, a verified flag and the money moment. Skippable, re-openable, state in `localStorage`.
- **FR-JUDGE-2 · Cached instant replay.** Every green analysis writes a precomputed SSE fixture to `data/replays/{event_id}.jsonl`. The frontend falls back to it when: the backend does not produce a first event within the `NFR-2` budget, the daily cap is hit, or the request errors. Cached runs are **clearly labelled as cached** with the timestamp of the run they came from.
- **FR-JUDGE-3 · Anonymous visitors.** Unauthenticated traffic is served cached replays at zero LLM cost. Live runs are reserved per session, so a popular post cannot show a judge an error.
- **FR-JUDGE-4 · Glossary.** Hover and keyboard-focus definitions for *cedent, layer, retention, limit, burn, reinstatement, hours clause, as-if, loss occurrence, quota share* — sourced from `DOMAIN_PRIMER.md`. Extends UI-10.
- **FR-JUDGE-5 · Friendly limits.** Cap and rate-limit responses explain what happened, when it resets, and link to a cached result. Never a bare 429.
- **Acceptance:** with the backend stopped entirely, a first-time visitor can still complete the full Jebi demo path from cache and understands that it is cached.

---

## 2. New agent specifications

Extends `REQUIREMENTS.md` §6. Orchestration is an ADK 2.x graph `Workflow`. `SequentialAgent` remains an acceptable fallback **for the linear spine only** — it cannot express the AG-5 loop or the AG-6/7 fan-out, so a `SequentialAgent` fallback run must degrade to Scenario B behaviour explicitly rather than silently skipping verification.

| ID | Agent | Model | Tools | Reads state | Writes | Output schema |
|---|---|---|---|---|---|---|
| AG-5 | `verifier` | `MODEL_REASON` | `verify_quote` (deterministic) | `{wording_flags}`, chunk store | `verified_flags`, `withheld_flags` | `VerificationResult` |
| AG-6 | `cedent_counsel` | `MODEL_MAIN` | `search_treaty_clauses` | `{event}`, `{impact}`, `{verified_flags}` | `cedent_reading` | `CourtroomSide` |
| AG-7 | `reinsurer_counsel` | `MODEL_MAIN` | `search_treaty_clauses` | same | `reinsurer_reading` | `CourtroomSide` |
| AG-8 | `arbiter` | `MODEL_REASON` | `price_scenario` | both readings, `{impact}` | `courtroom` | `CourtroomVerdict` |

AG-6 and AG-7 run concurrently and **must not** see each other's output — that is what makes the readings independent rather than a single model talking to itself.

### New Pydantic schemas (`schemas.py`)

```
VerificationResult { flag_id, deterministic_pass: bool, semantic_pass: bool,
                     reason: str|None, attempts: int, source: "text"|"transcription" }

CourtroomSide    { party: "cedent"|"reinsurer", reading: str, quoted_text: str,
                   citation: Citation, scenario: ScenarioParams,
                   argument_md: str, verified: bool, dropped_reason: str|None }

ScenarioParams   { hours_window: int, occurrences: int, window_starts: list[datetime],
                   our_share_override: float|None, retention_override: float|None,
                   track_offset_km: float|None }

PricedOutcome    { total_ceded, cedent_retention, layers[{layer_no, ceded, burn, exhausted}],
                   our_loss, our_rip, our_net }

CourtroomVerdict { flag_ref, sides: list[CourtroomSide],
                   priced: dict[str, PricedOutcome],
                   money_at_stake: dict[str, float],   # per party, signed
                   arbiter_md: str, position: str|None, decided_at: datetime|None }
```

### Instruction principles (additional)

- *"Never compute numbers. Call the tool and copy its output exactly."*
- *"You are arguing one side. Make the strongest honest case from the cited text. Do not invent text, and do not argue the other side."*
- *"If the clause does not support your side, say so and return `verified: false` rather than stretching the reading."*
- Arbiter: *"Summarise the dispute and the risk. Do not decide. Do not state a number that is not in the engine output."*

---

## 3. New UI requirements

Extends `REQUIREMENTS.md` §8.

| ID | Component | Requirements |
|---|---|---|
| UI-13 | **Trust panel** | Header reads `"n of n displayed citations verified · k withheld"`. A withheld tray lists each held flag with the checker's reason. Verified badges distinguish text-layer from transcription verification. Clicking any badge opens the cited page. |
| UI-14 | **Money moment / Courtroom** | Two columns, cedent and reinsurer, each with the reading, the verified quote, the citation and the priced outcome. A centre strip shows `money at stake` **per party**, with direction and sign. Arbiter summary below. Analyst position control with note. Labelled *issue-spotting, not legal advice*. Explicitly states when the Courtroom was skipped, or when a side was dropped for lack of verified text. |
| UI-15 | **What-if** | Bounded controls (not free text alone) for hours window and occurrence split, plus a question box routed to `FR-WHATIF`. Delta overlay on the layer chart. Scenario results visually distinct from the base analysis. |
| UI-16 | **Guided tour** | Per `FR-JUDGE-1`. Keyboard navigable, respects `prefers-reduced-motion`. |

**Accessibility applies to all of the above** (UI-12): the Courtroom's two-column layout must linearise under keyboard navigation and at tablet width, and `money at stake` must not rely on colour alone to convey direction.

---

## 4. New tests

Extends `REQUIREMENTS.md` §10.

| ID | What | How | Pass bar |
|---|---|---|---|
| QA-10 | Verifier correctness | Candidate flags with deliberately corrupted quotes (wrong page, truncated, paraphrased, right text wrong treaty) | 100% of corrupted quotes withheld; 0 false withholds on the planted set |
| QA-11 | Courtroom determinism and pricing | The Jebi/Sakura hours case, 5 runs | Both sides verified every run; `money_at_stake` identical every run and equal to `MONEY_MOMENT.md` §3; no number in `arbiter_md` absent from engine output |
| QA-12 | Endorsement extraction | The scanned endorsement page | Planted change extracted; override flagged; citation resolves to the scanned page; badge reads `verified against transcription` |
| QA-13 | Cached replay fidelity | Compare a cached fixture against a live run | Same stages, same final numbers; cached run clearly labelled |

`QA-5` (ADK eval) extends to the new graph: `tool_trajectory_avg_score` IN_ORDER = 1.0 including the verifier loop, and `hallucinations_v1 ≥ 0.8` on the arbiter output specifically.

---

## 5. Blind set (supersedes nothing; closes risk #5)

The team writes both the wordings and the answer key, so a ≥ 95% score on them is self-graded.

- **3 additional wordings**, authored by a team member **not** involved in writing extraction prompts or `ground_truth.json`, with planted issues unknown to the prompt author.
- Held out of all prompt iteration. Run **once** per checkpoint.
- Reported **separately** in `RESULTS.md` and on the results slide, honestly, including misses.
- The tuned-set and blind-set numbers are never averaged into a single figure.

---

## 6. Revised non-functional targets

The added agents change the cost and latency envelopes. v1's figures assumed 4 agents and ~7 model calls.

### NFR-4 revised · cost per analysis

Price table from `EXECUTION_PLAN.md` §4.2 — `MODEL_MAIN` $0.30/M in, $2.50/M out; `MODEL_REASON` $0.75/M in, $3.75/M out.

| Component | Calls | Tokens (in / out) | Cost |
|---|---|---|---|
| Base pipeline AG-1..4 (v1 estimate) | ~7 | 28K / 6K | $0.028 |
| AG-5 verifier, batched | ~2 | 6K / 1.2K | $0.009 |
| AG-6 + AG-7 counsels, parallel, on `MODEL_MAIN` | 2 | 10K / 3K | $0.011 |
| AG-8 arbiter on `MODEL_REASON` | 1 | 6K / 1.5K | $0.010 |

- **Standard analysis** (Courtroom not triggered): **≈ $0.037** · target **≤ $0.05**
- **Courtroom path**: **≈ $0.058** · target **≤ $0.08**
- What-if re-run (engine + one parameter-selection call): **≈ $0.004**

**B6 reports the two paths separately**, with the share of analyses that trigger the Courtroom. Running the counsels on `MODEL_MAIN` rather than `MODEL_REASON`, and in parallel, is what keeps this affordable — the arbiter is the only place the reasoning model is needed.

### NFR-1 revised · latency

| Path | p50 | p95 |
|---|---|---|
| Standard (warm) | ≤ 50 s | ≤ 95 s |
| Courtroom path (warm) | ≤ 70 s | ≤ 120 s |

`NFR-2` (time to first SSE event ≤ 3 s) and `NFR-3` (cold start ≤ 15 s) are unchanged — the added stages are at the end of the pipeline, so they do not delay the first event. Cloud Run `--timeout 300` still covers the Courtroom path with margin.

The counsel fan-out is **parallel**: running AG-6 and AG-7 serially would add their latencies and break this budget.

---

## 7. New configuration

Extends `REQUIREMENTS.md` §13.

| Var | Default | Notes |
|---|---|---|
| `MODEL_DEV` | *(unset)* | Explicit opt-in for cheap local runs. **Never** achieved by redefining `MODEL_MAIN`. |
| `COURTROOM_ENABLED` | `true` | Kill switch, so the Courtroom can be disabled without a redeploy if it misbehaves during judging |
| `VERIFIER_MAX_RETRIES` | `1` | Per `FR-VERIFY-3` |
| `CACHED_REPLAY_ONLY` | `false` | Forces all traffic to cached replays — the lever to pull if quota is at risk mid-judging |
| `REPLAY_FIXTURE_DIR` | `data/replays` | |
| `FIRST_EVENT_TIMEOUT_MS` | `4000` | Client-side trigger for the cached fallback |

---

## 8. Revised cut line

**Never cut:** `FR-LOSS` · `FR-WORD` with citations · **`FR-VERIFY`** · UI-1..7 · UI-13 · QA-1, QA-3, QA-4, QA-10 · S9 deliverables.

**Cut order if forced** (bottom up): `X2` → `X1` → `FR-WHATIF` → `FR-ENDORSE` → live mode → PDF export → `FR-ASK` → Taiwan coverage → Hagibis and Haiyan replays → **`FR-COURT`**.

`FR-VERIFY` moves into the never-cut set because it *strengthens* the design v1 already has rather than adding surface area, and because it is what makes the citation rule visible to a judge.

`FR-COURT` is cut last — it is the clearest evidence of non-superficial Gen AI — but it is cut **first** if it cannot be finished well. A Courtroom that shows one side, or unverified quotes, or a number the engine did not produce, is worse than no Courtroom at all.
