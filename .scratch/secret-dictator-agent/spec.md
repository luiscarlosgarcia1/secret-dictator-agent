# Build the Secret Dictator agent

Status: ready-for-agent

## Problem Statement

An Arenova competitor needs one dependable Secret Dictator agent for the `secret-dictator-7p-event-sourced-v1` profile. The supplied Baseline Agent is a useful protocol reference but makes predictable, non-faction-aware decisions. A more capable agent must improve its play without ever relying on hidden global replay information, producing an invalid Legal Response, contaminating stdout, or missing a decision deadline. Those failures can abort an early match or cause the runner to substitute the Baseline Agent, so tactical strength is only meaningful when fault resistance is already in place.

## Solution

Deliver one self-contained Python 3.13 agent packaged for Arenova. It will run as a persistent JSONL process, reconstruct a seat's authoritative Visible History into a bounded Read Model, make deterministic role-aware choices, and pass every choice through a final Legal Response builder with a deterministic fallback.

The agent will cover all currently known decision kinds, use only the private observations authorized to its Seat, and keep public discussion bounded and non-sensitive. Its strategy will use conservative public evidence for Liberals and the authorized Fascist setup knowledge for Fascists, while the Dictator follows the public-evidence model because it lacks teammate knowledge in this profile. Local replay-driven and synthetic validation will establish protocol readiness; competitive-improvement claims remain conditional on a separately measured, role-balanced tournament.

## User Stories

1. As an Arenova competitor, I want one self-contained Python agent package, so that I can submit it without installing dependencies or combining multiple services.
2. As an assigned Seat, I want the agent to preserve its JSONL process across requests, so that each Decision Request receives a timely response.
3. As the runner, I want exactly one newline-terminated JSON response for each request, so that the agent does not cause an Agent Fault through malformed output.
4. As the runner, I want initialization requests answered with the expected empty response, so that the agent enters a match without a startup fault.
5. As an acting Seat, I want every current decision reconstructed from Visible History, so that the decision reflects only evidence I am authorized to see.
6. As a Liberal, I want policy, government, and executive decisions based on bounded public evidence, so that I can advance Liberal wins while avoiding unsupported certainty.
7. As a Fascist, I want to use the setup knowledge authorized to me, so that I can coordinate with known teammates and protect the Dictator without protocol risk.
8. As the Dictator, I want a strategy that does not assume I know my teammates, so that I behave correctly under the seven-player profile's information rules.
9. As a Liberal at three Fascist Policies, I want high Dictator-risk Chancellors rejected unless legal alternatives are no safer, so that I reduce the immediate Dictator-election loss condition.
10. As a Fascist President after three Fascist Policies, I want to nominate the known Dictator whenever it is legal, so that the Fascist faction can pursue its decisive election win.
11. As a President, I want only eligible live Seats offered as Chancellor or executive targets, so that every target response is legal.
12. As a Chancellor or President with Legislative Information, I want the selected Policy to come from my actual private hand, so that private-policy decisions cannot fault.
13. As a Liberal Chancellor facing two Fascist Policies late in the game, I want to request or accept a veto only in the defined terminal-risk case, so that a veto is legal and strategically purposeful.
14. As a Fascist officeholder, I want Fascist Policies preferred when my private hand permits them, so that faction strategy is consistent and deterministic.
15. As a Seat receiving incomplete or inconsistent history, I want a computed legal fallback whenever one exists, so that recoverable uncertainty does not become an Agent Fault.
16. As a participant in public discussion, I want concise optional public messages that never reveal private setup knowledge, private policy hands, or private investigation results, so that the agent does not leak faction information.
17. As a maintainer, I want stdout reserved exclusively for protocol responses and diagnostics directed to stderr, so that logs cannot invalidate a response stream.
18. As a maintainer, I want unsupported request kinds and malformed optional content handled in a controlled, tested manner, so that faults are visible without unexpected process crashes.
19. As a maintainer, I want a seat-visible replay harness, so that replay artifacts can test behavior without granting the agent global roles, deck order, or other hidden data.
20. As a maintainer, I want a contract matrix covering every known decision kind, role, and legal boundary, so that response validity has evidence beyond a single replay.
21. As a release owner, I want a package smoke test after archive extraction, so that the submitted artifact—not merely the source tree—is proven runnable.
22. As a competitor, I want protocol readiness and competitive performance reported separately, so that unmeasured strategy hypotheses are not presented as proven win-rate gains.

## Implementation Decisions

