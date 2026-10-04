# CatSight — Video script

> **Hard limit 3:00. Target 2:45.** English. YouTube, unlisted or public.
>
> Every `[PENDING]` is a number that must come from `benchmarks/results/RESULTS.md` or a real screen recording. **Nothing is invented for the video.**
>
> Tone: calm and factual. Jebi, Hagibis, Haiyan and Noto all cost lives. No triumph, no disaster-movie music, no celebratory framing. One respectful acknowledgement, placed at 2:38.

---

## Timing

| # | Time | Length | Scene |
|---|---|---|---|
| 1 | 0:00–0:15 | 15 s | Hook |
| 2 | 0:15–0:35 | 20 s | The morning after |
| 3 | 0:35–1:05 | 30 s | One click |
| 4 | 1:05–1:40 | 35 s | **The money moment** |
| 5 | 1:40–2:00 | 20 s | Trust |
| 6 | 2:00–2:20 | 20 s | Results |
| 7 | 2:20–2:38 | 18 s | Built on Google Cloud |
| 8 | 2:38–2:45 | 7 s | Close |

The money moment gets the most time of any scene. That is deliberate.

---

## 1 · Hook — 0:00–0:15

**Screen.** Jebi's track sweeping into Osaka Bay, animating on the CatSight map. One figure resolves on screen.

**On screen.** `Early estimates: ~$2.3–5.5bn` → `One year later: ~$15bn`

**Voice-over.**
> "In September 2018, Typhoon Jebi hit western Japan. Within days, modellers put insured losses in the low billions. A year later the figure was around fifteen billion. For a reinsurer, the question isn't just how big — it's how much of it lands on us, and which contract words decide that."

*Note: a judge who stops watching at 0:20 must already understand the stakes. No jargon before 0:35.*

---

## 2 · The morning after — 0:15–0:35

**Screen.** Split screen. Left: a stack of treaty PDFs and a spreadsheet, scrolling. Right: a stopwatch from the B1 recording.

**On screen.** `Manual: [PENDING B1] minutes` · `CatSight: [PENDING B2 p50] seconds`

**Voice-over.**
> "A catastrophe analyst has until noon to give the CFO a defensible number. The work is real: overlay the storm on the portfolio, apply retentions and limits by hand, then re-read the contracts for the clauses that change the answer. We timed it on our own synthetic portfolio: **[PENDING B1]**."

*Source: `benchmarks/b1_manual_log.csv`, screen-recorded. If B1 is not complete, this scene is cut rather than estimated.*

---

## 3 · One click — 0:35–1:05

**Screen.** A single click on **"Run demo: Typhoon Jebi 2018"**. Agent stages stream in. The map colours in by wind band. The treaty table fills. The layer chart builds.

**On screen caption.** `Gemini reads. Tested code calculates.`

**Voice-over.**
> "One click. The agents work in the open: hazard footprint, exposure overlay, layer maths, then the wording. Every number you see comes from tested Python — the language model never does arithmetic. It reads, retrieves and explains. Twenty-four treaties, eight cedents, [PENDING: matched count] matched in **[PENDING B2 p50]** seconds."

*Use the real stream, at real speed if it fits, lightly sped up with an on-screen "×2" if not. Never fake the stream.*

---

## 4 · The money moment — 1:05–1:40

The climax. Figures from `docs/MONEY_MOMENT.md`, confirmed against a real run.

**Screen.** A HIGH flag on the hours clause. Click. The Clause Courtroom opens: two columns.

**Voice-over.**
> "Then it finds the clause every catastrophe team argues about. The hours clause — the definition of one event.
>
> So CatSight argues both sides. One agent takes the cedent's reading: all of it is a single occurrence. The other takes the reinsurer's: these losses first occurred in two separate windows. Each quotes the contract. Each citation is checked against the page.
>
> And then the engine prices both.
>
> One clause. **Ten million dollars**, or twenty-two and a half percent of total recoveries. The cedent's retention doubles. And here's what a single headline would hide — our share is concentrated in the lower layer, so **the reading that saves the treaty ten million costs us seven percent more**. On this programme our interest sits with the cedent, against the rest of the market.
>
> The agents don't decide. The analyst does."

