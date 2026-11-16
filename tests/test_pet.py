from __future__ import annotations

import json
from pathlib import Path
import re

import pytest

import terminalpet
from terminalpet import pet as petmod


def test_version_matches_pyproject() -> None:
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    text = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    assert match is not None
    assert terminalpet.__version__ == match.group(1) == "0.2.0"


def test_add_xp_multi_level_gain_and_guards() -> None:
    p = petmod.new_pet("Mochi", "dragon")
    # Level 1 -> 2 costs 100 XP, Level 2 -> 3 costs 200 XP (total 300 XP)
    assert p.add_xp(350) is True
    assert p.level == 3
    assert p.xp == 50

    # Non-positive XP does nothing
    assert p.add_xp(0) is False
    assert p.add_xp(-50) is False
    assert p.level == 3
    assert p.xp == 50

    # Guard against corrupt level < 1 causing infinite loop
    p.level = 0
    p.xp = 0
    assert p.add_xp(120) is True
    assert p.level == 2
    assert p.xp == 20


def test_save_and_load_utf8_names(isolated_state: Path) -> None:
    p = petmod.new_pet("もち🐉Café", "cat")
    p.death_reason = ""
    petmod.save(p)

    raw_text = isolated_state.read_text(encoding="utf-8")
    assert "もち🐉Café" in raw_text

    loaded = petmod.load()
    assert loaded is not None
    assert loaded.name == "もち🐉Café"
    assert loaded.species == "cat"


def test_save_creates_parent_when_only_state_file_patched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    custom_file = tmp_path / "nested" / "dir" / "pet.json"
    monkeypatch.setattr(petmod, "STATE_FILE", custom_file)
    p = petmod.new_pet("Pip", "blob")
    petmod.save(p)
    assert custom_file.exists()


@pytest.mark.parametrize(
    "bad_payload",
    [
        b"{not valid json",
        b"\xff\xfe\x00\x00",
        b"[]",
        b'{"name": "OnlyName"}',
        b'{"name": "Bad", "species": "cat", "birth_time": 1.0, "last_update": 1.0, "hunger": "NaN"}',
        b'{"name": "Bad", "species": "cat", "birth_time": 1.0, "last_update": 1.0, "alive": "yes"}',
        b'{"name": "Bad", "species": "cat", "birth_time": true, "last_update": 1.0}',
    ],
)
def test_load_corrupt_state_backs_up_and_warns(
    isolated_state: Path, capsys: pytest.CaptureFixture[str], bad_payload: bytes
) -> None:
    isolated_state.parent.mkdir(parents=True, exist_ok=True)
    isolated_state.write_bytes(bad_payload)

    loaded = petmod.load()
    assert loaded is None
    assert not isolated_state.exists()

    backups = list(isolated_state.parent.glob("pet.json.corrupt.*"))
    assert len(backups) == 1
    assert backups[0].read_bytes() == bad_payload

    err = capsys.readouterr().err
    assert "Warning:" in err


def test_unknown_species_in_state_does_not_crash_feed_or_play() -> None:
    p = petmod.Pet(
        name="Sparkle",
        species="unicorn",
        birth_time=1000.0,
        last_update=1000.0,
        energy=80.0,
    )
    feed_msg = petmod.feed(p)
    play_msg = petmod.play(p)
    assert "Sparkle" in feed_msg and "(+15 XP)" in feed_msg
    assert "Sparkle" in play_msg and "(+25 XP)" in play_msg


def test_tick_decay_and_neglect_death(monkeypatch: pytest.MonkeyPatch) -> None:
    now = 1_000_000.0
    monkeypatch.setattr(petmod.time, "time", lambda: now)
    p = petmod.new_pet("Rex", "dog")

    # 10 hours later
    now += 10 * 3600.0
    p, elapsed = petmod.tick(p)
    assert elapsed == pytest.approx(10.0)
    assert p.hunger == pytest.approx(60.0)
    assert p.happiness == pytest.approx(50.0)
    assert p.energy == pytest.approx(60.0)
    assert p.alive is True

    # 15 more hours -> hits 100 hunger, starving_since starts
    now += 15 * 3600.0
    p, _ = petmod.tick(p)
    assert p.hunger == 100.0
    assert p.starving_since == now
    assert p.alive is True

    # 72 hours at 100 hunger -> dies
    now += petmod.NEGLECT_DEATH_HOURS * 3600.0
    p, _ = petmod.tick(p)
    assert p.alive is False
    assert "starved" in p.death_reason

    # Dead pet ticks do not advance
    now += 50 * 3600.0
    p, elapsed_after = petmod.tick(p)
    assert elapsed_after == 0.0


def test_actions_and_dead_pet_guards() -> None:
    p = petmod.new_pet("Bolt", "robot")
    p.energy = 10.0
    tired_msg = petmod.play(p)
    assert "too tired" in tired_msg
    assert p.xp == 0

    nap_msg = petmod.nap(p)
    assert "(+10 XP)" in nap_msg
    assert p.energy == 40.0

    p.alive = False
    assert "nothing left to feed" in petmod.feed(p)
    assert "no one left to play" in petmod.play(p)
    assert "no one left to tuck in" in petmod.nap(p)
    assert p.xp == 10


def test_mood_and_age_str(monkeypatch: pytest.MonkeyPatch) -> None:
    now = 2_000_000.0
    monkeypatch.setattr(petmod.time, "time", lambda: now)
    p = petmod.new_pet("Goo", "blob")
    assert petmod.age_str(p) == "just hatched"
    assert petmod.mood(p) == "happy"

    p.hunger = 10.0
    p.happiness = 95.0
    assert petmod.mood(p) == "ecstatic"

    p.energy = 15.0
    assert petmod.mood(p) == "tired"

    p.happiness = 10.0
    assert petmod.mood(p) == "sad"

    p.hunger = 95.0
    assert petmod.mood(p) == "starving"

    now += (2 * 86400) + (5 * 3600)
    assert petmod.age_str(p) == "2d 5h old"

    p.alive = False
    assert petmod.mood(p) == "dead"
