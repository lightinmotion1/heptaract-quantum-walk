# Getting more quantum time — the real map
**Drafted 2026-09-18. Nothing sent. Every draft below needs Miah's approval before going anywhere.**

---

## The blunt part first

**IBM Quantum Credits will not take us, and we should not apply.** Two disqualifiers, both stated
plainly on IBM's own page:

1. Applicants must be **"tenure-track or permanent academic staff at a research institute."** We are
   an independent shop. No amount of good writing gets around a stated eligibility rule.
2. They fund **utility-scale work, above 30 qubits**, wanting "clear progress within 5–10 hours."
   Our tests run on 5 to 8 qubits. Even eligible, the shape is wrong.

Sending an application that stretches either point would fail on contact with anyone who reads it,
and would put a dishonest document under our name in the one place our name has to stay clean.

## What is actually open to us

| route | what we get | eligible? | effort |
|---|---|---|---|
| **Unitary Foundation microgrant** | **$4,000**, rolling | **Yes — "no organizational affiliation is required"** | short form + a 2-minute video |
| IBM Pay-As-You-Go | **~$96/minute** | yes, anyone | money only |
| IBM Credits via an academic collaborator | 5–10 hours | only through a partner who qualifies | months, and a real relationship |
| Other clouds' free tiers (Braket, Azure, IQM, Quantinuum) | small, varies | yes | a day of plumbing each |

**The arithmetic that matters.** At $96/minute, a $4,000 microgrant buys about **41 minutes** — a bit
over four times the current allowance, and roughly the 5× that was asked for. The microgrant is not
a consolation route. The microgrant *is* the route.

And the application asks for a short form and **a two-minute video**. Miah has spent nearly two
decades making documentary film for a living. Most applicants dread that requirement; for us it is
the cheapest part of the whole exercise and the place we can be better than everyone else in the pile.

---

## What we must not claim

This matters more than the wording of any paragraph below.

**Our hardware results so far reproduce known physics.** P-18 is entanglement swapping, published in
the nineteen-nineties. P-15's coupling, P-16's echo scheduling, the MUB work — all of it is textbook,
carefully measured but not new. Any outreach implying we have discovered new physics is false, and it
would be seen through instantly by exactly the people we are writing to.

**What is genuinely unusual is the practice, not the findings.** Twenty-one pre-registered tests,
each hashed before its data existed. Nulls published in the same size type as passes. Two findings
caught wrong by our own controls and retracted publicly within hours of publication. A fully open
repository anyone can rerun. That record is rarer than a result, and it is the honest thing to lead
with.

The ask that follows from that: *time to test the parts of the framework that are not yet settled,
by a group that has already demonstrated it will publish the answer either way.*

---

## DRAFT A — Unitary Foundation microgrant (form answers)

Rolling submissions. Contact: info@unitary.foundation

**Project title**
HEPTARACT: a public, pre-registered test bench for relational quantum claims

**What are you building?**

An open testing practice, and the tooling that keeps it honest.

HEPTARACT is an independent framework built around one claim — that the relationship between two
systems is its own object, not a description of the two. Rather than argue the claim, we have been
converting it into circuits and running them on IBM hardware under a strict discipline: every
prediction written down with its falsifier and hashed by SHA-256 before the data exists, every null
published beside the passes in the same size type, every script and count file public.

Twenty-one tests so far. Some hold. Several narrow. Two we got wrong, caught with our own controls,
and retracted publicly within hours — including one where an elegant mechanism we had published
turned out to be ruled out by a scheduling check that cost no quantum time at all.

The tooling that came out of that is what we would like to harden and give away:

- a pre-registration harness that refuses to ship a metric until it has been calibrated against
  states whose answers are known in advance (ours nearly published a seventeen-sigma "pass" for a
  state containing no entanglement, and the calibration caught it)
- a replication arm that is placed ahead of the interesting question and given veto power over it
- an append-only calibration log that records each backend's recalibration events, so a result can
  be read against the machine's condition at the hour it ran — the record whose absence forced one
  of our two retractions
- a backend chooser that makes the machine a declared, reasoned choice in the pre-registration
  rather than whatever `least_busy()` happened to return

**Why does this matter?**