- The deliverable is one standard-library-only Python 3.13 entrypoint plus the required package manifest. It is a persistent JSONL process; it writes exactly one response object per input line and flushes immediately. Diagnostic output is stderr-only.
- The JSONL boundary is the principal seam and the final authority for behavior. The agent accepts initialization and decision requests, returning an empty object for initialization and one response matching the requested decision kind.
- A Visible-History reconstructor builds a Read Model for each decision. It tracks ordered Seats, the acting Seat's authorized role knowledge, live Seats, current and prior Government members, Policy totals, investigations, veto state, and the acting Seat's private policy observations. Replay-only global fields, including the complete deck and global roles, are never inputs to the Read Model.
- The supported decision kinds are Chancellor nomination, voting, presidential discard, Chancellor legislation, presidential veto response, loyalty investigation, special election, execution, and discussion. The response builder owns the response-type and field contract for each kind.
- Legal-target computation is centralized. Chancellor nominees exclude the current President and term-limited officials, with the five-live-Seat exception; investigations exclude the current President and previously investigated targets; special elections and executions exclude the current President. Every strategy target is filtered through this computation.
- The deterministic fallback selects the first clockwise eligible Seat from the acting Seat, uses an allowed policy from the relevant private hand, chooses valid vote and Boolean enums, and keeps discussion minimal. Strategy failure, mismatch, or incomplete evidence must resolve to this fallback whenever a legal response can be derived.
- The strategy layer returns only decision intent. A final Legal Response builder independently checks the required type, enum values, Seat membership, and policy membership before emitting it. It substitutes the fallback on invalid strategy output or a handled exception.
- The public-evidence model maintains separate bounded `fascist_score` and `dictator_risk` values per living Seat, alongside hard facts. It uses only structured visible events, fixed capped weights, and Seat order as the stable tie-breaker. Free-form claims are ignored unless the protocol exposes them as structured facts.
- Liberal strategy chooses low combined-risk eligible Governments, tolerates a borderline low-risk Government when two failed Governments make Chaos imminent, investigates high Dictator risk, executes high combined risk while favoring confirmed Fascists, and calls special elections for low-risk candidates. A known Liberal investigation result is the strongest Chancellor evidence; at three Fascist Policies, known Fascists are never approved as Chancellor.
- Fascist strategy uses authorized team knowledge to support Fascist Governments, protect the Dictator, and direct executive powers away from known teammates. At three or more Fascist Policies it pursues legal election of the known Dictator; when that is unavailable it selects the safest known teammate. The Dictator never assumes teammate knowledge and follows the public-evidence approach except when voting for its own legal Chancellor election after three Fascist Policies.
- Legislative strategy is private-hand-validated. Liberals discard or enact Liberal when present; Fascists prefer Fascist where present. A Liberal veto is limited to the all-Fascist, late-game terminal-risk condition without a preceding rejection. No first-version camouflage rule is included for a Fascist Liberal enactment.
- Discussion passes by default. When the protocol supports it immediately after a Policy, the agent may make one short ASCII-only statement about the public Policy result and, at three Fascist Policies, a high-risk Chancellor warning. It never discloses private observations, team knowledge, received investigation results, or internal scores.
- Packaging places the manifest at the archive root, declares the Python 3.13 runtime, and includes only the runtime files required by the entrypoint. Strategy contains no model relay or other network call in its critical decision path.
- This design follows the existing fault-resistance ADR. Tactics may be improved after protocol coverage, but no optimization may weaken deterministic validation or legal fallbacks.

## Testing Decisions

- The primary test seam is a process-level JSONL harness. It launches the packaged agent, submits one request at a time, and observes only externally visible behavior: one parseable stdout response before a short local timeout, no stdout contamination or second response, and no process exception.
- Contract tests cover initialization and every supported decision kind for Liberal, Fascist, and Dictator roles and for each action-bearing Seat position. They assert response type, permitted enum, legal target membership, private-hand policy membership, and lack of private-fact leakage in discussion; they do not assert internal scoring steps or a particular tactical target where more than one is legal.
- Boundary cases include the first Government; seven, six, and five live Seats; President and Chancellor term limits; a single legal target; exhausted investigation targets; mixed and uniform policy hands; zero, three, and five Fascist Policies; accepted and rejected vetoes; Chaos; execution; special-election return; deck reshuffle; and empty or malformed optional text.
- Replay regression tests derive seat-projected prefixes and observations from the completed Replay, rather than providing its global event stream or hidden facts. They assert that every reconstructable Decision Request yields a legal, deterministic response, not that the agent copies the historical agent's tactical choice.
- Small hand-built fixtures cover branches absent from the Replay, including presidential discard, veto request and response, execution, failed Governments and Chaos, and future policy-peek support if it becomes an exposed decision.
- After fixed contract coverage is passing, coherent randomized histories exercise the response builder. At least 1,000 generated legal requests must produce no faults; malformed-history cases must not throw and must use a bounded fallback whenever legal state is recoverable.
- Release validation compiles the entrypoint with Python 3.13, runs a clean JSONL smoke test, passes the full contract matrix and replay regression suite, creates the archive, extracts it to a temporary directory, validates its manifest and root layout, and repeats the smoke test against the extracted entrypoint.
- The Baseline Agent is prior art for request, history, legality, and fallback contract behavior. The supplied Replay is prior art for event and observation vocabulary. Neither defines the desired tactical decisions.
- The agent is called protocol-ready only after all fixed contract cases, all reconstructable replay requests, packaging checks, and the randomized legal-response threshold pass with zero faults. It is called competitively improved only after a reproducible, multi-seed, role- and Seat-balanced tournament against the exact Baseline Agent and a stated mixed-opponent lineup reports wins, faults, and confidence intervals.

## Out of Scope

- Submitting, publishing, or running paid or practice Arenova matches.
- Changing the assessment rules, runner protocol, or the `secret-dictator-7p-event-sourced-v1` profile.
- Claiming a measured win rate or a large-majority advantage before the specified tournament evidence exists.
- Using global Replay roles, deck order, unobserved policy hands, hidden opponent state, or an AI relay in the live decision path.
- Advanced free-form social deduction, parsing unstructured claims, or a first-version Fascist camouflage policy.
- Support for decision kinds not exposed by the recovered contract, except controlled handling and a future extension point.

## Further Notes

The required test seam is intentionally the highest existing seam: the persistent JSONL process. This preserves the core architectural rule that all internal strategy must be safely convertible to a Legal Response. The only supported source of current match truth is the acting Seat's Visible History; the Replay is validation evidence, not runtime knowledge.

The specification deliberately distinguishes design confidence from competitive proof. The strategy should be materially stronger than the predictable Baseline Agent in design, but release language must not imply that strength has been measured until the defined tournament gates are complete.
