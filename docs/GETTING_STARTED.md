# Starting development with a Claude Code session

> How to hand this project to Claude Code and drive it phase by phase. Each phase is one or more Claude Code sessions. **You review and approve at each checkpoint.**

## 1. Before the first session (human, about 1 hour)

1. Complete **[SETUP.md](SETUP.md)** §1–8: infrastructure, credentials and the Gemini check.
2. Create the **fresh public GitHub repo** (e.g. `catsight`). Clone it, then copy in `CLAUDE.md` and the whole `docs/` folder. Commit them as the first commit.
   - Alternatively, initialise git in this folder. Either way, the repo must contain only work created during the hackathon.
3. Open the repo folder in VS Code and start Claude Code there. It reads `CLAUDE.md` automatically.
4. Suggested permission settings: allow `pytest`, `npm`, `pip` and `git` (except push) without prompts. Keep `gcloud`, `firebase deploy` and `git push` on manual approval.

## 2. Session prompts (copy and paste, one phase at a time)

Start every session with this prompt:
> Read CLAUDE.md and docs/REQUIREMENTS.md. We are on phase **Px**. Confirm the requirement IDs in scope, then implement them with tests. Stop at the phase exit check and summarise what to verify.

| Phase | Prompt to add | Checkpoint (you verify) |
|---|---|---|
| **P0 Foundations** | "Implement P0: the repo layout from REQUIREMENTS §3.1, FastAPI `/healthz`, Vite app calling it, `scripts/setup_gcp.sh`, `scripts/deploy.sh`, `scripts/smoke_test.sh`, `.gitignore`, LICENSE. Give me the deploy commands to run in Cloud Shell." | You run the deploy. The live URL shows healthz OK. |
| **P1 Data** | "Implement P1 (DR-1..DR-6): `build_regions.py`, `build_events.py` (download IBTrACS/USGS into `data/raw/`), `seed_portfolio.py`, `build_wordings.py` + `ground_truth.json`, `data/ASSUMPTIONS.md`." | Review the 8 wording PDFs for realism (**your domain expertise**). Check the seeded data in the Firestore console. |
| **P2 Core engine** | "Implement P2: FR-LOSS + QA-1 first (the worked example must pass), then `hazard.py` + QA-2, then FR-INGEST + QA-3, then `retrieval.py`." | `pytest` green. QA-3 ≥ 95%. Spot-check the extracted terms. |
| **P3 Agents and API** | "Implement P3: schemas, prompts, AG-1..4, the Workflow (fall back to SequentialAgent), SSE API-1..5. Run end to end on jebi-2018 and show me the flags." | Read one full report. Are the wording flags correct, with citations on the right page? |
| **P4 UI** | "Implement P4: UI-1..8 following the demo path, then UI-9..12." | Click through the demo yourself. Check that it's understandable to a non-expert. |
| **P5 Quality** | "Implement P5: FR-GUARD, observability, QA-4..8, the benchmark harness (REQUIREMENTS §10.1), FR-ASK, FR-REVIEW, FR-EXPORT. Run `benchmarks/run_all.py` against the live URL." | Review `benchmarks/results/RESULTS.md`. **Do B1 and B8 yourself** (§3 below). |
| **P6 Deliverables** | "Implement P6: README per FR-DOC, `docs/ARCHITECTURE.md` + diagram, `docs/DECK_OUTLINE.md`, `docs/VIDEO_SCRIPT.md` (≤ 2:45), using the benchmark results." | Build the deck, record the video, and submit by **Oct 15**. |

**Tips**
- Start a **new session per phase**. If a phase is large, use one session per requirement group, to keep the context focused.
- If Claude Code proposes deviating from REQUIREMENTS, decide, then update REQUIREMENTS.md so later sessions follow it.
- Ask for `git commit` at each green checkpoint, with requirement IDs in the message.
- If time runs short, use the **cut line** in REQUIREMENTS §11.

## 3. Team of 3: suggested roles

| Member | Owns |
|---|---|
| **M1: Domain and product lead** (reinsurance background) | Reviewing wordings and reports for realism, practitioner interviews, B1 manual run (wording step), the impact narrative, the video voice-over |
| **M2: Build driver** | Runs the Claude Code sessions P0–P5, approves checkpoints, does deploys (Cloud Shell), runs `benchmarks/run_all.py` |
| **M3: Delivery and ops** | SETUP.md, Discord questions, B1 timing (as the non-expert tester) and B8 usability, deck PDF, video editing, README review, submission form, LinkedIn, post-submission monitoring |

- **Two people can run Claude Code sessions in parallel** on separate branches. For example, M2 runs the backend phases P1–P3 while M3 starts the P4 UI against the API contract in REQUIREMENTS §7. Merge at each checkpoint.
- **Only 2 members travel to the finale.** Decide who now.
- **Add the 3rd member on Hack2skill by Oct 4** (T&C roster lock).

## 4. Human-only work (do it in parallel with the build)

| Task | When | Output |
|---|---|---|
| Discord questions (category label, URL uptime, updates after submission, credits) | Now | Written replies saved in `docs/` |
| 1–2 practitioner interviews (BUSINESS_IMPACT §4) | Before P5 | `benchmarks/templates/interviews.md` |
| **B1 manual timing run** on Jebi with the same synthetic data (BUSINESS_IMPACT §3.2) | After P1 (data exists) | `benchmarks/templates/b1_manual_log.csv` |
| B8 usability test with 2–3 people | After P4 | `benchmarks/templates/b8_usability.md` |
| Review the wording PDFs and the flash report for domain realism | P1, P3 | Notes to Claude Code |
| Deck, video recording and voice-over, LinkedIn post, submission form | P6 | Submission by Oct 15 |

## 5. Benchmark flow at a glance

```
P1 data ──► YOU: B1 manual run (stopwatch) ──┐
P3–P5 build ──► run_all.py: B2–B7 automated ──┼──► results/RESULTS.md ──► deck + README impact slide
P4 UI ──► YOU: B8 usability ─────────────────┘
```
