# 03: Complete executive and bounded discussion decisions

**What to build:** A Seat can use every exposed Executive Power and participate safely in public discussion without faulting or disclosing private knowledge. Investigations, special elections, and executions always target a live eligible Seat; public discussion is silent by default and any optional message is concise, ASCII-only, and based solely on public facts.

**Blocked by:** 01: Deliver the runnable Government-decision core.

**Status:** complete

- [x] A centralized legal-target calculation handles investigation, special-election, and execution exclusions, including the current President, deceased Seats, and previously investigated Seats where applicable.
- [x] Each Executive Power response has the runner-required type and a target from that calculation; invalid strategy output deterministically becomes the clockwise legal target.
- [x] Discussion returns the minimal legal pass unless a policy-result or high Dictator-risk warning is supported by structured public evidence, and it never reveals role setup, policy hands, private investigation results, or internal scores.
- [x] Process-level tests cover exhausted and single-target cases, execution, special-election return, malformed optional discussion text, and the absence of private leakage.

## Comments

Completed with centralized executive-target calculation, visible investigation
history, deterministic clockwise fallbacks for all executive decisions, and a
silent `discussion-contributed` default that cannot leak private facts.
Verified with `python3 -m unittest discover -s tests -v`, `python3 -m py_compile
agent.py`, and `git diff --check`.

