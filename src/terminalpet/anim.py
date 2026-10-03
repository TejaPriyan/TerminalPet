"""Animations, ASCII art, and ANSI color styling for terminalpet."""
from __future__ import annotations

import os
import sys
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pet import Pet

# ANSI Escape Sequences
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
CLEAR_SCREEN = "\033[2J\033[H"

# Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
WHITE = "\033[97m"
ORANGE = "\033[38;5;208m"

# Enable ANSI & UTF-8 support in Windows CMD / PowerShell
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if os.name == "nt":
    os.system("")


def hide_cursor() -> None:
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor() -> None:
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def colored(text: str, color_code: str) -> str:
    return f"{color_code}{text}{RESET}"


# Species-specific ASCII Art for each mood
SPECIES_ART: dict[str, dict[str, str]] = {
    "dragon": {
        "ecstatic": rf"""
     {YELLOW}▲  _  ▲{RESET}   {MAGENTA}*~ ✨ ♨{RESET}
   {GREEN}\( {CYAN}^ ‿ ^{GREEN} )/{RESET}  {YELLOW}♨♨{RESET}
    {MAGENTA}/({GREEN}=={RED}♥{GREEN}=={MAGENTA})\{RESET}
   {MAGENTA}<  {GREEN})   (  {MAGENTA}>{RESET} {YELLOW}~>>{RESET}
     {GREEN}/     \{RESET}
""",
        "happy": rf"""
     {YELLOW}▲  _  ▲{RESET}
    {GREEN}( {CYAN}•{GREEN} ‿ {CYAN}• ){RESET}  {YELLOW}*~♨{RESET}
   {MAGENTA}/({GREEN}=={RED}♥{GREEN}=={MAGENTA})\{RESET}
  {MAGENTA}<  {GREEN})   (  {MAGENTA}>{RESET} {YELLOW}~>>{RESET}
    {GREEN}d     b{RESET}
""",
        "content": rf"""
     {YELLOW}▲  _  ▲{RESET}
    {GREEN}( {CYAN}- ‿ -{GREEN} ){RESET}
   {MAGENTA}/({GREEN}=={RED}♥{GREEN}=={MAGENTA})\{RESET}
  {MAGENTA}<  {GREEN})   (  {MAGENTA}>{RESET} {YELLOW}~>>{RESET}
    {GREEN}d     b{RESET}
""",
        "tired": rf"""
     {YELLOW}▲  _  ▲{RESET}
    {GREEN}( {CYAN}- . -{GREEN} ){RESET} {BLUE}zzZ{RESET}
   {MAGENTA}/({GREEN}=={RED}♥{GREEN}=={MAGENTA})\{RESET}
  {MAGENTA}<  {GREEN})   (  {MAGENTA}>{RESET} {YELLOW}~>>{RESET}
    {GREEN}d     b{RESET}
""",
        "sad": rf"""
     {YELLOW}▲  _  ▲{RESET}
    {BLUE}( {CYAN}; _ ;{BLUE} ){RESET}
   {CYAN}/({GREEN}=={RED}♥{GREEN}=={CYAN})\{RESET}
  {CYAN}<  {GREEN})   (  {CYAN}>{RESET} {YELLOW}~>{RESET}
    {DIM}d     b{RESET}
""",
        "starving": rf"""
     {YELLOW}▲  _  ▲{RESET}
    {RED}( {WHITE}> _ <{RED} ){RESET} {RED}! !{RESET}
   {RED}/({DIM}==   =={RED})\{RESET}
  {RED}<  {DIM})     (  {RED}>{RESET}
    {DIM}d       b{RESET}
""",
        "dead": rf"""
     {DIM}▲  _  ▲{RESET}
    {DIM}( x _ x ){RESET}
   {DIM}/(==RIP==)\{RESET}
  {DIM}<  )     (  >{RESET}
    {DIM}d       b{RESET}
""",
    },
    "cat": {
        "ecstatic": rf"""
     {YELLOW}/\\_____/\\{RESET}   {MAGENTA}✨ *purr*{RESET}
   {WHITE}\(  =^‿^=  )/{RESET}
    {CYAN}/(  \"w\"  )\\{RESET}
   {WHITE}(  )     (  ){RESET}{MAGENTA}~{RESET}
     {DIM}d       b{RESET}
""",
        "happy": rf"""
     {YELLOW}/\\_____/\\{RESET}
    {WHITE}(  =•‿•=  ){RESET}  {MAGENTA}~♥{RESET}
    {CYAN}/(  \"w\"  )\\{RESET}
   {WHITE}(  )     (  ){RESET}{MAGENTA}~{RESET}
     {DIM}d       b{RESET}
""",
        "content": rf"""
     {YELLOW}/\\_____/\\{RESET}
    {WHITE}(  =•.•=  ){RESET}
    {CYAN}/(  \"w\"  )\\{RESET}
   {WHITE}(  )     (  ){RESET}{MAGENTA}~{RESET}
     {DIM}d       b{RESET}
""",
        "tired": rf"""
     {YELLOW}/\\_____/\\{RESET}
    {WHITE}(  =-.-=  ){RESET} {BLUE}zzZ{RESET}
    {CYAN}/(  \"w\"  )\\{RESET}
   {WHITE}(  )     (  ){RESET}{MAGENTA}~{RESET}
     {DIM}d       b{RESET}
""",
        "sad": rf"""
     {YELLOW}/\\_____/\\{RESET}
    {BLUE}(  =;.;=  ){RESET}
    {CYAN}/(  \"w\"  )\\{RESET}
   {WHITE}(  )     (  ){RESET}{MAGENTA}~{RESET}
     {DIM}d       b{RESET}
""",
        "starving": rf"""
     {YELLOW}/\\_____/\\{RESET}
    {RED}(  =>.<=  ){RESET} {RED}! !{RESET}
    {CYAN}/(  \"w\"  )\\{RESET}
   {WHITE}(  )     (  ){RESET}
     {DIM}d       b{RESET}
""",
        "dead": rf"""
     {DIM}/\\_____/\\{RESET}
    {DIM}(  =x.x=  ){RESET}
    {DIM}/(  R.I.P )\\{RESET}
   {DIM}(  )     (  ){RESET}
     {DIM}d       b{RESET}
""",
    },
    "dog": {
        "ecstatic": rf"""
     {YELLOW}/ᐢ_____ᐢ\\{RESET}   {MAGENTA}✨ *wag wag*{RESET}
   {WHITE}\(   ^‿^   )/{RESET}
    {CYAN}/(  \"U\"  )\\{RESET}  {GREEN}~{RESET}
   {WHITE}(  )     (  ){RESET}
     {DIM}d       b{RESET}
""",
        "happy": rf"""
     {YELLOW}/ᐢ_____ᐢ\\{RESET}
    {WHITE}(   •‿•   ){RESET}  {GREEN}*wag*{RESET}
    {CYAN}/(  \"U\"  )\\{RESET}  {GREEN}~{RESET}
   {WHITE}(  )     (  ){RESET}
     {DIM}d       b{RESET}
""",
        "content": rf"""
     {YELLOW}/ᐢ_____ᐢ\\{RESET}
    {WHITE}(   -‿-   ){RESET}
    {CYAN}/(  \"U\"  )\\{RESET}  {GREEN}~{RESET}
   {WHITE}(  )     (  ){RESET}
     {DIM}d       b{RESET}
""",
        "tired": rf"""
     {YELLOW}/ᐢ_____ᐢ\\{RESET}
    {WHITE}(   -.-   ){RESET} {BLUE}zzZ{RESET}
    {CYAN}/(  \"U\"  )\\{RESET}  {GREEN}~{RESET}
   {WHITE}(  )     (  ){RESET}
     {DIM}d       b{RESET}
""",
        "sad": rf"""
     {YELLOW}/ᐢ_____ᐢ\\{RESET}
    {BLUE}(   ;_;   ){RESET}
    {CYAN}/(  \"U\"  )\\{RESET}  {GREEN}~{RESET}
   {WHITE}(  )     (  ){RESET}
     {DIM}d       b{RESET}
""",
        "starving": rf"""
     {YELLOW}/ᐢ_____ᐢ\\{RESET}
    {RED}(   >_<   ){RESET} {RED}! !{RESET}
    {CYAN}/(  \"U\"  )\\{RESET}
   {WHITE}(  )     (  ){RESET}
     {DIM}d       b{RESET}
""",
        "dead": rf"""
     {DIM}/ᐢ_____ᐢ\\{RESET}
    {DIM}(   x_x   ){RESET}
    {DIM}/(  R.I.P )\\{RESET}
   {DIM}(  )     (  ){RESET}
     {DIM}d       b{RESET}
""",
    },
    "robot": {
        "ecstatic": rf"""
     {CYAN}.-[ o ]-.{RESET}   {YELLOW}⚡ *BEEP!*{RESET}
   {WHITE}\[  ^ ‿ ^  ]/{RESET} {CYAN}✨{RESET}
   {CYAN}/|[  ⚙ ⚙  ]|\\{RESET}
  {WHITE}(o)  ====   (o){RESET}
""",
        "happy": rf"""
     {CYAN}.-[ o ]-.{RESET}   {YELLOW}⚡{RESET}
    {WHITE}[  • ‿ •  ]{RESET} {CYAN}✨{RESET}
   {CYAN}/|[  ⚙ ⚙  ]|\\{RESET}
  {WHITE}(o)  ====   (o){RESET}
""",
        "content": rf"""
     {CYAN}.-[ o ]-.{RESET}
    {WHITE}[  - ‿ -  ]{RESET}
   {CYAN}/|[  ⚙ ⚙  ]|\\{RESET}
  {WHITE}(o)  ====   (o){RESET}
""",
        "tired": rf"""
     {CYAN}.-[ o ]-.{RESET}   {BLUE}zzZ{RESET}
    {WHITE}[  - . -  ]{RESET}
   {CYAN}/|[  ⚙ ⚙  ]|\\{RESET}
  {WHITE}(o)  ====   (o){RESET}
""",
        "sad": rf"""
     {CYAN}.-[ o ]-.{RESET}
    {BLUE}[  ; _ ;  ]{RESET}
   {CYAN}/|[  ⚙ ⚙  ]|\\{RESET}
  {WHITE}(o)  ====   (o){RESET}
""",
        "starving": rf"""
     {RED}.-[ o ]-.{RESET}   {RED}LOW BATT{RESET}
    {RED}[  > _ <  ]{RESET} {RED}! !{RESET}
   {CYAN}/|[  ░ ░  ]|\\{RESET}
  {WHITE}(o)  ====   (o){RESET}
""",
        "dead": rf"""
     {DIM}.-[ x ]-.{RESET}
    {DIM}[  x _ x  ]{RESET}
   {DIM}/|[  R I P ]|\\{RESET}
  {DIM}(o)  ====   (o){RESET}
""",
    },
    "blob": {
        "ecstatic": rf"""
      {CYAN}.-------.{RESET}   {MAGENTA}✨ *bounce!*{RESET}
   {WHITE}\(   ^ ‿ ^   )/{RESET}
   {GREEN}(     \"w\"     ){RESET}
    {DIM}'==========='{RESET}
""",
        "happy": rf"""
      {CYAN}.-------.{RESET}
    {CYAN}(   • ‿ •   ){RESET}  {MAGENTA}~♥{RESET}
   {GREEN}(     \"w\"     ){RESET}
    {DIM}'==========='{RESET}
""",
        "content": rf"""
      {CYAN}.-------.{RESET}
    {CYAN}(   - ‿ -   ){RESET}
   {GREEN}(     \"w\"     ){RESET}
    {DIM}'==========='{RESET}
""",
        "tired": rf"""
      {CYAN}.-------.{RESET}
    {CYAN}(   - . -   ){RESET} {BLUE}zzZ{RESET}
   {GREEN}(     \"w\"     ){RESET}
    {DIM}'-----------'{RESET}
""",
        "sad": rf"""
      {BLUE}.-------.{RESET}
    {BLUE}(   ; _ ;   ){RESET}
   {CYAN}(     \"w\"     ){RESET}
    {DIM}'-----------'{RESET}
""",
        "starving": rf"""
      {RED}.-------.{RESET}
    {RED}(   > _ <   ){RESET} {RED}! !{RESET}
   {CYAN}(     \"w\"     ){RESET}
    {DIM}'-----------'{RESET}
""",
        "dead": rf"""
      {DIM}.-------.{RESET}
    {DIM}(   x _ x   ){RESET}
   {DIM}(    R.I.P    ){RESET}
    {DIM}'-----------'{RESET}
""",
    },
}


