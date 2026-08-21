"""
chat_sidebar.py — dropdown chat selector (collapsible, like WheelDropdown).
Shows: compact button with current selection + popup with MAIN CHAT + channels.
"""

from pathlib import Path

from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRectF
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QPainterPath, QEnterEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy,
)

from core.theme import (
    BG_COLOR, CARD_COLOR, CARD_LIGHT, TEXT_MAIN, TEXT_SEC,
    BORDER_COLOR, ACCENT_CYAN, FONT_FAMILY, GLOBAL_RADIUS,
    RECYCLE_BIN_PATH, RECYCLE_BIN_ACTIVE_PATH,
    CIRCLE_ACTIVE_PATH, CIRCLE_DISABLED_PATH,
)
from .platform_registry import PlatformInfo, PLATFORM_PURPLE, PLATFORM_RED
from .chat_manager import ChatManager, ChatConnection

APP_DIR = Path(__file__).resolve().parent.parent.parent
RESOURCES = APP_DIR / "resources"


class _ChannelRow(QFrame):
    """A single channel row in the sidebar."""
    clicked = pyqtSignal(str)       # connection_id
    remove_requested = pyqtSignal(str)  # connection_id

    def __init__(self, connection_id: str, platform: str, channel: str,
                 number: int, platform_info: PlatformInfo, parent=None):
        super().__init__(parent)
        self.connection_id = connection_id
        self._hovered = False
        self._selected = False

        self.setFixedHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"background: transparent; border: none;")
        self.setMouseTracking(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 4, 0)
        layout.setSpacing(6)

        # Number badge
        self._number_badge = QLabel(str(number))
        self._number_badge.setFixedSize(20, 20)
        self._number_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_color = PLATFORM_RED if platform == "youtube" else PLATFORM_PURPLE
        self._number_badge.setStyleSheet(f"""
            background-color: {badge_color};
            color: #FFFFFF;
            font-size: 10px;
            font-weight: 800;
            border-radius: 10px;
        """)
        layout.addWidget(self._number_badge)

        # Platform icon
        icon_lbl = QLabel()
        icon_path = platform_info.icon_path
        if icon_path.exists():
            pix = QPixmap(str(icon_path))
            icon_lbl.setPixmap(pix.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation))
        icon_lbl.setFixedSize(16, 16)
        layout.addWidget(icon_lbl)

        # Channel name
        name_lbl = QLabel(channel)
        name_lbl.setStyleSheet(f"""
            color: {TEXT_MAIN};
            font-size: 11px;
            background: transparent;
            font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
        """)
        layout.addWidget(name_lbl, 1)

        # Recycle bin button (visible on hover)
        self._remove_btn = QPushButton()
        self._remove_btn.setIcon(QIcon(str(RECYCLE_BIN_PATH)))
        self._remove_btn.setIconSize(QSize(14, 14))
        self._remove_btn.setFixedSize(24, 24)
        self._remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._remove_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
            }
            QPushButton:hover {
                background: rgba(255, 59, 48, 0.15);
                border-radius: 6px;
            }
        """)
        self._remove_btn.hide()
        self._remove_btn.clicked.connect(
            lambda: self.remove_requested.emit(self.connection_id)
        )
        layout.addWidget(self._remove_btn)

    def set_selected(self, selected: bool):
        self._selected = selected
        self.update()

    def enterEvent(self, event: QEnterEvent):
        self._hovered = True
        self._remove_btn.show()
        self.update()

    def leaveEvent(self, event):
        self._hovered = False
        self._remove_btn.hide()
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.connection_id)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._selected or self._hovered:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            if self._selected:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(CARD_LIGHT))
                painter.drawRoundedRect(self.rect(), 10, 10)
            elif self._hovered:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(255, 255, 255, 8))
                painter.drawRoundedRect(self.rect(), 10, 10)


class _MainChatRow(QFrame):
    """The MAIN CHAT row — always visible, always first."""
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected = True
        self._hovered = False

        self.setFixedHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"background: transparent; border: none;")
        self.setMouseTracking(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(8)

        # Globe indicator
        globe = QLabel("🌐" if False else "◎")
        globe.setFixedSize(20, 20)
        globe.setAlignment(Qt.AlignmentFlag.AlignCenter)
        globe.setStyleSheet(f"""
            color: {ACCENT_CYAN};
            font-size: 11px;
            font-weight: 800;
            background: transparent;
        """)
        layout.addWidget(globe)

        name = QLabel("MAIN CHAT")
        name.setStyleSheet(f"""
            color: {ACCENT_CYAN};
            font-size: 12px;
            font-weight: 700;
            background: transparent;
            font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
        """)
        layout.addWidget(name, 1)

    def set_selected(self, selected: bool):
        self._selected = selected
        self.update()

    def enterEvent(self, event: QEnterEvent):
        self._hovered = True
        self.update()

    def leaveEvent(self, event):
        self._hovered = False
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._selected or self._hovered:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            if self._selected:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(CARD_LIGHT))
                painter.drawRoundedRect(self.rect(), 10, 10)
            elif self._hovered:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QColor(255, 255, 255, 8))
                painter.drawRoundedRect(self.rect(), 10, 10)


class ChatSidebar(QFrame):
    """Accordion-style sidebar for channel selection."""

    view_changed = pyqtSignal(str)  # "main" or connection_id
    remove_connection = pyqtSignal(str)  # connection_id

    def __init__(self, chat_manager: ChatManager, parent=None):
        super().__init__(parent)
        self._manager = chat_manager
        self._selected_id = "main"
        self._rows: dict[str, _ChannelRow] = {}

        self.setObjectName("chatSidebar")
        self.setStyleSheet(f"""
            QFrame#chatSidebar {{
                background-color: {CARD_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 20px;
            }}
        """)
        self.setMinimumWidth(200)
        self.setMaximumWidth(280)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 12, 8, 12)
        main_layout.setSpacing(0)

        # Title
        title = QLabel("CHAT LIST")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            color: {TEXT_SEC};
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1.5px;
            background: transparent;
            font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
            padding-bottom: 8px;
            border-bottom: 1px solid {BORDER_COLOR};
            margin-bottom: 8px;
        """)
        main_layout.addWidget(title)

        # Scrollable channel list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 4px;
                border-radius: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER_COLOR};
                border-radius: 2px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)

        self._channels_widget = QWidget()
        self._channels_widget.setStyleSheet("background: transparent;")
        self._channels_layout = QVBoxLayout(self._channels_widget)
        self._channels_layout.setContentsMargins(0, 0, 0, 0)
        self._channels_layout.setSpacing(2)
        self._channels_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self._channels_widget)
        main_layout.addWidget(scroll, 1)

        # Build initial UI
        self._rebuild()

        # Wire manager callbacks
        self._manager.set_on_connection_added(lambda c: self._rebuild())
        self._manager.set_on_connection_removed(lambda c: self._rebuild())

    def _rebuild(self):
        """Rebuild the channel list from manager state."""
        self._rows.clear()

        # Clear layout
        while self._channels_layout.count():
            item = self._channels_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Main chat row
        main_row = _MainChatRow()
        main_row.clicked.connect(self._on_main_selected)
        main_row.set_selected(self._selected_id == "main")
        self._channels_layout.addWidget(main_row)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER_COLOR}; margin: 4px 8px;")
        self._channels_layout.addWidget(sep)

        # Channel rows
        for conn in self._manager.connections:
            row = _ChannelRow(
                conn.connection_id,
                conn.platform,
                conn.channel,
                conn.number,
                conn.platform_info,
            )
            row.clicked.connect(self._on_channel_selected)
            row.remove_requested.connect(self._on_remove)
            row.set_selected(self._selected_id == conn.connection_id)
            self._rows[conn.connection_id] = row
            self._channels_layout.addWidget(row)

        self._channels_layout.addStretch()

    def _on_main_selected(self):
        self._selected_id = "main"
        self._manager.set_view("main")
        self._rebuild()
        self.view_changed.emit("main")

    def _on_channel_selected(self, connection_id: str):
        self._selected_id = connection_id
        self._manager.set_view(connection_id)
        self._rebuild()
        self.view_changed.emit(connection_id)

    def _on_remove(self, connection_id: str):
        self.remove_connection.emit(connection_id)