**On screen.** Side-by-side priced outcomes, then the three-party strip — cedent prefers one event, market prefers two, **we** prefer one — then the analyst recording a position.

*Figures resolved in `MONEY_MOMENT.md` §4: our net 6.82 → 7.33, +7.4%. All of scene 4 is safe to script. The three-party divergence in §4.4 is the strongest 10 seconds in the video — give it room.*

---

## 5 · Trust — 1:40–2:00

**Screen.** Click a verified flag — the treaty PDF page opens with the clause highlighted and a green `verified · W1, p. 7, cl. 4.2` badge. Pan to the report header: `"n of n displayed citations verified · k withheld"`. Open the withheld tray. Then the endorsement detective: a scanned, stamped page, flagged *endorsement overrides base wording*.

**Voice-over.**
> "Every flag carries a citation, and every citation is machine-checked against the source page. What can't be verified isn't shown — it's held for human review, and counted. And when a term is buried in a scanned endorsement with no text layer, Gemini reads the image, and the override is flagged and cited."

---

## 6 · Results — 2:00–2:20

**Screen.** Approve, then export. Metrics overlay.

**On screen.** `Time: [PENDING B1 vs B2]` · `Extraction: [PENDING B3]% · blind set [PENDING B3-blind]%` · `Flags: [PENDING B4] recall / [PENDING B4] precision` · `Citations verified: [PENDING]%` · `Cost: $[PENDING B6] per analysis` · `SUS: [PENDING B8] (n=5)`

**Voice-over.**
> "A human approves before anything leaves. Our measured numbers: extraction accuracy **[PENDING B3]** percent — and **[PENDING B3-blind]** percent on a blind set written outside the build team. Flag recall **[PENDING B4]**. Every displayed citation verified. **[PENDING B6]** cents an analysis."

*The blind-set number is reported out loud alongside the tuned number, including if it is worse. That honesty is worth more than the extra point.*

---

## 7 · Built on Google Cloud — 2:20–2:38

**Screen.** The architecture diagram from `docs/ARCHITECTURE.md` §1, each service highlighting as named.

**Voice-over.**
> "Gemini 3.5 Flash-Lite and 3.8 Flash on Agent Platform. A Google ADK graph — a verification loop, and a parallel fan-out for the courtroom. Firestore vector search for the clauses. Cloud Run streaming to a React app on Firebase Hosting. Cloud Trace for every agent stage. Synthetic contracts, public hazard data."

*Name each service exactly once. No feature list — the diagram does the work.*

---

## 8 · Close — 2:38–2:45

**Screen.** Return to the map, now still. The one-sentence pitch.

**Voice-over.**
> "Jebi, Hagibis, Haiyan, Noto — real events, and real losses for the people in them. Reinsurance recoveries are what let insurers pay households and small businesses after a disaster. Across Asia, only a fraction of catastrophe losses are insured. CatSight is about settling those recoveries faster, and arguing about them less."

**Final card.** `CatSight — faster, fairer disaster recovery` · live URL · repo URL · *Indicative first view on synthetic data. Not a catastrophe-model output.*

---

## Production checklist

- [ ] Total runtime **< 3:00** — verify in the editor, not by estimate
- [ ] B1 and B2 figures in from `RESULTS.md`; every `[PENDING]` resolved or its scene cut
- [ ] `MONEY_MOMENT.md` §4 signed off by the domain lead before scene 4 is recorded
- [ ] Recorded against the **live URL**, not localhost
- [ ] Captions burned in — judges may watch muted
- [ ] No real company names anywhere on screen; fictional names web-checked
- [ ] Disclaimer legible in the final card
- [ ] Backup full-run screen recording saved to `docs/demo/`
- [ ] Uploaded to YouTube, link in README and the submission form
- [ ] Watched once end to end by someone who has never seen CatSight — do they understand the stakes by 0:20?
