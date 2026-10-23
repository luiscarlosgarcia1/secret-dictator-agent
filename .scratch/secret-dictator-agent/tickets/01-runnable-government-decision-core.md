# 01: Deliver the runnable Government-decision core

**What to build:** A submit-ready, standard-library Python 3.13 Secret Dictator agent can stay alive as a persistent JSONL process, return the required empty initialization response, and make a legal Chancellor nomination or Government vote from its Seat's Visible History. It never writes protocol-unrelated text to stdout, reconstructs only Seat-authorized match facts, and replaces an invalid or failed decision intent with a deterministic legal response.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] A fresh process handles initialization and repeated nomination or vote Decision Requests with exactly one newline-terminated JSON response per request, flushing each response and sending diagnostics only to stderr.
- [ ] The Read Model derives ordered Seats, the acting Seat's role/setup knowledge, living Seats, current and prior Government, policy totals, and Chaos term-limit reset exclusively from Visible History.
- [ ] Nomination excludes ineligible Government members (including the five-living-Seat term-limit exception), and the response builder substitutes a clockwise legal nomination or a valid vote enum if strategy output is invalid or history is partly recoverable.
- [ ] Process-level tests demonstrate the initialization, nomination, vote, malformed-optional-content, and stdout-purity contract without using replay-global roles, deck order, or unobserved hands.

