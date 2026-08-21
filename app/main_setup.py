from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QVBoxLayout, QStackedWidget, QWidget, QLabel, QFrame, QHBoxLayout, QSplitter, QSizePolicy, QPushButton
from core.theme import *
from core.config import ConfigManager
from gui.widgets.widgets import HoverIconButton, GlowButton, ToggleSwitch, RoundedButton, RoundedLineEdit
from gui.widgets.wheel_widget import WheelWidget
from gui.widgets.chat_widget import ChatWidget
from gui.widgets.dice_widget import DicePanel
from gui.chat import ChatSidebar, ChatListDropdown
from gui.detach import DetachableSection, DetachablePanel
from gui.dialogs.primitives import DragHandle
from gui.dialogs.modern_dialog import show_info
from ui_kit.ui_kit_demo import TabBarTemplate
from gui.titlebar import TitleBar


class MainSetupMixin:
    def _setup_main_tab(self):

        page = self.lottery_page

        page_layout = QVBoxLayout(page)

        page_layout.setContentsMargins(0, 0, 0, 0)

        page_layout.setSpacing(0)

        self._main_panels_stack = QStackedWidget()

        page_layout.addWidget(self._main_panels_stack)

        lottery_panel = QWidget()

        lottery_panel.setStyleSheet("background: transparent;")

        self._setup_lottery_tab(lottery_panel)

        chat_panel = QWidget()

        chat_panel.setStyleSheet("background: transparent;")

        chat_main_layout = QHBoxLayout(chat_panel)

        chat_main_layout.setContentsMargins(0, 0, 0, 0)

        chat_splitter = QSplitter(Qt.Orientation.Horizontal)

        chat_splitter.setHandleWidth(5)

        chat_splitter.setChildrenCollapsible(False)

        chat_main_layout.addWidget(chat_splitter)

        chat_left = QWidget()

        left_layout = QVBoxLayout(chat_left)

        left_layout.setContentsMargins(12, 8, 8, 8)

        self.chat_widget = ChatWidget()

        if self.twitch_bot:

            self.chat_widget.set_twitch_bot(self.twitch_bot)

        if self.bot:

            self.chat_widget.set_youtube_bot(self.bot)

        # Connect to chat_manager for multi-platform polling
        if hasattr(self, 'chat_manager'):
            self.chat_widget.set_chat_manager(self.chat_manager)
            self.chat_manager.set_on_view_changed(
                lambda vid: self.chat_widget.clear_messages()
            )

        left_layout.addWidget(self.chat_widget)

        chat_splitter.addWidget(chat_left)

        chat_right = QFrame()
        chat_right.setObjectName("chatRightPanel")
        chat_right.setStyleSheet(f"""
            QFrame#chatRightPanel {{
                background-color: transparent;
                border: 1px solid {BORDER_COLOR};
                border-radius: 20px;
            }}
        """)
        right_layout = QVBoxLayout(chat_right)
        right_layout.setContentsMargins(20, 16, 20, 16)
        right_layout.setSpacing(0)

        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        right_title = QLabel("CHAT DETAILS")
        right_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_title.setStyleSheet(f"""
            color: {TEXT_MAIN}; font-size: 14px; font-weight: 700;
            letter-spacing: 1.5px; margin-bottom: 12px;
            font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
        """)
        right_layout.addWidget(right_title)

        # ── Channel status ──────────────────────────────────
        status_section = QFrame()
        status_section.setStyleSheet("background: transparent;")
        status_layout = QVBoxLayout(status_section)
        status_layout.setContentsMargins(0, 4, 0, 4)
        status_layout.setSpacing(4)

        twitch_row = QWidget()
        twitch_row.setStyleSheet("background: transparent;")
        twitch_row_layout = QHBoxLayout(twitch_row)
        twitch_row_layout.setContentsMargins(0, 0, 0, 0)
        twitch_row_layout.setSpacing(6)
        twitch_lbl = QLabel("Twitch:")
        twitch_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px;")
        twitch_row_layout.addWidget(twitch_lbl)
        self._chat_twitch_status = QLabel("None")
        self._chat_twitch_status.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px;")
        twitch_row_layout.addWidget(self._chat_twitch_status)
        twitch_row_layout.addStretch()
        status_layout.addWidget(twitch_row)

        yt_row = QWidget()
        yt_row.setStyleSheet("background: transparent;")
        yt_row_layout = QHBoxLayout(yt_row)
        yt_row_layout.setContentsMargins(0, 0, 0, 0)
        yt_row_layout.setSpacing(6)
        yt_lbl = QLabel("YouTube:")
        yt_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px;")
        yt_row_layout.addWidget(yt_lbl)
        self._chat_yt_status = QLabel("None")
        self._chat_yt_status.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px;")
        yt_row_layout.addWidget(self._chat_yt_status)
        yt_row_layout.addStretch()
        status_layout.addWidget(yt_row)

        right_layout.addWidget(status_section)

        # ── Keyword ─────────────────────────────────────────
        kw_section = QFrame()
        kw_section.setStyleSheet("background: transparent;")
        kw_layout = QVBoxLayout(kw_section)
        kw_layout.setContentsMargins(0, 8, 0, 0)
        kw_layout.setSpacing(4)

        kw_label = QLabel("Keyword")
        kw_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 700; letter-spacing: 1.2px;")
        kw_layout.addWidget(kw_label)

        self._chat_keyword_entry = RoundedLineEdit()
        self._chat_keyword_entry.setPlaceholderText("!join")
        kw_default = self.config_mgr.get("lottery", "default_keyword", "!join")
        self._chat_keyword_entry.setText(kw_default)
        kw_layout.addWidget(self._chat_keyword_entry)

        # Sync keyword between lottery and chat tabs
        self._keyword_updating = False
        if hasattr(self, 'keyword_entry'):
            self.keyword_entry.textChanged.connect(
                lambda t: self._sync_keyword(t, from_lottery=True)
            )
            self._chat_keyword_entry.textChanged.connect(
                lambda t: self._sync_keyword(t, from_lottery=False)
            )

        right_layout.addWidget(kw_section)

        right_layout.addSpacing(12)

        # ── Chat List Dropdown (collapsible, like wheel list) ──
        if hasattr(self, 'chat_manager'):
            self.chat_sidebar = ChatListDropdown(self.chat_manager)
            self.chat_sidebar.view_changed.connect(self._on_chat_sidebar_view_changed)
            self.chat_sidebar.remove_connection.connect(self._on_chat_sidebar_remove)
            right_layout.addWidget(self.chat_sidebar)
        right_layout.addSpacing(12)

        search_btn = RoundedButton("  Search")

        search_btn.set_colors(
            bg="transparent", text=TEXT_MAIN, border=BORDER_COLOR,
            hover_bg="#2A2A2A", hover_text=ACCENT_LIME, hover_border=ACCENT_LIME
        )

        search_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        search_btn.setFixedHeight(38)

        search_btn.setIcon(QIcon(str(SEARCH_PATH)))

        search_btn.setIconSize(QSize(16, 16))

        search_btn.clicked.connect(self.chat_widget.toggle_search)

        right_layout.addWidget(search_btn)

        # Wrap in detachable panel
        self.chat_details_panel = DetachablePanel(chat_right, "CHAT DETAILS")
        chat_splitter.addWidget(self.chat_details_panel)

        chat_splitter.setSizes([400, 250])

        self.lottery_section = DetachableSection(lottery_panel, "LOTTERY")

        self.chat_section = DetachableSection(chat_panel, "CHAT")

        self._main_sub_sections = [self.lottery_section, self.chat_section]

        self._main_panels_stack.addWidget(self.lottery_section)

        self._main_panels_stack.addWidget(self.chat_section)

        self._main_panels_stack.setCurrentIndex(0)

        self.main_sub_nav = QFrame(page)

        self.main_sub_nav.setObjectName("mainSubNav")

        self.main_sub_nav.setStyleSheet(f"""

            QFrame#mainSubNav {{

                background-color: {BG_COLOR};

                border-bottom: 1px solid {BORDER_COLOR};

            }}

        """)

        self.main_sub_nav.setFixedHeight(32)

        self.main_sub_nav.hide()

        sub_nav_layout = QHBoxLayout(self.main_sub_nav)

        sub_nav_layout.setContentsMargins(0, 0, 0, 0)

        sub_nav_layout.setSpacing(0)

        self.main_sub_nav_btns = []

        for i, text in enumerate(["LOTTERY", "CHAT"]):

            btn = QPushButton(text, self.main_sub_nav)

            btn.setCursor(Qt.CursorShape.PointingHandCursor)

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

            btn.setFixedHeight(32)

            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            btn.clicked.connect(lambda checked, p=i: self._switch_main_sub_panel(p))

            sub_nav_layout.addWidget(btn, 1)

            self.main_sub_nav_btns.append(btn)

        self._update_main_sub_nav_active(0)

        self.tab_btns[0].installEventFilter(self)

        self.main_sub_nav.installEventFilter(self)

        self._main_sub_nav_visible = False

        self._main_sub_nav_hover_timer = QTimer(self)

        self._main_sub_nav_hover_timer.setSingleShot(True)

        self._main_sub_nav_hover_timer.timeout.connect(self._check_main_sub_nav_hide)