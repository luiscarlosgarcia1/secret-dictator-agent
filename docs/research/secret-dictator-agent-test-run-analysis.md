# Secret Dictator agent: test-run weakness analysis

## Scope and limits

This review examined the ten completed JSON artifacts already in `test runs/` and the current `agent.py`.  Every artifact seats the same user source (`4da4a928...`), which is also the SHA-256 of the current `agent.py`, at `seat-1`; therefore the decisions below are from this implementation, not an inferred bot identity.  The ten outcomes are 4 faction wins and 6 losses: Liberal 1/4, Fascist 3/3, Dictator 1/3.  Seat and role are randomized while the evaluated bot is always `seat-1`, and opponent pools differ (Default Dana, Rookie Ray, Champion Charles, Aspiring Amelia, and mixed).  This is a useful trace sample, not a controlled estimate of win rate or causal effect.

The artifacts preserve complete server events and per-seat visible observations, but do not retain the user agent's submitted request bodies.  The report therefore treats a decision as attributable only when the source SHA, seat, wire action, legal game result, and applicable deterministic branch align.  It does not treat private facts from a different seat's observation as available to `seat-1`.

Four independent read-only passes cross-checked the run-level interpretation: three batches of three artifacts and one final single-artifact batch.  For each artifact, the reviewers ranked three explanations, separating a direct seat-1 action from card draw, role assignment, and other-seat play.  Their common result was that only the two Liberal votes identified below are counterfactually decisive; most wins and the other losses contain substantial outcome variance.

| Run | `seat-1` role | Outcome | Relevant result |
| --- | --- | --- | --- |
| `4616b2f7` | Liberal | loss | Dictator elected Chancellor (4F/2L) |
| `516838e7` | Fascist | win | six Fascist policies |
| `5f12f881` | Dictator | loss | Dictator executed |
| `635976b7` | Dictator | loss | five Liberal policies |
| `6c02bbae` | Liberal | loss | Dictator elected Chancellor (3F/3L) |
| `6daf104a` | Fascist | win | Dictator elected Chancellor |
| `84e4843d` | Liberal | win | five Liberal policies |
| `a8f9b092` | Liberal | loss | Dictator elected Chancellor (3F/4L) |
| `bb845a93` | Fascist | win | Dictator elected Chancellor |
| `d30a9068` | Dictator | win | six Fascist policies |

## Per-run batch cross-check

This compact index preserves the three ranked explanations requested for every examined run.  “Direct” means the event trace supports a material seat-1 contribution; it does **not** mean a claim that the action alone determined the match.

| Run | Three strongest explanations from its batch review |
| --- | --- |
| `4616b2f7` | **Pivotal bot error:** Liberal yes at event 160 elected the zero-risk Dictator 4–2; Fascist early-government/policy cluster accelerated the threshold; seat-1 silence is a plausible but unproven lost-information channel. |
| `516838e7` | **Confirmed flaw, non-causal here:** Fascist seat-1 rejected self/Dictator governments; teammate nominations used faction knowledge; the six-policy win was mainly other-seat play against one homogeneous opponent pool. |
| `5f12f881` | Liberal President executed Dictator seat-1; opponents/card sequence reached execution; silent Dictator had no counter-narrative, but no causal counterfactual. |
| `635976b7` | Liberal enactments and draw/opponent sequence produced five Liberal policies; executive shots missed actual Liberals but are not proven causal; seat-1 special-election governments did yield Fascist policies. |
| `6c02bbae` | Seat-1 correctly but non-pivotally rejected the final Dictator government; its earlier Dictator nomination had genuinely ambiguous evidence; investigation of a Fascist had no demonstrated public follow-through. |
| `6daf104a` | Seat-1’s legislative choices directly supplied two early Fascist policies; it contradicted itself by voting no on a known-Dictator nomination; the eventual Dictator election depended on others/card sequence. |
| `84e4843d` | Seat-1 enacted one Liberal policy from an available Liberal; its forced `FFF` Presidency was deck variance; the remaining Liberal policies were mostly other-seat outcome. |
| `a8f9b092` | **Pivotal bot error:** Liberal yes at event 197 elected zero-risk Dictator 4–3; public threshold warnings were not incorporated by the score-only/silent policy; earlier legislative play was not the loss mechanism. |
| `bb845a93` | **Confirmed flaw, non-causal here:** Fascist Chancellor voted no on its own government; it then enacted Fascist and supported the Dictator at threshold; the win chiefly relied on teammate nomination and broad other-seat support. |
| `d30a9068` | Dictator seat-1 enacted Fascist while holding Liberal; fellow Fascists/opponents and deck sequence produced most of the 6–1 result; late self-nomination/no votes were harmless but not evidence of strong play. |

