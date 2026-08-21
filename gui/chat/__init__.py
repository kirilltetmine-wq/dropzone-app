"""
gui.chat — multi-platform chat system with merged view and individual channels.
Extensible: add new platforms via platform_registry without changing logic.
"""

from .platform_registry import (
    PlatformInfo, PLATFORM_REGISTRY, get_platform, register_platform,
    YOUTUBE_PATH, TWITCH_PATH, PLATFORM_PURPLE, PLATFORM_RED,
)
from .chat_manager import ChatManager, ChatConnection
from .chat_sidebar import ChatSidebar, ChatListDropdown