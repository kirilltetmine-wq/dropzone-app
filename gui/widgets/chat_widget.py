import os

import re

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QFrame, QScrollArea, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect, QApplication, QDialog,
)

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QSize, QRectF, QPropertyAnimation, QEasingCurve, QEvent

from PyQt6.QtGui import (

    QFont, QColor, QPainter, QPen, QBrush, QIcon, QPixmap,

    QFontMetrics, QPainterPath

)

BG_COLOR = "#0A0A0B"

CARD_COLOR = "#141416"

CARD_LIGHT = "#1C1C1E"

BORDER_COLOR = "#232326"

TEXT_MAIN = "#FFFFFF"

TEXT_SEC = "#8E8E93"

ACCENT_CYAN = "#00F5FF"

ACCENT_LIME = "#CCFF00"

DANGER_COLOR = "#FF3B30"

SUCCESS_COLOR = "#34C759"

ORANGE = "#FF9500"

PURPLE = "#AF52DE"

FONT_FAMILY = "Segoe UI"

APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESOURCES = os.path.join(APP_DIR, "resources")

ICON_TWITCH = os.path.join(RESOURCES, "twitch.svg")
ICON_YOUTUBE = os.path.join(RESOURCES, "youtube.svg")
ICON_KICK = os.path.join(RESOURCES, "kick.svg")

ICON_TWITCH_BLACK = os.path.join(RESOURCES, "twitch_black.svg")

ICON_YOUTUBE_BLACK = os.path.join(RESOURCES, "youtube_black.svg")

ICON_KICK_BLACK = os.path.join(RESOURCES, "kick_black.svg")

ICON_SHIELD = os.path.join(RESOURCES, "shield.svg")

ICON_SEARCH = os.path.join(RESOURCES, "search.svg")

ICON_ARROW_UP = os.path.join(RESOURCES, "arrow-up.svg")

ICON_ARROW_DOWN = os.path.join(RESOURCES, "arrow-down.svg")

ICON_CLOSE = os.path.join(RESOURCES, "krestik.svg")

