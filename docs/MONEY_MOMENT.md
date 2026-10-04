# The money moment

> The climax of the demo, the video and the deck: **one clause, one number.**
>
> Every figure here is derived below from the `DOMAIN_PRIMER.md` worked example. **None of it goes on a slide until it comes out of a real engine run** (`QA-11`). This document exists so the engine can be built to produce it, and so the domain lead can sign off the framing before it is rehearsed.
>
> **Status: §4 needs the domain lead.**

---

## 1. The question

Every catastrophe team argues about it after a big storm:

> **Is this one event or two — and which losses belong to which?**

It is not academic. In 2024 the English Court of Appeal ruled on how a 168-hour clause works in *UnipolSai v Covéa*, holding that "occur" means "first occur". Jebi's own loss development was driven partly by overlapping Typhoon Trami claims arriving weeks later, and the market's insured-loss estimate moved from roughly $6bn at end-2018 to around $15bn by mid-2019.

The hours clause is the clause that decides the answer. CatSight finds it, verifies the quote, and prices both readings.

## 2. The setup

Sakura General Insurance's Cat XL programme, from the worked example (synthetic):

| Layer | Structure | Limit | Attaches at | Premium | Lion Re share | Reinstatements |
|---|---|---|---|---|---|---|
| L1 | 20 xs 10 | 20.0 | 10.0 | 2.0 | **25%** | 1 @ 100%, pro rata as to amount |
| L2 | 30 xs 30 | 30.0 | 30.0 | 1.5 | **10%** | — |
| L3 | 40 xs 60 | 40.0 | 60.0 | 1.0 | 0% | — |

Gross loss from the event: **54.4**. All figures $M.

Note where Lion Re's money sits: **25% of L1, only 10% of L2.** That asymmetry is the whole point of what follows.

## 3. The two readings, priced

### Reading A — one event (54.4)

The cedent's reading: all damage falls inside one hours window.

```
L1  ceded = min(max(54.4 − 10, 0), 20) = min(44.4, 20) = 20.0   burn 100%  EXHAUSTED
L2  ceded = min(max(54.4 − 30, 0), 30) = min(24.4, 30) = 24.4   burn  81.3%
L3  ceded = min(max(54.4 − 60, 0), 40) =                   0    burn   0%
```

- Total ceded **44.4** · cedent retention **10.0**
- Lion Re loss = 20.0 × 25% + 24.4 × 10% = 5.00 + 2.44 = **7.44**
- Lion Re RIP receipts = (20/20 × 2.0 × 1.0) × 25% + (24.4/30 × 1.5 × 1.0) × 10% = 0.500 + 0.122 = **0.622**
- **Lion Re net = 7.44 − 0.622 = 6.82**

### Reading B — two events (35.0 + 19.4)

The reinsurer's reading: the losses first occur in two separate windows. Each occurrence carries its own retention.

```
Occurrence 1 (35.0)          Occurrence 2 (19.4)
L1  min(25, 20) = 20.0       L1  min(9.4, 20) =  9.4   ← needs the reinstatement
L2  min( 5, 30) =  5.0       L2  min(  0, 30) =    0
L3                 0         L3                   0
```

- L1 total **29.4** (within 20 limit + 1 reinstatement = 40 available ✓) · L2 total **5.0**
- Total ceded **34.4** · cedent retention **10.0 + 10.0 = 20.0**
- Lion Re loss = 29.4 × 25% + 5.0 × 10% = 7.35 + 0.50 = **7.85**
- Lion Re RIP receipts — **basis-dependent, see §4** — 0.26 to 0.525
- **Lion Re net = 7.33 to 7.59**

### The money at stake, per party

| | Reading A · one event | Reading B · two events | Move |
|---|---|---|---|
| **Total ceded** | 44.4 | 34.4 | **−10.0 · −22.5%** |
| Cedent retention | 10.0 | 20.0 | +10.0 · doubles |
| L1 ceded | 20.0 | 29.4 | +9.4 · burden shifts **down** into L1 |
| L2 ceded | 24.4 | 5.0 | −19.4 |
| **Lion Re gross** | 7.44 | **7.85** | **+0.41 · +5.5%** |
| **Lion Re net** | 6.82 | 7.33 – 7.59 | **+0.51 to +0.77 · +7.4% to +11.3%** |

### Why this is the moment

**The split that saves the treaty $10.0M costs Lion Re more.**

Because Lion Re holds 25% of L1 and 10% of L2, the reading that cuts total ceded recoveries by 22.5% pushes the surviving burden down into the layer where Lion Re's share is heaviest. The cedent argues one event. The reinsurer argues two. **They are not arguing about the same pot of money** — and a single headline number would hide that.

