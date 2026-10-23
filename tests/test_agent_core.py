from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from agent import ReadModel


ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / "agent.py"


def start_event(*, president: str = "seat-1", role: str = "liberal") -> dict:
    return {
        "event": {
            "type": "game-started",
            "seats": [f"seat-{number}" for number in range(1, 8)],
            "you": {"seat": "seat-1", "role": role},
            "knownFascists": [],
            "knownDictator": None,
            "president": president,
        }
    }


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


if __name__ == "__main__":
    unittest.main()
