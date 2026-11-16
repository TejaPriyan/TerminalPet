from __future__ import annotations

import importlib
from pathlib import Path
import sys
from unittest.mock import patch

import pytest

from terminalpet import anim


def test_anim_has_no_import_time_os_system() -> None:
    anim_source = Path(anim.__file__).read_text(encoding="utf-8")
    assert "os.system" not in anim_source
    with patch("os.system", side_effect=AssertionError("os.system must not run")) as mock_sys:
        importlib.reload(anim)
        mock_sys.assert_not_called()


def test_visible_len_and_truncate_visible() -> None:
    assert anim.visible_len("hello") == 5
    assert anim.visible_len(f"{anim.CYAN}hello{anim.RESET}") == 5
    assert anim.visible_len("✨") == 2
    assert anim.visible_len("🐾") == 2
    assert anim.visible_len("🛋️") == 2
    assert anim.visible_len("✨\ufe0f") == 2
    assert anim.visible_len("a\ufe0f") == 1
    assert anim.visible_len("e\u0301") == 1
    assert anim.visible_len("中文") == 4
    assert anim.visible_len("👨\u200d👩\u200d👧") == 2

    truncated = anim.truncate_visible(f"{anim.GREEN}🛋️  Teja is roaming{anim.RESET}", 8)
    assert anim.visible_len(truncated) == 8
    assert truncated.endswith(f"…{anim.RESET}")
    assert "🛋️" in truncated

    wide_boundary = anim.truncate_visible("🐾🐾🐾", 3)
    assert anim.visible_len(wide_boundary) == 3
    assert wide_boundary == "🐾…"

    assert anim.truncate_visible("abc", 0) == ""


@pytest.mark.parametrize("room_width", [30, 52, 68, 74, 100])
def test_render_room_box_never_overflows_or_misaligns(room_width: int) -> None:
    for species in ("dragon", "cat", "dog", "robot", "blob", "unknown"):
        sprite = anim.get_roam_sprite(species, "dance", 0)
        box = anim.render_room_box(
            pet_name="VeryLongDragonName✨",
            species=species,
            level=12,
            xp=450,
            mood_name="ecstatic",
            hunger=25.0,
            happiness=85.0,
            energy=60.0,
            sprite_lines=sprite,
            offset=99,
            activity_msg="🛋️  VeryLongDragonName✨ reached the corner and curled up cozily!",
            room_width=room_width,
        )
        lines = box.splitlines()
        assert len(lines) >= 10
        for line in lines:
            assert anim.visible_len(line) == room_width


def test_get_roam_sprite_dead_returns_dead_art() -> None:
    for species in ("dragon", "cat", "dog", "robot", "blob"):
        lines = anim.get_roam_sprite(species, "dead", 0)
        joined = "\n".join(lines).lower()
        assert "x" in joined
        assert "rip" in joined or "r.i.p" in joined or "r i p" in joined


def test_animate_hatch_non_tty_prints_clean_final_frame(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(anim.time, "sleep", lambda _s: None)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False, raising=False)

    anim.animate_hatch("Teja", "dragon")
    out = capsys.readouterr().out
    assert "Hatching in progress" in out
    assert "Teja the dragon has hatched into the world!" in out
    assert "mysterious egg" not in out
    assert "\033[?25l" not in out
    assert "\033[3A" not in out


def test_animate_hatch_tty_overwrites_in_place_with_cursor_control(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    chunks: list[str] = []

    class FakeTTY:
        def isatty(self) -> bool:
            return True

        def write(self, s: str) -> int:
            chunks.append(s)
            return len(s)

        def flush(self) -> None:
            pass

    monkeypatch.setattr(anim.time, "sleep", lambda _s: None)
    monkeypatch.setattr(sys, "stdout", FakeTTY())

    anim.animate_hatch("Teja", "dragon")
    combined = "".join(chunks)
    assert combined.index("\033[?25l") < combined.index("\033[?25h")
    assert "\033[3A\r" in combined
    assert "\033[K\n" in combined
    assert "Teja the dragon has hatched into the world!" in combined


def test_other_animations_non_tty_and_tty(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(anim.time, "sleep", lambda _s: None)
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False, raising=False)

    anim.animate_feed("Mochi", "cat")
    anim.animate_play("Mochi", "cat")
    anim.animate_nap("Mochi")
    out = capsys.readouterr().out
    assert "So delicious" in out
    assert "So much fun" in out
    assert "dreaming happily" in out

    chunks: list[str] = []

    class FakeTTY:
        def isatty(self) -> bool:
            return True

        def write(self, s: str) -> int:
            chunks.append(s)
            return len(s)

        def flush(self) -> None:
            pass

    monkeypatch.setattr(sys, "stdout", FakeTTY())
    anim.animate_feed("Mochi", "cat")
    combined = "".join(chunks)
    assert "\033[?25l" in combined
    assert "\033[?25h" in combined
    assert "*CHOMP!*" in combined