This is why the Courtroom is genuinely adversarial rather than theatrical, and it is the detail a specialist judge will notice. Two agents are not performing a debate; they are advancing the readings their actual economics dictate.

## 4. Assumptions needing the domain lead ⚠

The headline is robust. The magnitude of Lion Re's net change is not.

### 4.1 Reinstatement-premium basis

`REQUIREMENTS.md` FR-LOSS-3 specifies `RIP = (ceded / limit) × premium × rate`. That is unambiguous for a single occurrence. For the two-occurrence case it is not, and the three readings give different answers:

| Basis | Rule | L1 RIP | Lion Re's share | Lion Re net |
|---|---|---|---|---|
| **A** | Reinstate in full on exhaustion: the full 20 is restored, so the full premium is due | (20/20) × 2.0 = 2.00 | 0.500 | **7.33** |
| **B** | Pro rata on the amount actually reinstated and used (9.4) | (9.4/20) × 2.0 = 0.94 | 0.235 | **7.59** |
| **C** | Literal FR-LOSS-3 on aggregate ceded | (29.4/20) × 2.0 = 2.94 | 0.735 | 7.12 |

**Basis C is wrong** and the engine must not implement it: it implies 1.47 reinstatements where the treaty provides one. This is a real ambiguity in FR-LOSS-3 as written, and it needs restating **per occurrence** rather than on aggregate ceded:

> For each occurrence after the first that draws on reinstated limit, `reinstated_amount = min(amount drawn, limit, remaining reinstatement capacity)` and `RIP = (reinstated_amount / limit) × premium × rate`, accumulated across occurrences and capped at the reinstatements available.

That formulation yields basis **B**, which is also the more common market treatment of "pro rata as to amount". **It is the recommended default — and the domain lead confirms it, not the engineer.**

### 4.2 Secondary questions for the domain lead

1. **Is RIP due at all in Reading A?** L1 is exhausted and never drawn on again. The primer charges the full 2.0 anyway, which is defensible if reinstatement is automatic on loss — but it should be a stated assumption, not an accident.
2. **Window placement.** Standard wording lets the cedent choose when each window starts, but not before the first recorded loss, and **windows may not overlap**. The 35.0 / 19.4 split must be shown to follow from a legitimate window placement, not chosen to make the demo work. The engine enforces non-overlap (`FR-WHATIF-1`).
3. **Would the cedent actually advance Reading A?** It retains 10.0 instead of 20.0 and recovers 44.4 instead of 34.4, so yes — but confirm there is no reinstatement-premium interaction that reverses it.
4. **The 54.4 → 35.0 + 19.4 split itself.** It comes from the primer as an illustration. The engine must derive the split from the event's loss timeline and the hours window, and the numbers it produces are the ones that go on the slide.

### 4.3 What is safe to rehearse now

Robust across **every** RIP basis, so these can be scripted before sign-off:

- Total ceded swings **−10.0, or −22.5%**, on one clause.
- Cedent retention **doubles**.
- **Lion Re is worse off under the split** — direction is certain, magnitude is 7% to 11%.

Do not rehearse a specific Lion Re net figure until §4.1 is settled.

## 5. How it is used

| Where | Treatment |
|---|---|
| **Product** (`FR-COURT`) | Both readings, both quotes verified, both priced by the engine, `money_at_stake` computed per party in Python. The analyst records a position. |
| **Video** 1:05–1:40 | The Courtroom on the hours clause. Two readings side by side, both cited. The engine prices both. Caption: *"Gemini reads. Tested code calculates."* |
| **Deck** slide 7 | "The money moment: one clause, one number." Lead with −$10.0M / −22.5%, then reveal the per-party asymmetry. |
| **Q&A** | *"What is Gen AI doing that rules can't?"* — constructing both sides of a genuinely ambiguous reading from heterogeneous wordings, with machine-checked citations, then letting tested code price each one. |

**Framing guardrails.** Issue-spotting, not legal advice. The human decides. Synthetic contracts, fictional cedent. The event is real and people died in it — state the number plainly, with no triumph in the voice-over.

## 6. Engine requirements this implies

- `split_occurrences(event, hours)` derives windows from the loss timeline, enforcing non-overlap and "first occur".
- Retentions and reinstatements apply **per occurrence** (FR-LOSS-5).
- Reinstatement capacity is tracked and **capped**; exceeding it is an error, not a silent overrun.
- RIP accumulates per occurrence on the amount reinstated (§4.1 basis B, pending confirmation).
- The engine returns the **full result set for both readings in one call**, so the UI never has to recombine numbers — and `money_at_stake` is a Python subtraction over those results, per party, never an LLM output.
- All four perspectives — total ceded, cedent retention, Lion Re gross, Lion Re net — are returned, because the story needs all four.

**QA-11 asserts these exact figures.** If a code change moves them, the test fails and the slide is wrong.
