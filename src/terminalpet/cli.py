"""Command-line interface for terminalpet."""
from __future__ import annotations

import argparse
import sys
import time

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
    print(f"{anim.BOLD}{pet.name}{anim.RESET} the {pet.species} — {anim.CYAN}{petmod.age_str(pet)}{anim.RESET} — feeling {anim.BOLD}{m}{anim.RESET}")
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


def cmd_watch(args: argparse.Namespace) -> None:
    """Live interactive Tamagotchi dashboard mode with roaming & corner sitting."""
    import random
    import shutil

    pet = _load_or_prompt()
    if pet is None:
        return

    cols, _ = shutil.get_terminal_size((80, 24))
    room_width = max(52, min(74, cols - 4))
    inner_width = room_width - 2
    max_offset = inner_width - 18
    min_offset = 2

    print(anim.colored("Starting live playground... Press 'q' or Ctrl+C to quit.", anim.CYAN))
    time.sleep(0.5)

    offset = max(2, (max_offset + min_offset) // 2)
    direction = 1
    state = "roam"
    state_timer = 0
    frame_idx = 0
    activity_msg = f"{pet.name} is happily roaming around the terminal!"

    try:
        anim.hide_cursor()
        while True:
            # Tick decay
            pet, _ = petmod.tick(pet)
            petmod.save(pet)

            m = petmod.mood(pet)
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
                        activity_msg = f"🛋️  {pet.name} reached the right corner and curled up to sit."
                    else:
                        direction = -1
                        activity_msg = f"🐾  {pet.name} turned around and trotted left."
                elif offset <= min_offset:
                    offset = min_offset
                    if random.random() < 0.6:
                        state = "corner_sit"
                        state_timer = 0
                        activity_msg = f"🛋️  {pet.name} found the left corner and sat down comfortably."
                    else:
                        direction = 1
                        activity_msg = f"🐾  {pet.name} turned around and trotted right."
                else:
                    activity_msg = f"🐾  {pet.name} is roaming across the terminal... (Press [C] for corner)"

            elif state == "corner_sit":
                sprite_name = "corner_sit"
                activity_msg = f"🛋️  {pet.name} is resting cozily in the corner. (Press [R] to roam)"
                if state_timer >= 12:  # After ~4 seconds
                    state = "roam"
                    direction = 1 if offset <= min_offset else -1
                    state_timer = 0
                    activity_msg = f"🐾  {pet.name} hopped up from the corner and started roaming!"

            elif state == "dance":
                sprite_name = "dance"
                if state_timer >= 5:
                    state = "roam"
                    state_timer = 0
                    activity_msg = f"🐾  {pet.name} finished playing and resumed walking around."

            # Fetch sprite
            sprite_lines = anim.get_roam_sprite(pet.species, sprite_name, frame_idx)

            # Render room box
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

            # Non-blocking key check
            key_pressed = None
            if sys.platform == "win32":
                import msvcrt
                start = time.time()
                while time.time() - start < 0.35:
                    if msvcrt.kbhit():
                        ch = msvcrt.getch()
                        try:
                            key_pressed = ch.decode("utf-8").lower()
                        except UnicodeDecodeError:
                            pass
                        break
                    time.sleep(0.04)
            else:
                time.sleep(0.35)

            if key_pressed == "q":
                break
            elif key_pressed == "f":
                _ = petmod.feed(pet)
                petmod.save(pet)
                state = "dance"
                state_timer = 0
                activity_msg = f"🍴  {pet.name} chowed down the treat! (+15 XP)"
            elif key_pressed == "p":
                if pet.energy < 15:
                    activity_msg = f"😴  {pet.name} is too tired to play right now. Let it nap first!"
                else:
                    _ = petmod.play(pet)
                    petmod.save(pet)
                    state = "dance"
                    state_timer = 0
                    activity_msg = f"🎾  {pet.name} caught the toy and danced with joy! (+25 XP)"
            elif key_pressed == "n":
                _ = petmod.nap(pet)
                petmod.save(pet)
                state = "corner_sit"
                state_timer = 0
                offset = max_offset if direction == 1 else min_offset
                activity_msg = f"💤  {pet.name} curled up in the corner for a restoring nap! (+10 XP)"
            elif key_pressed == "c":
                state = "corner_sit"
                state_timer = 0
                offset = max_offset if direction == 1 else min_offset
                activity_msg = f"🛋️  {pet.name} went to sit comfortably in the corner."
            elif key_pressed == "r":
                state = "roam"
                state_timer = 0
                direction = 1 if offset <= min_offset else -1
                activity_msg = f"🐾  {pet.name} jumped up to roam around!"

    except KeyboardInterrupt:
        pass
    finally:
        anim.show_cursor()
        print("\nExited playground mode. Your pet is resting safely!")


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
