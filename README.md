# Arenova Secret Dictator Agent

A role-aware, fault-resistant agent for the **Arenova Agent Challenge** Secret
Dictator assessment. The game follows the assessment's Secret Hitler-style
hidden-role rules: Liberals work to enact Liberal policies or execute the
Dictator, while the Fascist team seeks Fascist policies and a successful
Dictator election.

It was built as an interview-process assessment artifact—less a game demo than
a practical demonstration of building a reliable agent that can interpret
event-sourced history, act only on seat-authorized information, and make
legally shaped decisions in a social-deduction setting.

[Watch the Secret Dictator walkthrough](https://youtu.be/HZfxI_VF6MA)

## Highlights

- Reconstructs the seat-visible state from event history on every request.
- Keeps private role and faction knowledge separate from public game evidence.
- Handles nominations, votes, legislative policy choices, vetoes, executive
  powers, and discussion turns with one narrow response-building boundary.
- Applies role-aware behavior: pursue the Liberal win condition as a Liberal,
  coordinate from authorized faction knowledge as a Fascist, and protect the
  Dictator's election path without exposing hidden information.
- Validates targets against live seats, term limits, policy tracks, and the
  current request so a bad strategy choice does not become a protocol fault.

The result is designed to make the right kind of decision even when its
faction ultimately loses. In this game, a single match result does not tell the
whole story: roles, the policy deck, government votes, other agents' claims,
and executive choices can overwhelm one otherwise correct ballot.

## Replay snapshots

These assessment replays illustrate the kinds of terminal states and decision
contexts reviewed during development. They are examples, not a controlled
win-rate study.

| Replay evidence | What it shows |
| --- | --- |
| ![Fascist victory by Dictator election](screenshots/Screenshot%202026-10-23%20at%204.27.35%E2%80%AFPM.png) | A completed replay ending in a Fascist win through a Dictator election. |
| ![Liberal victory replay](screenshots/Screenshot%202026-10-23%20at%204.27.51%E2%80%AFPM.png) | A completed replay ending in a Liberal win—useful context for evaluating decisions separately from the final faction result. |
| ![Dictator-seat winning replay](screenshots/Screenshot%202026-10-23%20at%204.28.09%E2%80%AFPM.png) | A completed winning replay in which Moriarty is visibly marked as the Dictator. |

## How it was made

The implementation is a small, self-contained Python 3.13 JSONL process. On
each decision it reconstructs the game from the provided history, then passes
the selected intent through one response builder responsible for the legal wire
format. That separation is important: tactical logic can change without
bypassing the protections that prevent malformed, late, or mismatched actions.

The agent's behavior is driven by structured game evidence rather than hidden
server state. It tracks public policy outcomes, governments, term limits,
chaos, executive actions, and authorized private observations. It uses that
model to distinguish ordinary faction suspicion from the much more urgent
question of whether a Chancellor may be the Dictator once the Fascist track is
at the election threshold.

## Run locally

The Arenova runner communicates over newline-delimited JSON. Start the agent
locally with:

```bash
cd dictator
python3 agent.py
```

Run the regression suite with:

```bash
cd dictator
python3 -m unittest tests/test_agent_core.py tests/test_release.py
```

Create and smoke-test the minimal submission archive with:

```bash
cd dictator
python3 scripts/release.py
```

That command produces `dist/secret-dictator-agent.zip`, containing only the
assessment manifest (`crucible.json`) and runtime entry point (`agent.py`).

## Measuring performance honestly

This agent is built to compete, but it should not be represented with a single
unqualified win-rate number. The outcome varies materially with role draw,
seat order, policy draws, opponents, voting coalitions, and match length. A
credible benchmark should report player count, role distribution, opponent
pool, number of matches, and whether results came from a fresh held-out cohort.

The stronger claim this repository can support is architectural: it is designed
to preserve legal decision-making, use only authorized information, and retain
useful decision quality even in games its faction does not win.

## Repository guide

- `agent.py` — the standalone Secret Dictator JSONL agent.
- `crucible.json` — runtime manifest for the Arenova submission.
- `scripts/release.py` — archive creation and smoke test.
- `tests/` — protocol, strategy, replay-prefix, and release regressions.
- `example_run.json` — local event-history example.
- `screenshots/` — replay evidence shown above.
- `docs/research/` — bounded replay analysis and follow-up validation ideas.

## Scope

This is an independent interview-assessment project for an Arenova challenge.
It is not an official implementation, endorsement, or affiliate of the
commercial game that inspired the assessment rules.
