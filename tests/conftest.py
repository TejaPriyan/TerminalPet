from __future__ import annotations

from pathlib import Path
import sys

import pytest

SRC_DIR = str(Path(__file__).resolve().parents[1] / "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from terminalpet import pet as petmod  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Keep all tests isolated from the real ~/.terminalpet/pet.json file."""
    state_dir = tmp_path / ".terminalpet"
    state_file = state_dir / "pet.json"
    monkeypatch.setattr(petmod, "STATE_DIR", state_dir)
    monkeypatch.setattr(petmod, "STATE_FILE", state_file)
    return state_file
