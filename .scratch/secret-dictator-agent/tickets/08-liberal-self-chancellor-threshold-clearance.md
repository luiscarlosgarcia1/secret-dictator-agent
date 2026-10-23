# 08: Clear the acting Liberal Seat as non-Dictator when it is Chancellor

**What to build:** At the Dictator-election threshold, a Liberal Seat recognizes its own private role as affirmative proof that it cannot be the Dictator. When that Seat is the legal Chancellor, it can approve the Government without weakening the existing fail-closed protection for every other un-cleared Chancellor. The decision continues to use only the acting Seat's Visible History and always produces a Legal Response.

**Blocked by:** None (can start immediately).

**Status:** complete

- [x] A Liberal Seat at three or more Fascist Policies approves a legal Government when it is the Chancellor, even when it has not received a separate Liberal investigation result about itself.
- [x] Seat-visible regressions reproduce the two decisive Liberal-seat votes from completed run `20711f3a`: at four Fascist Policies, changing only the acting Seat's vote from no to yes turns each tied self-Chancellor Government into a passed Government.
- [x] The change does not clear any other Chancellor merely because that Seat has low or absent public risk; an un-cleared non-self Chancellor still receives the existing threshold protection, subject only to the documented Chaos-imminence exception.
- [x] The behavior is limited to an acting Liberal Seat. A Fascist or Dictator Seat does not receive Liberal self-clearance, and the rule does not consult replay-only role assignments, deck order, or another Seat's private observations.
- [x] The decision remains deterministic and fault-resistant with incomplete optional history, emits only a valid vote response, and preserves existing threshold-voting, protocol, replay, and release validation.
- [x] Validation records the narrow evidence claim: the two pivotal ballots prove a corrected decision branch, not a measured tournament win-rate increase.

## Evidence and scope

The confirmed defect is in a Liberal Seat's threshold vote. In completed run `20711f3a`, the acting Liberal Seat was nominated Chancellor at four Fascist Policies twice and voted no both times. Each vote tied 3--3; its own yes vote would have passed a Government whose Chancellor it knew could not be the Dictator. The current affirmative-clearance model recognizes a Liberal investigation result but does not incorporate the acting Seat's already-authorized Liberal role.

This ticket corrects only that missing self-clearance. It does not relax the threshold policy for other un-cleared Chancellors, alter legislative choices, add hidden-information inference, or introduce free-form discussion parsing.

## Comments

Completed with a narrowly scoped Liberal self-clearance condition: at the
Dictator-election threshold, an acting Liberal Seat approves a Government when
it is the nominated Chancellor. The existing investigation clearance,
un-cleared non-self rejection, and Chaos-imminence exception remain unchanged.
Seat-visible prefix regressions for events 117 and 138 in `20711f3a` reproduce
the corrected ballots at four Fascist Policies. This confirms the two decision
branches only; it does not establish a tournament win-rate increase.