Reproducibility on quantum hardware is unusually fragile, and a great deal of published work rests
on a single backend on a single day. We learned that the expensive way: a result we published came
from one chip on one evening, and the same circuit on another machine gave a figure nine times
larger. Nobody had written down what the first machine was like that night, so the question could not
be settled from the record.

Everything above is MIT-licensed and public already. We would like to finish it as something others
can drop into their own work.

**What would the funds be used for?**

Quantum compute time, almost entirely. At current pay-as-you-go rates the grant converts to roughly
forty minutes of QPU — against the ten minutes per rolling month that the Open Plan allows, which is
the binding constraint on everything above. The remainder goes to packaging the tooling and writing
the documentation.

**Links**
- Repository: github.com/lightinmotion1/heptaract-quantum-walk
- Living record of every test, receipt and retraction: lightinmotionfilms.com/lightbox/heptaract

---

## DRAFT B — the two-minute video

Shoot this properly. The film is the differentiator.

**0:00–0:20 — the hook, no framework talk yet.**
One sentence: we ran a quantum test, published the result, and then proved ourselves wrong in
public within the hour. Show the two changelog entries side by side on screen. Do not explain yet.

**0:20–0:50 — what we are doing.**
Independent shop, no lab, no affiliation. A framework about relationships between systems, converted
into circuits and run on real hardware under pre-registration. Show a hash being taken before a run.

**0:50–1:25 — the retraction, told straight.**
The two-hop test failed. An explanation was invented that used our own prior findings correctly and
was completely wrong. A check costing no quantum time killed the explanation. Both the failure and
the retraction are published in the same size type as the passes. **This is the whole pitch.** Say
plainly that we are not claiming new physics — the physics we have measured is decades old — and
that what we are offering is a practice.

**1:25–1:50 — the ask and the arithmetic.**
Ten minutes per rolling month is the ceiling on everything. The grant is roughly forty minutes. Name
what those forty minutes buy: the open questions, tested across more than one machine.

**1:50–2:00 — close.**
Repo and living tree on screen. Whatever comes back gets published either way.

Tone: plain, unhurried, no music swell on the retraction beat. Let the retraction be the quiet part.

---

## DRAFT C — academic collaborator (the slower, larger door)

For a tenure-track researcher in quantum information whose published work touches relational or
contextual quantum structure, entanglement swapping, or reproducibility on NISQ hardware. Send only
after reading at least two of their papers properly — a generic version of this is worse than none.

> **Subject:** Independent pre-registered hardware testing — an offer of labour, not a request for a favour
>
> Dr. [NAME],
>
> I read [SPECIFIC PAPER] and [SPECIFIC POINT THAT ACTUALLY LANDED]. I am writing because of a
> practice rather than a result.
>
> I run an independent shop with no academic affiliation. Over the past months we have been putting
> a framework of our own on IBM hardware under a discipline I have not often seen applied outside
> registered-report journals: every prediction hashed before the data exists, every null published
> beside the passes, every script and count file public. Twenty-one tests so far. Two of them we got
> wrong, caught with our own controls, and retracted publicly within hours.
>
> None of the physics is new — the last round reproduced entanglement swapping, and we say so plainly
> in the write-up. What may be worth something to you is the apparatus and the willingness to run
> nulls and publish them.
>
> Two things I would value, in either order:
>
> Would you be willing to tell me where the methodology is weak? Unsparing is what I am after; I have
> already published two of my own errors and would rather find the third from you than from the data.
>
> And if any part of your programme needs careful, pre-registered hardware runs that nobody has time
> to babysit, I would do that work. The Open Plan's ten minutes a rolling month is our ceiling; a
> collaboration that carried QPU access would be worth more to us than a grant, and I would expect to
> earn the access rather than receive it.
>
> Everything is at github.com/lightinmotion1/heptaract-quantum-walk and
> lightinmotionfilms.com/lightbox/heptaract, including both retractions.
>
> Miah J. Fry
> Light in Motion Films

---

## Order of play

1. **Unitary microgrant** — the only door we are plainly eligible for, rolling, and the video plays
   to our strongest skill. Do this one first.
2. **Collaborator letters** — three to five, each genuinely specific. Slow, but the only route to
   hours rather than minutes.
3. **Pay-as-you-go** — keep in reserve. Knowing a minute costs $96 is itself useful: it prices every
   experiment we design and is a reason to keep aiming tests with the calibration log.
