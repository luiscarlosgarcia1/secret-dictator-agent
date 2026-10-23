from __future__ import annotations

import json
import random
import subprocess
import sys
import unittest
from pathlib import Path

from agent import ReadModel, build_response


ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / "agent.py"
SEATS = [f"seat-{number}" for number in range(1, 8)]
KINDS = ("nominate-chancellor", "vote", "president-discard", "chancellor-legislate", "president-veto-response", "investigate-player", "special-election", "execute-player", "discuss")


def start(role: str, seat: str = "seat-1") -> dict:
    faction = "fascist" if role in ("fascist", "dictator") else "liberal"
    return {"event": {"type": "game-started", "seats": SEATS, "president": "seat-2", "you": {"seat": seat, "role": role, "faction": faction}, "knownFascists": ["seat-3"] if role == "fascist" else [], "knownDictator": "seat-4" if role == "fascist" else None}}


def assert_legal(test: unittest.TestCase, history: list[dict], kind: str, response: dict) -> None:
    state = ReadModel.from_history(history)
    if kind == "nominate-chancellor":
        test.assertEqual(response.get("type"), "chancellor-nominated")
        test.assertIn(response.get("target"), state.chancellor_candidates())
    elif kind == "vote":
        test.assertEqual(response.get("vote"), "yes" if response.get("vote") == "yes" else "no")
    elif kind == "president-discard":
        test.assertIn(response.get("policy"), state.president_policies)
    elif kind == "chancellor-legislate":
        test.assertTrue(response.get("type") == "veto-requested" or response.get("policy") in state.chancellor_policies)
    elif kind == "president-veto-response":
        test.assertIsInstance(response.get("accepted"), bool)
    elif kind == "discuss":
        test.assertEqual(response, {"type": "discussion-contributed"})
    else:
        test.assertIn(response.get("target"), state.executive_candidates(kind))


class ReleaseGateTests(unittest.TestCase):
    def test_contract_matrix_for_all_decisions_roles_and_positions(self) -> None:
        for role in ("liberal", "fascist", "dictator"):
            for position in range(1, 8):
                for kind in KINDS:
                    with self.subTest(role=role, position=position, kind=kind):
                        history = [start(role, f"seat-{position}"), {"event": {"type": "president-cards-drawn", "policies": ["liberal", "fascist", "fascist"]}}, {"event": {"type": "chancellor-policies-received", "policies": ["liberal", "fascist"]}}]
                        assert_legal(self, history, kind, build_response(ReadModel.from_history(history), {"kind": kind}))

    def test_one_thousand_randomized_coherent_legal_requests(self) -> None:
        randomizer = random.Random(20261023)
        cases: list[tuple[list[dict], str]] = []
        requests = []
        for _ in range(1_000):
            role = randomizer.choice(("liberal", "fascist", "dictator"))
            kind = randomizer.choice(KINDS)
            president = randomizer.choice(SEATS)
            history = [start(role, randomizer.choice(SEATS)), {"event": {"type": "president-announced", "president": president}}]
            for _ in range(randomizer.randrange(6)):
                history.append({"event": {"type": "policy-enacted", "policy": randomizer.choice(("liberal", "fascist"))}})
            if kind == "president-discard":
                history.append({"event": {"type": "president-cards-drawn", "policies": [randomizer.choice(("liberal", "fascist")) for _ in range(3)]}})
            if kind == "chancellor-legislate":
                history.append({"event": {"type": "chancellor-policies-received", "policies": [randomizer.choice(("liberal", "fascist")) for _ in range(2)]}})
            cases.append((history, kind))
            requests.append({"type": "decision", "history": history, "decision": {"kind": kind}})
        process = subprocess.run(
            [sys.executable, str(AGENT)], input="".join(json.dumps(request) + "\n" for request in requests),
            text=True, capture_output=True, timeout=10, check=False,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        responses = [json.loads(line) for line in process.stdout.splitlines()]
        self.assertEqual(len(responses), len(cases))
        for (history, kind), response in zip(cases, responses, strict=True):
            state = ReadModel.from_history(history)
            # Exhaustion is the sole recoverable no-target case.
            if kind in ("investigate-player", "special-election", "execute-player") and not state.executive_candidates(kind):
                self.assertEqual(response, {})
            else:
                assert_legal(self, history, kind, response)

    def test_replay_visible_observations_are_deterministic_and_legal(self) -> None:
        replay = json.loads((ROOT / "example_run.json").read_text())
        checked = 0
        for item in replay.get("events", []):
            for observed in item.get("observedAs", []):
                history = [{"event": entry["event"]} for entry in observed.get("events", []) if isinstance(entry.get("event"), dict)]
                for kind in KINDS:
                    state = ReadModel.from_history(history)
                    response = build_response(state, {"kind": kind})
                    repeated = build_response(ReadModel.from_history(history), {"kind": kind})
                    self.assertEqual(response, repeated)
                    # Only assert kinds where the observation reconstructs a legal action.
                    if kind in ("president-discard", "chancellor-legislate") and not (state.president_policies if kind == "president-discard" else state.chancellor_policies):
                        continue
                    if kind in ("investigate-player", "special-election", "execute-player") and not state.executive_candidates(kind):
                        continue
                    if kind == "nominate-chancellor" and not state.chancellor_candidates():
                        continue
                    assert_legal(self, history, kind, response)
                    checked += 1
        self.assertGreater(checked, 100)

    def test_release_script_creates_extracted_smoke_tested_archive(self) -> None:
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "release.py")], text=True, capture_output=True, timeout=10, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("protocol-ready package", result.stdout)
        self.assertIn("unmeasured", result.stdout)


if __name__ == "__main__":
    unittest.main()
