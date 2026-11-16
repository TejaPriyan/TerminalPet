"""Core state, decay, and actions for a terminalpet."""
from __future__ import annotations

import dataclasses
import json
import math
import os
import random
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path

STATE_DIR = Path.home() / ".terminalpet"
STATE_FILE = STATE_DIR / "pet.json"

MAX_STAT = 100.0
MIN_STAT = 0.0

# Decay rates, per hour of real elapsed time.
HUNGER_PER_HOUR = 4.0
HAPPINESS_DECAY_PER_HOUR = 3.0
ENERGY_DECAY_PER_HOUR = 2.0

# If hunger sits at 100 continuously for this many real hours, the pet dies.
NEGLECT_DEATH_HOURS = 72.0

SPECIES = ["cat", "dog", "dragon", "blob", "robot"]

SPECIES_FLAVOR = {
    "cat": {"noun": "cat", "sound": "meows", "affection": "headbutts your hand"},
    "dog": {"noun": "dog", "sound": "barks", "affection": "wags its whole body"},
    "dragon": {"noun": "dragon", "sound": "chirrs", "affection": "puffs a small friendly smoke ring"},
    "blob": {"noun": "blob", "sound": "blorps", "affection": "wobbles happily"},
    "robot": {"noun": "robot", "sound": "beeps", "affection": "whirs contentedly"},
}

DEFAULT_FLAVOR = {"noun": "pet", "sound": "chirps", "affection": "nuzzles your hand"}


def clamp(value: float) -> float:
    return max(MIN_STAT, min(MAX_STAT, value))


@dataclass
class Pet:
    name: str
    species: str
    birth_time: float
    last_update: float
    hunger: float = 20.0       # 0 = full, 100 = starving
    happiness: float = 80.0    # 0 = miserable, 100 = ecstatic
    energy: float = 80.0       # 0 = exhausted, 100 = fully rested
    alive: bool = True
    death_reason: str = ""
    starving_since: float = 0.0  # 0 means "not currently starving"
    level: int = 1
    xp: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        if not isinstance(data, dict):
            raise ValueError("Pet state must be a JSON object")
        valid_fields = {f.name for f in dataclasses.fields(cls)}
        filtered = {k: v for k, v in data.items() if k in valid_fields}

        for req in ("name", "species", "birth_time", "last_update"):
            if req not in filtered:
                raise TypeError(f"Missing required field: {req}")

        if not isinstance(filtered["name"], str) or not isinstance(filtered["species"], str):
            raise TypeError("Pet name and species must be strings")

        for num_field in ("birth_time", "last_update", "hunger", "happiness", "energy", "starving_since"):
            if num_field in filtered:
                raw = filtered[num_field]
                if isinstance(raw, bool):
                    raise TypeError(f"Field '{num_field}' must be numeric")
                val = float(raw)
                if not math.isfinite(val):
                    raise ValueError(f"Field '{num_field}' must be finite")
                filtered[num_field] = val

        for stat_field in ("hunger", "happiness", "energy"):
            if stat_field in filtered:
                filtered[stat_field] = clamp(filtered[stat_field])

        for int_field, min_val in (("level", 1), ("xp", 0)):
            if int_field in filtered:
                raw = filtered[int_field]
                if isinstance(raw, bool) or not isinstance(raw, (int, float)):
                    raise TypeError(f"Field '{int_field}' must be an integer")
                if not math.isfinite(raw):
                    raise ValueError(f"Field '{int_field}' must be finite")
                filtered[int_field] = max(min_val, int(raw))

        if "alive" in filtered and not isinstance(filtered["alive"], bool):
            raise TypeError("Field 'alive' must be a boolean")

        if "death_reason" in filtered and not isinstance(filtered["death_reason"], str):
            filtered["death_reason"] = str(filtered["death_reason"])

        return cls(**filtered)

    def add_xp(self, amount: int) -> bool:
        """Add XP and return True if at least one level was gained."""
        if amount <= 0:
            return False
        if self.level < 1:
            self.level = 1
        self.xp += amount
        leveled = False
        while self.xp >= self.level * 100:
            self.xp -= self.level * 100
            self.level += 1
            leveled = True
        return leveled


def new_pet(name: str, species: str | None = None) -> Pet:
    if species is None:
        species = random.choice(SPECIES)
    now = time.time()
    return Pet(name=name, species=species, birth_time=now, last_update=now)


def _backup_corrupt_state() -> Path | None:
    timestamp = int(time.time())
    backup = STATE_FILE.with_name(f"{STATE_FILE.name}.corrupt.{timestamp}")
    counter = 1
    while backup.exists():
        backup = STATE_FILE.with_name(f"{STATE_FILE.name}.corrupt.{timestamp}.{counter}")
        counter += 1
    try:
        STATE_FILE.replace(backup)
        return backup
    except OSError:
        return None


