# 02: Make private legislation and veto decisions fault-resistant

**What to build:** The same running agent can safely make every President discard, Chancellor legislation, and President veto decision using only the acting Seat's actual Legislative Information. Liberal and Fascist choices follow their deterministic policy priorities, while any absent, contradictory, or unusable private-hand evidence falls back to a response that the runner can legally accept whenever one exists.

**Blocked by:** 01: Deliver the runnable Government-decision core.

**Status:** ready-for-agent

- [ ] Presidential discards and Chancellor enactments select only a Policy present in the relevant private observation, with faction-specific preference applied after that constraint.
- [ ] A veto request is emitted only for the defined late-game all-Fascist Chancellor hand and never immediately after a rejected veto; the President's Boolean response observes the same terminal-risk policy.
- [ ] Private hands and veto state are updated or cleared from visible events so repeated requests cannot reuse obsolete Legislative Information.
- [ ] Process-level contract cases cover mixed and uniform hands, zero/five Fascist policies, accepted and rejected vetoes, and incomplete history, asserting legal responses and no private-fact stdout leakage.