def get_art(species: str, mood_name: str) -> str:
    art_map = SPECIES_ART.get(species, SPECIES_ART["dragon"])
    return art_map.get(mood_name, art_map.get("content", ""))


def color_bar(value: float, width: int = 20, is_hunger: bool = False) -> str:
    clamped = max(0.0, min(100.0, value))
    filled = int(round((clamped / 100.0) * width))
    empty = width - filled

    if is_hunger:
        # Hunger: Low is good (green), High is bad (red)
        if clamped <= 35:
            bar_color = GREEN
            status_text = colored("Well Fed", GREEN)
        elif clamped <= 70:
            bar_color = YELLOW
            status_text = colored("Peckish", YELLOW)
        else:
            bar_color = RED
            status_text = colored("Starving!", RED)
    else:
        # Happiness/Energy: High is good (green), Low is bad (red)
        if clamped >= 65:
            bar_color = GREEN
            status_text = colored("Great", GREEN)
        elif clamped >= 30:
            bar_color = YELLOW
            status_text = colored("Okay", YELLOW)
        else:
            bar_color = RED
            status_text = colored("Critical!", RED)

    bar_str = f"{bar_color}{'█' * filled}{DIM}{'░' * empty}{RESET}"
    return f"[{bar_str}] {int(clamped):>3}/100  {status_text}"


