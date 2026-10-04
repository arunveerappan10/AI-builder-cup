# CatSight — Submission answers (draft)

> Draft answers for the Hack2skill submission form, plus prepared answers for judge Q&A.
>
> **Check the actual form early** for field names and character limits — these are drafted blind and will need trimming. Record the real limits here once seen.
>
> `[PENDING]` = must come from `benchmarks/results/RESULTS.md`. Nothing invented.

---

## 1 · Form fields

### Theme
**BFSI: Intelligent Risk, Fraud & Financial Experiences**

### Problem statement — one line
> After a catastrophe, a reinsurer cannot say quickly or defensibly how much it owes, because the answer depends on contract clauses buried in PDF treaty wordings that take teams hours or days to re-read.

### Solution summary — ~100 words
> CatSight replays a catastrophe over a reinsurer's portfolio and tells the analyst, within minutes, which treaties respond, what each layer pays, and which contract clauses change that number — citing the treaty, page and clause for every claim. A deterministic, unit-tested engine computes every figure; Gemini reads the wordings, decides whether this event's timeline, perils and geography fall inside each clause, and argues both sides of genuinely ambiguous ones while the engine prices each reading. Every citation is machine-verified against the source page, unverifiable claims are withheld and counted, and a human approves before anything leaves.

### How Gen AI is used — ~150 words
> Gemini does the work a rules engine cannot. It extracts structured terms from heterogeneous PDF wordings with a page reference for every field, including a scanned, stamped endorsement with no text layer that overrides the base contract. It decides whether this specific event's timeline, perils and geography fall inside each clause. Where a clause reads two ways, two agents independently argue the cedent's and the reinsurer's readings from verified quoted text, and a reasoning agent summarises the dispute risk without deciding it.
>
> What Gemini never does is arithmetic. Every number comes from deterministic Python with full branch coverage. Each agent's citation passes a normalised quote-match and a semantic check; on failure it retries once with the checker's feedback, then abstains — and the abstention is shown and counted rather than hidden.
>
> Built on Google ADK 2.x as a graph: a verification loop and a parallel fan-out/fan-in.

### Google Cloud technologies used
> Gemini 3.5 Flash-Lite and Gemini 3.8 Flash on Gemini Enterprise Agent Platform (Vertex AI), global endpoint · Google Agent Development Kit (ADK) 2.x graph Workflow · `gemini-embedding-001` at 768 dimensions · Firestore native mode with vector search · Cloud Run (SSE streaming, service-account auth) · Firebase Hosting · Cloud Storage · Secret Manager · Cloud Trace and Cloud Logging · Cloud Build · Artifact Registry · Google Search grounding (event context only)

### How will this benefit the community?
> Reinsurance recoveries are what let primary insurers pay households and small businesses at scale after a disaster. When a recovery is slow or disputed, the delay reaches the policyholder. Asia carries roughly 30% of global economic catastrophe losses but only about 5% of insured losses — around 8% of its 2025 catastrophe losses were insured, against a global protection gap of $424bn. Anything that makes catastrophe cover quicker and cheaper to administer helps close that gap, including for public disaster-risk pools such as SEADRIF, which spans eight countries including Japan, the Philippines and Singapore.
>
> We are deliberate about not overclaiming: CatSight is decision support for the people who settle recoveries, not a payout engine.

### What makes it innovative?
> Event response and AI contract review both exist commercially. Catastrophe modellers provide hazard footprints and modelled losses; document-AI tools extract clauses with page citations. To our knowledge, nothing joins them: applying one specific event's facts — its timeline, perils, footprint and geography — to specific clauses in your own treaties, and pricing the difference when a clause reads two ways.
>
> The Clause Courtroom is the clearest example. Two agents argue opposing readings of the hours clause from verified quoted text, and the deterministic engine prices both. In our worked example one clause moves total ceded recoveries by $10.0M, or 22.5% — and because our share is concentrated in the lower layer, the reading that saves the treaty money costs us more. A single number would hide that.
>
> We position CatSight as complementary to existing tools: it can consume a licensed vendor footprint instead of public hazard data.

### Deployment / demo link
> Live: `https://techno-crackers-catsight.web.app` — click **"Run demo: Typhoon Jebi 2018"**. No sign-up. A guided 60-second tour runs on first visit.
>
> Note for judges: the demo runs on synthetic contracts and a synthetic portfolio over real historical hazard data. If the backend is cold or at its daily cap, a clearly-labelled cached replay of a real run is served so the walkthrough always completes.

### Repository
> `https://github.com/arunveerappan10/AI-builder-cup` — Apache-2.0. README includes the architecture, benchmark results, cost per analysis, data licences and limitations.

### Video
> `[PENDING: YouTube URL]` — 2:45.

---

## 2 · Judge Q&A — prepared answers

### "Moody's and Verisk already do event response. Why does this need to exist?"
> They provide the hazard picture and the modelled loss, and they do it well. CatSight starts where they stop: it applies your actual contract wording to that event and shows which clauses move the money, with verified citations. It can take a vendor footprint instead of public data, so it complements them rather than competing. The hazard layer is an interface in our code for exactly that reason.