# ── ChatListPopup ──────────────────────────────────────────────────

class ChatListPopup(QFrame):
    """Dropdown popup with chat list — styled like WheelPopup."""
    item_selected = pyqtSignal(str)       # "main" or connection_id
    remove_requested = pyqtSignal(str)    # connection_id

    def __init__(self, manager: ChatManager, selected_id: str, parent=None):
        super().__init__(None, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(False)

        container = QFrame(self)
        container.setObjectName("popupContainer")
        container.setStyleSheet(f"""
            #popupContainer {{
                background-color: #141416;
                border: 1px solid {BORDER_COLOR};
                border-radius: 20px;
            }}
        """)

        # Fix cut-off: Use a layout for the popup and ensure 
        # the container takes up all space
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(6, 8, 6, 8)
        layout.setSpacing(2)

        # ── MAIN CHAT row ──
        main_row = QFrame()
        main_row.setCursor(Qt.CursorShape.PointingHandCursor)
        main_row.setFixedHeight(36)
        main_row.setStyleSheet("background: transparent; border: none;")
        is_main_active = (selected_id == "main")

        ml = QHBoxLayout(main_row)
        ml.setContentsMargins(12, 0, 12, 0)
        ml.setSpacing(8)

        # Circle icon instead of ◎
        globe_icon = QLabel()
        globe_pix = QPixmap(str(CIRCLE_ACTIVE_PATH if is_main_active else CIRCLE_DISABLED_PATH))
        globe_icon.setPixmap(globe_pix.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation))
        globe_icon.setFixedSize(16, 16)
        ml.addWidget(globe_icon)

        main_name = QLabel("MAIN CHAT")
        main_name.setStyleSheet(f"""
            color: {TEXT_MAIN};
            font-size: 12px; font-weight: 700; background: transparent;
            font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
        """)
        ml.addWidget(main_name, 1)

        main_row.mousePressEvent = lambda e: self._on_select("main")
        main_row.enterEvent = lambda e: self._hover_row(main_row, True)
        main_row.leaveEvent = lambda e: self._hover_row(main_row, False)
        if is_main_active:
            self._paint_highlight(main_row)
        layout.addWidget(main_row)

        # ── Separator (only if there are channels) ──
        if manager.connections:
            sep = QFrame()
            sep.setFixedHeight(1)
            sep.setStyleSheet(f"background: {BORDER_COLOR}; margin: 4px 12px;")
            layout.addWidget(sep)

        # ── Channel rows ──
        for conn in manager.connections:
            is_active = (selected_id == conn.connection_id)

            row = QFrame()
            row.setCursor(Qt.CursorShape.PointingHandCursor)
            row.setFixedHeight(36)
            row.setStyleSheet("background: transparent; border: none;")
            row.setMouseTracking(True)

            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 0, 4, 0)
            rl.setSpacing(6)

            # Number badge
            badge = QLabel(str(conn.number))
            badge.setFixedSize(20, 20)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge_color = PLATFORM_RED if conn.platform == "youtube" else PLATFORM_PURPLE
            badge.setStyleSheet(f"""
                background-color: {badge_color}; color: #FFFFFF;
                font-size: 10px; font-weight: 800; border-radius: 10px;
            """)
            rl.addWidget(badge)

            # Platform icon
            icon_lbl = QLabel()
            icon_path = conn.platform_info.icon_path
            if icon_path.exists():
                pix = QPixmap(str(icon_path))
                icon_lbl.setPixmap(pix.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation))
            icon_lbl.setFixedSize(16, 16)
            rl.addWidget(icon_lbl)

            # Channel name
            name = QLabel(conn.channel)
            name.setStyleSheet(f"""
                color: {TEXT_MAIN}; font-size: 11px; background: transparent;
                font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
            """)
            rl.addWidget(name, 1)

            # Delete button
            del_btn = QPushButton()
            del_btn.setIcon(QIcon(str(RECYCLE_BIN_PATH)))
            del_btn.setIconSize(QSize(14, 14))
            del_btn.setFixedSize(24, 24)
            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            del_btn.setStyleSheet("""
                QPushButton { background: transparent; border: none; }
                QPushButton:hover { background: rgba(255, 59, 48, 15); border-radius: 6px; }
            """)
            cid = conn.connection_id
            del_btn.clicked.connect(lambda checked, cid=cid: self._on_remove(cid))
            del_btn.hide()
            rl.addWidget(del_btn)

            row.mousePressEvent = lambda e, cid=cid: self._on_select(cid)
            row.enterEvent = lambda e, r=row, b=del_btn: self._hover_channel(r, b, True)
            row.leaveEvent = lambda e, r=row, b=del_btn: self._hover_channel(r, b, False)
            if is_active:
                self._paint_highlight(row)
            layout.addWidget(row)

    def _on_select(self, view_id: str):
        self.item_selected.emit(view_id)
        self.close()

    def _on_remove(self, connection_id: str):
        self.remove_requested.emit(connection_id)
        self.close()

    def _hover_row(self, row: QFrame, hover: bool):
        if hover:
            row.setStyleSheet("background: rgba(255,255,255,8); border: none; border-radius: 10px;")
        else:
            row.setStyleSheet("background: transparent; border: none;")

    def _hover_channel(self, row: QFrame, del_btn: QPushButton, hover: bool):
        if hover:
            row.setStyleSheet("background: rgba(255,255,255,8); border: none; border-radius: 10px;")
            del_btn.show()
        else:
            row.setStyleSheet("background: transparent; border: none;")
            del_btn.hide()

    def _paint_highlight(self, row: QFrame):
        """Mark row as selected via paint."""
        def paint_sel(event):
            super(type(row), row).paintEvent(event)
            p = QPainter(row)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(CARD_LIGHT))
            p.drawRoundedRect(row.rect(), 10, 10)
            p.end()
        row.paintEvent = paint_sel


