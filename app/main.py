import pickle

import random

import re

import json

import math

import threading

import time

import os

import sys

from pathlib import Path

os.environ["QT_OPENGL"] = "software"

os.environ["QSG_RHI_BACKEND"] = "software"

from PyQt6.QtWidgets import (

    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,

    QPushButton, QLabel, QLineEdit, QStackedWidget,

    QFrame, QScrollArea, QGridLayout, QSizePolicy, QSplitter,

    QDialog, QGraphicsDropShadowEffect, QGraphicsBlurEffect,

    QComboBox, QListView, QMessageBox, QInputDialog, QFileDialog

)

from PyQt6.QtCore import (

    Qt, QTimer, QRectF, QRect, QEvent,

    QPointF, QPoint, pyqtSignal, QObject, QSize,

    QPropertyAnimation, QEasingCurve, QVariantAnimation, QMimeData,

    QUrl

)

from PyQt6.QtGui import (

    QFont, QColor, QPainter, QBrush, QPen,

    QFontDatabase, QPixmap, QImage, QPainterPath,

    QPolygonF, QFontMetrics, QIcon, QRegion, QDrag,

    QLinearGradient, QTransform, QDesktopServices,

)

from services.bot import YouTubeChatBot

from core.storage import Storage

from core.theme import (

    APP_DIR, TOKEN_PATH, CLIENT_SECRET_PATH, FONT_PATH,

    CIRCLE_ACTIVE_PATH, CIRCLE_DISABLED_PATH, RECYCLE_BIN_PATH,

    RECYCLE_BIN_ACTIVE_PATH, LEFT_ARROW_PATH, RIGHT_ARROW_PATH,

    PLUS_PATH, MINUS_PATH, KVADRAT_PATH, KRESTIK_PATH, SEARCH_PATH,

    FONT_GLOBAL, FONT_FAMILY, load_font_global,

    BG_COLOR, CARD_COLOR, CARD_LIGHT, ACCENT_CYAN, ACCENT_LIME,

    TEXT_MAIN, TEXT_SEC, BORDER_COLOR, DANGER_COLOR, SUCCESS_COLOR,

    TWITCH_CLIENT_ID, GLOBAL_RADIUS, GLOBAL_FONT_SIZE, get_stylesheet

)

from core.config import ConfigManager

from core.utils import _dialog_adaptive, _get_cached_pixmap, _clear_image_cache

from gui.widgets.widgets import (

    RoundedButton, RoundedLineEdit, RoundedFrame, RoundedListView,

    WheelDropdown, WheelPopup, GlowButton, ToggleSwitch,

    ModernSlider, HoverIconButton, TabButton

)

from gui.widgets.wheel_widget import WheelWidget

from gui.dialogs.primitives import DragHandle, DropContainer
from gui.dialogs.modern_dialog import ModernDialog, show_info, ask_string
from gui.dialogs.color_picker import ModernColorPicker
from gui.dialogs.item_picker import ModernItemPicker
from gui.dialogs.confirm_dialogs import DeleteConfirmDialog, BatchValueDialog, SegmentInfoPopup

from gui.dialogs.image_editor import ImageEditorDialog

from gui.splash import SplashScreen

from gui.titlebar import TitleBar

from gui.widgets.case_strip import WheelTabPage, _CaseStripWidget

from gui.detach import DetachableSection, DetachablePanel

from gui.widgets.dice_widget import DicePanel

from gui.widgets.chat_widget import ChatWidget
from gui.chat import ChatSidebar, ChatListDropdown

from gui.templates.case_mixin import CaseMixin

from gui.templates.wheel_mixin import WheelMixin

from gui.templates.app_lottery_mixin import LotteryMixin

from gui.templates.app_config_mixin import ConfigMixin

from gui.templates.app_youtube_mixin import YouTubeMixin

from gui.templates.app_twitch_mixin import TwitchMixin

from ui_kit.ui_kit_demo import TabBarTemplate
from app.panels import AppWheelPanel
from app.wheel_setup import WheelSetupMixin
from app.main_setup import MainSetupMixin
from app.event_filter import EventFilterMixin


