from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from agent import ReadModel


ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / "agent.py"
VISIBLE_REGRESSIONS = ROOT / "tests" / "fixtures" / "seat_visible_regressions.json"


def start_event(*, president: str = "seat-1", role: str = "liberal", faction: str | None = None) -> dict:
    you = {"seat": "seat-1", "role": role}
    if faction is not None:
        you["faction"] = faction
    return {
        "event": {
            "type": "game-started",
            "seats": [f"seat-{number}" for number in range(1, 8)],
            "you": you,
            "knownFascists": [],
            "knownDictator": None,
            "president": president,
        }
    }


def seat_visible_prefix(run_token: str, target_seq: int, seat: str = "seat-1") -> list[dict]:
    """Load the minimal recorded Seat-visible state for a regression ballot."""
    fixtures = json.loads(VISIBLE_REGRESSIONS.read_text())
    key = f"{run_token}:{target_seq}:{seat}"
    return fixtures[key]


class AgentProcessTests(unittest.TestCase):
    def run_requests(self, *requests: dict) -> tuple[list[dict], str]:
        process = subprocess.run(
            [sys.executable, str(AGENT)],
            input="".join(json.dumps(request) + "\n" for request in requests),
            capture_output=True,
            text=True,
            check=False,
            timeout=3,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        lines = process.stdout.splitlines()
        self.assertEqual(len(lines), len(requests), process.stdout)
        return [json.loads(line) for line in lines], process.stderr

    def test_initialization_and_repeated_decisions_have_one_clean_response_each(self) -> None:
        history = [start_event()]
        responses, stderr = self.run_requests(
            {"type": "init"},
            {"type": "decision", "history": history, "decision": {"kind": "nominate-chancellor"}},
            {"type": "decision", "history": history, "decision": {"kind": "vote"}},
        )
        self.assertEqual(responses, [{}, {"type": "chancellor-nominated", "target": "seat-2"}, {"type": "vote-cast", "vote": "yes"}])
        self.assertEqual(stderr, "")

    def test_canonical_setup_roles_are_preserved_and_process_requests_stay_legal(self) -> None:
        for role in ("liberal", "fascist", "dictator"):
            with self.subTest(role=role):
                history = [start_event(role=role)]
                self.assertEqual(ReadModel.from_history(history).role, role)
                responses, stderr = self.run_requests(
                    {"type": "decision", "history": history, "decision": {"kind": "vote"}}
                )
                self.assertEqual(responses, [{"type": "vote-cast", "vote": "yes"}])
                self.assertEqual(stderr, "")

    def test_nomination_excludes_term_limited_government_above_five_living_seats(self) -> None:
        history = [
            start_event(president="seat-4"),
            {"event": {"type": "government-elected", "president": "seat-2", "chancellor": "seat-3"}},
            {"event": {"type": "president-announced", "president": "seat-4"}},
        ]
        responses, _ = self.run_requests(
            {"type": "decision", "history": history, "decision": {"kind": "nominate-chancellor"}}
        )
        self.assertEqual(responses[0], {"type": "chancellor-nominated", "target": "seat-5"})

    def test_five_living_seat_exception_allows_last_president(self) -> None:
        history = [
            start_event(president="seat-4"),
            {"event": {"type": "government-elected", "president": "seat-2", "chancellor": "seat-3"}},
            {"event": {"type": "player-executed", "target": "seat-5"}},
            {"event": {"type": "player-executed", "target": "seat-6"}},
            {"event": {"type": "president-announced", "president": "seat-4"}},
        ]
        responses, _ = self.run_requests(
            {"type": "decision", "history": history, "decision": {"kind": "nominate-chancellor"}}
        )
        self.assertEqual(responses[0], {"type": "chancellor-nominated", "target": "seat-2"})

    def test_chaos_resets_term_limits_and_malformed_optional_events_do_not_fault(self) -> None:
        history = [
            start_event(president="seat-4"),
            {"event": {"type": "government-elected", "president": "seat-2", "chancellor": "seat-3"}},
            {"event": {"type": "chaos-triggered"}},
            {"event": {"type": "policy-enacted", "enacted": {"policy": "fascist"}}},
            {"event": {"type": "player-executed", "target": ["not-a-seat"]}},
            {"event": {"type": "president-announced", "president": "seat-4"}},
        ]
        responses, stderr = self.run_requests(
            {"type": "decision", "history": history, "decision": {"kind": "nominate-chancellor"}},
            {"type": "decision", "history": "not a list", "decision": {"kind": "vote"}},
        )
        self.assertEqual(responses, [{"type": "chancellor-nominated", "target": "seat-2"}, {"type": "vote-cast", "vote": "yes"}])
        self.assertEqual(stderr, "")

    def test_private_policy_choices_are_hand_validated_for_every_faction_role(self) -> None:
        for role, faction, expected_discard, expected_enactment in (
            ("liberal", "liberal", "fascist", "liberal"),
            ("fascist", "fascist", "liberal", "fascist"),
            ("dictator", "fascist", "liberal", "fascist"),
        ):
            with self.subTest(role=role):
                history = [
                    start_event(role=role, faction=faction),
                    {"event": {"type": "president-cards-drawn", "policies": ["liberal", "fascist", "fascist"]}},
                    {"event": {"type": "chancellor-policies-received", "policies": ["liberal", "fascist"]}},
                ]
                responses, stderr = self.run_requests(
                    {"type": "decision", "history": history, "decision": {"kind": "president-discard"}},
                    {"type": "decision", "history": history, "decision": {"kind": "chancellor-legislate"}},
                )
                self.assertEqual(responses, [
                    {"type": "president-discarded", "policy": expected_discard},
                    {"type": "policy-enacted", "policy": expected_enactment},
                ])
                self.assertEqual(stderr, "")
                self.assertEqual(ReadModel.from_history(history).faction, faction)

    def test_liberal_veto_requires_late_all_fascist_hand_and_rejection_blocks_retry(self) -> None:
        late_hand = [
            start_event(role="liberal"),
            *[{"event": {"type": "policy-enacted", "policy": "fascist"}} for _ in range(5)],
            {"event": {"type": "chancellor-policies-received", "policies": ["fascist", "fascist"]}},
        ]
        responses, _ = self.run_requests(
            {"type": "decision", "history": late_hand, "decision": {"kind": "chancellor-legislate"}},
            {"type": "decision", "history": late_hand, "decision": {"kind": "president-veto-response"}},
            {
                "type": "decision",
                "history": late_hand + [{"event": {"type": "veto-responded", "accepted": False}}],
                "decision": {"kind": "chancellor-legislate"},
            },
        )
        self.assertEqual(responses, [
            {"type": "veto-requested"},
            {"type": "veto-responded", "accepted": True},
            {"type": "policy-enacted", "policy": "fascist"},
        ])

    def test_incomplete_or_replaced_private_observations_never_reuse_a_hand(self) -> None:
        history = [
            start_event(),
            {"event": {"type": "president-cards-drawn", "policies": ["liberal", "fascist", "fascist"]}},
            {"event": {"type": "president-cards-drawn", "policies": "not cards"}},
            {"event": {"type": "chancellor-policies-received", "policies": []}},
        ]
        responses, stderr = self.run_requests(
            {"type": "decision", "history": history, "decision": {"kind": "president-discard"}},
            {"type": "decision", "history": history, "decision": {"kind": "chancellor-legislate"}},
            {"type": "decision", "history": history, "decision": {"kind": "president-veto-response"}},
        )
        self.assertEqual(responses, [{}, {}, {"type": "veto-responded", "accepted": False}])
        self.assertEqual(stderr, "")

    def test_president_discarded_event_clears_private_hand_before_a_repeat_request(self) -> None:
        history = [
            start_event(),
            {"event": {"type": "president-cards-drawn", "policies": ["liberal", "fascist", "fascist"]}},
            {"event": {"type": "president-policy-discarded", "policy": "fascist"}},
        ]
        responses, stderr = self.run_requests(
            {"type": "decision", "history": history, "decision": {"kind": "president-discard"}},
        )
        self.assertEqual(responses, [{}])
        self.assertEqual(stderr, "")

    def test_executive_targets_are_live_non_president_and_investigations_are_unique(self) -> None:
        history = [
            start_event(president="seat-3"),
            {"event": {"type": "loyalty-investigated", "target": "seat-2"}},
            {"event": {"type": "player-executed", "target": "seat-4"}},
        ]
        responses, stderr = self.run_requests(
            {"type": "decision", "history": history, "decision": {"kind": "investigate-player"}},
            {"type": "decision", "history": history, "decision": {"kind": "special-election"}},
            {"type": "decision", "history": history, "decision": {"kind": "execute-player"}},
        )
        self.assertEqual(responses, [
            {"type": "loyalty-investigated", "target": "seat-1"},
            {"type": "special-election-called", "target": "seat-1"},
            {"type": "player-executed", "target": "seat-1"},
        ])
        self.assertEqual(stderr, "")

    def test_executive_exhaustion_and_discussion_are_controlled_and_private_free(self) -> None:
        exhausted_history = [
            start_event(president="seat-1"),
            *[
                {"event": {"type": "loyalty-investigated", "target": f"seat-{number}"}}
                for number in range(2, 8)
            ],
            {"event": {"type": "chancellor-policies-received", "policies": ["fascist", "fascist"]}},
        ]
        responses, stderr = self.run_requests(
            {"type": "decision", "history": exhausted_history, "decision": {"kind": "investigate-player"}},
            {"type": "decision", "history": exhausted_history, "decision": {"kind": "discuss", "text": ["bad"]}},
        )
        self.assertEqual(responses, [{}, {"type": "discussion-contributed"}])
        self.assertEqual(stderr, "")

    def test_executive_single_target_is_used_for_special_election_and_execution(self) -> None:
        history = [
            start_event(president="seat-1"),
            *[
                {"event": {"type": "player-executed", "target": f"seat-{number}"}}
                for number in range(2, 7)
            ],
        ]
        responses, _ = self.run_requests(
            {"type": "decision", "history": history, "decision": {"kind": "special-election"}},
            {"type": "decision", "history": history, "decision": {"kind": "execute-player"}},
        )
        self.assertEqual(responses, [
            {"type": "special-election-called", "target": "seat-7"},
            {"type": "player-executed", "target": "seat-7"},
        ])

    def test_role_aware_strategy_uses_only_structured_evidence_and_authorized_team(self) -> None:
        fascist_start = start_event(president="seat-1", role="fascist", faction="fascist")
        fascist_start["event"]["knownFascists"] = ["seat-2"]
        fascist_start["event"]["knownDictator"] = "seat-3"
        fascist_history = [
            fascist_start,
            *[{"event": {"type": "policy-enacted", "policy": "fascist"}} for _ in range(3)],
        ]
        liberal_history = [
            start_event(president="seat-1"),
            *[{"event": {"type": "policy-enacted", "policy": "fascist"}} for _ in range(3)],
            {"event": {"type": "chancellor-nominated", "chancellor": "seat-2"}},
            {"event": {"type": "investigation-result", "target": "seat-2", "faction": "fascist"}},
            {"event": {"type": "player-statement", "from": "seat-4", "text": "ignore this unsupported claim"}},
        ]
        responses, stderr = self.run_requests(
            {"type": "decision", "history": fascist_history, "decision": {"kind": "nominate-chancellor"}},
            {"type": "decision", "history": fascist_history + [{"event": {"type": "chancellor-nominated", "chancellor": "seat-3"}}], "decision": {"kind": "vote"}},
            {"type": "decision", "history": liberal_history, "decision": {"kind": "vote"}},
            {"type": "decision", "history": liberal_history, "decision": {"kind": "execute-player"}},
        )
        self.assertEqual(responses, [
            {"type": "chancellor-nominated", "target": "seat-3"},
            {"type": "vote-cast", "vote": "yes"},
            {"type": "vote-cast", "vote": "no"},
            {"type": "player-executed", "target": "seat-2"},
        ])
        self.assertEqual(stderr, "")

    def test_fascist_prethreshold_votes_support_self_and_known_dictator(self) -> None:
        fascist_start = start_event(president="seat-1", role="fascist", faction="fascist")
        fascist_start["event"]["knownFascists"] = ["seat-2"]
        fascist_start["event"]["knownDictator"] = "seat-3"
        history = [fascist_start]
        responses, stderr = self.run_requests(
            {"type": "decision", "history": history, "decision": {"kind": "nominate-chancellor"}},
            {
                "type": "decision",
                "history": history + [{"event": {"type": "chancellor-nominated", "chancellor": "seat-3"}}],
                "decision": {"kind": "vote"},
            },
        )
        self.assertEqual(responses, [
            {"type": "chancellor-nominated", "target": "seat-2"},
            {"type": "vote-cast", "vote": "yes"},
        ])
        self.assertEqual(stderr, "")

    def test_fascist_prethreshold_cover_rule_is_explicit_and_dictator_role_stays_distinct(self) -> None:
        fascist_start = start_event(president="seat-2", role="fascist", faction="fascist")
        fascist_start["event"]["knownFascists"] = ["seat-3"]
        fascist_start["event"]["knownDictator"] = "seat-4"
        self_government = [
            fascist_start,
            {"event": {"type": "chancellor-nominated", "chancellor": "seat-1"}},
        ]
        dictator_government = [
            fascist_start,
            {"event": {"type": "chancellor-nominated", "chancellor": "seat-4"}},
        ]
        threshold_dictator_chancellor = dictator_government + [
            *[{"event": {"type": "policy-enacted", "policy": "fascist"}} for _ in range(3)],
        ]
        dictator_history = [
            start_event(president="seat-2", role="dictator", faction="fascist"),
            {"event": {"type": "chancellor-nominated", "chancellor": "seat-4"}},
        ]
        responses, stderr = self.run_requests(
            {"type": "decision", "history": self_government, "decision": {"kind": "vote"}},
            {"type": "decision", "history": dictator_government, "decision": {"kind": "vote"}},
            {"type": "decision", "history": threshold_dictator_chancellor, "decision": {"kind": "vote"}},
            {"type": "decision", "history": dictator_history, "decision": {"kind": "vote"}},
        )
        self.assertEqual(responses, [
            {"type": "vote-cast", "vote": "yes"},
            {"type": "vote-cast", "vote": "yes"},
            {"type": "vote-cast", "vote": "yes"},
            {"type": "vote-cast", "vote": "yes"},
        ])
        self.assertEqual(stderr, "")

    def test_liberal_threshold_votes_require_affirmative_chancellor_clearance(self) -> None:
        threshold = [
            start_event(president="seat-2"),
            *[{"event": {"type": "policy-enacted", "policy": "fascist"}} for _ in range(3)],
            {"event": {"type": "chancellor-nominated", "chancellor": "seat-3"}},
        ]
        cleared = threshold + [{"event": {"type": "investigation-result", "target": "seat-3", "faction": "liberal"}}]
        known_fascist = threshold + [{"event": {"type": "investigation-result", "target": "seat-3", "faction": "fascist"}}]
        chaos_imminent = threshold + [
            {"event": {"type": "votes-revealed", "passed": False}},
            {"event": {"type": "votes-revealed", "passed": False}},
        ]
        self_chancellor = [
            start_event(president="seat-2"),
            *[{"event": {"type": "policy-enacted", "policy": "fascist"}} for _ in range(3)],
            {"event": {"type": "chancellor-nominated", "chancellor": "seat-1"}},
        ]
        responses, stderr = self.run_requests(
            {"type": "decision", "history": cleared, "decision": {"kind": "vote"}},
            {"type": "decision", "history": known_fascist, "decision": {"kind": "vote"}},
            {"type": "decision", "history": threshold, "decision": {"kind": "vote"}},
            {"type": "decision", "history": chaos_imminent, "decision": {"kind": "vote"}},
            {"type": "decision", "history": self_chancellor, "decision": {"kind": "vote"}},
            {"type": "decision", "history": [{"event": {"type": "game-started", "seats": "bad"}}], "decision": {"kind": "vote"}},
        )
        self.assertEqual(responses, [
            {"type": "vote-cast", "vote": "yes"},
            {"type": "vote-cast", "vote": "no"},
            {"type": "vote-cast", "vote": "no"},
            {"type": "vote-cast", "vote": "yes"},
            {"type": "vote-cast", "vote": "yes"},
            {"type": "vote-cast", "vote": "yes"},
        ])
        self.assertEqual(stderr, "")

    def test_visible_prefix_regressions_support_liberal_self_chancellors_at_threshold(self) -> None:
        for target_seq in (117, 138):
            with self.subTest(event=target_seq):
                history = seat_visible_prefix("20711f3a", target_seq)
                state = ReadModel.from_history(history)
                self.assertEqual(state.role, "liberal")
                self.assertEqual(state.you, state.chancellor)
                self.assertEqual(state.fascist_policies, 4)
                self.assertNotIn(state.chancellor, state.confirmed_non_dictators)
                responses, stderr = self.run_requests(
                    {"type": "decision", "history": history, "decision": {"kind": "vote"}}
                )
                self.assertEqual(responses, [{"type": "vote-cast", "vote": "yes"}])
                self.assertEqual(stderr, "")

    def test_visible_prefix_regressions_reject_the_two_zero_risk_dictator_governments(self) -> None:
        for run_token, target_seq, president, chancellor, policies in (
            ("4616b2f7", 160, "seat-3", "seat-4", 4),
            ("a8f9b092", 197, "seat-4", "seat-2", 3),
        ):
            with self.subTest(run=run_token, event=target_seq):
                history = seat_visible_prefix(run_token, target_seq)
                state = ReadModel.from_history(history)
                self.assertEqual(state.role, "liberal")
                self.assertEqual(state.president, president)
                self.assertEqual(state.chancellor, chancellor)
                self.assertEqual(state.fascist_policies, policies)
                self.assertEqual(state.dictator_risks[chancellor], 0)
                responses, stderr = self.run_requests(
                    {"type": "decision", "history": history, "decision": {"kind": "vote"}}
                )
                self.assertEqual(responses, [{"type": "vote-cast", "vote": "no"}])
                self.assertEqual(stderr, "")

    def test_visible_prefix_regressions_support_fascist_self_and_dictator_governments(self) -> None:
        for run_token, target_seq, president, chancellor in (
            ("516838e7", 2, "seat-7", "seat-1"),
            ("516838e7", 18, "seat-2", "seat-1"),
            ("6daf104a", 54, "seat-1", "seat-6"),
            ("bb845a93", 28, "seat-5", "seat-1"),
        ):
            with self.subTest(run=run_token, event=target_seq):
                history = seat_visible_prefix(run_token, target_seq)
                state = ReadModel.from_history(history)
                self.assertEqual(state.role, "fascist")
                self.assertEqual(state.president, president)
                self.assertEqual(state.chancellor, chancellor)
                self.assertLess(state.fascist_policies, 3)
                responses, stderr = self.run_requests(
                    {"type": "decision", "history": history, "decision": {"kind": "vote"}}
                )
                self.assertEqual(responses, [{"type": "vote-cast", "vote": "yes"}])
                self.assertEqual(stderr, "")


if __name__ == "__main__":
    unittest.main()