# ── ChatListDropdown ───────────────────────────────────────────────

class ChatListDropdown(QWidget):
    """Compact dropdown button for chat selection — like WheelDropdown."""

    view_changed = pyqtSignal(str)      # "main" or connection_id
    remove_connection = pyqtSignal(str)  # connection_id

    def __init__(self, chat_manager: ChatManager, parent=None):
        super().__init__(parent)
        self._manager = chat_manager
        self._selected_id = "main"
        self._popup = None
        self._hovered = False

        self.setFixedHeight(38)

        self.setMinimumWidth(160)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Wire manager callbacks
        self._manager.set_on_connection_added(lambda c: self.update())
        self._manager.set_on_connection_removed(lambda c: self._on_conn_removed(c))

    def _on_conn_removed(self, connection_id):
        """If the selected connection was removed, fall back to main."""
        if connection_id and connection_id == self._selected_id:
            self._selected_id = "main"
            self._manager.set_view("main")
            self.view_changed.emit("main")
        elif connection_id is None:
            # clear_all — reset to main
            self._selected_id = "main"
            self._manager.set_view("main")
            self.view_changed.emit("main")
        self.update()

    def _current_label(self) -> str:
        """Return the display text for the current selection."""
        if self._selected_id == "main":
            return "MAIN CHAT"
        conn = self._manager.get_connection(self._selected_id)
        if conn:
            return conn.channel
        return "MAIN CHAT"

    def _current_number_info(self) -> tuple:
        """Return (number, number_color, icon_path) for current selection."""
        if self._selected_id == "main":
            return 0, ACCENT_CYAN, None
        conn = self._manager.get_connection(self._selected_id)
        if conn:
            color = PLATFORM_RED if conn.platform == "youtube" else PLATFORM_PURPLE
            return conn.number, color, str(conn.platform_info.icon_path)
        return 0, ACCENT_CYAN, None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        radius = h / 2
        border_w = 2
        pad = border_w / 2

        bg = QColor("#1C1C1E")
        border_col = QColor(ACCENT_CYAN) if self._hovered else QColor(BORDER_COLOR)

        rect = QRectF(pad, pad, w - border_w, h - border_w)
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        painter.setBrush(bg)
        pen = QPen(border_col, border_w)
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawPath(path)

        painter.setClipPath(path)

        # Draw content
        num, num_color, icon_path = self._current_number_info()
        label = self._current_label()

        x = 16

        # Number badge (if not main)
        if num > 0:
            badge_rect = QRectF(x, (h - 20) / 2, 20, 20)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(num_color))
            painter.drawRoundedRect(badge_rect, 10, 10)
            painter.setPen(QColor("#FFFFFF"))
            font = painter.font()
            font.setPixelSize(10)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, str(num))
            x += 28

        # Platform icon
        if icon_path:
            pix = QPixmap(icon_path).scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(int(x), int((h - 16) / 2), pix)
            x += 22

        # Label
        font = painter.font()
        font.setPointSize(11)
        font.setBold(True)
        painter.setFont(font)
        if self._selected_id == "main":

            painter.setPen(QColor(TEXT_MAIN))

        else:

            painter.setPen(QColor(TEXT_MAIN))
        text_rect = QRectF(x, 0, w - x - 40, h)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter, label)

        # Chevron
        chevron_rect = QRectF(w - 36, 0, 20, h)
        painter.setPen(QColor("#888888"))
        cf = painter.font()
        cf.setPointSize(9)
        painter.setFont(cf)
        painter.drawText(chevron_rect, Qt.AlignmentFlag.AlignVCenter, "▼")

        painter.end()

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_popup()
        super().mousePressEvent(event)

    def wheelEvent(self, event):
        """Scroll through connections without opening popup."""
        all_ids = ["main"] + [c.connection_id for c in self._manager.connections]
        if len(all_ids) < 2:
            return
        delta = event.angleDelta().y()
        try:
            idx = all_ids.index(self._selected_id)
        except ValueError:
            idx = 0
        if delta > 0:
            idx = (idx - 1) % len(all_ids)
        else:
            idx = (idx + 1) % len(all_ids)
        self._select(all_ids[idx])
        event.accept()

    def _toggle_popup(self):
        if self._popup and self._popup.isVisible():
            self._popup.close()
            return

        self._popup = ChatListPopup(self._manager, self._selected_id, self)
        self._popup.item_selected.connect(self._on_popup_select)
        self._popup.remove_requested.connect(self._on_popup_remove)

        btn_rect = self.rect()
        global_pos = self.mapToGlobal(btn_rect.bottomLeft())
        
        # Popup width should match button width if we want them to be the same
        popup_width = self.width()
        self._popup.setFixedWidth(popup_width)
        self._popup.move(global_pos)
        self._popup.show()

    def _on_popup_select(self, view_id: str):
        self._select(view_id)

    def _on_popup_remove(self, connection_id: str):
        self.remove_connection.emit(connection_id)

    def _select(self, view_id: str):
        if view_id != self._selected_id:
            self._selected_id = view_id
            self._manager.set_view(view_id)
            self.view_changed.emit(view_id)
        self.update()