## Findings, ordered by likely impact

### Confirmed: the Liberal late-game vote rule let two Dictator governments pass

At the Dictator-election threshold, the Liberal branch rejects a Chancellor only when that seat already has a positive `dictator_risks` score ([`agent.py:315`](../../agent.py#L315)); otherwise it accepts any government whose two additive policy scores are at most 1 ([`agent.py:317-319`](../../agent.py#L317-L319)).  Those scores receive only +/-1 from enacted government policy and an exact private investigation ([`agent.py:162-177`](../../agent.py#L162-L177), [`agent.py:202-207`](../../agent.py#L202-L207)); public statements and card-account consistency are deliberately ignored.

* In `4616b2f7`, with four Fascist policies already enacted, `seat-3` nominated `seat-4`. `seat-1` voted **yes** at event 160; the Fascist team (`seat-2`, `seat-3`, `seat-4`) also voted yes, while the two surviving other Liberals voted no. The election therefore passed 4-2 and immediately ended the match because `seat-4` was the Dictator. This was a deciding vote, not merely a losing-side vote.
* In `a8f9b092`, at three Fascist policies, `seat-4` nominated `seat-2`; `seat-1` voted **yes** at event 197. `seat-2`, `seat-3`, and `seat-4` supplied the other yes votes; `seat-5`, `seat-6`, and `seat-7` voted no. The 4-3 government elected Dictator `seat-2` and ended the match. Again, changing `seat-1` to no would have defeated that government.

The first trace includes a public investigation that only told `seat-1` that `seat-2` had investigated `seat-4`, not the private Fascist result, so it would be wrong to call this a dropped-evidence fault. The weakness is the much narrower one demonstrated by both traces: the score has no uncertainty or election-threshold safety margin, so an unmarked Dictator is treated as a routine low-risk Chancellor.

**Next validation:** run 3--5 targeted Liberal `seat-1` matches that reach 3+ Fascist policies with the actual Dictator as a zero-score, non-term-limited Chancellor. Hold the opponent pool fixed, and compare the current vote against a threshold rule that defaults to no unless the Chancellor is affirmatively cleared. Record whether the bot's vote is pivotal and whether the replacement produces chaos or a Liberal win; do not infer a universal default-no policy from these two traces alone.

### Confirmed in code and observed: a Fascist votes against some governments containing itself or the Dictator

For a Fascist, `_vote` returns yes only for a post-threshold known-Dictator Chancellor or when the President/Chancellor is in `knownFascists` ([`agent.py:308-312`](../../agent.py#L308-L312)). `knownFascists` intentionally excludes both the acting Fascist and the known Dictator ([`agent.py:278-282`](../../agent.py#L278-L282)). Thus before three Fascist policies, the bot votes no on a government in which it is Chancellor and its known Dictator is President.

`516838e7` shows the branch on the wire: Fascist `seat-1` voted no in round 3 when Dictator `seat-2` nominated `seat-1` (events 17--24), and also voted no in round 1 when it itself was Chancellor (events 1--8). Both governments failed. The faction nevertheless won by six policies, so these actions are **not proven to have cost a game**; they are confirmed self-sabotaging actions that can make the team's voting pattern predictable and throw away a legal government.

**Next validation:** 3--5 Fascist `seat-1` runs before the election threshold with (a) self as Chancellor under a liberal President, (b) self as Chancellor under known Dictator President, and (c) a government containing only the known Dictator. Compare election pass rate, policy result, and later suspicion/execution outcome against a rule that always supports a government containing self and treats Dictator inclusion separately.

### Plausible: a permanently silent discussion policy leaves the agent unable to exploit the strongest public evidence

The only discussion response is `{"type":"discussion-contributed"}` ([`agent.py:374-377`](../../agent.py#L374-L377)), so it cannot publish a card account, probe contradictory accounts, reinforce a vote coalition, or make a faction-appropriate cover claim. In all ten examined artifacts, every `seat-1` `discussion-contributed` event has `statement: null`. This is especially visible in `4616b2f7`: other seats exchanged detailed card-account and suspicion messages after rounds 1--3, while every `seat-1` contribution at events 11, 18, 25, 39, 46, 66, and 73 was null.

This coincides with three Liberal losses out of four, including the pivotal late votes above, but no artifact counterfactual shows that speaking would have changed another player's vote. Silence may also be a deliberate anti-leak tactic for Fascists. It should therefore not be represented as a confirmed cause of a loss.

**Next validation:** replay matched seeds/opponent sets with a minimal role-safe discussion policy: Liberal posts only its own authorized card facts or a concrete threshold warning; Fascist/Dictator use a non-private neutral statement. Compare other-seat votes, government pass rates, executions, and fault count. Retain only messages that are valid under the recipient seat's visible history.

### Plausible: the risk model confuses weak policy correlation with Dictator identification

`dictator_risks` is incremented exactly alongside `fascist_scores` for a Fascist government policy ([`agent.py:170-177`](../../agent.py#L170-L177)); executive targeting and nominations use their sum ([`agent.py:244-253`](../../agent.py#L244-L253), [`agent.py:294-301`](../../agent.py#L294-L301)). A player with few governments, forced Fascist hands, or successful concealment remains at zero and becomes a preferred late candidate; the two pivotal loss traces are concrete examples of that blind spot. Conversely, the model makes no distinction between President and Chancellor responsibility despite their different policy choices.

The evidence supports the model limitation but not a particular replacement weighting: observed enacted policy alone cannot prove either officeholder's faction, and cards/claims are not fully public. The run set has too few bot executive decisions in losing Liberal games to quantify whether executions/investigations are also degraded.

**Next validation:** instrument a read-only replay scorer that labels each decision state by actual hidden role after the match, then measure rank of the actual Dictator under the present score at every 3+ Fascist-policy vote/nomination/execution. Stratify by forced versus discretionary legislative hands from the server artifact. This isolates score calibration before changing behavior.

## Insufficient evidence / no finding

* **Protocol faults or malformed legal actions:** none are evidenced. All ten matches are `completed`; the event traces show `seat-1` actions being accepted, and no outcome reports an agent fault. The ADR's fault-resistance priority appears intact for these exercised shapes.
* **Legislative and veto policy cost:** there are no trace-backed losses tied to a `seat-1` private-card decision. The source selects faction-preferred legal cards only from authorized hands ([`agent.py:256-264`](../../agent.py#L256-L264)) and the sole observed veto is in a Dictator win. More targeted hands are needed.
* **Executive-power cost:** `seat-1` received investigation/execution authority in only a subset of runs. The Liberal loss `6c02bbae` includes a bot investigation of `seat-2`, but the later Dictator election was `seat-4`/`seat-3` and `seat-1` voted no; it is not evidence that the investigation target caused the loss.
* **Role or seat disadvantage:** three Fascist wins versus two Dictator losses and three Liberal losses are compatible with random deck/opponent effects at n=10. The fixed evaluated seat and changing opponent pool prevent a role-strength conclusion.

## Bottom line

The clearest loss-linked defect is the late Liberal vote gate: it produced the deciding yes vote in two Dictator-election losses because the real Dictator had accumulated no narrow policy-derived risk. The separately confirmed Fascist own-government/no-Dictator vote bug is strategically serious but has not yet shown a loss in this sample. The next evidence should be a small, deliberately stratified set of threshold votes and Fascist own/Dictator governments, not a broad additional tournament.