class PlatformIcon(QLabel):

    def __init__(self, icon_path, parent=None):

        super().__init__(parent)

        self._pixmap = QPixmap(icon_path).scaled(14, 14, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.setPixmap(self._pixmap)

        self.setFixedSize(14, 14)

class BadgeLabel(QLabel):

    COLORS = {

        "MOD": (ACCENT_CYAN, BG_COLOR),

        "VIP": (PURPLE, TEXT_MAIN),

        "SUB": (ACCENT_LIME, BG_COLOR),

    }

    def __init__(self, text, parent=None):

        super().__init__(text, parent)

        bg, fg = self.COLORS.get(text, (TEXT_SEC, BG_COLOR))

        self.setStyleSheet(f"""

            background-color: {bg}; color: {fg};

            font-size: 9px; font-weight: 700; padding: 1px 4px;

            border-radius: 4px; text-transform: uppercase; letter-spacing: 0.5px;

        """)

        self.setFixedHeight(16)

HIGHLIGHT_BG = "#CCFF00"
HIGHLIGHT_FG = "#000000"

class MessageRow(QFrame):

    moderation_requested = pyqtSignal(object, object)  # (self, global_pos: QPoint)

    def __init__(self, author, text, color, platform_icon_path, timestamp,
                 badges=None, is_entry=False, is_mod=False, number=0,
                 number_color="#8E8E93", connection_id="", platform="",
                 user_identifier="", msg_id="", parent=None):

        super().__init__(parent)

        self._is_entry = is_entry
        self._original_text = text
        self._author_name = author
        self._author_color = ACCENT_CYAN if is_mod else color
        self._is_mod = is_mod
        self._connection_id = connection_id
        self._platform = platform
        self._user_identifier = user_identifier
        self._msg_id = msg_id
        self._can_moderate = bool(connection_id and platform)

        if is_entry:

            self.setStyleSheet(f"""
                QFrame {{
                    background: rgba(204,255,0,10);
                    border-left: 2px solid {ACCENT_LIME};
                    border-radius: 0;
                }}
            """)

            layout = QHBoxLayout(self)

            layout.setContentsMargins(12, 6, 14, 6)

            layout.setSpacing(8)

        else:

            self.setStyleSheet("QFrame { background: transparent; border: none; border-radius: 0; }")

            layout = QHBoxLayout(self)

            layout.setContentsMargins(14, 6, 14, 6)

            layout.setSpacing(8)

        # Number badge (circle) — before platform icon
        if number > 0:
            num_badge = QLabel(str(number))
            num_badge.setFixedSize(20, 20)
            num_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            num_badge.setStyleSheet(f"""
                background-color: {number_color};
                color: #FFFFFF;
                font-size: 10px;
                font-weight: 800;
                border-radius: 10px;
            """)
            layout.addWidget(num_badge)

        icon = PlatformIcon(platform_icon_path)

        layout.addWidget(icon)

        time_lbl = QLabel(timestamp)

        time_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; background: transparent; font-variant-numeric: tabular-nums;")

        layout.addWidget(time_lbl)

        if badges:

            for badge_text in badges:

                badge = BadgeLabel(badge_text)

                layout.addWidget(badge)

        content = QWidget()

        content.setStyleSheet("background: transparent;")

        clayout = QHBoxLayout(content)

        clayout.setContentsMargins(0, 0, 0, 0)

        clayout.setSpacing(0)

        self._author_lbl = QLabel(author)

        self._author_lbl.setStyleSheet(f"color: {self._author_color}; font-weight: 700; font-size: 12px; background: transparent; margin-right: 4px;")
        self._author_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        self._author_lbl.installEventFilter(self)

        clayout.addWidget(self._author_lbl)

        if is_mod:

            shield = QLabel()

            shield_pix = QPixmap(ICON_SHIELD).scaled(14, 14, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            shield.setPixmap(shield_pix)

            shield.setFixedSize(14, 14)

            clayout.addWidget(shield)

        colon = QLabel(":")

        colon.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; background: transparent; margin-right: 4px;")

        clayout.addWidget(colon)

        self._text_lbl = QLabel()

        self._text_lbl.setWordWrap(True)

        self._text_lbl.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 12px; background: transparent;")

        self._text_lbl.setTextFormat(Qt.TextFormat.RichText)

        self._render_text(text)

        clayout.addWidget(self._text_lbl, 1)

        layout.addWidget(content, 1)

        self._opacity_effect = QGraphicsOpacityEffect()

        self._opacity_effect.setOpacity(0.0)

        self.setGraphicsEffect(self._opacity_effect)

        self._anim_opacity = QPropertyAnimation(self._opacity_effect, b"opacity", self)

        self._anim_opacity.setDuration(200)

        self._anim_opacity.setStartValue(0.0)

        self._anim_opacity.setEndValue(1.0)

        self._anim_opacity.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._anim_opacity.start()

    def _render_text(self, text, search_term=None):

        html = re.sub(
            r'(!\w+)',
            rf'<span style="color: {ACCENT_LIME}; font-weight: 700;">\1</span>',
            text
        )
        if search_term:
            html = re.sub(
                re.escape(search_term),
                rf'<span style="background-color: {HIGHLIGHT_BG}; color: {HIGHLIGHT_FG}; font-weight: 700;">\g<0></span>',
                html,
                flags=re.IGNORECASE
            )
        self._text_lbl.setText(html)

    def apply_search(self, search_term, is_user_search):
        if is_user_search:
            if search_term.lower() in self._author_name.lower():
                self._author_lbl.setStyleSheet(
                    f"color: {self._author_color}; font-weight: 700; font-size: 12px;"
                    f" background-color: {HIGHLIGHT_BG}; color: {HIGHLIGHT_FG};"
                    f" margin-right: 4px; border-radius: 2px; padding: 0 2px;"
                )
                return True
            return False
        if search_term.lower() in self._original_text.lower():
            self._render_text(self._original_text, search_term)
            return True
        return False

    def clear_search(self):
        self._author_lbl.setStyleSheet(
            f"color: {self._author_color}; font-weight: 700; font-size: 12px;"
            f" background: transparent; margin-right: 4px;"
        )
        self._render_text(self._original_text)

    def enterEvent(self, event):

        if not self._is_entry:

            self.setStyleSheet("QFrame { background: rgba(255,255,255,5); border: none; border-radius: 0; }")

        super().enterEvent(event)

    def leaveEvent(self, event):

        if self._is_entry:

            self.setStyleSheet(f"""

                QFrame {{

                    background: rgba(204,255,0,10);

                    border-left: 2px solid {ACCENT_LIME};

                    border-radius: 0;

                }}

            """)

        else:

            self.setStyleSheet("QFrame { background: transparent; border: none; border-radius: 0; }")

        super().leaveEvent(event)

    def eventFilter(self, obj, event):
        """Handle hover outline and right-click on the author label."""
        if obj is self._author_lbl:
            if event.type() == QEvent.Type.Enter:
                if self._can_moderate and not self._is_entry:
                    self._author_lbl.setStyleSheet(
                        f"color: {self._author_color}; font-weight: 700; font-size: 12px;"
                        f" background: rgba(255,255,255,20);"
                        f" margin-right: 4px; border-radius: 3px; padding: 0 2px;"
                    )
                return False
            elif event.type() == QEvent.Type.Leave:
                self._author_lbl.setStyleSheet(
                    f"color: {self._author_color}; font-weight: 700; font-size: 12px;"
                    f" background: transparent; margin-right: 4px;"
                )
                return False
            elif event.type() == QEvent.Type.MouseButtonPress:
                if (event.button() == Qt.MouseButton.RightButton
                        and self._can_moderate and not self._is_entry):
                    self.moderation_requested.emit(self, event.globalPosition().toPoint())
                    return True
        return super().eventFilter(obj, event)

class SystemMessage(QFrame):

    def __init__(self, tag, text, tag_color, parent=None):

        super().__init__(parent)

        self.setStyleSheet(f"""

            QFrame {{

                background: rgba(255,255,255,5);

                border-radius: 8px;

            }}

        """)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(12, 6, 12, 6)

        layout.setSpacing(6)

        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tag_lbl = QLabel(f"[{tag}]")

        tag_lbl.setStyleSheet(f"color: {tag_color}; font-weight: 700; font-size: 11px; background: transparent;")

        layout.addWidget(tag_lbl)

        text_lbl = QLabel(text)

        text_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; background: transparent;")

        layout.addWidget(text_lbl)

class SplitSendButton(QFrame):

    platform_changed = pyqtSignal(str, str)

    PLATFORMS = [
        {"id": "twitch", "name": "Twitch", "icon": ICON_TWITCH_BLACK},
        {"id": "youtube", "name": "YouTube", "icon": ICON_YOUTUBE_BLACK},
        {"id": "kick", "name": "Kick", "icon": ICON_KICK_BLACK},
    ]

    def __init__(self, parent=None):

        super().__init__(parent)

        self._current = self.PLATFORMS[0]

        self._dropdown = None

        self.setFixedHeight(40)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(2, 2, 2, 2)

        layout.setSpacing(0)

        self._btn_main = QPushButton()

        self._btn_main.setCursor(Qt.CursorShape.PointingHandCursor)

        self._btn_main.setStyleSheet(f"""

            QPushButton {{

                background: transparent; color: {BG_COLOR};

                border: none; border-radius: 18px;

                padding: 8px 14px 8px 16px;

                font-size: 12px; font-weight: 700;

                text-transform: uppercase; letter-spacing: 0.5px;

                font-family: '{FONT_FAMILY}', sans-serif;

            }}

            QPushButton:hover {{  background: rgba(0,0,0,20); }}

        """)

        self._update_main_button()

        layout.addWidget(self._btn_main)

        self._btn_arrow = QPushButton("\u25BE")

        self._btn_arrow.setCursor(Qt.CursorShape.PointingHandCursor)

        self._btn_arrow.setStyleSheet(f"""

            QPushButton {{

                background: transparent; color: {BG_COLOR};

                border: none; border-radius: 0 9999px 9999px 0;

                padding: 8px 10px; font-size: 10px;

                font-family: '{FONT_FAMILY}', sans-serif;

            }}

            QPushButton:hover {{  background: rgba(0,0,0,20); }}

        """)

        self._btn_arrow.clicked.connect(self._toggle_dropdown)

        layout.addWidget(self._btn_arrow)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()

        r = self.rect()

        radius = min(r.width(), r.height()) // 2

        path.addRoundedRect(QRectF(r), radius, radius)

        painter.setClipPath(path)

        painter.fillPath(path, QColor(ACCENT_LIME))

        super().paintEvent(event)

    def _update_main_button(self):

        icon = QIcon(self._current["icon"])

        self._btn_main.setIcon(icon)

        self._btn_main.setIconSize(QSize(16, 16))

        self._btn_main.setText("  SEND")

    def _toggle_dropdown(self):

        if self._dropdown and self._dropdown.isVisible():

            self._dropdown.close()

            return

        self._dropdown = PlatformDropdown(self._current["id"])

        self._dropdown.platform_selected.connect(self._on_platform_selected)

        self._dropdown.show()

        self._dropdown.adjustSize()

        arrow_pos = self._btn_arrow.pos()

        pos = self.mapToGlobal(QPoint(

            arrow_pos.x() + self._btn_arrow.width() - 160,

            arrow_pos.y() - self._dropdown.height() - 8

        ))

        self._dropdown.move(pos)

    def _on_platform_selected(self, platform_id, icon_path):

        for p in self.PLATFORMS:

            if p["id"] == platform_id:

                self._current = p

                break

        self._update_main_button()

        self.platform_changed.emit(platform_id, icon_path)

    def current_platform_id(self):

        return self._current["id"]

    def current_icon_path(self):

        return self._current["icon"]

class PlatformDropdown(QFrame):

    platform_selected = pyqtSignal(str, str)

    PLATFORMS = [

        {"id": "twitch", "name": "Twitch", "icon": ICON_TWITCH},

        {"id": "youtube", "name": "YouTube", "icon": ICON_YOUTUBE},

        {"id": "kick", "name": "Kick", "icon": ICON_KICK},

    ]

    def __init__(self, current_id, parent=None):

        super().__init__(None, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.setStyleSheet("QFrame { border-radius: 12px; }")

        self._radius = 12

        layout = QVBoxLayout(self)

        layout.setContentsMargins(6, 6, 6, 6)

        layout.setSpacing(2)

        for p in self.PLATFORMS:

            btn = QPushButton()

            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            is_current = (p["id"] == current_id)

            btn.setStyleSheet(f"""

                QPushButton {{

                    background: {'rgba(204,255,0,25)' if is_current else 'transparent'};

                    color: {ACCENT_LIME if is_current else TEXT_MAIN};

                    border: none; border-radius: 8px;

                    padding: 8px 12px; font-size: 12px; font-weight: 600;

                    text-align: left;

                    font-family: '{FONT_FAMILY}', sans-serif;

                }}

                QPushButton:hover {{  background: rgba(255,255,255,15); }}

            """)

            icon = QIcon(p["icon"])

            btn.setIcon(icon)

            btn.setIconSize(QSize(16, 16))

            btn.setText("  " + p["name"])

            btn.clicked.connect(lambda checked, pid=p["id"], ip=p["icon"]: self._select(pid, ip))

            layout.addWidget(btn)

        self.setFixedWidth(160)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()

        rect = self.rect()

        path.addRoundedRect(QRectF(rect), self._radius, self._radius)

        painter.setClipPath(path)

        painter.fillPath(path, QColor(CARD_LIGHT))

        painter.setPen(QPen(QColor(BORDER_COLOR), 1))

        painter.drawRoundedRect(QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5), self._radius, self._radius)

    def _select(self, platform_id, icon_path):

        self.platform_selected.emit(platform_id, icon_path)

        self.close()

class ModerationMenu(QDialog):
    """Popup menu for chat moderation: ban, timeout, delete, mod."""

    def __init__(self, connection_id, platform, user_identifier, msg_id,
                 on_action, parent=None):
        super().__init__(None, Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._connection_id = connection_id
        self._platform = platform
        self._user_identifier = user_identifier
        self._msg_id = msg_id
        self._on_action = on_action
        self._radius = 14

        self.setStyleSheet("QFrame { border-radius: 14px; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(2)

        is_twitch = (platform == "twitch")

        items = []
        items.append(("ban", "BAN"))
        items.append(("timeout", "TIMEOUT"))
        if is_twitch:
            items.append(("delete", "DELETE MESSAGE"))
        items.append(("mod", "MAKE MOD"))

        for action_id, label in items:
            btn = QPushButton()
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 14px;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 0.5px;
                    text-align: left;
                    font-family: 'Segoe UI', sans-serif;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,15);
                }
            """)
            if action_id == "timeout":
                btn.setText(label + "  \u25B6")
                btn.clicked.connect(self._show_timeout_menu)
            else:
                btn.setText(label)
                btn.clicked.connect(lambda checked, aid=action_id: self._trigger(aid))
            layout.addWidget(btn)

        self.setFixedWidth(160)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        rect = self.rect()
        path.addRoundedRect(QRectF(rect), self._radius, self._radius)
        painter.setClipPath(path)
        painter.fillPath(path, QColor("#1C1C1E"))
        painter.setPen(QPen(QColor("#232326"), 1))
        painter.drawRoundedRect(QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5), self._radius, self._radius)

    def _trigger(self, action):
        if self._on_action:
            self._on_action(self._connection_id, self._platform, action,
                            self._user_identifier, self._msg_id)
        self.close()

    def _show_timeout_menu(self):
        """Open timeout duration submenu at the same position."""
        pos = self.mapToGlobal(QPoint(0, 0))
        menu = TimeoutSubmenu(self._connection_id, self._platform,
                              self._user_identifier, self._msg_id,
                              self._on_action, pos)
        menu.exec()
        self.close()


class TimeoutSubmenu(QDialog):
    """Submenu for selecting timeout duration."""

    def __init__(self, connection_id, platform, user_identifier, msg_id,
                 on_action, position, parent=None):
        super().__init__(None, Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._connection_id = connection_id
        self._platform = platform
        self._user_identifier = user_identifier
        self._msg_id = msg_id
        self._on_action = on_action
        self._radius = 14

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(2)

        TIMEOUTS = [
            ("1 min", 60),
            ("5 min", 300),
            ("10 min", 600),
            ("30 min", 1800),
            ("1 hour", 3600),
            ("24 hours", 86400),
        ]

        for label, seconds in TIMEOUTS:
            btn = QPushButton()
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 14px;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 0.5px;
                    text-align: left;
                    font-family: 'Segoe UI', sans-serif;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,15);
                }
            """)
            btn.setText(label)
            btn.clicked.connect(lambda checked, s=seconds: self._trigger(s))
            layout.addWidget(btn)

        self.setFixedWidth(160)

        # Position to the right of the main menu
        self.move(position.x() + 160 - 6, position.y())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        rect = self.rect()
        path.addRoundedRect(QRectF(rect), self._radius, self._radius)
        painter.setClipPath(path)
        painter.fillPath(path, QColor("#1C1C1E"))
        painter.setPen(QPen(QColor("#232326"), 1))
        painter.drawRoundedRect(QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5), self._radius, self._radius)

    def _trigger(self, duration_seconds):
        if self._on_action:
            self._on_action(self._connection_id, self._platform, "timeout",
                            self._user_identifier, self._msg_id, duration_seconds)
        self.close()

class ChatWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._chat_manager = None
        self._channel_id = None
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_messages)
        self._search_results = []
        self._search_current = -1
        self._replaying = False
        self._mod_menu = None
        self._setup_ui()

    def set_chat_manager(self, manager):
        """Set the ChatManager for multi-platform support."""
        self._chat_manager = manager
        if manager is not None and not self._poll_timer.isActive():
            self._poll_timer.start(1000)
        if manager is not None:
            manager.set_on_view_changed(self._on_manager_view_changed)

    def _on_manager_view_changed(self, view_id: str):
        """Replay cached messages when the view switches."""
        self._replay_cached_messages(view_id)

    def _replay_cached_messages(self, view_id: str):
        """Clear display and replay cached messages for the given view."""
        if self._chat_manager is None:
            return

        self._replaying = True
        self.clear_messages()

        # Determine which connection_ids to replay
        if view_id == "main":
            cached = self._chat_manager.get_cached_messages()
        else:
            cached = self._chat_manager.get_cached_messages(view_id)

        for msg in cached:
            platform_info = msg.get("platform_info")
            conn_number = msg.get("number", 0)
            platform = msg.get("platform", "")

            if platform_info:
                color = platform_info.message_color
                icon_path = str(platform_info.icon_path)
            else:
                color = "#8E8E93"
                icon_path = ""

            conn_id = msg.get("connection_id", "")
            platform = msg.get("platform", "")
            ch_id_yt = msg.get("channel_id", "")
            # For Twitch: user_identifier = author (login), for YouTube: channel_id
            user_ident = ch_id_yt if platform == "youtube" else msg["author"]
            msg_id = msg.get("msg_id", "")

            self.add_message(
                author=msg["author"],
                text=msg["text"],
                color=color,
                platform_icon_path=icon_path,
                badges=msg.get("badges", []),
                is_mod=msg.get("is_mod", False),
                channel_id=ch_id_yt,
                number=conn_number,
                number_color=platform_info.number_color if platform_info else "#8E8E93",
                connection_id=conn_id,
                platform=platform,
                user_identifier=user_ident,
                msg_id=msg_id,
            )

        self._replaying = False

        # Scroll to bottom after all messages are added
        QTimer.singleShot(50, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        ))

    def set_twitch_bot(self, bot):
        # Legacy support — kept for config tab connections
        pass

    def set_youtube_bot(self, bot):
        # Legacy support — kept for config tab connections
        pass

    def set_channel_id(self, channel_id):
        self._channel_id = channel_id

    def _poll_messages(self):
        if self._chat_manager is None:
            return

        try:
            messages = self._chat_manager.poll_all_messages()
        except Exception:
            return

        for msg in messages:
            platform_info = msg.get("platform_info")
            conn_number = msg.get("number", 0)
            platform = msg.get("platform", "")

            # Build color and icon from platform info
            if platform_info:
                color = platform_info.message_color
                icon_path = str(platform_info.icon_path)
            else:
                color = "#8E8E93"
                icon_path = ""

            author = msg["author"]
            conn_id = msg.get("connection_id", "")
            platform = msg.get("platform", "")
            ch_id_yt = msg.get("channel_id", "")
            # For Twitch: user_identifier = author (login), for YouTube: channel_id
            user_ident = ch_id_yt if platform == "youtube" else author
            msg_id = msg.get("msg_id", "")

            self.add_message(
                author=author,
                text=msg["text"],
                color=color,
                platform_icon_path=icon_path,
                badges=msg.get("badges", []),
                is_mod=msg.get("is_mod", False),
                channel_id=ch_id_yt,
                number=conn_number,
                number_color=platform_info.number_color if platform_info else "#8E8E93",
                connection_id=conn_id,
                platform=platform,
                user_identifier=user_ident,
                msg_id=msg_id,
            )

    def _setup_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)

        layout.setSpacing(12)

        messages_card = QFrame()

        messages_card.setObjectName("chatMessagesCard")

        messages_card.setStyleSheet(f"""

            QFrame#chatMessagesCard {{

                background-color: transparent;

                border: none;

                border-radius: 16px;

            }}

        """)

        card_layout = QVBoxLayout(messages_card)

        card_layout.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()

        self._scroll.setWidgetResizable(True)

        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._scroll.setStyleSheet(f"""

            QScrollArea {{

                background: transparent;

                border: none;

                border-radius: 16px;

            }}

            QScrollArea > QWidget > QWidget {{

                background: transparent;

            }}

            QScrollBar:vertical {{  width: 4px; margin: 4px 0; background: transparent; }}

            QScrollBar::handle:vertical {{  background: {BORDER_COLOR}; border-radius: 2px; min-height: 30px; }}

            QScrollBar::add-line, QScrollBar::sub-line {{  height: 0; background: none; }}

            QScrollBar::add-page, QScrollBar::sub-page {{  background: none; }}

        """)

        self._messages_container = QWidget()

        self._messages_container.setStyleSheet("background: transparent;")

        self._messages_layout = QVBoxLayout(self._messages_container)

        self._messages_layout.setContentsMargins(0, 10, 0, 10)

        self._messages_layout.setSpacing(0)

        self._messages_layout.addStretch()

        self._scroll.setWidget(self._messages_container)

        card_layout.addWidget(self._scroll)

        self._search_bar = QFrame()

        self._search_bar.setObjectName("chatSearchBar")

        self._search_bar.setFrameShape(QFrame.Shape.NoFrame)

        self._search_bar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._search_bar.setAutoFillBackground(False)

        self._search_bar.setStyleSheet(f"""
            QFrame#chatSearchBar {{
                background-color: {CARD_LIGHT};
                border: 1px solid {BORDER_COLOR};
                border-radius: 9999px;
            }}
        """)

        self._search_bar.setFixedHeight(44)

        self._search_bar.setVisible(False)

        search_layout = QHBoxLayout(self._search_bar)

        search_layout.setContentsMargins(12, 0, 4, 0)

        search_layout.setSpacing(4)

        search_icon = QLabel()

        search_icon.setPixmap(QPixmap(ICON_SEARCH).scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        search_icon.setFixedSize(16, 16)

        search_icon.setStyleSheet("background: transparent;")

        search_layout.addWidget(search_icon)

        self._search_input = QLineEdit()

        self._search_input.setObjectName("chatSearchInput")

        self._search_input.setPlaceholderText("Search messages or @user...")

        self._search_input.setStyleSheet(f"""
            QLineEdit#chatSearchInput {{
                background: transparent;
                border: none;
                color: {TEXT_MAIN};
                font-size: 12px;
            }}
            QLineEdit#chatSearchInput::placeholder {{ color: {TEXT_SEC}; }}
        """)

        self._search_input.textChanged.connect(self._on_search_text_changed)

        search_layout.addWidget(self._search_input, 1)

        self._search_count = QLabel("")

        self._search_count.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; background: transparent;")

        self._search_count.setFixedWidth(60)

        self._search_count.setAlignment(Qt.AlignmentFlag.AlignCenter)

        search_layout.addWidget(self._search_count)

        def _make_search_nav_btn(icon_path):
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(16, 16))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: 1px solid {BORDER_COLOR};
                    border-radius: 9999px;
                }}
                QPushButton:hover {{
                    background: rgba(255,255,255,10);
                    border-color: {TEXT_SEC};
                }}
            """)
            return btn

        prev_btn = _make_search_nav_btn(ICON_ARROW_UP)
        prev_btn.clicked.connect(self._search_prev)
        search_layout.addWidget(prev_btn)

        next_btn = _make_search_nav_btn(ICON_ARROW_DOWN)
        next_btn.clicked.connect(self._search_next)
        search_layout.addWidget(next_btn)

        close_btn = _make_search_nav_btn(ICON_CLOSE)
        close_btn.clicked.connect(self._search_close)
        search_layout.addWidget(close_btn)

        card_layout.addWidget(self._search_bar)

        layout.addWidget(messages_card, 1)

        input_row = QWidget()

        input_row.setObjectName("chatInputRow")

        input_row.setStyleSheet("QWidget#chatInputRow { background: transparent; }")

        input_layout = QHBoxLayout(input_row)

        input_layout.setContentsMargins(0, 0, 0, 0)

        input_layout.setSpacing(8)

        self._input = QLineEdit()

        self._input.setObjectName("chatInput")

        self._input.setPlaceholderText("Message...")

        self._input.setFixedHeight(40)
        self._input.setStyleSheet(f"""
            QLineEdit#chatInput {{
                background-color: {BG_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 20px;
                padding: 8px 14px;
                color: #FFFFFF;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
            }}
            QLineEdit#chatInput::placeholder {{  color: #555; }}
        """)

        self._input.returnPressed.connect(self._send_message)

        input_layout.addWidget(self._input, 1)

        self._split_btn = SplitSendButton()

        self._split_btn._btn_main.clicked.connect(self._send_message)

        input_layout.addWidget(self._split_btn)

        layout.addWidget(input_row)

    def _get_message_rows(self):

        rows = []

        for i in range(self._messages_layout.count()):

            item = self._messages_layout.itemAt(i)

            if item and item.widget() and isinstance(item.widget(), MessageRow):

                rows.append(item.widget())

        return rows

    def toggle_search(self):

        self._search_bar.setVisible(not self._search_bar.isVisible())

        if self._search_bar.isVisible():

            self._search_input.setFocus()

            self._search_input.selectAll()

        else:

            self._search_close()

    def _on_search_text_changed(self, text):

        rows = self._get_message_rows()

        for row in rows:

            row.clear_search()

        if not text.strip():

            self._search_count.setText("")

            self._search_results = []

            self._search_current = -1

            return

        is_user = text.startswith("@")

        term = text[1:] if is_user else text

        if not term:

            self._search_count.setText("")

            self._search_results = []

            self._search_current = -1

            return

        self._search_results = []

        for row in rows:

            if row.apply_search(term, is_user):

                self._search_results.append(row)

        if self._search_results:

            self._search_current = 0

            self._scroll_to_row(self._search_results[0])

            self._update_search_count()

        else:

            self._search_current = -1

            self._search_count.setText("No results")

    def _scroll_to_row(self, row):

        self._scroll.ensureWidgetVisible(row, 0, 100)

    def _update_search_count(self):

        total = len(self._search_results)

        if total == 0:

            self._search_count.setText("No results")

            return

        cur = self._search_current + 1

        self._search_count.setText(f"{cur} of {total}")

    def _search_next(self):

        if not self._search_results:

            return

        self._search_current = (self._search_current + 1) % len(self._search_results)

        self._scroll_to_row(self._search_results[self._search_current])

        self._update_search_count()

    def _search_prev(self):

        if not self._search_results:

            return

        self._search_current = (self._search_current - 1) % len(self._search_results)

        self._scroll_to_row(self._search_results[self._search_current])

        self._update_search_count()

    def clear_search(self):
        """Публичный метод: очистить поиск и скрыть строку поиска"""
        self._search_close()

    def _search_close(self):

        self._search_bar.setVisible(False)

        self._search_input.clear()

        rows = self._get_message_rows()

        for row in rows:

            row.clear_search()

        self._search_results = []

        self._search_current = -1

        self._search_count.setText("")

    def _send_message(self):
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()

        if self._chat_manager:
            # Main view → send to all; individual view → send to that channel
            if self._chat_manager.is_main_view():
                self._chat_manager.send_message(text, target="all")
            else:
                self._chat_manager.send_message(text, target="current")

    def add_system_message(self, tag, text, tag_color):

        container = QWidget()

        container.setStyleSheet("background: transparent;")

        clayout = QHBoxLayout(container)

        clayout.setContentsMargins(14, 4, 14, 4)

        clayout.addWidget(SystemMessage(tag, text, tag_color))

        self._messages_layout.insertWidget(self._messages_layout.count() - 1, container)

    def add_message(self, author, text, color, platform_icon_path, timestamp=None,
                    badges=None, is_entry=False, channel_id=None, is_mod=False,
                    number=0, number_color="#8E8E93", connection_id="",
                    platform="", user_identifier="", msg_id=""):

        if timestamp is None:

            timestamp = datetime.now().strftime("%H:%M")

        if self._channel_id and channel_id == self._channel_id:

            color = ACCENT_LIME

        row = MessageRow(author, text, color, platform_icon_path, timestamp,
                         badges or [], is_entry, is_mod, number, number_color,
                         connection_id, platform, user_identifier, msg_id)

        row.moderation_requested.connect(self._show_moderation_menu)
        self._messages_layout.insertWidget(self._messages_layout.count() - 1, row)

        if not self._replaying:
            QTimer.singleShot(50, lambda: self._scroll.verticalScrollBar().setValue(
                self._scroll.verticalScrollBar().maximum()
            ))

    def _show_moderation_menu(self, row, global_pos):
        """Show moderation popup menu at the given position."""
        # Close any existing menu
        if self._mod_menu:
            self._mod_menu.close()
            self._mod_menu = None

        conn_id = row._connection_id
        platform = row._platform
        user_ident = row._user_identifier
        msg_id = row._msg_id

        menu = ModerationMenu(conn_id, platform, user_ident, msg_id,
                              self._perform_moderation)
        QApplication.beep()
        menu.adjustSize()
        menu.move(global_pos - QPoint(menu.width() // 2, 0))
        self._mod_menu = menu
        menu.exec()
        self._mod_menu = None

    def _perform_moderation(self, connection_id, platform, action,
                            user_identifier, msg_id, duration=0):
        """Execute a moderation action using the appropriate bot."""
        if self._chat_manager is None:
            return
        conn = self._chat_manager.get_connection(connection_id)
        if not conn or not conn.bot:
            return
        bot = conn.bot

        try:
            if platform == "twitch":
                if action == "ban":
                    bot.ban_user(user_identifier)
                elif action == "timeout":
                    bot.timeout_user(user_identifier, duration or 300)
                elif action == "delete":
                    bot.delete_message(msg_id)
                elif action == "mod":
                    bot.make_moderator(user_identifier)
            elif platform == "youtube":
                if action == "ban":
                    bot.ban_user(user_identifier)
                elif action == "timeout":
                    bot.ban_user(user_identifier, duration or 300)
                elif action == "mod":
                    bot.make_moderator(user_identifier)
        except Exception as e:
            print(f"[MOD] {action} failed: {e}")

    def clear_messages(self):
        """Remove all message rows from the chat display."""
        i = 0
        while i < self._messages_layout.count():
            item = self._messages_layout.itemAt(i)
            if item and item.widget() and isinstance(item.widget(), MessageRow):
                widget = item.widget()
                self._messages_layout.takeAt(i)
                widget.deleteLater()
            else:
                i += 1
        self._search_results = []
        self._search_current = -1