def play_frames(frames: list[str], delay: float = 0.22) -> None:
    hide_cursor()
    try:
        for i, frame in enumerate(frames):
            # Clear previous frame or print frame
            sys.stdout.write("\r" + frame)
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write("\n")
        sys.stdout.flush()
    finally:
        show_cursor()


def animate_hatch(name: str, species: str) -> None:
    """Animation when adopting / hatching a new pet."""
    frames = [
        f"\n  {YELLOW}(   ?   ){RESET}\n  {DIM}A mysterious egg appears...{RESET}\n",
        f"\n  {YELLOW}(  /?   ){RESET}\n  {CYAN}*wobble wobble*{RESET}\n",
        f"\n  {YELLOW}(  /*\\  ){RESET}\n  {YELLOW}*CRACK!*{RESET}\n",
        f"\n  {MAGENTA}💥  *POOF!*  💥{RESET}\n  {GREEN}Shell pieces fly everywhere!{RESET}\n",
        f"\n  {YELLOW}✨ \\( ^o^ )/ ✨{RESET}\n  {GREEN}{BOLD}{name} the {species} has hatched into the world!{RESET}\n",
    ]
    print(colored(">>> Hatching in progress...", CYAN))
    for frame in frames:
        sys.stdout.write("\r\033[K" + frame)
        sys.stdout.flush()
        time.sleep(0.35)


