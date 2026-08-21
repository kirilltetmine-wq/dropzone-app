"""
ui_kit_pages — шаблоны страниц
  T001: TabBarTemplate(parent) — панель вкладок
  T002: WheelTabTemplate(parent) — вкладка колеса
  T003: LotteryTabTemplate(parent) — вкладка лотереи
  T004: ConfigTabTemplate(parent) — вкладка настроек
  T005: LogsTabTemplate(parent) — вкладка логов
"""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QScrollArea, QSplitter, QStackedWidget, QSizePolicy,
)

from core.theme import (
    BG_COLOR, CARD_COLOR, CARD_LIGHT, ACCENT_CYAN, ACCENT_LIME,
    TEXT_MAIN, TEXT_SEC, BORDER_COLOR, FONT_FAMILY,
    PLUS_PATH, APP_DIR, SUCCESS_COLOR, DANGER_COLOR,
)

from .ui_kit_buttons import GlowButton, HoverIconButton, RoundedButton, TabButton
from .ui_kit_inputs import RoundedLineEdit, WheelDropdown, ToggleSwitch, ModernSlider
from .ui_kit_widgets import WheelWidget
from .ui_kit_windows import DetachablePanel

# ============================================================================
#                    T001: TabBarTemplate
# ============================================================================

class TabBarTemplate(QFrame):
    """
    [T001]  Панель вкладок (MAIN / WHEEL / LOGS / CONFIG)
    ───────
    Использование:
        tab_bar = TabBarTemplate()
        tab_bar.tab_names = ["MAIN", "WHEEL", "LOGS", "CONFIG"]
        tab_bar.setup(stack_widget)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tabBar")
        self.setStyleSheet(f"""
            QFrame#tabBar {{
                background-color: {BG_COLOR};
                border-bottom: 1px solid {BORDER_COLOR};
            }}
        """)
        self.setFixedHeight(38)

        self.tab_btns = []
        self.glow_line = None
        self.tab_names = ["MAIN", "WHEEL", "LOGS", "CONFIG"]
        self._stack = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for name in self.tab_names:
            btn = QPushButton(name, self)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: none;
                    color: {TEXT_SEC}; font-size: 12px; font-weight: 800;
                    letter-spacing: 0.8px; text-transform: uppercase;
                    padding: 0 24px;
                    font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
                }}
                QPushButton:hover {{ color: {TEXT_MAIN}; }}
            """)
            btn.setMinimumHeight(38)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            layout.addWidget(btn, 1)
            self.tab_btns.append(btn)

        self.glow_line = QFrame(self)
        self.glow_line.setFixedHeight(2)
        self.glow_line.setStyleSheet(f"""
            background-color: {ACCENT_LIME}; border-radius: 1px;
        """)
        self.glow_line.setGeometry(0, 36, self.width(), 2)
        self.glow_line.lower()

    def connect_to_stack(self, stack: QStackedWidget):
        """Привязать кнопки к QStackedWidget"""
        self._stack = stack
        for i, btn in enumerate(self.tab_btns):
            btn.clicked.connect(lambda checked, idx=i: self._switch(idx))

    def _switch(self, idx):
        if self._stack:
            self._stack.setCurrentIndex(idx)
        for i, btn in enumerate(self.tab_btns):
            active = (i == idx)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: none;
                    color: {ACCENT_LIME if active else TEXT_SEC};
                    font-size: 12px; font-weight: 800;
                    letter-spacing: 0.8px; text-transform: uppercase;
                    padding: 0 24px;
                    font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
                }}
                QPushButton:hover {{ color: {ACCENT_LIME if active else TEXT_MAIN}; }}
            """)
        if self._stack:
            tab_btn = self.tab_btns[idx]
            self.glow_line.setGeometry(tab_btn.x(), 36, tab_btn.width(), 2)
            self.glow_line.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.glow_line and self.tab_btns:
            idx = self._stack.currentIndex() if self._stack else 0
            if idx < len(self.tab_btns):
                tab_btn = self.tab_btns[idx]
                self.glow_line.setGeometry(tab_btn.x(), 36, tab_btn.width(), 2)

# ============================================================================
#                    T002: WheelTabTemplate
# ============================================================================

class WheelTabTemplate(QWidget):
    """
    [T002]  Вкладка колеса: QSplitter(wheel_area + sidebar_configurator)
    ───────
    Использование:
        wheel_page = WheelTabTemplate()
        stack.addWidget(wheel_page)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(5)
        splitter.setChildrenCollapsible(False)
        layout.addWidget(splitter)

        # -- Левая часть: колесо --
        wheel_area = QWidget()
        wheel_area.setMinimumWidth(400)
        wheel_layout = QVBoxLayout(wheel_area)
        wheel_layout.setContentsMargins(30, 20, 20, 20)

        header = QHBoxLayout()
        wheel_layout.addLayout(header)

        self.wheel_combo = WheelDropdown()
        self.wheel_combo.setPlaceholderText("Select wheel...")
        header.addWidget(self.wheel_combo, 1)

        self.btn_frame = QHBoxLayout()
        self.btn_frame.setSpacing(4)
        header.addLayout(self.btn_frame)

        self.add_btn = HoverIconButton(PLUS_PATH, PLUS_PATH)
        self.add_btn.setFixedSize(36, 36)
        self.add_btn.setIconSize(self.add_btn.size())
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; padding: 0; }
            QPushButton:hover { background: rgba(255,255,255,12); border-radius: 18px; }
        """)
        self.btn_frame.addWidget(self.add_btn)

        self.del_btn = GlowButton("DELETE", "ghost")
        self.btn_frame.addWidget(self.del_btn)
        self.rename_btn = GlowButton("RENAME", "ghost")
        self.btn_frame.addWidget(self.rename_btn)
        self.manage_btn = GlowButton("MANAGE", "ghost")
        self.btn_frame.addWidget(self.manage_btn)

        self.wheel_widget = WheelWidget()
        self.wheel_widget.set_segments([
            {"prize": "Prize 1", "chance": 25, "color": "#FF3B30"},
            {"prize": "Prize 2", "chance": 25, "color": "#FF9500"},
            {"prize": "Prize 3", "chance": 25, "color": "#CCFF00"},
            {"prize": "Prize 4", "chance": 25, "color": "#00F5FF"},
        ])
        self.wheel_layout = wheel_layout
        self.wheel_layout.addWidget(self.wheel_widget, 1)

        self.spin_btn = GlowButton("SPIN WHEEL", "lime")
        self.wheel_layout.addWidget(self.spin_btn, 0, Qt.AlignmentFlag.AlignCenter)

        splitter.addWidget(wheel_area)

        # -- Правая часть: конфигуратор --
        sidebar = QFrame()
        sidebar.setMinimumWidth(280)
        sidebar.setObjectName("sidebarFrame")
        sidebar.setStyleSheet("QFrame#sidebarFrame { background-color: transparent; border: 1px solid #232326; border-radius: 20px; }")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        side_scroll = QScrollArea()
        side_scroll.setWidgetResizable(True)
        side_scroll.setStyleSheet("""
            QScrollArea { background-color: transparent; border: none; }
        """)

        side_content = QWidget()
        side_content.setStyleSheet("background-color: transparent;")
        self.side_layout = QVBoxLayout(side_content)
        self.side_layout.setContentsMargins(30, 40, 30, 40)

        side_scroll.setWidget(side_content)
        sidebar_layout.addWidget(side_scroll)

        config_title = QLabel("WHEEL CONFIGURATOR")
        config_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        config_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.side_layout.addWidget(config_title)

        # Auto Color
        self.auto_color_row = QWidget()
        self.auto_color_row.setStyleSheet("background: transparent;")
        toggle_row = QHBoxLayout(self.auto_color_row)
        toggle_row.setContentsMargins(0, 0, 0, 0)
        self.side_layout.addWidget(self.auto_color_row)
        toggle_label = QLabel("Auto Color Gradient")
        toggle_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px;")
        toggle_row.addWidget(toggle_label)
        toggle_row.addStretch()
        self.auto_toggle = ToggleSwitch(initial=True)
        toggle_row.addWidget(self.auto_toggle)

        # Random Colors
        self.random_color_row = QWidget()
        self.random_color_row.setStyleSheet("background: transparent;")
        random_layout = QHBoxLayout(self.random_color_row)
        random_layout.setContentsMargins(0, 0, 0, 0)
        self.side_layout.addWidget(self.random_color_row)
        random_label = QLabel("Random Colors")
        random_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px;")
        random_layout.addWidget(random_label)
        random_layout.addStretch()
        self.random_toggle = ToggleSwitch(initial=False)
        random_layout.addWidget(self.random_toggle)

        # General Color
        self.general_color_row = QWidget()
        self.general_color_row.setStyleSheet("background: transparent;")
        general_layout = QHBoxLayout(self.general_color_row)
        general_layout.setContentsMargins(0, 0, 0, 0)
        self.side_layout.addWidget(self.general_color_row)
        general_label = QLabel("General Color")
        general_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px;")
        general_layout.addWidget(general_label)
        general_layout.addStretch()
        self.general_toggle = ToggleSwitch(initial=False)
        general_layout.addWidget(self.general_toggle)

        # Buttons
        btn_row = QHBoxLayout()
        self.side_layout.addLayout(btn_row)
        self.add_sector_btn = GlowButton("ADD SECTOR", "outline")
        btn_row.addWidget(self.add_sector_btn)
        self.equalize_btn = GlowButton("EQUALIZE", "outline")
        btn_row.addWidget(self.equalize_btn)

        self.side_layout.addSpacing(10)

        detachable_sidebar = DetachablePanel(sidebar, "WHEEL CONFIGURATOR")
        splitter.addWidget(detachable_sidebar)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([700, 400])

# ============================================================================
#                    T003: LotteryTabTemplate
# ============================================================================

class LotteryTabTemplate(QWidget):
    """
    [T003]  Вкладка лотереи: стрим-коннекшн + управление
    ───────
    Использование:
        lottery_page = LotteryTabTemplate()
        lottery_page.start_btn.clicked.connect(self.toggle_collection)
        stack.addWidget(lottery_page)
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)

        conn_card = QFrame()
        conn_card.setObjectName("cardLight")
        conn_layout = QVBoxLayout(conn_card)
        conn_layout.setContentsMargins(30, 20, 30, 20)
        layout.addWidget(conn_card)

        conn_title = QLabel("LIVE STREAM CONNECTION")
        conn_title.setStyleSheet(f"color: {ACCENT_LIME}; font-size: 14px; font-weight: bold;")
        conn_layout.addWidget(conn_title)

        inputs_row = QHBoxLayout()
        conn_layout.addLayout(inputs_row)

        self.video_url_entry = RoundedLineEdit()
        self.video_url_entry.setPlaceholderText("Enter YouTube Video URL / Twitch channel name...")
        inputs_row.addWidget(self.video_url_entry, 1)

        self.keyword_entry = RoundedLineEdit()
        self.keyword_entry.setPlaceholderText("Keyword...")
        self.keyword_entry.setText("!join")
        self.keyword_entry.setMaximumWidth(200)
        inputs_row.addWidget(self.keyword_entry)

        controls_row = QHBoxLayout()
        conn_layout.addLayout(controls_row)

        self.start_btn = GlowButton("START TRACKING", "ghost")
        controls_row.addWidget(self.start_btn)

        self.collect_btn = GlowButton("START COLLECTING", "outline")
        self.collect_btn.setEnabled(False)
        controls_row.addWidget(self.collect_btn)

        self.pick_winner_btn = GlowButton("PICK WINNER", "lime")
        controls_row.addWidget(self.pick_winner_btn)

        self.clear_btn = GlowButton("CLEAR LIST", "ghost")
        controls_row.addWidget(self.clear_btn)

        self.manual_add_row = QWidget()
        self.manual_add_row.setStyleSheet("background: transparent;")
        add_row = QHBoxLayout(self.manual_add_row)
        add_row.setContentsMargins(0, 0, 0, 0)
        conn_layout.addWidget(self.manual_add_row)

        add_label = QLabel("Manual add:")
        add_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px;")
        add_row.addWidget(add_label)

        self.manual_add_entry = RoundedLineEdit()
        self.manual_add_entry.setPlaceholderText("@username")
        self.manual_add_entry.setMaximumWidth(200)
        add_row.addWidget(self.manual_add_entry)
        
        self.add_user_btn = GlowButton("ADD", "outline")
        add_row.addWidget(self.add_user_btn)

        add_row.addStretch()

        toggle_row = QHBoxLayout()
        conn_layout.addLayout(toggle_row)

        gray_label = QLabel("Delete winners")
        gray_label.setFixedWidth(120)
        gray_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px;")
        toggle_row.addWidget(gray_label)

        self.auto_gray_toggle = ToggleSwitch(initial=True)
        toggle_row.addWidget(self.auto_gray_toggle)
        toggle_row.addStretch()

        wheel_toggle_row = QHBoxLayout()
        conn_layout.addLayout(wheel_toggle_row)

        wheel_label = QLabel("Auto wheel")
        wheel_label.setFixedWidth(120)
        wheel_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px;")
        wheel_toggle_row.addWidget(wheel_label)

        self.auto_wheel_toggle = ToggleSwitch(initial=False)
        wheel_toggle_row.addWidget(self.auto_wheel_toggle)
        wheel_toggle_row.addStretch()

        self.status_label = QLabel("STANDBY")
        self.status_label.setStyleSheet(f"color: {TEXT_SEC}; font-weight: bold;")
        toggle_row.addWidget(self.status_label)

        # Connected streams list — in main layout to align with PARTICIPANTS
        conn_list_label = QLabel("CONNECTED STREAMS")
        conn_list_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; margin-top: 12px; margin-bottom: 4px;")
        layout.addWidget(conn_list_label)

        self.connections_container = QWidget()
        self.connections_container.setStyleSheet("background: transparent;")
        self.connections_layout = QVBoxLayout(self.connections_container)
        self.connections_layout.setContentsMargins(0, 0, 0, 0)
        self.connections_layout.setSpacing(4)
        self.connections_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.connections_container)

        self.participants_label = QLabel("PARTICIPANTS")
        self.participants_label.setStyleSheet("font-size: 15px; font-weight: bold; margin-top: 24px; margin-left: 6px;")
        layout.addWidget(self.participants_label)

        scroll = QScrollArea()
        scroll.setObjectName("cardScroll")
        scroll.setWidgetResizable(True)

        self.participants_container = QWidget()
        self.participants_container.setStyleSheet("background-color: transparent; border-radius: 30px;")

        scroll.setWidget(self.participants_container)
        layout.addWidget(scroll, 1)

