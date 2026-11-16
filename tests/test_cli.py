from __future__ import annotations

import builtins
import io
import os
from pathlib import Path
import subprocess
import sys
import types
from unittest.mock import MagicMock

import pytest

from terminalpet import anim, cli
from terminalpet import pet as petmod


def test_cli_adopt_status_feed_play_nap_rename_reset(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # No pet -> help
    assert cli.main([]) == 0
    assert "Adopt a new pet" in capsys.readouterr().out

    # Adopt
    assert cli.main(["adopt", "Mochi", "--species", "dragon", "--no-anim"]) == 0
    out = capsys.readouterr().out
    assert "You adopted Mochi, a dragon!" in out

    # Duplicate adopt prevented while alive
    assert cli.main(["adopt", "Other", "--species", "cat", "--no-anim"]) == 0
    assert "already have a pet" in capsys.readouterr().out

    # Feed / Play / Nap / Rename
    assert cli.main(["feed", "--no-anim"]) == 0
    assert "(+15 XP)" in capsys.readouterr().out

    assert cli.main(["play", "--no-anim"]) == 0
    assert "(+25 XP)" in capsys.readouterr().out

    assert cli.main(["nap", "--no-anim"]) == 0
    assert "(+10 XP)" in capsys.readouterr().out

    assert cli.main(["rename", "Draco"]) == 0
    assert "Mochi is now known as Draco." in capsys.readouterr().out

    # No-subcommand prints status when pet exists
    assert cli.main([]) == 0
    assert "Draco" in capsys.readouterr().out

    # Reset cancelled then confirmed
    monkeypatch.setattr(builtins, "input", lambda _prompt: "no")
    assert cli.main(["reset"]) == 0
    assert "Cancelled." in capsys.readouterr().out
    assert petmod.load() is not None

    assert cli.main(["reset", "--yes"]) == 0
    assert petmod.load() is None


def test_cmd_watch_does_not_save_every_frame_and_handles_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    p = petmod.new_pet("Teja", "dragon")
    p.xp = 90  # Next feed (+15 XP) triggers Level 2
    petmod.save(p)

    now = p.last_update
    monkeypatch.setattr(petmod.time, "time", lambda: now)
    monkeypatch.setattr(cli.time, "sleep", lambda _s: None)
    monkeypatch.setattr(anim, "hide_cursor", lambda: None)
    monkeypatch.setattr(anim, "show_cursor", lambda: None)

    save_calls: list[tuple[int, int, float]] = []
    real_save = petmod.save

    def tracking_save(pet_obj: petmod.Pet) -> None:
        save_calls.append((pet_obj.level, pet_obj.xp, pet_obj.hunger))
        real_save(pet_obj)

    monkeypatch.setattr(petmod, "save", tracking_save)

    # 6 idle frames (0.35s each), then 'f' (feed + level up), 1 idle frame, 'c', 'r', 'q'
    keys = iter([None, None, None, None, None, None, "f", None, "c", "r", "q"])
    rendered_frames: list[str] = []

    def fake_poll(_timeout: float = 0.35) -> str | None:
        nonlocal now
        now += 0.35
        return next(keys, "q")

    fake_stdout = io.StringIO()
    real_write = fake_stdout.write

    def capture_write(s: str) -> int:
        if "┌" in s:
            rendered_frames.append(s)
        return real_write(s)

    fake_stdout.write = capture_write  # type: ignore[method-assign]
    monkeypatch.setattr(cli, "_poll_key", fake_poll)
    monkeypatch.setattr(sys, "stdout", fake_stdout)

    cli.main(["watch"])

    # Only saved ONCE (for the 'f' feed action), NOT on the 6 idle 0.35s frames or 'c'/'r'/'q'!
    assert len(save_calls) == 1
    assert save_calls[0][:2] == (2, 5)
    # Level-up message from feed was rendered and held on screen
    assert any("LEVEL UP!" in frame and "Level 2" in frame for frame in rendered_frames)


def test_cmd_watch_dead_pet_stops_actions_and_renders_dead_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    p = petmod.new_pet("Ash", "cat")
    p.alive = False
    p.death_reason = "starved after days without being fed"
    p.energy = 0.0
    petmod.save(p)

    monkeypatch.setattr(cli.time, "sleep", lambda _s: None)
    monkeypatch.setattr(anim, "hide_cursor", lambda: None)
    monkeypatch.setattr(anim, "show_cursor", lambda: None)

    save_mock = MagicMock()
    monkeypatch.setattr(petmod, "save", save_mock)

    # Try f, p, n, c, r, then q on a dead pet
    keys = iter(["f", "p", "n", "c", "r", "q"])
    rendered_frames: list[str] = []
    fake_stdout = io.StringIO()
    real_write = fake_stdout.write

    def capture_write(s: str) -> int:
        if "┌" in s:
            rendered_frames.append(s)
        return real_write(s)

    fake_stdout.write = capture_write  # type: ignore[method-assign]
    monkeypatch.setattr(cli, "_poll_key", lambda _t=0.35: next(keys, "q"))
    monkeypatch.setattr(sys, "stdout", fake_stdout)

    cli.main(["watch"])

    save_mock.assert_not_called()
    assert len(rendered_frames) >= 4
    # Dead ASCII art shown, never live roaming/dance XP messages
    assert "R.I.P" in rendered_frames[0]
    joined = "\n".join(rendered_frames)
    assert "(+15 XP)" not in joined
    assert "(+25 XP)" not in joined
    assert "(+10 XP)" not in joined
    assert "nothing left to feed" in joined
    assert "no one left to play" in joined
    assert "no one left to tuck in" in joined


def test_posix_keyboard_polling_tty_and_non_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "platform", "linux")

    # 1) Non-TTY stdin: safe fallback, sleeps and returns None
    slept: list[float] = []
    monkeypatch.setattr(cli.time, "sleep", lambda s: slept.append(s))
    fake_non_tty = io.StringIO("")
    monkeypatch.setattr(sys, "stdin", fake_non_tty)

    with cli._posix_cbreak_mode():
        assert cli._poll_key(0.35) is None
    assert slept == [0.35]

    # 2) TTY stdin with mocked termios, tty, select, and os.read
    saved_attrs = ["original"]
    tcsetattr_calls: list[tuple] = []
    setcbreak_calls: list[int] = []

    fake_termios = types.SimpleNamespace(
        TCSADRAIN=1,
        error=OSError,
        tcgetattr=lambda _fd: saved_attrs,
        tcsetattr=lambda fd, when, attrs: tcsetattr_calls.append((fd, when, attrs)),
    )
    fake_tty = types.SimpleNamespace(setcbreak=lambda fd: setcbreak_calls.append(fd))

    class FakeStdin:
        def isatty(self) -> bool:
            return True

        def fileno(self) -> int:
            return 7

    monkeypatch.setitem(sys.modules, "termios", fake_termios)
    monkeypatch.setitem(sys.modules, "tty", fake_tty)
    monkeypatch.setattr(sys, "stdin", FakeStdin())

    # Simulate 'F' keypress, then arrow-key escape sequence '\x1b[A', then timeout
    select_responses = [([7], [], []), ([7], [], []), ([7], [], []), ([], [], []), ([], [], [])]
    read_bytes = [b"F", b"\x1b", b"[", b"A"]

    import select as select_mod

    monkeypatch.setattr(select_mod, "select", lambda *_args: select_responses.pop(0))
    monkeypatch.setattr(os, "read", lambda _fd, _n: read_bytes.pop(0))

    with cli._posix_cbreak_mode():
        assert cli._poll_key(0.35) == "f"
        assert cli._poll_key(0.35) is None  # escape sequence drained cleanly
        assert cli._poll_key(0.35) is None  # timeout

    assert setcbreak_calls == [7]
    assert tcsetattr_calls == [(7, 1, saved_attrs)]