def load() -> Pet | None:
    if not STATE_FILE.exists():
        return None
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return Pet.from_dict(data)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError, ValueError) as exc:
        backup = _backup_corrupt_state()
        if backup is not None:
            print(
                f"Warning: Could not read pet state ({exc}). "
                f"Backed up corrupt file to {backup}.",
                file=sys.stderr,
            )
        else:
            print(
                f"Warning: Could not read pet state ({exc}). Starting fresh.",
                file=sys.stderr,
            )
        return None


def save(pet: Pet) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=STATE_FILE.parent,
            prefix=f".{STATE_FILE.name}.",
            suffix=".tmp",
            delete=False,
        ) as f:
            tmp_path = f.name
            json.dump(pet.to_dict(), f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, STATE_FILE)
    except Exception:
        if tmp_path is not None and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        raise


def reset() -> None:
    if STATE_FILE.exists():
        STATE_FILE.unlink()


def tick(pet: Pet) -> tuple[Pet, float]:
    """Apply time-based decay since the last check-in. Returns (pet, hours_elapsed)."""
    if not pet.alive:
        return pet, 0.0

    now = time.time()
    elapsed_hours = max(0.0, (now - pet.last_update) / 3600.0)
    if elapsed_hours == 0:
        return pet, 0.0

    pet.hunger = clamp(pet.hunger + HUNGER_PER_HOUR * elapsed_hours)
    pet.happiness = clamp(pet.happiness - HAPPINESS_DECAY_PER_HOUR * elapsed_hours)
    pet.energy = clamp(pet.energy - ENERGY_DECAY_PER_HOUR * elapsed_hours)

    if pet.hunger >= MAX_STAT:
        if pet.starving_since == 0.0:
            pet.starving_since = now
        starving_hours = (now - pet.starving_since) / 3600.0
        if starving_hours >= NEGLECT_DEATH_HOURS:
            pet.alive = False
            pet.death_reason = "starved after days without being fed"
    else:
        pet.starving_since = 0.0

    pet.last_update = now
    return pet, elapsed_hours


def feed(pet: Pet) -> str:
    if not pet.alive:
        return f"{pet.name} is gone. There's nothing left to feed."
    pet.hunger = clamp(pet.hunger - 35)
    pet.happiness = clamp(pet.happiness + 5)
    pet.energy = clamp(pet.energy + 2)
    leveled = pet.add_xp(15)
    flavor = SPECIES_FLAVOR.get(pet.species, DEFAULT_FLAVOR)
    msg = f"{pet.name} {flavor['sound']} and devours the food. Much better. (+15 XP)"
    if leveled:
        msg += f"\n  ✨ 🎉 LEVEL UP! {pet.name} is now Level {pet.level}! 🎉 ✨"
    return msg


def play(pet: Pet) -> str:
    if not pet.alive:
        return f"{pet.name} is gone. There's no one left to play with."
    if pet.energy < 15:
        return f"{pet.name} is too tired to play right now. Let it nap first."
    pet.happiness = clamp(pet.happiness + 20)
    pet.energy = clamp(pet.energy - 15)
    pet.hunger = clamp(pet.hunger + 10)
    leveled = pet.add_xp(25)
    flavor = SPECIES_FLAVOR.get(pet.species, DEFAULT_FLAVOR)
    msg = f"{pet.name} {flavor['affection']} and plays with you. So much fun! (+25 XP)"
    if leveled:
        msg += f"\n  ✨ 🎉 LEVEL UP! {pet.name} is now Level {pet.level}! 🎉 ✨"
    return msg


def nap(pet: Pet) -> str:
    if not pet.alive:
        return f"{pet.name} is gone. There's no one left to tuck in."
    pet.energy = clamp(pet.energy + 30)
    pet.happiness = clamp(pet.happiness - 2)
    leveled = pet.add_xp(10)
    msg = f"{pet.name} curls up for a nap and wakes up more rested. (+10 XP)"
    if leveled:
        msg += f"\n  ✨ 🎉 LEVEL UP! {pet.name} is now Level {pet.level}! 🎉 ✨"
    return msg


def mood(pet: Pet) -> str:
    if not pet.alive:
        return "dead"
    if pet.hunger >= 90:
        return "starving"
    if pet.happiness <= 20:
        return "sad"
    if pet.energy <= 20:
        return "tired"
    if pet.happiness >= 90 and pet.hunger <= 20:
        return "ecstatic"
    if pet.happiness >= 65:
        return "happy"
    return "content"


def age_str(pet: Pet) -> str:
    end = pet.last_update if not pet.alive else time.time()
    seconds = max(0.0, end - pet.birth_time)
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    if days == 0 and hours == 0:
        return "just hatched"
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    return " ".join(parts) + " old"


def bar(value: float, width: int = 20, is_hunger: bool = False) -> str:
    from . import anim
    return anim.color_bar(value, width=width, is_hunger=is_hunger)