### "Why should a finance team trust an LLM in a loss report?"
> Because the LLM never calculates. Every number comes from a deterministic engine with full branch coverage on the core maths, tested against a hand-checked worked example. Every wording flag must pass a normalised quote-match against the stored source page and a semantic check, or it is withheld — and we show the withheld count rather than hiding it. Nothing leaves without human approval. Grounded web search is confined to event context and never touches a number or a flag.

### "Your contracts are synthetic. How do you know it works on real wordings?"
> The wordings follow standard clause families, paraphrased in the style of publicly filed Cat XL contracts, and our domain lead reviewed them for realism. Because we wrote both the wordings and the answer key, we also report accuracy on a blind set of three wordings authored by a team member outside the prompt work, with planted issues the prompt author never saw — [PENDING B3-blind]% against [PENDING B3]% on the tuned set. The next step is a pilot on an anonymised real treaty pack.

### "Why replay historical events?"
> Replays give a fixed, reproducible test bed for accuracy and timing, which is what lets us publish real numbers. The same pipeline runs on live feeds — the only difference is where the event comes from. `[If X1 shipped: show the Watch panel.]`

### "What is Gen AI doing that rules couldn't?"
> Four things. Reading heterogeneous and sometimes scanned wordings, including a stamped endorsement with no text layer that overrides the base contract. Deciding whether this event's timeline, perils and geography fall inside each clause — which is judgement over unstructured text, not pattern matching. Constructing both sides of a genuinely ambiguous reading. And writing the narrative. All of it with machine-checked citations. The arithmetic is deliberately not on that list.

### "How does it scale, and what does it cost?"
> Stateless Cloud Run with scale-to-zero, Firestore and vector search next to the operational data. Measured [PENDING B2] p50 and p95 latency, and [PENDING B6] per analysis — we report the standard path and the Courtroom path separately, because the Courtroom runs only when a clause is genuinely ambiguous. Multi-tenancy by project or per-tenant collections; ingestion through an authenticated API; Pub/Sub triggers from public disaster alerts for automatic runs.

### "What are the limitations?"
> It is an indicative first view, not a catastrophe model. Synthetic portfolio and contracts. Typhoon wind and earthquake shaking only — flood appears as a wording concept, not a modelled hazard. Japan, the Philippines and Taiwan. Damage curves are published functions with country calibration, back-tested at market level within [PENDING B5] of actuals, which is an order-of-magnitude check and nothing finer. No user accounts or multi-tenancy. Our blind-set accuracy is [PENDING B3-blind]%, and we list the known misses.

### "What if an incumbent just adds this?"
> They could — this is a hackathon prototype, not a defensible moat, and we would rather say so. What we would point to is that the join is harder than either half: it needs the deterministic contract maths and the clause reasoning to share one data model, and it needs the citation discipline to survive an audit. Our value is demonstrating that the join works and is trustworthy.

### "How did you build it?"
> Written during the hackathon window in a fresh repository, with Claude Code as a coding assistant. The published rules require Gemini or Google agentic platforms at runtime, which is what CatSight runs on — every model call in the product is Gemini on Agent Platform.

### "Is this legal advice?"
> No, and the product says so wherever the Courtroom appears. It is issue-spotting: it surfaces that a clause can be read two ways, quotes the text, prices each reading, and leaves the decision to the analyst. The position the analyst records is stored with the analysis as an audit trail.

---

## 3 · LinkedIn post (Social Choice) — draft

> When Typhoon Jebi hit Japan in 2018, early insured-loss estimates sat in the low billions. A year later the figure was around $15bn.
>
> For the reinsurers who fund the recovery, the hard part isn't the headline. It's which contract clauses decide how much lands on them — clauses buried in PDF treaty wordings that take teams hours to re-read while a CFO waits for a number.
>
> We built CatSight for the Google Cloud AI Builder Cup: it replays a catastrophe over a reinsurer's portfolio and shows, in minutes, which treaties respond, what each layer pays, and which clauses change that answer — with the treaty, page and clause cited for every claim.
>
> The part we're most pleased with: when a clause can be read two ways, two Gemini agents argue the opposing readings from verified quoted text, and a tested engine prices both. In our worked example, one clause moves recoveries by $10M — 22.5%. The language model never does the arithmetic. It reads, reasons and cites; tested code calculates.
>
> Across Asia only a fraction of catastrophe losses are insured. Faster, less-disputed recoveries are part of closing that gap.
>
> Built on Gemini, Google ADK, Cloud Run and Firestore. Synthetic contracts, real hazard data, every number from code.
>
> `[live URL]` · `[repo]` · `[video]`
>
> #GoogleCloud #Gemini #AIBuilderCup #Reinsurance #InsurTech

*Keep the tone measured — real events, real victims. No disaster imagery.*

---

## 4 · Pre-submission checklist

- [ ] Real form fields and character limits recorded here; answers trimmed to fit
- [ ] Every `[PENDING]` resolved from `RESULTS.md`
- [ ] Live URL tested in a fresh incognito window, on a phone, and from a different network
- [ ] Repo public; README per FR-DOC; LICENSE present; secret scan clean
- [ ] Video < 3:00, uploaded, link live
- [ ] Deck exported to PDF and attached
- [ ] Theme selected correctly
- [ ] Two finale presenters named; passports and Singapore visa requirements checked
- [ ] Organiser replies on open questions (category label, URL uptime expectations, whether the finale demo may differ from the judged submission) saved in `docs/`
- [ ] Tagged and frozen; no production deploys after the tag
