# Secret Dictator: four new root-run analysis

## Scope, method, and limits

This report examines only the four untracked root-level replay artifacts: `0ff64651`, `20711f3a`, `94d547a1`, and `e48d8286`.  In every run, the evaluated agent is Moriarty at `seat-1`; its recorded source SHA is `eacd793...45834eb1`, which matches the current `agent.py`.  Evidence below is from the artifacts' authoritative event histories and the deterministic code paths in `agent.py`, not from hidden-role facts that `seat-1` could not have known while playing.

The cohort is three Fascist wins and one Liberal win: Moriarty has three losses (two as Liberal, one as Fascist) and one win (as Dictator).  Seat remains fixed, but decks, roles, opponent decisions, and opponent mix vary; several opponents use AI.  Four games are enough to expose deterministic bad branches, but not to estimate win rate or prove that a non-pivotal choice changed a result.  All four matches completed, and no event records an invalid action, timeout, or baseline fallback.

| Run | Bot role | Result | What it can establish |
| --- | --- | --- | --- |
| `20711f3a` | Liberal | loss, Dictator elected at 4F/1L | A bot vote flipped two tied, safe self-Chancellor governments from pass to fail. |
| `e48d8286` | Liberal | loss, Dictator elected at 3F/4L | Terminal bot vote was correct but non-pivotal; its legislation was forced or Liberal-favourable. |
| `94d547a1` | Fascist | loss, five Liberal policies (2F/5L) | Teammate-first nomination failed; bot had no completed legislative or executive turn. |
| `0ff64651` | Dictator | win, Dictator elected at 3F/2L | Bot's mixed-hand Fascist enactment made it publicly suspicious; allies/opponents created the win. |

## Findings, ordered by likely impact

### Confirmed, high impact: a Liberal rejects a government with itself as Chancellor at the Dictator-election threshold

In `20711f3a`, Liberal `seat-1` was nominated Chancellor at four Fascist policies in round 6 and round 9.  It voted **no** both times (`events[117]` and `events[138]`); each vote finished 3--3, so changing only seat-1's vote would have passed a government whose Chancellor was known by seat-1 to be Liberal.  The failed-government chain continued through a Liberal chaos policy, then Fascist `seat-5` nominated the real Dictator `seat-7`, which passed 4--2 and ended the game (`events[144]`--`events[150]`; outcome `dictator-elected-chancellor`, 4F/1L).

The cause is deterministic.  Setup records the bot's private role and faction (`agent.py:116-132`), but `confirmed_non_dictators` is populated only by a private `investigation-result` of Liberal (`agent.py:204-214`).  At 3+ Fascist policies, `_vote` accepts only a Chancellor in that set, apart from the imminent-chaos exception (`agent.py:334-343`).  It never treats `state.you` as a known non-Dictator.  This is a strategic error, not a protocol fault: the actions were legal, but the bot discarded its strongest available certainty twice.

**Next validation:** replay the exact round-6 and round-9 visible prefixes with one isolated correction: approve when the bot is the Chancellor and its own role is Liberal.  Confirm the wire action remains legal, then run 3--5 matched Liberal-seat games reaching 3+ Fascist policies with self as Chancellor; record whether the vote is pivotal and the resulting policy/chaos path.

### Confirmed behavior; plausible broader weakness: blank discussion provides no defense, coordination, or cover

`agent.py:400-403` always returns an empty `discussion-contributed` response.  This occurred in every analyzed run.

* In `0ff64651`, Dictator seat-1 enacted Fascist from an F/L Chancellor hand in round 3 (`events[26]`).  The Liberal President publicly said it had passed F/L and called for seat-1's rejection/execution; seat-1 submitted null discussion contributions in each following wave (`events[28]`, `[35]`, `[42]`).
* In `20711f3a`, Liberal seat-1 enacted forced F/F hands in rounds 1 and 3; it did not publish the forced-hand explanation, and Fascist seat-5 framed both Fascist enactments (`events[10]`, `[12]`, `[63]`--`[65]`).
* In `e48d8286`, after the third Fascist policy, seat-4 warned publicly about unconfirmed Chancellors, but seat-1 was silent (`events[191]`, `[194]`, `[201]`, `[203]`).  A special election then enabled the final Dictator ticket.

