#!/usr/bin/env python3
"""Create and verify the self-contained Secret Dictator submission archive."""

from __future__ import annotations

import json
import py_compile
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "dist" / "secret-dictator-agent.zip"


def smoke(entrypoint: Path) -> None:
    request = {"type": "decision", "history": [{"event": {
        "type": "game-started", "seats": ["seat-1", "seat-2"],
        "president": "seat-1", "you": {"seat": "seat-1", "role": "liberal", "faction": "liberal"},
        "knownFascists": [], "knownDictator": None,
    }}], "decision": {"kind": "vote"}}
    process = subprocess.run(
        [sys.executable, str(entrypoint)], input=json.dumps({"type": "init"}) + "\n" + json.dumps(request) + "\n",
        text=True, capture_output=True, timeout=3, check=False,
    )
    assert process.returncode == 0, process.stderr
    assert [json.loads(line) for line in process.stdout.splitlines()] == [{}, {"type": "vote-cast", "vote": "yes"}]


def main() -> None:
    py_compile.compile(str(ROOT / "agent.py"), doraise=True)
    manifest = json.loads((ROOT / "crucible.json").read_text())
    assert manifest == {"runtime": "python313", "entrypoint": "agent.py"}
    ARCHIVE.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(ARCHIVE, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(ROOT / "agent.py", "agent.py")
        archive.write(ROOT / "crucible.json", "crucible.json")
    with tempfile.TemporaryDirectory() as temporary:
        extracted = Path(temporary)
        with zipfile.ZipFile(ARCHIVE) as archive:
            assert sorted(archive.namelist()) == ["agent.py", "crucible.json"]
            archive.extractall(extracted)
        assert json.loads((extracted / "crucible.json").read_text()) == manifest
        smoke(extracted / manifest["entrypoint"])
    print(f"protocol-ready package: {ARCHIVE}")
    print("Competitive performance is unmeasured; no competitive-improvement claim is made.")


if __name__ == "__main__":
    main()
