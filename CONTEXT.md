# Arenova Secret Dictator Agent

This project produces a competing agent for Arenova's Secret Dictator assessment. The agent plays under the `secret-dictator-7p-event-sourced-v1` rules profile, using only the information visible to its assigned seat.

## Match and Roles

**Secret Dictator**:
The assessment's event-sourced implementation of the Secret Hitler social-deduction game. A match has an elected government, legislative sessions, executive powers, and hidden factions.
_Avoid_: Secret Hitler, Clue

**Seat**:
A stable player identity, such as `seat-1`, assigned one independently running agent process for a match.
_Avoid_: Player number, bot slot

**Liberal**:
A role on the Liberal faction. Liberals win by enacting five Liberal policies or executing the Dictator.
_Avoid_: Good role, civilian

**Fascist**:
A non-Dictator role on the Fascist faction. Fascists know their fellow Fascists and the Dictator at match start in the seven-player profile.
_Avoid_: Evil role, enemy

**Dictator**:
The hidden Fascist-faction leader. The Dictator wins with the Fascists if elected Chancellor after three Fascist policies, but does not know the other Fascists in the seven-player profile.
_Avoid_: Hitler, fascist leader

**Visible History**:
The complete sequence of public events and seat-authorized private observations delivered with a decision request. It is the agent's authoritative evidence for the current match state.
_Avoid_: Global replay, server state

## Government and Policies

**Government**:
The President and Chancellor pair proposed, voted on, and, if elected, authorized to run a legislative session.
_Avoid_: Administration, ticket

**Policy**:
A Liberal or Fascist policy enacted by a government or by chaos. Policy totals determine win conditions and unlock executive powers.
_Avoid_: Card, law

**Legislative Information**:
The private policy observations held by the sitting President or Chancellor and the public claims made about them. These observations may constrain, but do not prove, faction alignment.
_Avoid_: Proven card history, shared hand

**Chaos**:
The forced policy enactment after three consecutive failed governments. Chaos resets term limits and does not grant the executive power that a normal Fascist enactment might grant.
_Avoid_: Failed round, random government

**Executive Power**:
A one-use President action unlocked by an eligible Fascist policy, including loyalty investigation, special election, policy peek, or execution.
_Avoid_: Bonus turn, presidential policy

## Decisions and Reliability

**Decision Request**:
One runner input that names the acting seat, required decision kind, visible history, and a response allowance. Exactly one matching game response is required.
_Avoid_: Event, turn notification

**Legal Response**:
A response object whose type and fields match the current decision kind and whose target or policy is allowed by the reconstructed visible state.
_Avoid_: Best move, plausible response

**Agent Fault**:
The runner outcome for an invalid, late, or failed decision. Startup and first-government-round faults abort the match; later faults fall back to a baseline decision for that request.
_Avoid_: Bad strategy, lost round

**Baseline Agent**:
The provided deterministic reference player, `default-dana.mjs`. It is a protocol and fallback-behavior reference, not the competitive target.
_Avoid_: Opponent model, optimal agent

**Replay**:
A completed match artifact such as `example_run.json`, used to learn the event and observation shapes and to test reconstructed decisions.
_Avoid_: Visible history, live match
