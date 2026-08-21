"""
chat_manager.py — central multi-platform chat manager.
Manages connections, assigns numbers, routes messages.
"""

import uuid
from dataclasses import dataclass, field
from typing import Optional, Callable

from .platform_registry import PlatformInfo, get_platform


@dataclass
class ChatConnection:
    """A single chat connection (platform + channel + bot)."""
    connection_id: str
    platform: str
    channel: str
    bot: object
    platform_info: PlatformInfo
    number: int = 0          # Assigned number (1, 2, 3... per platform)
    chat_id: str = ""        # YouTube chat_id, etc.


MAX_CACHE = 200  # max messages cached per connection


class ChatManager:
    """Manages all chat connections, provides merged and individual views."""

    def __init__(self):
        self.connections: list[ChatConnection] = []
        self._current_view: str = "main"   # "main" or connection_id
        self._number_counters: dict[str, int] = {}  # platform -> next number
        self._on_connection_added: Optional[Callable] = None
        self._on_connection_removed: Optional[Callable] = None
        self._on_view_changed: Optional[Callable[[str], None]] = None
        self._message_cache: dict[str, list[dict]] = {}  # connection_id -> messages

    # ── signals ──────────────────────────────────────

    def set_on_connection_added(self, callback: Callable):
        self._on_connection_added = callback

    def set_on_connection_removed(self, callback: Callable):
        self._on_connection_removed = callback

    def set_on_view_changed(self, callback: Callable[[str], None]):
        self._on_view_changed = callback

    # ── connection management ────────────────────────

    def add_connection(self, platform: str, channel: str, bot: object,
                       chat_id: str = "") -> ChatConnection:
        """Add a new connection. Returns the created ChatConnection."""
        info = get_platform(platform)
        if not info:
            raise ValueError(f"Unknown platform: {platform}")

        conn_id = str(uuid.uuid4())[:8]
        number = self._next_number(platform)

        conn = ChatConnection(
            connection_id=conn_id,
            platform=platform,
            channel=channel,
            bot=bot,
            platform_info=info,
            number=number,
            chat_id=chat_id,
        )
        self.connections.append(conn)

        if self._on_connection_added:
            self._on_connection_added(conn)

        return conn

    def remove_connection(self, connection_id: str):
        """Remove a connection by ID."""
        for conn in self.connections:
            if conn.connection_id == connection_id:
                self.connections.remove(conn)
                if self._current_view == connection_id:
                    self._current_view = "main"
                if self._on_connection_removed:
                    self._on_connection_removed(conn)
                return True
        return False

    def get_connection(self, connection_id: str) -> Optional[ChatConnection]:
        for conn in self.connections:
            if conn.connection_id == connection_id:
                return conn
        return None

    def has_connections(self) -> bool:
        return len(self.connections) > 0

    def clear_all(self):
        for conn in list(self.connections):
            self.connections.remove(conn)
        self._number_counters.clear()
        if self._on_connection_removed:
            self._on_connection_removed(None)  # Signal rebuild

    # ── view management ──────────────────────────────

    @property
    def current_view(self) -> str:
        return self._current_view

    def set_view(self, view_id: str):
        """Set current view: 'main' for merged, or connection_id for individual."""
        self._current_view = view_id
        if self._on_view_changed:
            self._on_view_changed(view_id)

    def is_main_view(self) -> bool:
        return self._current_view == "main"

    def get_active_connections_for_view(self) -> list[ChatConnection]:
        """Get connections relevant to the current view."""
        if self._current_view == "main":
            return list(self.connections)
        conn = self.get_connection(self._current_view)
        return [conn] if conn else []

    # ── message routing ──────────────────────────────

    def poll_all_messages(self) -> list[dict]:
        """Poll all bots and return merged message list.
        Each message dict has: author, text, platform, connection_id, number,
        platform_info, badges, is_mod, channel_id.
        Returns messages for current view only.
        """
        active = self.get_active_connections_for_view()
        result = []

        for conn in active:
            try:
                messages = self._drain_bot(conn)
                # Cache messages per connection (trim to MAX_CACHE)
                if conn.connection_id not in self._message_cache:
                    self._message_cache[conn.connection_id] = []
                cache = self._message_cache[conn.connection_id]
                cache.extend(messages)
                if len(cache) > MAX_CACHE:
                    self._message_cache[conn.connection_id] = cache[-MAX_CACHE:]

                for msg in messages:
                    msg["platform"] = conn.platform
                    msg["connection_id"] = conn.connection_id
                    msg["number"] = conn.number
                    msg["platform_info"] = conn.platform_info
                    result.append(msg)
            except Exception:
                pass

        return result

    def get_cached_messages(self, connection_id: str = "") -> list[dict]:
        """Get cached messages. Empty string = all connections (main view)."""
        if not connection_id:
            # Main view — merge all caches
            merged = []
            for cid in self._message_cache:
                merged.extend(self._message_cache[cid])
            return merged
        return list(self._message_cache.get(connection_id, []))

    def _drain_bot(self, conn: ChatConnection) -> list[dict]:
        """Drain message queue from a single bot. Returns list of message dicts."""
        bot = conn.bot
        if bot is None:
            return []

        if conn.platform == "twitch":
            if not getattr(bot, 'is_running', False):
                return []
            try:
                with bot._queue_lock:
                    messages = bot._message_queue.copy()
                    bot._message_queue.clear()
                return [
                    {
                        "author": m["author"],
                        "text": m["text"],
                        "badges": [],
                        "is_mod": m.get("is_mod", False),
                        "channel_id": conn.channel,
                        "user_id": m.get("user_id", ""),
                        "msg_id": m.get("msg_id", ""),
                    }
                    for m in messages
                ]
            except Exception:
                return []

        elif conn.platform == "youtube":
            if not getattr(bot, 'live_chat_id', None):
                return []
            try:
                messages = bot.get_display_messages()
                return [
                    {
                        "author": m["author"],
                        "text": m["text"],
                        "badges": [],
                        "is_mod": m.get("is_mod", False),
                        "channel_id": m.get("channel_id", ""),
                        "user_id": "",
                        "msg_id": "",
                    }
                    for m in messages
                ]
            except Exception:
                return []

        return []

    # ── sending ──────────────────────────────────────

    def send_message(self, text: str, target: str = "current"):
        """Send a message. target='all' sends to all, 'current' sends to current view."""
        if target == "all" or (target == "current" and self._current_view == "main"):
            # Send to all connections
            for conn in self.connections:
                self._send_to_connection(conn, text)
        elif target == "current":
            conn = self.get_connection(self._current_view)
            if conn:
                self._send_to_connection(conn, text)

    def _send_to_connection(self, conn: ChatConnection, text: str):
        """Send a message to a single connection's bot."""
        bot = conn.bot
        if bot and hasattr(bot, 'send_message'):
            try:
                bot.send_message(text)
            except Exception:
                pass

    # ── numbering ────────────────────────────────────

    def _next_number(self, platform: str) -> int:
        if platform not in self._number_counters:
            self._number_counters[platform] = 0
        self._number_counters[platform] += 1
        return self._number_counters[platform]

    def _reassign_numbers(self):
        """Reassign numbers after removals to keep sequential."""
        self._number_counters.clear()
        for conn in self.connections:
            conn.number = self._next_number(conn.platform)