# ============================================================================
#                    T004: ConfigTabTemplate
# ============================================================================

class ConfigTabTemplate(QWidget):
    """
    [T004]  Вкладка настроек: sidebar + контент
    ───────
    Использование:
        config_page = ConfigTabTemplate()
        stack.addWidget(config_page)
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_COLOR};
                border-right: 1px solid {BORDER_COLOR};
            }}
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 16, 0, 16)
        sidebar_layout.setSpacing(0)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(sidebar)

        sections = [
            ("GENERAL", ["General", "Appearance"]),
            ("WHEEL", ["Wheel", "Segments", "Animation"]),
            ("CASE", ["Case", "Prize"]),
            ("LOTTERY", ["Lottery", "Participants"]),
            ("CHAT", ["Chat", "Commands"]),
        ]

        self._nav_btns = []
        self._content_stack = QStackedWidget()

        for section_name, items in sections:
            lbl = QLabel(section_name)
            lbl.setStyleSheet(f"""
                color: {TEXT_MAIN}; font-size: 10px; font-weight: 700;
                letter-spacing: 1.2px; padding: 10px 20px 4px;
                font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
            """)
            sidebar_layout.addWidget(lbl)

            for item_name in items:
                btn = QPushButton(item_name)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent; border: none;
                        border-left: 2px solid transparent;
                        color: {TEXT_SEC}; font-size: 12px; font-weight: 600;
                        letter-spacing: 0.3px; padding: 8px 0 8px 20px;
                        text-align: left;
                        font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
                    }}
                    QPushButton:hover {{ color: {TEXT_MAIN}; }}
                """)
                sidebar_layout.addWidget(btn)
                self._nav_btns.append(btn)

                content_page = QWidget()
                content_page.setStyleSheet("background: transparent;")
                content_layout = QVBoxLayout(content_page)
                content_layout.setContentsMargins(40, 30, 40, 30)
                placeholder = QLabel(f"[{item_name}] Settings content here")
                placeholder.setStyleSheet(f"color: {TEXT_SEC}; font-size: 14px;")
                content_layout.addWidget(placeholder)
                content_layout.addStretch(1)
                self._content_stack.addWidget(content_page)

        sidebar_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._content_stack)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background: {BG_COLOR}; }}
            QScrollBar:vertical {{
                background: {BG_COLOR}; width: 8px; margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER_COLOR}; border-radius: 4px; min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)
        layout.addWidget(scroll, 1)

        for i, btn in enumerate(self._nav_btns):
            btn.clicked.connect(lambda checked, idx=i: self._content_stack.setCurrentIndex(idx))

