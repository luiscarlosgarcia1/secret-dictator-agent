# 06: Fail closed on un-cleared Chancellor elections at the Dictator threshold

**What to build:** When three or more Fascist Policies are enacted, a Liberal Seat safely rejects a Government whose Chancellor has not been affirmatively cleared as non-Dictator, while retaining a defined, legal Chaos-imminence exception. The resulting vote must be derived solely from that Seat's Visible History and remain convertible to a Legal Response under incomplete but recoverable history.

**Blocked by:** None (can start immediately).

**Status:** complete

- [x] A Liberal Seat at the Dictator-election threshold does not approve a Chancellor merely because the current bounded public-risk model has assigned that Seat zero Dictator risk; a documented affirmative-clearance rule and narrow Chaos exception define every outcome.
- [x] Regression coverage reproduces the decisive `seat-1` votes in completed runs `4616b2f7` (event 160) and `a8f9b092` (event 197), demonstrating that the revised decision rejects each actual Dictator Government without access to global roles, deck order, or another Seat's private observations.
- [x] Coverage distinguishes an affirmatively cleared Chancellor, a known Fascist, an un-cleared eligible Chancellor, and a two-failed-Government Chaos-imminence state, asserting a valid deterministic vote response for each.
- [x] The change preserves the fault-resistance boundary: malformed or incomplete optional history does not throw, no decision path emits a non-legal vote enum, and existing replay/contract validation remains green.
- [x] Validation reports the exact targeted scenarios exercised and does not claim a tournament win-rate gain from the two trace counterfactuals alone.

## Evidence and scope

Both available loss traces were decided by the evaluated Liberal Seat's vote for an actual Dictator whose public Dictator-risk value was zero. In `4616b2f7`, changing that vote would turn the final 4--2 pass into a 3--3 failed Government. In `a8f9b092`, it would turn the final 4--3 pass into a 3--4 failure. This ticket corrects that narrow, demonstrated decision rule; it does not introduce free-form claim parsing, hidden-information inference, or a general always-reject policy.

## Comments

Completed with an affirmative-clearance gate: only an authorized Liberal
investigation result clears a Chancellor as non-Dictator. At three or more
Fascist Policies, un-cleared Chancellors are rejected except at two failed
Governments when the entire proposed Government has non-positive bounded public
risk, avoiding an otherwise imminent Chaos policy. The targeted tests rebuild
the two decisive prefixes only from `seat-1` recorded observations and reject
both zero-risk Dictator Chancellors. This is a trace counterfactual correction,
not a measured tournament win-rate claim.

