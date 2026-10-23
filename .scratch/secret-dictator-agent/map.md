# Secret Dictator agent wayfinder map

## Destination

Produce an implementation-ready route for one self-contained Python 3.13 Secret Dictator agent that is materially stronger than `default-dana.mjs` while prioritizing valid, timely decisions under the `secret-dictator-7p-event-sourced-v1` profile.

## Notes

The deliverable will be packaged with `crucible.json` at ZIP root and run as a persistent JSONL process. `Visible History` is authoritative. The existing ADR requires fault resistance before tactical optimization; strategy claims require replay or practice evidence.

## Decisions so far

- [Recover the authoritative protocol contract](issues/01-protocol-and-replay-contract.md): Cover eight baseline decision kinds, reconstruct only seat-visible state, and validate every strategic choice against deterministic legal fallbacks.
- [Choose the faction-aware information model and tactics](issues/02-faction-information-and-tactics.md): Use bounded public-evidence scores, role-specific deterministic play, and a final legal-response guard instead of a model call in the move path.
- [Define replay validation and release gates](issues/03-replay-harness-and-release-gates.md): Gate release on a seat-visible contract matrix, replay regressions, packaging smoke tests, and clearly separated protocol and competitive evidence.

## Not yet specified

- None.

## Out of scope

- Submitting, publishing, or running paid/practice Arena matches.
- Changing the assessment's game rules or runner protocol.
- Measuring the exact win rate and opponent mix; this follows implementation and the defined validation gates.