def animate_feed(pet_name: str, species: str) -> None:
    """Eating and munching animation."""
    food_emoji = "🥩" if species in ["cat", "dog", "dragon"] else ("⚡" if species == "robot" else "🍬")
    frames = [
        f"  [ {food_emoji} ]  --->  ( •o• )  {pet_name} spots the treat!",
        f"       [ {food_emoji} ]-> ( ^o^ )  *CHOMP!*",
        f"             ( >‿< )  *nom nom nom...*",
        f"        ✨ ( ^‿^ ) ♥  *burp!* So delicious!",
    ]
    is_tty = sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else False
    if not is_tty:
        sys.stdout.write(f"{CYAN}{frames[-1]}{RESET}\n")
        sys.stdout.flush()
        return

    for frame in frames:
        sys.stdout.write(f"\r\033[K{CYAN}{frame}{RESET}")
        sys.stdout.flush()
        time.sleep(0.3)
    sys.stdout.write("\n")


def animate_play(pet_name: str, species: str) -> None:
    """Playing animation with bouncing toy."""
    toy = "🎾" if species in ["cat", "dog"] else ("🔥" if species == "dragon" else ("🎮" if species == "robot" else "🎈"))
    frames = [
        f"  {toy}  . . . . .  ( •‿• )  Get ready, {pet_name}!",
        f"    . . {toy} . . .  ( •o• )  Here it comes!",
        f"  . . . . . {toy} ( ^o^ )/  *CAUGHT IT!*",
        f"  ✨ \\( ^o^ )/ ✨  So much fun! *wheee!*",
    ]
    is_tty = sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else False
    if not is_tty:
        sys.stdout.write(f"{MAGENTA}{frames[-1]}{RESET}\n")
        sys.stdout.flush()
        return

    for frame in frames:
        sys.stdout.write(f"\r\033[K{MAGENTA}{frame}{RESET}")
        sys.stdout.flush()
        time.sleep(0.3)
    sys.stdout.write("\n")


def animate_nap(pet_name: str) -> None:
    """Napping animation with floating Z's."""
    frames = [
        f"  ( -o- )  {pet_name} yawns warmly...",
        f"  ( -.- ) .  z",
        f"  ( -.- ) .. zz",
        f"  ( -.- ) ... zZz  {BLUE}*dreaming happily*{RESET}",
    ]
    is_tty = sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else False
    if not is_tty:
        sys.stdout.write(f"{BLUE}{frames[-1]}{RESET}\n")
        sys.stdout.flush()
        return

    for frame in frames:
        sys.stdout.write(f"\r\033[K{BLUE}{frame}{RESET}")
        sys.stdout.flush()
        time.sleep(0.35)
    sys.stdout.write("\n")


import re
import random

