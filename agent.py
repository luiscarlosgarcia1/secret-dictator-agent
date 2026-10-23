#!/usr/bin/env python3
"""Fault-resistant JSONL entrypoint for a Secret Dictator Seat.

This module deliberately keeps the protocol boundary small: all decision
strategy returns an intent, while ``build_response`` owns the legal wire
shape.  Later ticket slices extend strategy without bypassing that boundary.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from typing import Any, Iterable


LIBERAL = "liberal"
FASCIST = "fascist"


def _string_list(value: Any) -> list[str]:
    """Return unique string items in order, ignoring malformed optional data."""
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, str) and item not in result:
            result.append(item)
    return result


def _seat_from_you(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("seat"), str):
        return value["seat"]
    return None


def _policy_name(value: Any) -> str | None:
    if isinstance(value, str) and value in (LIBERAL, FASCIST):
        return value
    if isinstance(value, dict):
        for key in ("policy", "kind", "type"):
            candidate = value.get(key)
            if candidate in (LIBERAL, FASCIST):
                return candidate
    return None


@dataclass
class ReadModel:
    seats: list[str] = field(default_factory=list)
    you: str | None = None
    role: str | None = None
    known_fascists: list[str] = field(default_factory=list)
    known_dictator: str | None = None
    alive: list[str] = field(default_factory=list)
    president: str | None = None
    chancellor: str | None = None
    last_president: str | None = None
    last_chancellor: str | None = None
    liberal_policies: int = 0
    fascist_policies: int = 0
    chaos: int = 0

    @classmethod
    def from_history(cls, history: Any) -> "ReadModel":
        state = cls()
        if not isinstance(history, list):
            return state
        for entry in history:
            if not isinstance(entry, dict):
                continue
            event = entry.get("event")
            if not isinstance(event, dict):
                continue
            event_type = event.get("type")
            if event_type == "game-started":
                seats = _string_list(event.get("seats"))
                if seats:
                    state.seats = seats
                    state.alive = list(seats)
                state.you = _seat_from_you(event.get("you")) or state.you
                role = event.get("role")
                if isinstance(role, str):
                    state.role = role
                state.known_fascists = _string_list(event.get("knownFascists"))
                dictator = event.get("knownDictator")
                state.known_dictator = dictator if isinstance(dictator, str) else None
                president = event.get("president")
                state.president = president if isinstance(president, str) else state.president
            elif event_type == "president-announced":
                president = event.get("president")
                if isinstance(president, str):
                    state.president = president
                    state.chancellor = None
            elif event_type == "chancellor-nominated":
                chancellor = event.get("chancellor")
                if isinstance(chancellor, str):
                    state.chancellor = chancellor
            elif event_type == "government-elected":
                president, chancellor = event.get("president"), event.get("chancellor")
                if isinstance(president, str):
                    state.last_president = president
                    state.president = president
                if isinstance(chancellor, str):
                    state.last_chancellor = chancellor
                    state.chancellor = chancellor
            elif event_type == "chaos-triggered":
                state.chaos += 1
                state.last_president = None
                state.last_chancellor = None
            elif event_type == "policy-enacted":
                policy = _policy_name(event.get("policy"))
                if policy is None:
                    policy = _policy_name(event.get("enacted"))
                if policy == LIBERAL:
                    state.liberal_policies += 1
                elif policy == FASCIST:
                    state.fascist_policies += 1
            elif event_type == "player-executed":
                target = event.get("target")
                if isinstance(target, str):
                    state.alive = [seat for seat in state.alive if seat != target]
        return state

    def chancellor_candidates(self) -> list[str]:
        """Compute the legal nomination set from visible state only."""
        candidates = [
            seat
            for seat in self.alive
            if seat != self.president and seat != self.last_chancellor
        ]
        if len(self.alive) > 5:
            candidates = [seat for seat in candidates if seat != self.last_president]
        return candidates

    def clockwise(self, candidates: Iterable[str]) -> str | None:
        legal = set(candidates)
        if not legal:
            return None
        if self.you in self.seats:
            start = self.seats.index(self.you)
            for offset in range(1, len(self.seats) + 1):
                candidate = self.seats[(start + offset) % len(self.seats)]
                if candidate in legal:
                    return candidate
        return next((seat for seat in self.seats if seat in legal), None)


def build_response(state: ReadModel, decision: Any) -> dict[str, Any]:
    """Build the only ticket-01 response shapes, with deterministic fallbacks."""
    kind = decision.get("kind") if isinstance(decision, dict) else None
    if kind == "nominate-chancellor":
        target = state.clockwise(state.chancellor_candidates())
        if target is not None:
            return {"type": "chancellor-nominated", "target": target}
        # The runner cannot issue a valid nomination without a target.  This is
        # intentionally a controlled sentinel rather than an uncaught failure.
        return {"type": "chancellor-nominated", "target": None}
    if kind == "vote":
        return {"type": "vote-cast", "vote": "yes"}
    return {}


def handle_request(request: Any) -> dict[str, Any]:
    if not isinstance(request, dict):
        return {}
    if request.get("type") == "init":
        return {}
    if request.get("type") == "decision":
        return build_response(ReadModel.from_history(request.get("history")), request.get("decision"))
    return {}


def run() -> None:
    for raw_line in sys.stdin:
        try:
            request = json.loads(raw_line)
            response = handle_request(request)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            print(f"protocol input ignored: {exc}", file=sys.stderr)
            response = {}
        sys.stdout.write(json.dumps(response, separators=(",", ":")) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    run()
