"""
platform_registry.py — extensible platform definitions.
Add new platforms by calling register_platform() with a PlatformInfo.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

APP_DIR = Path(__file__).resolve().parent.parent.parent
RESOURCES = APP_DIR / "resources"

YOUTUBE_PATH = RESOURCES / "youtube.svg"
TWITCH_PATH = RESOURCES / "twitch.svg"
KICK_PATH = RESOURCES / "kick.svg"

PLATFORM_RED = "#FF0000"
PLATFORM_PURPLE = "#9146FF"


@dataclass
class PlatformInfo:
    key: str                          # "youtube", "twitch", "kick"
    display_name: str                 # "YouTube", "Twitch", "Kick"
    icon_path: Path                   # SVG icon path
    color: str                        # Main brand color
    number_color: str                 # Color for message number badges
    message_color: str               # Color for message author name

    def __hash__(self):
        return hash(self.key)


# Built-in platforms
PLATFORM_REGISTRY: dict[str, PlatformInfo] = {
    "youtube": PlatformInfo(
        key="youtube",
        display_name="YouTube",
        icon_path=YOUTUBE_PATH,
        color=PLATFORM_RED,
        number_color=PLATFORM_RED,
        message_color=PLATFORM_RED,
    ),
    "twitch": PlatformInfo(
        key="twitch",
        display_name="Twitch",
        icon_path=TWITCH_PATH,
        color=PLATFORM_PURPLE,
        number_color=PLATFORM_PURPLE,
        message_color=PLATFORM_PURPLE,
    ),
    "kick": PlatformInfo(
        key="kick",
        display_name="Kick",
        icon_path=KICK_PATH,
        color="#53FC18",
        number_color="#53FC18",
        message_color="#53FC18",
    ),
}


def get_platform(key: str) -> Optional[PlatformInfo]:
    """Get platform info by key. Returns None if not found."""
    return PLATFORM_REGISTRY.get(key)


def register_platform(info: PlatformInfo):
    """Register a new platform. Call this at startup for custom platforms."""
    PLATFORM_REGISTRY[info.key] = info