def test_win32_keyboard_polling(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "platform", "win32")

    kbhit_seq = iter([True, True, True, False])
    getch_seq = iter([b"Q", b"\xe0", b"H"])

    fake_msvcrt = types.SimpleNamespace(
        kbhit=lambda: next(kbhit_seq, False),
        getch=lambda: next(getch_seq),
    )
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt)
    monkeypatch.setattr(cli.time, "sleep", lambda _s: None)

    assert cli._poll_key(0.1) == "q"
    assert cli._poll_key(0.1) is None  # arrow prefix ignored cleanly
    assert cli._poll_key(0.01) is None  # timeout


def test_cmd_watch_play_tired_and_nap_messages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    p = petmod.new_pet("Pip", "blob")
    p.energy = 10.0  # Too tired to play until nap
    petmod.save(p)

    monkeypatch.setattr(cli.time, "sleep", lambda _s: None)
    monkeypatch.setattr(anim, "hide_cursor", lambda: None)
    monkeypatch.setattr(anim, "show_cursor", lambda: None)

    save_calls: list[int] = []
    real_save = petmod.save
    monkeypatch.setattr(
        petmod,
        "save",
        lambda pet_obj: (save_calls.append(pet_obj.xp), real_save(pet_obj)),
    )

    # Press 'p' (too tired -> no save), 'n' (nap -> saves +10 XP), 'p' (plays -> saves +25 XP), 'q'
    keys = iter(["p", "n", None, "p", "q"])
    rendered_frames: list[str] = []
    fake_stdout = io.StringIO()
    real_write = fake_stdout.write

    def capture_write(s: str) -> int:
        if "┌" in s:
            rendered_frames.append(s)
        return real_write(s)

    fake_stdout.write = capture_write  # type: ignore[method-assign]
    monkeypatch.setattr(cli, "_poll_key", lambda _t=0.35: next(keys, "q"))
    monkeypatch.setattr(sys, "stdout", fake_stdout)

    cli.main(["watch"])

    assert save_calls == [10, 35]
    joined = "\n".join(rendered_frames)
    assert "too tired to play" in joined
    assert "curls up for a nap" in joined
    assert "wobbles happily" in joined


def test_module_entrypoint_help() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")
    proc = subprocess.run(
        [sys.executable, "-m", "terminalpet", "--help"],
        cwd=str(repo_root),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "adopt" in proc.stdout
    assert "watch" in proc.stdout