# ============================================================================
#                    T005: LogsTabTemplate
# ============================================================================

class LogsTabTemplate(QWidget):
    """
    [T005]  Вкладка логов: таблица + экспорт
    ───────
    Использование:
        logs_page = LogsTabTemplate()
        stack.addWidget(logs_page)
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 30, 50, 30)

        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_LIGHT};
                border: none;
                border-radius: 0;
            }}
        """)
        header_layout = QHBoxLayout(header)
        for text in ["WINNER", "PRIZE", "WHEEL", "TIMESTAMP"]:
            lbl = QLabel(text)
            lbl.setStyleSheet("font-weight: bold;")
            header_layout.addWidget(lbl)
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { background-color: transparent; border: none; }
        """)
        self.logs_container = QWidget()
        self.logs_container.setStyleSheet("background-color: transparent;")
        self.logs_layout = QVBoxLayout(self.logs_container)
        self.logs_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self.logs_container)
        layout.addWidget(scroll, 1)

        self.btn_row = QHBoxLayout()
        self.btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_row.setSpacing(12)
        layout.addLayout(self.btn_row)

        self.export_btn = GlowButton("EXPORT LOGS", "outline")
        self.btn_row.addWidget(self.export_btn)

# ============================================================================
#                           АЛИАСЫ
# ============================================================================

T001 = TabBarTemplate
T002 = WheelTabTemplate
T003 = LotteryTabTemplate
T004 = ConfigTabTemplate
T005 = LogsTabTemplate