# 07: Make Fascist Government votes consistently support authorized allies

**What to build:** A Fascist Seat applies an explicit, deterministic pre-threshold vote rule for Governments containing itself or its known Dictator, so it no longer rejects an allied Government accidentally because those Seats are absent from the narrower fellow-Fascist collection. The behavior remains faction-aware without revealing unauthorized setup knowledge or weakening Legal Response validation.

**Blocked by:** 06: Fail closed on un-cleared Chancellor elections at the Dictator threshold.

**Status:** complete

- [x] Before three Fascist Policies, a Fascist Seat supports a legal Government containing itself; the outcome is deliberate rather than an incidental result of teammate-set membership.
- [x] Before the threshold, a Government containing the known Dictator follows a documented cover-strategy rule that is deterministic and separately testable; after the threshold, the existing legal Dictator-Chancellor win condition remains correctly prioritized.
- [x] Regression coverage reproduces the observed contradictory votes in completed runs `516838e7`, `6daf104a`, and `bb845a93`, including a Fascist Chancellor voting on its own Government and a known Dictator nominating the Fascist Seat.
- [x] Coverage verifies that the revised rule never relies on information unavailable to the acting Seat, never selects or approves an illegal Government, and leaves Dictator-role voting governed by the Dictator's distinct public-evidence strategy.
- [x] The full contract and replay validation remains fault-free, and the validation report distinguishes corrected self-sabotaging behavior from a demonstrated improvement in match outcome; the current evidence contains the behavior in wins, not a proven loss.

## Evidence and scope

The observed Fascist vote rule recognizes only the narrower set of fellow Fascists before the Dictator-election threshold. That set excludes both the acting Fascist and the known Dictator, producing legally valid but strategically contradictory “no” votes for allied Governments. The behavior is directly observed in winning runs, so this ticket corrects an avoidable and predictable voting signal without claiming it explains a recorded loss.

## Comments

Completed with an explicit pre-threshold Fascist cover rule: vote yes whenever
the acting Fascist or its setup-authorized known Dictator holds either office.
The rule uses no global role data and is deliberately bounded to the
pre-threshold phase; the existing post-threshold known-Dictator-Chancellor win
condition remains the first Fascist branch. Seat-visible prefixes reproduce
the corrected self/Dictator votes in `516838e7`, `6daf104a`, and `bb845a93`.
The traces are wins, so this is a corrected self-sabotaging behavior, not a
measured match-outcome gain. `python3 -m unittest discover -s tests -v` passed
all 22 tests, including contract, randomized, replay, and release-package
validation; `python3 -m py_compile agent.py` and `git diff --check` also pass.