The channel is therefore demonstrably unused precisely when it could communicate authorized public facts.  It is **not confirmed as a cause of a loss**: `e48d8286` already contained a public warning, and the decisive Liberal vote came from another seat; `0ff64651` still won.  Treat it as an exploitable and predictable information vacuum, not yet as quantified loss attribution.

**Next validation:** hold role/seat/opponent pool fixed in 3--5 threshold or post-legislation games.  Compare silence with (a) a Liberal statement limited to its own forced hand or a public threshold warning, and (b) a non-private Fascist/Dictator cover statement.  Measure other seats' votes, execution target, and fault count.

### Plausible: Fascist government construction is rigidly teammate-first and can sacrifice cover

In `94d547a1`, Fascist seat-1 became President at 2F/4L and nominated known Fascist teammate seat-5 (`events[158]`).  The ticket failed 3--4; the bot offered no discussion rationale.  This is exactly the nomination branch: before the election threshold, `_nomination_target` selects from known fellow Fascists whenever possible (`agent.py:294-300`), and the vote branch consistently supports known teammates or the known Dictator (`agent.py:315-330`).  The faction then lost 2F/5L.

This is the bot's only proactive government-building turn in that match.  It is **not a confirmed cause**: the bot never held a completed legislative or executive turn, and the trace cannot show that a cover nomination would have passed or enacted Fascist.  The loss was dominated by other Presidents/Chancellors and policy availability: six elected governments produced five Liberal policies.

**Next validation:** 3--5 matched Fascist-President games at 2F and 3--4 Liberal policies, where a teammate, the known Dictator, and a plausible cover candidate are all legal.  Compare pass rate, enacted policy, later suspicion, and execution survival across teammate-first and cover-oriented nomination policies.

### Confirmed non-finding: neither Liberal loss supports a legislative blunder claim

`e48d8286` is important negative evidence.  Liberal seat-1 received F/F as Chancellor in round 3 and had to enact Fascist (`events[25]`--`[26]`); later, as President, it discarded Fascist from F/F/L and Liberal Chancellor seat-4 enacted Liberal (`events[156]`--`[157]`).  At the deciding 3F election, it correctly voted no on the actual Dictator (`events[209]`--`[216]`), but the ticket still passed 4--3 because Liberal seat-2 and all Fascists voted yes.

The same source rule picks the faction-preferred legal policy from the authorized hand (`agent.py:263-271`, `374-385`).  This run does not justify changing legislative policy or the terminal default-no rule; it is an opponent-coalition loss, not bot-caused terminal play.

**Next validation:** none for legislative logic from this evidence alone.  Keep it out of the next tactical patch; use future reruns only if a bot-held mixed hand correlates with a loss.

## Per-run three-factor interpretation

| Run | Three most likely explanations, in order |
| --- | --- |
| `20711f3a` | 1. **Direct bot error:** self-Chancellor no votes twice broke two tied safe governments. 2. Failures/chaos then gave Fascists the route to their Dictator ticket. 3. Silent forced-hand explanations plausibly made the bot easier to frame, but are non-causal here. |
| `e48d8286` | 1. Other Liberal's final yes plus Fascist coordination elected the Dictator despite bot's correct no. 2. Bot silence plausibly failed to organize resistance but a public warning already existed. 3. Bot legislation was forced or Liberal-favourable, so it is excluded as a cause. |
| `94d547a1` | 1. Other-seat Liberal enactments/deck sequence drove 5L. 2. Teammate-first late nomination failed and is a plausible lost opportunity. 3. Rigid aligned-government voting was predictable but not pivotal in this trace. |
| `0ff64651` | 1. Allied special-election and nomination sequence created the decisive Dictator ticket. 2. Bot's F-over-L enactment advanced 3F but visibly incriminated the Dictator. 3. Silent discussion left the accusation unanswered; opponents nevertheless failed to capitalize. |

## What the cohort does and does not say

The self-Chancellor threshold vote is the only finding with a direct, repeatable code path and two in-run pivotal ballots.  Blank discussion and teammate-first Fascist nomination are real, visible policy limitations, but require matched reruns before claiming they cost games.  There is no evidence here of malformed responses, hidden-history reconstruction failure, veto mistakes, executive-target mistakes, or a general role/seat disadvantage.  Random role assignment is especially confounding: the same fixed seat appears once in each of the relevant roles, while the four outcomes are driven substantially by changing deck and opponent behavior.
