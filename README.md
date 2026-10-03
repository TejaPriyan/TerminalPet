# TerminalPet 🐉🐾

[![GitHub repo](https://img.shields.io/badge/GitHub-TejaPriyan%2FTerminalPet-blue?logo=github)](https://github.com/TejaPriyan/TerminalPet)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A tiny, charming virtual pet that lives inside your terminal! Feed it, play with it, watch it take cozy naps in the corner, and let it roam across your screen.

Unlike typical pet games, TerminalPet stats decay based on **real elapsed time** — not a background process or daemon. Close your terminal for a day and your pet will actually notice!

---

## ✨ Features

- **🐾 Active Roaming Playground (`pet watch`)**: Watch your pet physically walk across your terminal screen with animated steps and flapping wings/paws.
- **🛋️ Corner Sitting**: Pets seek cozy spots in the corners of your terminal to relax, rest, and watch you code.
- **🎨 High-Quality ASCII Art & Color**: Detailed character designs for 5 species:
  - **Dragon 🐉**: Golden horns, scaled heart chest, spiked tail, and smoke puffs.
  - **Cat 🐱**: Pointed ears, whiskers, fluffy body, and purring animation.
  - **Dog 🐶**: Floppy ears, cheerful smile, and wagging tail.
  - **Robot 🤖**: Sensor antenna, screen face, dual gears, and treads.
  - **Blob 🍮**: Bouncy jelly outline, cute smile, and squishy hops.
- **🎬 Frame-by-Frame Animations**:
  - **Adoption/Hatching**: Eggs wobble, crack, and burst open with confetti.
  - **Feeding**: Food slides toward pet $\rightarrow$ *CHOMP!* $\rightarrow$ *nom nom nom*.
  - **Playing**: Bouncing toy catch $\rightarrow$ celebratory dance.
  - **Napping**: Snoozing with floating `zZz`.
- **⭐ Leveling & XP**: Earn experience points by caring for your pet to level up!
- **📊 Smooth Color Gauges**: UTF-8 block gauges (`████░░░░`) with dynamic health color alerts (Green, Yellow, Red).

---

## 🚀 Installation

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/TejaPriyan/TerminalPet.git
cd TerminalPet
pip install -e .
```

---

## 🎮 Usage

```bash
# 1. Adopt a pet (choose: dragon, cat, dog, robot, blob)
pet adopt Teja --species dragon

# 2. Check status and dynamic poses
pet status

# 3. Enter the Live Interactive Playground
pet watch
# Hotkeys: [F]eed  [P]lay  [N]ap  [C]orner Sit  [R]oam  [Q]uit

# 4. Care Actions
pet feed    # Lowers hunger, awards +15 XP
pet play    # Boosts happiness, costs energy, awards +25 XP
pet nap     # Restores energy, awards +10 XP

# 5. Management
pet rename Buddy   # Rename your pet
pet reset          # Release your pet and start fresh
```

*(Tip: Add `--no-anim` to any command like `pet feed --no-anim` if you want instant output).*

---

## 🛠️ How It Works

- **State File**: Saved in `~/.terminalpet/pet.json`.
- **Elapsed Time Decay**: Every command calculates how many real hours passed since `last_update` and decays hunger, happiness, and energy accordingly.
- **Neglect Warning**: If hunger stays at 100 continuously for 72 real hours, the pet can starve.

---

## 👤 Author

Developed by **[Teja Priyan](https://github.com/TejaPriyan)**  
GitHub: [https://github.com/TejaPriyan/TerminalPet](https://github.com/TejaPriyan/TerminalPet)