class ChatLotteryApp(QMainWindow, CaseMixin, WheelMixin, LotteryMixin, ConfigMixin, YouTubeMixin, TwitchMixin, WheelSetupMixin, MainSetupMixin, EventFilterMixin):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Dropzone")

        self.setWindowIcon(QIcon(str(APP_DIR / "resources" / "logo.ico")))

        self.setMinimumSize(800, 550)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.config_mgr = ConfigManager()

        try:

            raw = str(self.config_mgr.get("general", "transparency", 90)).strip("\\ '")

            self.setWindowOpacity(int(raw) / 100.0)

        except Exception:

            self.setWindowOpacity(0.9)

        QApplication.instance().setStyleSheet(get_stylesheet())

        self._base_width = 1400

        self._base_font_size = 13

        self.bot = None

        self.credentials = self.load_credentials()

        if self.credentials:

            self.bot = YouTubeChatBot(self.credentials)

        self.current_wheel_data = []

        self.is_collecting = False

        self.is_connected = False

        self.auto_color_var = True

        self._random_color_mode = False

        self._general_color_mode = False

        self._general_color_value = ACCENT_CYAN

        self._prize_cards = {}

        self._batch_value_warned = False

        self._batch_mode_active = False

        self.auto_gray_winners = True

        self._current_winner = None

        self.participants_data = {}

        self._monitor_running = False

        self._monitor_timer = None

        self._monitored_streams = set()

        self.twitch_bot = None

        self._current_platform = "youtube"

        self._twitch_monitor_running = False

        self._twitch_monitor_timer = None

        self._twitch_monitored_streams = set()

        self._resize_margin = 8

        self._resizing = False

        self._resize_edge = None

        self._resize_start_global = None

        self._resize_start_rect = None

        self._resize_last_global = None

        self._tab_drag_active_idx = -1

        self._tab_drag_start_pos = None

        self._tab_drag_preview_shown = False

        self._tab_drag_preview = None

        self._sub_drag_active_idx = -1

        self._sub_drag_start_pos = None

        self._sub_drag_preview_shown = False

        self._main_sub_drag_active_idx = -1

        self._main_sub_drag_start_pos = None

        self._main_sub_drag_preview_shown = False

        QApplication.instance().installEventFilter(self)

        self._add_participant_signal = self._ParticipantSignal()

        self._add_participant_signal.add_participant.connect(lambda name: self.add_participant_widget(name, skip_whitelist=True))

        self._add_participant_signal.error_occurred.connect(self._on_tracking_error)

        self._setup_ui()

        self._apply_startup_config()

    def nativeEvent(self, eventType, message):

        if eventType == b"windows_generic_MSG":

            import ctypes

            from ctypes import wintypes

            msg = ctypes.wintypes.MSG.from_address(message.__int__())

            if msg.message == 0x0084:

                return True, 1

        return False, 0

    def resizeEvent(self, event):

        super().resizeEvent(event)

        self._scale_fonts()

        if hasattr(self, '_case_overlay'):

            self._resize_case_image()

        self._update_open_dialogs()

        if hasattr(self, 'sub_nav') and self.wheel_page:

            self.sub_nav.setGeometry(0, 0, self.wheel_page.width(), 32)

        if hasattr(self, 'main_sub_nav') and self.lottery_page:

            self.main_sub_nav.setGeometry(0, 0, self.lottery_page.width(), 32)

    def _get_resize_edge(self, pos):

        margin = self._resize_margin

        r = self.rect()

        edges = set()

        if pos.x() <= margin:

            edges.add('left')

        if pos.x() >= r.width() - margin:

            edges.add('right')

        if pos.y() <= margin:

            edges.add('top')

        if pos.y() >= r.height() - margin:

            edges.add('bottom')

        return edges

    def _set_resize_cursor(self, edges):

        if not edges:

            self.setCursor(Qt.CursorShape.ArrowCursor)

        elif 'left' in edges and 'top' in edges:

            self.setCursor(Qt.CursorShape.SizeFDiagCursor)

        elif 'right' in edges and 'bottom' in edges:

            self.setCursor(Qt.CursorShape.SizeFDiagCursor)

        elif 'left' in edges and 'bottom' in edges:

            self.setCursor(Qt.CursorShape.SizeBDiagCursor)

        elif 'right' in edges and 'top' in edges:

            self.setCursor(Qt.CursorShape.SizeBDiagCursor)

        elif 'left' in edges or 'right' in edges:

            self.setCursor(Qt.CursorShape.SizeHorCursor)

        elif 'top' in edges or 'bottom' in edges:

            self.setCursor(Qt.CursorShape.SizeVerCursor)

    def _set_channel_bound_ui(self, channel_id, display_name):

        if hasattr(self, '_channel_entry'):

            self._channel_entry.setText(channel_id)

            self._channel_entry.setReadOnly(True)

        if hasattr(self, '_channel_status_label'):

            self._channel_status_label.setText(f"Bound: {display_name}")

            self._channel_status_label.setStyleSheet(f"color: {SUCCESS_COLOR}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

        if hasattr(self, '_bind_channel_btn'):

            self._bind_channel_btn.setVisible(False)

        if hasattr(self, '_unbind_channel_btn'):
            self._unbind_channel_btn.setVisible(True)
        self._update_chat_status_labels()

    def _update_open_dialogs(self):

        for child in self.findChildren(QDialog):

            if child.isVisible() and child.isModal():

                if hasattr(child, '_dialog_w_factor'):

                    _dialog_adaptive(

                        child, self,

                        child._dialog_w_factor,

                        child._dialog_h_factor,

                        child._dialog_min_w,

                        child._dialog_min_h

                    )

    def _scale_fonts(self):

        global GLOBAL_FONT_SIZE

        w = self.width()

        scale = max(0.7, min(1.6, w / self._base_width))

        new_size = max(9, int(self._base_font_size * scale))

        if abs(GLOBAL_FONT_SIZE - new_size) >= 1:

            GLOBAL_FONT_SIZE = new_size

            font = self.font()

            font.setPixelSize(new_size)

            self.setFont(font)

            self._apply_transparency()

    def _apply_transparency(self, pct=None):

        if pct is None:

            try:

                raw = str(self.config_mgr.get("general", "transparency", "90")).strip("\\ '")

                pct = int(raw)

            except Exception:

                pct = 90

        pct = max(10, min(100, int(pct)))

        self.setWindowOpacity(pct / 100.0)

    def _is_over_detached_window(self, obj):

        from gui.detach import DetachedWindow

        parent = obj.parent() if hasattr(obj, 'parent') else None

        while parent is not None:

            if isinstance(parent, DetachedWindow):

                return True

            parent = parent.parent() if hasattr(parent, 'parent') else None

        return False

    def _highlight_tab_bar(self):

        tab_bar = self.findChild(QFrame, "tabBar")

        if tab_bar and not hasattr(self, '_tab_bar_highlighted'):

            self._tab_bar_original_style = tab_bar.styleSheet()

            tab_bar.setStyleSheet(f"""

                QFrame#tabBar {{

                    background-color: {BG_COLOR};

                    border-bottom: 2px solid {ACCENT_LIME};

                }}

            """)

            self._tab_bar_highlighted = True

    def _unhighlight_tab_bar(self):

        tab_bar = self.findChild(QFrame, "tabBar")

        if tab_bar and hasattr(self, '_tab_bar_highlighted'):

            tab_bar.setStyleSheet(self._tab_bar_original_style)

            del self._tab_bar_highlighted

            if hasattr(self, '_tab_bar_original_style'):

                del self._tab_bar_original_style

    def _apply_truncation_config(self, val):

        try:

            ratio = int(val) / 100.0

            ratio = max(0.1, min(5.0, ratio))

            if hasattr(self, 'wheel_widget'):

                self.wheel_widget.set_truncation_ratio(ratio)

        except:

            pass

    def _apply_startup_config(self):

        cfg = self.config_mgr

        if hasattr(self, 'add_sector_btn'):

            self.add_sector_btn.setVisible(cfg.get("wheels", "show_add_sector", True))

        if hasattr(self, 'equalize_btn'):

            self.equalize_btn.setVisible(cfg.get("wheels", "show_equalize", True))

        if hasattr(self, 'del_wheel_btn'):

            self.del_wheel_btn.setVisible(cfg.get("wheels", "show_delete", True))

        if hasattr(self, 'rename_wheel_btn'):

            self.rename_wheel_btn.setVisible(cfg.get("wheels", "show_rename", True))

        if hasattr(self, 'auto_color_row'):

            self.auto_color_row.setVisible(cfg.get("wheels", "show_auto_color", True))

        if hasattr(self, 'random_color_row'):

            self.random_color_row.setVisible(cfg.get("wheels", "show_random_color", True))

        if hasattr(self, 'general_color_row'):

            self.general_color_row.setVisible(cfg.get("wheels", "show_general_color", True))

        if hasattr(self, 'manual_add_row'):

            self.manual_add_row.setVisible(cfg.get("lottery", "show_manual_add", True))

        if hasattr(self, '_case_add_prize_btn'):

            self._case_add_prize_btn.setVisible(cfg.get("case", "show_add_prize", True))

        if hasattr(self, '_case_equalize_btn'):

            self._case_equalize_btn.setVisible(cfg.get("case", "show_equalize", True))

        if hasattr(self, '_case_auto_color_row'):

            self._case_auto_color_row.setVisible(cfg.get("case", "show_auto_color", True))

        if hasattr(self, '_case_random_color_row'):

            self._case_random_color_row.setVisible(cfg.get("case", "show_random_color", True))

        if hasattr(self, '_case_general_color_row'):
            self._case_general_color_row.setVisible(cfg.get("case", "show_general_color", True))

        # ── Tutorial on first launch ──
        if not cfg.get("general", "tutorial_shown", False):
            QTimer.singleShot(800, self._show_tutorial)

        # Auto-connect Twitch if channel was saved
        if hasattr(self, 'twitch_bot') and self.twitch_bot is None:
            tchan = cfg.get('twitch', 'channel_name', '')
            if tchan:
                QTimer.singleShot(500, lambda: self._connect_twitch(silent=True))

    def _update_chat_status_labels(self):
        if not hasattr(self, '_chat_twitch_status'):
            return
        # Twitch status
        tchan = self.config_mgr.get('twitch', 'channel_name', '')
        tbot = getattr(self, 'twitch_bot', None)
        if tchan and tbot and tbot.is_connected():
            self._chat_twitch_status.setText(tchan)
            self._chat_twitch_status.setStyleSheet(
                f"color: #9146FF; font-size: 11px; font-weight: 600;"
            )
        else:
            self._chat_twitch_status.setText("None")
            self._chat_twitch_status.setStyleSheet(
                f"color: {TEXT_SEC}; font-size: 11px;"
            )
        # YouTube status
        ychan = self.config_mgr.get('youtube', 'channel_name', '')
        yt_ok = getattr(self, 'bot', None) is not None
        if ychan and yt_ok:
            self._chat_yt_status.setText(ychan)
            self._chat_yt_status.setStyleSheet(
                f"color: #FF0000; font-size: 11px; font-weight: 600;"
            )
        else:
            self._chat_yt_status.setText("None")
            self._chat_yt_status.setStyleSheet(
                f"color: {TEXT_SEC}; font-size: 11px;"
            )

    def _on_chat_sidebar_view_changed(self, view_id: str):
        """Handle sidebar view change (main chat or individual channel)."""
        pass  # Sidebar already handles this via ChatManager.set_view

    def _on_chat_sidebar_remove(self, connection_id: str):
        """Handle remove connection from sidebar."""
        if hasattr(self, '_remove_connection_ui'):
            self._remove_connection_ui(connection_id)

    def _show_tutorial(self):
        """Show the onboarding tutorial overlay."""
        from gui.widgets.tutorial_overlay import TutorialOverlay
        self._tutorial = TutorialOverlay(self)
        self._tutorial.finished.connect(self._on_tutorial_finished)
        self._tutorial.step_changed.connect(self._on_tutorial_step)

        # Build tutorial steps
        steps = [
            {
                "title": "WELCOME TO DROPZONE",
                "text": "This is your all-in-one tool for chat lotteries on YouTube and Twitch. "
                        "Let's take a quick tour of the main features.",
                "target": None,
                "padding": 0,
                "tab_index": None,
                "sub_index": None,
            },
            {
                "title": "TITLE BAR",
                "text": "Drag the window by this bar. Use the buttons to minimize, maximize, or close the app. "
                        "You can also detach tabs as separate windows.",
                "target": self.title_bar,
                "padding": 4,
                "tab_index": None,
                "sub_index": None,
            },
            {
                "title": "TAB BAR",
                "text": "Switch between sections: Main (Lottery + Chat), Wheel, Case, Dice, and Config. "
                        "Each tab opens a different workspace.",
                "target": self.tab_bar,
                "padding": 4,
                "tab_index": None,
                "sub_index": None,
            },
            {
                "title": "MAIN — LOTTERY",
                "text": "Run your giveaways here. Set a keyword (e.g. !join), manage participants, "
                        "and pick winners. Connect to YouTube/Twitch chat to collect entries automatically.",
                "target": self.lottery_section,
                "padding": 8,
                "tab_index": 0,
                "sub_index": 0,
            },
            {
                "title": "MAIN — CHAT",
                "text": "View live chat from all connected streams. Right-click on a username to moderate "
                        "(ban, timeout, delete message). Use the sidebar to switch between channels.",
                "target": self.chat_widget,
                "padding": 8,
                "tab_index": 0,
                "sub_index": 1,
            },
            {
                "title": "WHEEL",
                "text": "Create custom prize wheels with colored sectors. Spin to randomly select a winner "
                        "from your participants. Add, remove, and edit sectors freely.",
                "target": self.wheel_section,
                "padding": 8,
                "tab_index": 1,
                "sub_index": None,
            },
            {
                "title": "CASE",
                "text": "Open cases with random rewards. Configure prizes, probabilities, and animations. "
                        "Perfect for mystery giveaways.",
                "target": self.stack if hasattr(self, 'stack') else None,
                "padding": 8,
                "tab_index": 1,
                "sub_index": None,
            },
            {
                "title": "DICE",
                "text": "Roll digital dice with custom faces. Great for quick decisions or mini-games "
                        "during your stream.",
                "target": None,
                "padding": 0,
                "tab_index": 1,
                "sub_index": None,
            },
            {
                "title": "CONFIG",
                "text": "Configure everything: API connections (YouTube OAuth, Twitch), appearance, "
                        "lottery settings, chat display, notifications, and more. "
                        "You can always replay this tutorial from the Config → How to use section.",
                "target": self.config_section,
                "padding": 8,
                "tab_index": 3,
                "sub_index": None,
            },
        ]
        self._tutorial.set_steps(steps)
        self._tutorial.start()

    def _on_tutorial_finished(self):
        self.config_mgr.set("general", "tutorial_shown", True)

    def _on_tutorial_step(self, step_index):
        """Switch to the tab and sub-panel corresponding to the current tutorial step."""
        step = self._tutorial._steps[step_index] if hasattr(self, '_tutorial') and self._tutorial._steps else None
        if step:
            tab_idx = step.get("tab_index")
            if tab_idx is not None and 0 <= tab_idx < len(self.tab_btns):
                self.tab_btns[tab_idx].click()
            # Switch sub-panel (e.g. Lottery ↔ Chat)
            sub_idx = step.get("sub_index")
            if sub_idx is not None and hasattr(self, '_switch_main_sub_panel'):
                QTimer.singleShot(250, lambda idx=sub_idx: self._switch_main_sub_panel(idx))

    class _ParticipantSignal(QObject):

        add_participant = pyqtSignal(str)

        error_occurred = pyqtSignal(str)

    def load_credentials(self):

        if TOKEN_PATH.exists():

            with TOKEN_PATH.open("rb") as f:

                return pickle.load(f)

        return None

    def _setup_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.setSpacing(0)

        self.title_bar = TitleBar(self)

        main_layout.addWidget(self.title_bar)

        self.tab_bar = TabBarTemplate()
        self.tab_btns = self.tab_bar.tab_btns
        self.glow_line = self.tab_bar.glow_line

        for btn in self.tab_btns:
            btn.clicked.connect(self._on_tab_btn_clicked)
            btn.installEventFilter(self)

        main_layout.addWidget(self.tab_bar)

        self.stack = QStackedWidget()

        main_layout.addWidget(self.stack)

        self.lottery_page = QWidget()

        self.wheel_page = WheelTabPage()

        self.logs_page = QWidget()

        self.config_page = QWidget()

        self.lottery_section = DetachableSection(self.lottery_page, "MAIN")

        self.wheel_section = DetachableSection(self.wheel_page, "WHEEL")

        self.logs_section = DetachableSection(self.logs_page, "LOGS")

        self.config_section = DetachableSection(self.config_page, "CONFIG")

        self._tab_sections = [

            self.lottery_section,

            self.wheel_section,

            self.logs_section,

            self.config_section,

        ]

        for sec in self._tab_sections:

            sec.section_detached.connect(self._on_section_detached)

        self.stack.addWidget(self.lottery_section)

        self.stack.addWidget(self.wheel_section)

        self.stack.addWidget(self.logs_section)

        self.stack.addWidget(self.config_section)

        self._setup_main_tab()

        self._setup_wheel_tab()

        self._setup_logs_tab()

        self._setup_config_tab()

        self._load_whitelist_participants()

        self.stack.setCurrentIndex(0)

        self.tab_btns[0].setStyleSheet(f"""

            QPushButton {{

                background: transparent;

                border: none;

                color: {ACCENT_LIME};

                font-size: 12px;

                font-weight: 800;

                letter-spacing: 0.8px;

                text-transform: uppercase;

                padding: 0 24px;

                font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

            }}

            QPushButton:hover {{

                color: {ACCENT_LIME};

            }}

            QPushButton:focus {{

                outline: none;

            }}

        """)

    def _switch_tab_by_index(self, idx):

        if self.stack.currentIndex() == idx:

            return

        for i, btn in enumerate(self.tab_btns):

            if i == idx:

                btn.setStyleSheet(f"""

                    QPushButton {{

                        background: transparent;

                        border: none;

                        color: {ACCENT_LIME};

                        font-size: 12px;

                        font-weight: 800;

                        letter-spacing: 0.8px;

                        text-transform: uppercase;

                        padding: 0 24px;

                        font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

                    }}

                    QPushButton:hover {{

                        color: {ACCENT_LIME};

                    }}

                    QPushButton:focus {{

                        outline: none;

                    }}

                """)

            else:

                btn.setStyleSheet(f"""

                    QPushButton {{

                        background: transparent;

                        border: none;

                        color: {TEXT_SEC};

                        font-size: 12px;

                        font-weight: 800;

                        letter-spacing: 0.8px;

                        text-transform: uppercase;

                        padding: 0 24px;

                        font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

                    }}

                    QPushButton:hover {{

                        color: {TEXT_MAIN};

                    }}

                """)

        self.stack.setCurrentIndex(idx)

        bar_w = self.tab_bar.width()

        tab_btn = self.tab_btns[idx]

        tab_x = tab_btn.x()

        tab_w = tab_btn.width()

        self.glow_line.raise_()

        self._animate_glow_line(tab_x, tab_w, bar_w)

        if idx == 0:

            self._show_main_sub_nav()

            self._switch_main_sub_panel(0)

        elif idx == 1:

            self._show_sub_nav()

            self._switch_sub_panel(0)

        else:

            if hasattr(self, '_sub_nav_visible') and self._sub_nav_visible:

                self._sub_nav_visible = False

                self._animate_sub_nav(False)

            if hasattr(self, '_main_sub_nav_visible') and self._main_sub_nav_visible:

                self._main_sub_nav_visible = False

                self._animate_main_sub_nav(False)

    def _on_tab_btn_clicked(self):

        btn = self.sender()

        if btn in self.tab_btns:

            idx = self.tab_btns.index(btn)

            self._switch_tab_by_index(idx)

    def _fade_tab_button(self, btn, show, duration=200):

        if show:

            btn.setGraphicsEffect(None)

            btn.setVisible(True)

        else:

            btn.setVisible(False)

    def _on_section_detached(self, section, is_detached):

        for i in range(self.stack.count()):

            if self.stack.widget(i) is section:

                if i < len(self.tab_btns):

                    self._fade_tab_button(self.tab_btns[i], not is_detached, duration=200)

                if is_detached and self.stack.currentIndex() == i:

                    for j, btn in enumerate(self.tab_btns):

                        if btn.isVisible():

                            self._switch_tab_by_index(j)

                            break

                break

    def _update_glow_line_for_current(self):

        idx = self.stack.currentIndex()

        if idx < 0 or idx >= len(self.tab_btns):

            return

        tab_bar = self.tab_btns[0].parent()

        bar_w = tab_bar.width()

        tab_btn = self.tab_btns[idx]

        self.glow_line.raise_()

        self.glow_line.setGeometry(tab_btn.x(), 36, tab_btn.width(), 2)

    def _animate_glow_line(self, start_x, start_w, total_w):

        self._glow_anim = QVariantAnimation(self)

        self._glow_anim.setDuration(350)

        self._glow_anim.setStartValue(0.0)

        self._glow_anim.setEndValue(1.0)

        self._glow_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        def on_glow_val(t):

            x = int(start_x * (1 - t))

            w = int(start_w + (total_w - start_w) * t)

            self.glow_line.setGeometry(x, 36, w, 2)

        self._glow_anim.valueChanged.connect(on_glow_val)

        self._glow_anim.start(QVariantAnimation.DeletionPolicy.DeleteWhenStopped)

    def _show_tab_drag_preview(self, section, pos):

        if self._tab_drag_preview is not None:

            self._tab_drag_preview.close()

            self._tab_drag_preview.deleteLater()

            self._tab_drag_preview = None

        idx = self._tab_drag_active_idx

        if idx < 0 or idx >= len(self.tab_btns):

            return

        tab_name = self.tab_btns[idx].text()

        preview = QFrame()

        preview.setWindowFlags(

            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint

        )

        preview.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        preview.setStyleSheet(f"""

            QFrame {{

                background-color: {CARD_COLOR};

                border: 1px solid {ACCENT_LIME};

                border-radius: 8px;

            }}

        """)

        layout = QHBoxLayout(preview)

        layout.setContentsMargins(12, 6, 12, 6)

        lbl = QLabel(f"\u2B61  {tab_name}")

        lbl.setStyleSheet(f"""

            color: {ACCENT_LIME}; font-size: 12px; font-weight: 700;

            background: transparent; border: none;

        """)

        layout.addWidget(lbl)

        preview.setFixedSize(lbl.sizeHint().width() + 40, 34)

        preview.move(pos - QPoint(preview.width() // 2, preview.height() // 2))

        preview.show()

        self._tab_drag_preview = preview

    def _show_sub_drag_preview(self, section, pos):

        if self._tab_drag_preview is not None:

            self._tab_drag_preview.close()

            self._tab_drag_preview.deleteLater()

            self._tab_drag_preview = None

        idx = self._sub_drag_active_idx

        if idx < 0 or idx >= len(self.sub_nav_btns):

            return

        name = self.sub_nav_btns[idx].text()

        preview = QFrame()

        preview.setWindowFlags(

            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint

        )

        preview.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        preview.setStyleSheet(f"""

            QFrame {{

                background-color: {CARD_COLOR};

                border: 1px solid {ACCENT_CYAN};

                border-radius: 8px;

            }}

        """)

        layout = QHBoxLayout(preview)

        layout.setContentsMargins(12, 6, 12, 6)

        lbl = QLabel(f"\u25C8  {name}")

        lbl.setStyleSheet(f"""

            color: {ACCENT_CYAN}; font-size: 12px; font-weight: 700;

            background: transparent; border: none;

        """)

        layout.addWidget(lbl)

        preview.setFixedSize(lbl.sizeHint().width() + 40, 34)

        preview.move(pos - QPoint(preview.width() // 2, preview.height() // 2))

        preview.show()

        self._tab_drag_preview = preview

    def _show_main_sub_drag_preview(self, section, pos):

        if self._tab_drag_preview is not None:

            self._tab_drag_preview.close()

            self._tab_drag_preview.deleteLater()

            self._tab_drag_preview = None

        idx = self._main_sub_drag_active_idx

        if idx < 0 or idx >= len(self.main_sub_nav_btns):

            return

        name = self.main_sub_nav_btns[idx].text()

        preview = QFrame()

        preview.setWindowFlags(

            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint

        )

        preview.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        preview.setStyleSheet(f"""

            QFrame {{

                background-color: {CARD_COLOR};

                border: 1px solid {ACCENT_CYAN};

                border-radius: 8px;

            }}

        """)

        layout = QHBoxLayout(preview)

        layout.setContentsMargins(12, 6, 12, 6)

        lbl = QLabel(f"\u25C6  {name}")

        lbl.setStyleSheet(f"""

            color: {ACCENT_CYAN}; font-size: 12px; font-weight: 700;

            background: transparent; border: none;

        """)

        layout.addWidget(lbl)

        preview.setFixedSize(lbl.sizeHint().width() + 40, 34)

        preview.move(pos - QPoint(preview.width() // 2, preview.height() // 2))

        preview.show()

        self._tab_drag_preview = preview

    def _hide_tab_drag_preview(self):

        if self._tab_drag_preview is not None:

            self._tab_drag_preview.close()

            self._tab_drag_preview.deleteLater()

            self._tab_drag_preview = None

    def _do_wheel_switch(self, delta):

        total = self._panels_stack.count()

        if total <= 1:

            return

        cur = self._panels_stack.currentIndex()

        if delta > 0:

            cur = (cur - 1) % total

        else:

            cur = (cur + 1) % total

        self._show_sub_nav()

        self._switch_sub_panel(cur)

    def _animate_sub_nav(self, show):

        if hasattr(self, '_sub_nav_anim'):

            try:

                if self._sub_nav_anim.state() == QVariantAnimation.State.Running:

                    self._sub_nav_anim.stop()

            except RuntimeError:

                pass

        target_h = 32 if show else 0

        start_h = 0 if show else 32

        if show:

            page = self.wheel_page

            self.sub_nav.setGeometry(0, 0, page.width(), 32)

            self.sub_nav.show()

            self.sub_nav.raise_()

            self.sub_nav.setFixedHeight(0)

        self._sub_nav_anim = QVariantAnimation(self)

        self._sub_nav_anim.setDuration(200)

        self._sub_nav_anim.setStartValue(float(start_h))

        self._sub_nav_anim.setEndValue(float(target_h))

        self._sub_nav_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        def on_anim(val):

            self.sub_nav.setFixedHeight(int(val))

        self._sub_nav_anim.valueChanged.connect(on_anim)

        if not show:

            self._sub_nav_anim.finished.connect(lambda: self.sub_nav.hide() if not self._sub_nav_visible else None)

        self._sub_nav_anim.start(QVariantAnimation.DeletionPolicy.DeleteWhenStopped)

    def _show_sub_nav(self):

        self._sub_nav_hover_timer.stop()

        if self.stack.currentIndex() != 1:

            return

        if not self._sub_nav_visible:

            self._sub_nav_visible = True

            page = self.wheel_page

            self.sub_nav.setGeometry(0, 0, page.width(), 32)

            self._animate_sub_nav(True)

    def _check_sub_nav_hide(self):

        if self.stack.currentIndex() != 1:

            if self._sub_nav_visible:

                self._sub_nav_visible = False

                self._animate_sub_nav(False)

        elif self._sub_nav_visible:

            self._sub_nav_visible = False

            self._animate_sub_nav(False)

    def _update_sub_nav_active(self, idx):

        for i, btn in enumerate(self.sub_nav_btns):

            if i == idx:

                btn.setStyleSheet(f"""

                    QPushButton {{

                        background: transparent;

                        border: none;

                        color: {ACCENT_LIME};

                        font-size: 11px;

                        font-weight: 700;

                        letter-spacing: 0.6px;

                        text-transform: uppercase;

                        padding: 0;

                        font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

                    }}

                    QPushButton:hover {{

                        color: {ACCENT_LIME};

                    }}

                """)

            else:

                btn.setStyleSheet(f"""

                    QPushButton {{

                        background: transparent;

                        border: none;

                        color: {TEXT_SEC};

                        font-size: 11px;

                        font-weight: 700;

                        letter-spacing: 0.6px;

                        text-transform: uppercase;

                        padding: 0;

                        font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

                    }}

                    QPushButton:hover {{

                        color: {TEXT_MAIN};

                    }}

                """)

    def _switch_sub_panel(self, idx):

        self._update_sub_nav_active(idx)

        if hasattr(self, '_panels_stack'):

            self._panels_stack.setCurrentIndex(idx)

    def _do_main_wheel_switch(self, delta):

        total = self._main_panels_stack.count()

        if total <= 1:

            return

        cur = self._main_panels_stack.currentIndex()

        if delta > 0:

            cur = (cur - 1) % total

        else:

            cur = (cur + 1) % total

        self._show_main_sub_nav()

        self._switch_main_sub_panel(cur)

    def _switch_main_sub_panel(self, idx):

        self._update_main_sub_nav_active(idx)

        if hasattr(self, '_main_panels_stack'):

            self._main_panels_stack.setCurrentIndex(idx)

    def _update_main_sub_nav_active(self, idx):

        for i, btn in enumerate(self.main_sub_nav_btns):

            if i == idx:

                btn.setStyleSheet(f"""

                    QPushButton {{

                        background: transparent;

                        border: none;

                        color: {ACCENT_LIME};

                        font-size: 11px;

                        font-weight: 700;

                        letter-spacing: 0.6px;

                        text-transform: uppercase;

                        padding: 0 16px;

                        font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

                    }}

                    QPushButton:hover {{

                        color: {ACCENT_LIME};

                    }}

                """)

            else:

                btn.setStyleSheet(f"""

                    QPushButton {{

                        background: transparent;

                        border: none;

                        color: {TEXT_SEC};

                        font-size: 11px;

                        font-weight: 700;

                        letter-spacing: 0.6px;

                        text-transform: uppercase;

                        padding: 0 16px;

                        font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

                    }}

                    QPushButton:hover {{

                        color: {TEXT_MAIN};

                    }}

                """)

    def _animate_main_sub_nav(self, show):

        if hasattr(self, '_main_sub_nav_anim'):

            try:

                if self._main_sub_nav_anim.state() == QVariantAnimation.State.Running:

                    self._main_sub_nav_anim.stop()

            except RuntimeError:

                pass

        target_h = 32 if show else 0

        start_h = 0 if show else 32

        if show:

            page = self.lottery_page

            self.main_sub_nav.setGeometry(0, 0, page.width(), 32)

            self.main_sub_nav.show()

            self.main_sub_nav.raise_()

            self.main_sub_nav.setFixedHeight(0)

        self._main_sub_nav_anim = QVariantAnimation(self)

        self._main_sub_nav_anim.setDuration(200)

        self._main_sub_nav_anim.setStartValue(float(start_h))

        self._main_sub_nav_anim.setEndValue(float(target_h))

        self._main_sub_nav_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        def on_anim(val):

            self.main_sub_nav.setFixedHeight(int(val))

        self._main_sub_nav_anim.valueChanged.connect(on_anim)

        if not show:

            self._main_sub_nav_anim.finished.connect(lambda: self.main_sub_nav.hide() if not self._main_sub_nav_visible else None)

        self._main_sub_nav_anim.start(QVariantAnimation.DeletionPolicy.DeleteWhenStopped)

    def _show_main_sub_nav(self):

        self._main_sub_nav_hover_timer.stop()

        if self.stack.currentIndex() != 0:

            return

        if not self._main_sub_nav_visible:

            self._main_sub_nav_visible = True

            page = self.lottery_page

            self.main_sub_nav.setGeometry(0, 0, page.width(), 32)

            self._animate_main_sub_nav(True)

    def _check_main_sub_nav_hide(self):

        if self.stack.currentIndex() != 0:

            if self._main_sub_nav_visible:

                self._main_sub_nav_visible = False

                self._animate_main_sub_nav(False)

        elif self._main_sub_nav_visible:

            self._main_sub_nav_visible = False

            self._animate_main_sub_nav(False)