ANSI_REGEX = re.compile(r"\033\[[0-9;]*[a-zA-Z]")


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences to calculate visible string length."""
    return ANSI_REGEX.sub("", text)


def visible_len(text: str) -> int:
    return len(strip_ansi(text))


# Roaming and active sprites for each species
ROAMING_ART: dict[str, dict[str, list[list[str]]]] = {
    "dragon": {
        "walk_right": [
            [
                f"     {YELLOW}▲  _  ▲{RESET}",
                f"    {GREEN}( {CYAN}•{GREEN} ‿ {CYAN}• ){RESET}> {YELLOW}~♨{RESET}",
                f"   {MAGENTA}/({GREEN}=={RED}♥{GREEN}=={MAGENTA})\\{RESET}",
                f"  {MAGENTA}<  {GREEN})   (  {MAGENTA}>{RESET} {YELLOW}~>>{RESET}",
                f"    {GREEN}/   >{RESET}",
            ],
            [
                f"     {YELLOW}▲  _  ▲{RESET}",
                f"    {GREEN}( {CYAN}•{GREEN} ‿ {CYAN}• ){RESET}>  {YELLOW}♨~{RESET}",
                f"   {MAGENTA}/({GREEN}=={RED}♥{GREEN}=={MAGENTA})\\{RESET}",
                f"  {MAGENTA}<  {GREEN})   (  {MAGENTA}>{RESET} {YELLOW}~>>{RESET}",
                f"    {GREEN}<   \\{RESET}",
            ],
        ],
        "walk_left": [
            [
                f"     {YELLOW}▲  _  ▲{RESET}",
                f"  {YELLOW}♨~{RESET}{GREEN}<( {CYAN}•{GREEN} ‿ {CYAN}• ){RESET}",
                f"   {MAGENTA}/({GREEN}=={RED}♥{GREEN}=={MAGENTA})\\{RESET}",
                f"  {YELLOW}<<~{RESET}{MAGENTA}<  {GREEN})   (  {MAGENTA}>{RESET}",
                f"        {GREEN}<   \\{RESET}",
            ],
            [
                f"     {YELLOW}▲  _  ▲{RESET}",
                f"  {YELLOW}~♨{RESET}{GREEN}<( {CYAN}•{GREEN} ‿ {CYAN}• ){RESET}",
                f"   {MAGENTA}/({GREEN}=={RED}♥{GREEN}=={MAGENTA})\\{RESET}",
                f"  {YELLOW}<<~{RESET}{MAGENTA}<  {GREEN})   (  {MAGENTA}>{RESET}",
                f"        {GREEN}/   >{RESET}",
            ],
        ],
        "corner_sit": [
            [
                f"     {YELLOW}▲  _  ▲{RESET}",
                f"    {GREEN}( {CYAN}- ‿ -{GREEN} ){RESET} {MAGENTA}~♥{RESET}",
                f"   {MAGENTA}/({GREEN}=={RED}♥{GREEN}=={MAGENTA})\\{RESET}",
                f"  {GREEN}c(_______)⊃{RESET} {YELLOW}~>>{RESET}",
                f"   {DIM}~~~~~~~~~{RESET}",
            ],
            [
                f"     {YELLOW}▲  _  ▲{RESET}",
                f"    {GREEN}( {CYAN}- . -{GREEN} ){RESET} {BLUE}zzZ{RESET}",
                f"   {MAGENTA}/({GREEN}=={RED}♥{GREEN}=={MAGENTA})\\{RESET}",
                f"  {GREEN}c(_______)⊃{RESET} {YELLOW}~>>{RESET}",
                f"   {DIM}~~~~~~~~~{RESET}",
            ],
        ],
        "dance": [
            [
                f"   {YELLOW}▲  _  ▲{RESET}  {MAGENTA}✨{RESET}",
                f" {GREEN}\\( {CYAN}^ ‿ ^{GREEN} )/{RESET} {YELLOW}♨♨{RESET}",
                f"  {MAGENTA}/({GREEN}=={RED}♥{GREEN}=={MAGENTA})\\{RESET}",
                f" {MAGENTA}<  {GREEN})   (  {MAGENTA}>{RESET} {YELLOW}~>>{RESET}",
                f"   {GREEN}/     \\{RESET}",
            ],
            [
                f"    {YELLOW}▲  _  ▲{RESET} {MAGENTA}*jump!*{RESET}",
                f"  {GREEN}( {CYAN}^ ‿ ^{GREEN} ){RESET} {YELLOW}♨♨{RESET}",
                f"  {MAGENTA}/({GREEN}=={RED}♥{GREEN}=={MAGENTA})\\{RESET}",
                f" {MAGENTA}<  {GREEN})   (  {MAGENTA}>{RESET} {YELLOW}~>>{RESET}",
                f"   {GREEN}<     >{RESET}",
            ],
        ],
    },
    "cat": {
        "walk_right": [
            [
                f"     {YELLOW}/\\_____/\\{RESET}",
                f"    {WHITE}(  =•‿•=  ){RESET}> {MAGENTA}~{RESET}",
                f"    {CYAN}/(  \"w\"  )\\{RESET}",
                f"   {WHITE}(  )     (  ){RESET}{MAGENTA}~{RESET}",
                f"     {DIM}d       b{RESET}",
            ],
            [
                f"     {YELLOW}/\\_____/\\{RESET}",
                f"    {WHITE}(  =•‿•=  ){RESET}>  {MAGENTA}~{RESET}",
                f"    {CYAN}/(  \"w\"  )\\{RESET}",
                f"   {WHITE}(  )     (  ){RESET}{MAGENTA}~{RESET}",
                f"     {DIM}/       >{RESET}",
            ],
        ],
        "walk_left": [
            [
                f"     {YELLOW}/\\_____/\\{RESET}",
                f"  {MAGENTA}~{RESET} <{WHITE}(  =•‿•=  ){RESET}",
                f"    {CYAN}/(  \"w\"  )\\{RESET}",
                f"  {MAGENTA}~{RESET}{WHITE}(  )     (  ){RESET}",
                f"     {DIM}d       b{RESET}",
            ],
            [
                f"     {YELLOW}/\\_____/\\{RESET}",
                f" {MAGENTA}~{RESET}  <{WHITE}(  =•‿•=  ){RESET}",
                f"    {CYAN}/(  \"w\"  )\\{RESET}",
                f"  {MAGENTA}~{RESET}{WHITE}(  )     (  ){RESET}",
                f"     {DIM}<       \\{RESET}",
            ],
        ],
        "corner_sit": [
            [
                f"     {YELLOW}/\\_____/\\{RESET}",
                f"    {WHITE}(  =-‿-=  ){RESET} {MAGENTA}~♥{RESET}",
                f"   {CYAN}c(   \"w\"   )⊃{RESET} {MAGENTA}~{RESET}",
                f"    {DIM}~~~~~~~~~{RESET}",
                f"                 ",
            ],
            [
                f"     {YELLOW}/\\_____/\\{RESET}",
                f"    {WHITE}(  =-.-=  ){RESET} {BLUE}zzZ{RESET}",
                f"   {CYAN}c(   \"w\"   )⊃{RESET} {MAGENTA}~{RESET}",
                f"    {DIM}~~~~~~~~~{RESET}",
                f"                 ",
            ],
        ],
        "dance": [
            [
                f"     {YELLOW}/\\_____/\\{RESET}   {MAGENTA}✨{RESET}",
                f"   {WHITE}\\(  =^‿^=  )/{RESET}",
                f"    {CYAN}/(  \"w\"  )\\{RESET}",
                f"   {WHITE}(  )     (  ){RESET}{MAGENTA}~{RESET}",
                f"     {DIM}d       b{RESET}",
            ],
            [
                f"     {YELLOW}/\\_____/\\{RESET}  {MAGENTA}*jump!*{RESET}",
                f"    {WHITE}(  =^‿^=  ){RESET}",
                f"    {CYAN}/(  \"w\"  )\\{RESET}",
                f"   {WHITE}(  )     (  ){RESET}{MAGENTA}~{RESET}",
                f"     {DIM}<       >{RESET}",
            ],
        ],
    },
    "dog": {
        "walk_right": [
            [
                f"     {YELLOW}/ᐢ_____ᐢ\\{RESET}",
                f"    {WHITE}(   •‿•   ){RESET}> {GREEN}*wag*{RESET}",
                f"    {CYAN}/(  \"U\"  )\\{RESET}  {GREEN}~{RESET}",
                f"   {WHITE}(  )     (  ){RESET}",
                f"     {DIM}d       b{RESET}",
            ],
            [
                f"     {YELLOW}/ᐢ_____ᐢ\\{RESET}",
                f"    {WHITE}(   •‿•   ){RESET}>  {GREEN}*wag*{RESET}",
                f"    {CYAN}/(  \"U\"  )\\{RESET} {GREEN}~{RESET}",
                f"   {WHITE}(  )     (  ){RESET}",
                f"     {DIM}/       >{RESET}",
            ],
        ],
        "walk_left": [
            [
                f"     {YELLOW}/ᐢ_____ᐢ\\{RESET}",
                f" {GREEN}*wag*{RESET}<{WHITE}(   •‿•   ){RESET}",
                f"    {CYAN}/(  \"U\"  )\\{RESET}  {GREEN}~{RESET}",
                f"   {WHITE}(  )     (  ){RESET}",
                f"     {DIM}d       b{RESET}",
            ],
            [
                f"     {YELLOW}/ᐢ_____ᐢ\\{RESET}",
                f"  {GREEN}*wag*{RESET}<{WHITE}(   •‿•   ){RESET}",
                f"    {CYAN}/(  \"U\"  )\\{RESET} {GREEN}~{RESET}",
                f"   {WHITE}(  )     (  ){RESET}",
                f"     {DIM}<       \\{RESET}",
            ],
        ],
        "corner_sit": [
            [
                f"     {YELLOW}/ᐢ_____ᐢ\\{RESET}",
                f"    {WHITE}(   -‿-   ){RESET} {MAGENTA}~♥{RESET}",
                f"   {CYAN}c(   \"U\"   )⊃{RESET} {GREEN}*thump*{RESET}",
                f"    {DIM}~~~~~~~~~{RESET}",
                f"                 ",
            ],
            [
                f"     {YELLOW}/ᐢ_____ᐢ\\{RESET}",
                f"    {WHITE}(   -.-   ){RESET} {BLUE}zzZ{RESET}",
                f"   {CYAN}c(   \"U\"   )⊃{RESET}",
                f"    {DIM}~~~~~~~~~{RESET}",
                f"                 ",
            ],
        ],
        "dance": [
            [
                f"     {YELLOW}/ᐢ_____ᐢ\\{RESET}   {MAGENTA}✨{RESET}",
                f"   {WHITE}\\(   ^‿^   )/{RESET}",
                f"    {CYAN}/(  \"U\"  )\\{RESET}  {GREEN}~{RESET}",
                f"   {WHITE}(  )     (  ){RESET}",
                f"     {DIM}d       b{RESET}",
            ],
            [
                f"     {YELLOW}/ᐢ_____ᐢ\\{RESET}  {MAGENTA}*jump!*{RESET}",
                f"    {WHITE}(   ^‿^   ){RESET}  {GREEN}*wag*{RESET}",
                f"    {CYAN}/(  \"U\"  )\\{RESET}",
                f"   {WHITE}(  )     (  ){RESET}",
                f"     {DIM}<       >{RESET}",
            ],
        ],
    },
    "robot": {
        "walk_right": [
            [
                f"     {CYAN}.-[ o ]-.{RESET}   {YELLOW}⚡{RESET}",
                f"    {WHITE}[  • ‿ •  ]{RESET}>",
                f"   {CYAN}/|[  ⚙ ⚙  ] \\{RESET}",
                f"  {WHITE}(o)  ====   (o){RESET} {DIM}===>{RESET}",
                f"                 ",
            ],
            [
                f"     {CYAN}.-[ o ]-.{RESET}    {YELLOW}⚡{RESET}",
                f"    {WHITE}[  • ‿ •  ]{RESET}>",
                f"   {CYAN}/|[  ⚙ ⚙  ] \\{RESET}",
                f"   {WHITE}(o)======(o){RESET}  {DIM}===>{RESET}",
                f"                 ",
            ],
        ],
        "walk_left": [
            [
                f"     {CYAN}.-[ o ]-.{RESET}   {YELLOW}⚡{RESET}",
                f"   <{WHITE}[  • ‿ •  ]{RESET}",
                f"   {CYAN}/ [  ⚙ ⚙  ]|\\{RESET}",
                f" {DIM}<==={RESET}{WHITE}(o)  ====   (o){RESET}",
                f"                 ",
            ],
            [
                f"     {CYAN}.-[ o ]-.{RESET}    {YELLOW}⚡{RESET}",
                f"   <{WHITE}[  • ‿ •  ]{RESET}",
                f"   {CYAN}/ [  ⚙ ⚙  ]|\\{RESET}",
                f" {DIM}<==={RESET} {WHITE}(o)======(o){RESET}",
                f"                 ",
            ],
        ],
        "corner_sit": [
            [
                f"     {CYAN}.-[ o ]-.{RESET}  {YELLOW}[CHARGING]{RESET}",
                f"    {WHITE}[  - ‿ -  ]{RESET} {YELLOW}⚡{RESET}",
                f"   {CYAN}/|[  ⚙ ⚙  ]|\\{RESET} {DIM}[==🔌]{RESET}",
                f"  {WHITE}(o)  ====   (o){RESET}",
                f"   {DIM}~~~~~~~~~~~~~{RESET}",
            ],
            [
                f"     {CYAN}.-[ o ]-.{RESET}  {GREEN}[100% READY]{RESET}",
                f"    {WHITE}[  • ‿ •  ]{RESET} {CYAN}✨{RESET}",
                f"   {CYAN}/|[  ⚙ ⚙  ]|\\{RESET} {DIM}[==🔌]{RESET}",
                f"  {WHITE}(o)  ====   (o){RESET}",
                f"   {DIM}~~~~~~~~~~~~~{RESET}",
            ],
        ],
        "dance": [
            [
                f"     {CYAN}.-[ o ]-.{RESET}   {YELLOW}⚡ *BEEP!*{RESET}",
                f"   {WHITE}\\[  ^ ‿ ^  ]/{RESET} {CYAN}✨{RESET}",
                f"   {CYAN}/|[  ⚙ ⚙  ]|\\{RESET}",
                f"  {WHITE}(o)  ====   (o){RESET}",
                f"                 ",
            ],
            [
                f"     {CYAN}.-[ o ]-.{RESET}   {CYAN}*WHIR!*{RESET}",
                f"    {WHITE}[  ^ ‿ ^  ]{RESET}",
                f"   {CYAN}/|[  ⚙ ⚙  ]|\\{RESET}",
                f"  {WHITE}<o>  ====   <o>{RESET}",
                f"                 ",
            ],
        ],
    },
    "blob": {
        "walk_right": [
            [
                f"      {CYAN}.-------.{RESET}",
                f"    {CYAN}(   • ‿ •   ){RESET}>",
                f"   {GREEN}(     \"w\"     ){RESET}",
                f"    {DIM}'==========='{RESET}",
                f"                 ",
            ],
            [
                f"      {CYAN}.-------.{RESET}",
                f"    {CYAN}(   • ‿ •   ){RESET}> {MAGENTA}~♥{RESET}",
                f"   {GREEN}(     \"w\"     ){RESET}",
                f"    {DIM}'~~~~~~~~~~~'{RESET}",
                f"                 ",
            ],
        ],
        "walk_left": [
            [
                f"      {CYAN}.-------.{RESET}",
                f"   <{CYAN}(   • ‿ •   ){RESET}",
                f"   {GREEN}(     \"w\"     ){RESET}",
                f"    {DIM}'==========='{RESET}",
                f"                 ",
            ],
            [
                f"      {CYAN}.-------.{RESET}",
                f" {MAGENTA}♥~{RESET}<{CYAN}(   • ‿ •   ){RESET}",
                f"   {GREEN}(     \"w\"     ){RESET}",
                f"    {DIM}'~~~~~~~~~~~'{RESET}",
                f"                 ",
            ],
        ],
        "corner_sit": [
            [
                f"      {CYAN}.-------.{RESET}",
                f"    {CYAN}(   - ‿ -   ){RESET} {MAGENTA}~♥{RESET}",
                f"   {GREEN}(     \"w\"     ){RESET}",
                f"    {DIM}'-----------'{RESET}",
                f"                 ",
            ],
            [
                f"      {CYAN}.-------.{RESET}",
                f"    {CYAN}(   - . -   ){RESET} {BLUE}zzZ{RESET}",
                f"   {GREEN}(     \"w\"     ){RESET}",
                f"    {DIM}'-----------'{RESET}",
                f"                 ",
            ],
        ],
        "dance": [
            [
                f"      {CYAN}.-------.{RESET}   {MAGENTA}✨ *bounce!*{RESET}",
                f"   {WHITE}\\(   ^ ‿ ^   )/{RESET}",
                f"   {GREEN}(     \"w\"     ){RESET}",
                f"    {DIM}'==========='{RESET}",
                f"                 ",
            ],
            [
                f"      {CYAN}.-------.{RESET}  {MAGENTA}*squish!*{RESET}",
                f"    {CYAN}(   ^ ‿ ^   ){RESET}",
                f"   {GREEN}(    ~~~~~    ){RESET}",
                f"    {DIM}'==========='{RESET}",
                f"                 ",
            ],
        ],
    },
}


def get_roam_sprite(species: str, state_name: str, frame_idx: int) -> list[str]:
    species_data = ROAMING_ART.get(species, ROAMING_ART["dragon"])
    frames = species_data.get(state_name, species_data.get("walk_right", []))
    if not frames:
        return ["", "", "", ""]
    return frames[frame_idx % len(frames)]


def get_dynamic_status_pose(species: str, mood_name: str) -> tuple[str, str]:
    """Return a dynamic ASCII art pose and flavor narrative for pet status."""
    if mood_name in ["dead", "starving"]:
        return get_art(species, mood_name), "Needs immediate attention!"

    choice = random.choice(["roam_right", "roam_left", "corner", "greeting"])
    sp_data = ROAMING_ART.get(species, ROAMING_ART["dragon"])

    if choice == "corner" or mood_name in ["tired", "sad"]:
        lines = sp_data["corner_sit"][0]
        art = "\n" + "\n".join("  " + l for l in lines) + "\n"
        narrative = "🛋️  Found curled up comfortably in the corner of your terminal."
        return art, narrative
    elif choice == "roam_right":
        lines = sp_data["walk_right"][0]
        art = "\n" + "\n".join("    " + l for l in lines) + "\n"
        narrative = "🐾  Was actively exploring and trotting across your terminal prompt!"
        return art, narrative
    elif choice == "roam_left":
        lines = sp_data["walk_left"][0]
        art = "\n" + "\n".join("    " + l for l in lines) + "\n"
        narrative = "🐾  Was wandering across your command line sniffing around!"
        return art, narrative
    else:
        art = get_art(species, mood_name)
        narrative = "✨  Saw you open the terminal and rushed over to greet you!"
        return art, narrative


def render_room_box(
    pet_name: str,
    species: str,
    level: int,
    xp: int,
    mood_name: str,
    hunger: float,
    happiness: float,
    energy: float,
    sprite_lines: list[str],
    offset: int,
    activity_msg: str,
    room_width: int = 68,
) -> str:
    """Render the pet playground box with roaming pet at horizontal offset."""
    inner_width = room_width - 2
    border_top = f"{CYAN}┌{'─' * inner_width}┐{RESET}"
    border_mid = f"{CYAN}├{'─' * inner_width}┤{RESET}"
    border_bot = f"{CYAN}└{'─' * inner_width}┘{RESET}"

    # Header line
    xp_needed = level * 100
    header_str = f" {BOLD}{pet_name}{RESET} the {species}  |  {GREEN}Level {level}{RESET} (XP: {xp}/{xp_needed})  |  Feeling: {BOLD}{mood_name}{RESET}"
    header_pad = inner_width - visible_len(header_str)
    header_line = f"{CYAN}│{RESET}{header_str}{' ' * max(0, header_pad)}{CYAN}│{RESET}"

    # Stat bar line (compact)
    h_bar = f"{color_bar(hunger, width=8, is_hunger=True)}"
    hap_bar = f"{color_bar(happiness, width=8, is_hunger=False)}"
    stats_str = f" Hunger: {h_bar}  Happy: {hap_bar}"
    stats_pad = inner_width - visible_len(stats_str)
    stats_line = f"{CYAN}│{RESET}{stats_str}{' ' * max(0, stats_pad)}{CYAN}│{RESET}"

    # Room sky / field
    room_lines = []
    room_lines.append(f"{CYAN}│{RESET}{' ' * inner_width}{CYAN}│{RESET}")

    # Render pet sprite lines with offset
    for raw_line in sprite_lines:
        v_len = visible_len(raw_line)
        clamped_offset = max(1, min(offset, inner_width - v_len - 1))
        pad_left = " " * clamped_offset
        pad_right = " " * max(0, inner_width - clamped_offset - v_len)
        room_lines.append(f"{CYAN}│{RESET}{pad_left}{raw_line}{pad_right}{CYAN}│{RESET}")

    # Ground terrain line
    terrain_pattern = "^ . ~ ~ . ^ ~ ~ ~ . ^ ~ ~ . ^ ~ ~ . ^ ~ ~ . ^ ~ ~ . ^ ~ ~ . ^ ~ ~ . ^ ~ ~ . ^ "
    terrain = terrain_pattern[:inner_width]
    ground_line = f"{CYAN}│{DIM}{GREEN}{terrain}{RESET}{CYAN}│{RESET}"
    room_lines.append(ground_line)

    # Activity message line
    act_str = f" {activity_msg}"
    act_pad = inner_width - visible_len(act_str)
    act_line = f"{CYAN}│{RESET}{act_str}{' ' * max(0, act_pad)}{CYAN}│{RESET}"

    # Controls line
    ctrl_str = f" {BOLD}Controls:{RESET}  [{GREEN}F{RESET}]eed  [{MAGENTA}P{RESET}]lay  [{BLUE}N{RESET}]ap  [{YELLOW}C{RESET}]orner Sit  [{CYAN}R{RESET}]oam  [{WHITE}Q{RESET}]uit"
    ctrl_pad = inner_width - visible_len(ctrl_str)
    ctrl_line = f"{CYAN}│{RESET}{ctrl_str}{' ' * max(0, ctrl_pad)}{CYAN}│{RESET}"

    output = [
        border_top,
        header_line,
        stats_line,
        border_mid,
        *room_lines,
        border_mid,
        act_line,
        ctrl_line,
        border_bot,
    ]
    return "\n".join(output)
