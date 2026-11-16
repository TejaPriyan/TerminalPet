"""Command-line interface for terminalpet."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import os
import random
import shutil
import sys
import time
from typing import Iterator

from . import anim
from . import pet as petmod


def _elapsed_message(hours: float) -> str | None:
    if hours < 1:
        return None
    if hours < 24:
        return f"(It's been about {int(hours)} hour(s) since you last checked in.)"
    days = hours / 24
    return f"(It's been about {days:.1f} day(s) since you last checked in.)"


def _print_status(pet: petmod.Pet, elapsed_hours: float = 0.0) -> None:
    msg = _elapsed_message(elapsed_hours)
    if msg:
        print(anim.colored(msg, anim.YELLOW))

    m = petmod.mood(pet)
    art, narrative = anim.get_dynamic_status_pose(pet.species, m)
    print(art.rstrip("\n"))

    if not pet.alive:
        print(f"{anim.BOLD}{pet.name}{anim.RESET} the {pet.species} — {petmod.age_str(pet)}")
        print(f"{anim.RED}Cause of end: {pet.death_reason}{anim.RESET}")
        print("Run `pet reset` when you're ready to adopt a new one.")
        return

    print(anim.colored(narrative, anim.CYAN))
    xp_needed = pet.level * 100
    xp_percent = int((pet.xp / xp_needed) * 100) if xp_needed > 0 else 0
    print(
        f"{anim.BOLD}{pet.name}{anim.RESET} the {pet.species} — "
        f"{anim.CYAN}{petmod.age_str(pet)}{anim.RESET} — feeling {anim.BOLD}{m}{anim.RESET}"
    )
    print(f"  {anim.BOLD}Level {pet.level}{anim.RESET} [XP: {pet.xp}/{xp_needed} ({xp_percent}%)]")
    print(f"  hunger    {petmod.bar(pet.hunger, is_hunger=True)}")
    print(f"  happiness {petmod.bar(pet.happiness)}")
    print(f"  energy    {petmod.bar(pet.energy)}")


def cmd_adopt(args: argparse.Namespace) -> None:
    existing = petmod.load()
    if existing is not None and existing.alive:
        print(f"You already have a pet: {existing.name} the {existing.species}.")
        print("Run `pet reset` first if you want to start over.")
        return
    species = args.species
    if species and species not in petmod.SPECIES:
        print(f"Unknown species '{species}'. Choose from: {', '.join(petmod.SPECIES)}")
        return
    new_pet = petmod.new_pet(args.name, species)
    petmod.save(new_pet)

    if not getattr(args, "no_anim", False):
        anim.animate_hatch(new_pet.name, new_pet.species)
    else:
        print(f"You adopted {new_pet.name}, a {new_pet.species}!")
    _print_status(new_pet)


def _load_or_prompt() -> petmod.Pet | None:
    pet = petmod.load()
    if pet is None:
        print("You don't have a pet yet. Run `pet adopt <name>` to get started.")
        return None
    return pet


def cmd_status(args: argparse.Namespace) -> None:
    pet = _load_or_prompt()
    if pet is None:
        return
    pet, elapsed = petmod.tick(pet)
    petmod.save(pet)
    _print_status(pet, elapsed)


def cmd_feed(args: argparse.Namespace) -> None:
    pet = _load_or_prompt()
    if pet is None:
        return
    pet, elapsed = petmod.tick(pet)
    if not getattr(args, "no_anim", False) and pet.alive:
        anim.animate_feed(pet.name, pet.species)
    print(petmod.feed(pet))
    petmod.save(pet)
    _print_status(pet)


def cmd_play(args: argparse.Namespace) -> None:
    pet = _load_or_prompt()
    if pet is None:
        return
    pet, elapsed = petmod.tick(pet)
    if not getattr(args, "no_anim", False) and pet.alive and pet.energy >= 15:
        anim.animate_play(pet.name, pet.species)
    print(petmod.play(pet))
    petmod.save(pet)
    _print_status(pet)


def cmd_nap(args: argparse.Namespace) -> None:
    pet = _load_or_prompt()
    if pet is None:
        return
    pet, elapsed = petmod.tick(pet)
    if not getattr(args, "no_anim", False) and pet.alive:
        anim.animate_nap(pet.name)
    print(petmod.nap(pet))
    petmod.save(pet)
    _print_status(pet)


def cmd_rename(args: argparse.Namespace) -> None:
    pet = _load_or_prompt()
    if pet is None:
        return
    old_name = pet.name
    pet.name = args.new_name
    petmod.save(pet)
    print(f"{old_name} is now known as {pet.name}.")


def cmd_reset(args: argparse.Namespace) -> None:
    pet = petmod.load()
    if pet is None:
        print("No pet to reset.")
        return
    if not args.yes:
        confirm = input(f"This will permanently release {pet.name}. Type 'yes' to confirm: ")
        if confirm.strip().lower() != "yes":
            print("Cancelled.")
            return
    petmod.reset()
    print("Done. Run `pet adopt <name>` whenever you're ready for a new one.")


@contextmanager
def _posix_cbreak_mode() -> Iterator[None]:
    """Put POSIX stdin in cbreak mode for single-keypress input if stdin is a TTY."""
    if sys.platform == "win32":
        yield
        return
    if not (hasattr(sys.stdin, "isatty") and sys.stdin.isatty()):
        yield
        return
    try:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
    except (ImportError, OSError, ValueError):
        yield
        return

    try:
        tty.setcbreak(fd)
        yield
    except (OSError, ValueError, termios.error):
        yield
    finally:
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except (OSError, ValueError, termios.error):
            pass


def _poll_key_win32(timeout: float) -> str | None:
    import msvcrt

    deadline = time.monotonic() + timeout
    while True:
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch in (b"\x00", b"\xe0"):
                if msvcrt.kbhit():
                    msvcrt.getch()
                return None
            try:
                return ch.decode("utf-8").lower()
            except UnicodeDecodeError:
                return None
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        time.sleep(min(0.04, remaining))


def _poll_key_posix(timeout: float) -> str | None:
    import select

    if not (hasattr(sys.stdin, "isatty") and sys.stdin.isatty()):
        time.sleep(timeout)
        return None
    try:
        fd = sys.stdin.fileno()
        ready, _, _ = select.select([fd], [], [], timeout)
    except (OSError, ValueError):
        time.sleep(timeout)
        return None
    if not ready:
        return None
    try:
        ch = os.read(fd, 1)
    except OSError:
        return None
    if not ch:
        return None
    if ch == b"\x1b":
        try:
            while select.select([fd], [], [], 0)[0]:
                os.read(fd, 1)
        except OSError:
            pass
        return None
    try:
        return ch.decode("utf-8").lower()
    except UnicodeDecodeError:
        return None


def _poll_key(timeout: float = 0.35) -> str | None:
    """Non-blocking single-key poll with timeout across Windows and POSIX."""
    if sys.platform == "win32":
        return _poll_key_win32(timeout)
    return _poll_key_posix(timeout)


def _pet_watch_snapshot(pet: petmod.Pet) -> tuple:
    """Comparable snapshot of persisted pet fields to avoid redundant disk writes."""
    return (
        pet.name,
        pet.species,
        round(pet.hunger, 1),
        round(pet.happiness, 1),
        round(pet.energy, 1),
        pet.alive,
        pet.death_reason,
        pet.starving_since > 0.0,
        pet.level,
        pet.xp,
    )


def _format_action_msg(icon: str, msg: str, pet_name: str, level: int, xp_gain: int) -> str:
    lines = msg.splitlines()
    first_line = lines[0] if lines else ""
    if len(lines) > 1 and "LEVEL UP!" in msg:
        return f"🎉  LEVEL UP! {pet_name} is now Level {level}! (+{xp_gain} XP)"
    return f"{icon}  {first_line}"


def cmd_watch(args: argparse.Namespace) -> None:
    """Live interactive Tamagotchi dashboard mode with roaming & corner sitting."""
    pet = _load_or_prompt()
    if pet is None:
        return

    cols, _ = shutil.get_terminal_size((80, 24))
    room_width = max(52, min(74, cols - 4))
    inner_width = room_width - 2
    max_offset = max(2, inner_width - 18)
    min_offset = 2

    print(anim.colored("Starting live playground... Press 'q' or Ctrl+C to quit.", anim.CYAN))
    time.sleep(0.5)

    last_saved = _pet_watch_snapshot(pet)
    if pet.alive:
        pet, _ = petmod.tick(pet)
        snap = _pet_watch_snapshot(pet)
        if snap != last_saved:
            petmod.save(pet)
            last_saved = snap

    offset = max(2, (max_offset + min_offset) // 2)
    direction = 1
    state = "roam" if pet.alive else "dead"
    state_timer = 0
    frame_idx = 0
    msg_hold_ticks = 0
    if pet.alive:
        activity_msg = f"{pet.name} is happily roaming around the terminal!"
    else:
        cause = pet.death_reason or "passed away"
        activity_msg = f"💀  {pet.name} has {cause}. Run `pet reset` to start fresh."

    try:
        anim.hide_cursor()
        with _posix_cbreak_mode():
            while True:
                if pet.alive:
                    pet, _ = petmod.tick(pet)
                    snap = _pet_watch_snapshot(pet)
                    if snap != last_saved:
                        petmod.save(pet)
                        last_saved = snap

                m = petmod.mood(pet)
                hold_msg = msg_hold_ticks > 0
                if hold_msg:
                    msg_hold_ticks -= 1

                if not pet.alive:
                    state = "dead"
                    sprite_name = "dead"
                    if not hold_msg:
                        cause = pet.death_reason or "passed away"
                        activity_msg = f"💀  {pet.name} has {cause}. Run `pet reset` to start fresh."
                else:
                    frame_idx += 1
                    state_timer += 1

                    # State machine for roaming and sitting in corner
                    if state == "roam":
                        sprite_name = "walk_right" if direction == 1 else "walk_left"
                        offset += direction
                        if offset >= max_offset:
                            offset = max_offset
                            # Hit right wall: 60% chance to sit in corner, 40% turn around
                            if random.random() < 0.6:
                                state = "corner_sit"
                                state_timer = 0
                                if not hold_msg:
                                    activity_msg = (
                                        f"🛋️  {pet.name} reached the right corner and curled up to sit."
                                    )
                            else:
                                direction = -1
                                if not hold_msg:
                                    activity_msg = f"🐾  {pet.name} turned around and trotted left."
                        elif offset <= min_offset:
                            offset = min_offset
                            if random.random() < 0.6:
                                state = "corner_sit"
                                state_timer = 0
                                if not hold_msg:
                                    activity_msg = (
                                        f"🛋️  {pet.name} found the left corner and sat down comfortably."
                                    )
                            else:
                                direction = 1
                                if not hold_msg:
                                    activity_msg = f"🐾  {pet.name} turned around and trotted right."
                        else:
                            if not hold_msg:
                                activity_msg = (
                                    f"🐾  {pet.name} is roaming across the terminal... (Press [C] for corner)"
                                )

                    elif state == "corner_sit":
                        sprite_name = "corner_sit"
                        if not hold_msg:
                            activity_msg = (
                                f"🛋️  {pet.name} is resting cozily in the corner. (Press [R] to roam)"
                            )
                        if state_timer >= 12:  # After ~4 seconds
                            state = "roam"
                            direction = 1 if offset <= min_offset else -1
                            state_timer = 0
                            if not hold_msg:
                                activity_msg = (
                                    f"🐾  {pet.name} hopped up from the corner and started roaming!"
                                )

                    elif state == "dance":
                        sprite_name = "dance"
                        if state_timer >= 5:
                            state = "roam"
                            state_timer = 0
                            if not hold_msg:
                                activity_msg = (
                                    f"🐾  {pet.name} finished playing and resumed walking around."
                                )
                    else:
                        sprite_name = "walk_right"

                sprite_lines = anim.get_roam_sprite(pet.species, sprite_name, frame_idx)

                box_text = anim.render_room_box(
                    pet_name=pet.name,
                    species=pet.species,
                    level=pet.level,
                    xp=pet.xp,
                    mood_name=m,
                    hunger=pet.hunger,
                    happiness=pet.happiness,
                    energy=pet.energy,
                    sprite_lines=sprite_lines,
                    offset=offset,
                    activity_msg=activity_msg,
                    room_width=room_width,
                )

                sys.stdout.write("\033[2J\033[H")
                sys.stdout.write(box_text + "\n")
                sys.stdout.flush()

                key_pressed = _poll_key(0.35)

                if key_pressed == "q":
                    break
                elif not pet.alive:
                    if key_pressed == "f":
                        activity_msg = f"💀  {petmod.feed(pet)}"
                        msg_hold_ticks = 6
                    elif key_pressed == "p":
                        activity_msg = f"💀  {petmod.play(pet)}"
                        msg_hold_ticks = 6
                    elif key_pressed == "n":
                        activity_msg = f"💀  {petmod.nap(pet)}"
                        msg_hold_ticks = 6
                    elif key_pressed in ("c", "r"):
                        activity_msg = (
                            f"💀  {pet.name} is gone. Press [Q] to quit or run `pet reset`."
                        )
                        msg_hold_ticks = 6
                elif key_pressed == "f":
                    msg = petmod.feed(pet)
                    snap = _pet_watch_snapshot(pet)
                    if snap != last_saved:
                        petmod.save(pet)
                        last_saved = snap
                    state = "dance"
                    state_timer = 0
                    activity_msg = _format_action_msg("🍴", msg, pet.name, pet.level, 15)
                    msg_hold_ticks = 6
                elif key_pressed == "p":
                    was_tired = pet.energy < 15
                    msg = petmod.play(pet)
                    if was_tired:
                        activity_msg = f"😴  {msg.splitlines()[0]}"
                        msg_hold_ticks = 6
                    else:
                        snap = _pet_watch_snapshot(pet)
                        if snap != last_saved:
                            petmod.save(pet)
                            last_saved = snap
                        state = "dance"
                        state_timer = 0
                        activity_msg = _format_action_msg("🎾", msg, pet.name, pet.level, 25)
                        msg_hold_ticks = 6
                elif key_pressed == "n":
                    msg = petmod.nap(pet)
                    snap = _pet_watch_snapshot(pet)
                    if snap != last_saved:
                        petmod.save(pet)
                        last_saved = snap
                    state = "corner_sit"
                    state_timer = 0
                    offset = max_offset if direction == 1 else min_offset
                    activity_msg = _format_action_msg("💤", msg, pet.name, pet.level, 10)
                    msg_hold_ticks = 6
                elif key_pressed == "c":
                    state = "corner_sit"
                    state_timer = 0
                    offset = max_offset if direction == 1 else min_offset
                    activity_msg = f"🛋️  {pet.name} went to sit comfortably in the corner."
                    msg_hold_ticks = 6
                elif key_pressed == "r":
                    state = "roam"
                    state_timer = 0
                    direction = 1 if offset <= min_offset else -1
                    activity_msg = f"🐾  {pet.name} jumped up to roam around!"
                    msg_hold_ticks = 6

    except KeyboardInterrupt:
        pass
    finally:
        anim.show_cursor()
        if pet.alive:
            print("\nExited playground mode. Your pet is resting safely!")
        else:
            print("\nExited playground mode. Run `pet reset` when you're ready to adopt a new one.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pet", description="A tiny virtual pet that lives in your terminal.")
    sub = parser.add_subparsers(dest="command")

    p_adopt = sub.add_parser("adopt", help="Adopt a new pet")
    p_adopt.add_argument("name", help="Name for your pet")
    p_adopt.add_argument("--species", choices=petmod.SPECIES, help="Species (random if omitted)")
    p_adopt.add_argument("--no-anim", action="store_true", help="Skip animations")
    p_adopt.set_defaults(func=cmd_adopt)

    p_status = sub.add_parser("status", help="Check on your pet")
    p_status.set_defaults(func=cmd_status)

    p_feed = sub.add_parser("feed", help="Feed your pet")
    p_feed.add_argument("--no-anim", action="store_true", help="Skip animations")
    p_feed.set_defaults(func=cmd_feed)

    p_play = sub.add_parser("play", help="Play with your pet")
    p_play.add_argument("--no-anim", action="store_true", help="Skip animations")
    p_play.set_defaults(func=cmd_play)

    p_nap = sub.add_parser("nap", help="Let your pet nap to restore energy")
    p_nap.add_argument("--no-anim", action="store_true", help="Skip animations")
    p_nap.set_defaults(func=cmd_nap)

    p_watch = sub.add_parser("watch", help="Open the live interactive pet dashboard")
    p_watch.set_defaults(func=cmd_watch)

    p_rename = sub.add_parser("rename", help="Rename your pet")
    p_rename.add_argument("new_name")
    p_rename.set_defaults(func=cmd_rename)

    p_reset = sub.add_parser("reset", help="Release your pet and start over")
    p_reset.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    p_reset.set_defaults(func=cmd_reset)

    return parser


def main(argv: list[str] | None = None) -> int:
    anim.enable_windows_ansi()
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        # No subcommand given: show status if a pet exists, else help.
        pet = petmod.load()
        if pet is None:
            parser.print_help()
        else:
            cmd_status(args)
        return 0
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
