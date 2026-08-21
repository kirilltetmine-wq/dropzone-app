from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import QVBoxLayout, QStackedWidget, QWidget, QLabel, QFrame, QHBoxLayout, QSplitter, QSizePolicy, QLineEdit, QPushButton, QScrollArea, QGraphicsBlurEffect
from core.theme import *
from core.config import ConfigManager
from gui.widgets.widgets import HoverIconButton, GlowButton, ToggleSwitch, WheelDropdown
from gui.widgets.wheel_widget import WheelWidget
from gui.widgets.chat_widget import ChatWidget
from gui.widgets.dice_widget import DicePanel
from gui.chat import ChatSidebar, ChatListDropdown
from gui.detach import DetachableSection
from gui.dialogs.primitives import DragHandle, DropContainer
from gui.dialogs.modern_dialog import show_info
from ui_kit.ui_kit_demo import TabBarTemplate
from gui.widgets.case_strip import _CaseStripWidget
from gui.titlebar import TitleBar
from app.panels import AppWheelPanel


class WheelSetupMixin:
    def _setup_wheel_tab(self):

        page = self.wheel_page

        page_layout = QVBoxLayout(page)

        page_layout.setContentsMargins(0, 0, 0, 0)

        page_layout.setSpacing(0)

        self._panels_stack = QStackedWidget()

        page_layout.addWidget(self._panels_stack)

        wheel_panel = AppWheelPanel()

        # Copy references from template's widgets
        self.wheel_combo = wheel_panel.wheel_combo
        self.wheel_combo.currentIndexChanged.connect(self.on_wheel_selected)

        self.wheel_widget = wheel_panel.wheel_widget
        max_name_len = int(self.config_mgr.get("wheels", "max_name_length", "16"))
        trunc_ratio = int(self.config_mgr.get("wheels", "truncation_threshold", "100")) / 100.0
        self.wheel_widget.set_truncation_ratio(trunc_ratio)
        self._config_max_name_length = max_name_len
        self.wheel_widget.segment_clicked.connect(self.on_segment_clicked)
        self.wheel_widget.selection_changed.connect(self._on_wheel_selection_changed)

        # Connect template button signals
        wheel_panel.add_btn.clicked.connect(self.add_wheel)
        self.del_wheel_btn = wheel_panel.del_btn
        self.del_wheel_btn.clicked.connect(self.delete_wheel)
        self.rename_wheel_btn = wheel_panel.rename_btn
        self.rename_wheel_btn.clicked.connect(self.rename_wheel)
        self.manage_wheel_btn = wheel_panel.manage_btn
        self.manage_wheel_btn.clicked.connect(self._manage_wheel)

        self.spin_btn = wheel_panel.spin_btn
        self.spin_btn.clicked.connect(self.start_spin)

        # Connect toggle signals
        self.auto_toggle = wheel_panel.auto_toggle
        self.auto_toggle.toggled.connect(self.on_auto_color_toggle)
        self.random_toggle = wheel_panel.random_toggle
        self.random_toggle.toggled.connect(self.on_random_toggle)
        self.general_toggle = wheel_panel.general_toggle
        self.general_toggle.toggled.connect(self.on_general_toggle)

        # Connect sector buttons
        self.add_sector_btn = wheel_panel.add_sector_btn
        self.add_sector_btn.clicked.connect(self.add_prize_item)
        self.equalize_btn = wheel_panel.equalize_btn
        self.equalize_btn.clicked.connect(self.balance_chances_equally)

        # Store visibility-controlled rows
        self.auto_color_row = wheel_panel.auto_color_row
        self.random_color_row = wheel_panel.random_color_row
        self.general_color_row = wheel_panel.general_color_row

        # Add prev/next buttons to the template's btn_frame
        prev_wheel_btn = HoverIconButton(LEFT_ARROW_PATH, LEFT_ARROW_PATH)
        prev_wheel_btn.setFixedSize(36, 36)
        prev_wheel_btn.setIconSize(prev_wheel_btn.size())
        prev_wheel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        prev_wheel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 12);
                border-radius: 18px;
            }
        """)
        prev_wheel_btn.clicked.connect(self._prev_wheel)
        wheel_panel.btn_frame.addWidget(prev_wheel_btn)

        next_wheel_btn = HoverIconButton(RIGHT_ARROW_PATH, RIGHT_ARROW_PATH)
        next_wheel_btn.setFixedSize(36, 36)
        next_wheel_btn.setIconSize(next_wheel_btn.size())
        next_wheel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        next_wheel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 12);
                border-radius: 18px;
            }
        """)
        next_wheel_btn.clicked.connect(self._next_wheel)
        wheel_panel.btn_frame.addWidget(next_wheel_btn)

        # Add extra widgets to the wheel area (winner row, confirm prize)
        wheel_layout = wheel_panel.wheel_layout

        winner_row = QWidget()
        winner_row.setStyleSheet("background: transparent;")
        winner_row_layout = QHBoxLayout(winner_row)
        winner_row_layout.setContentsMargins(0, 5, 0, 0)
        winner_row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        winner_lbl = QLabel("Winner:")
        winner_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px;")
        winner_row_layout.addWidget(winner_lbl)
        self.winner_entry = QLineEdit()
        self.winner_entry.setPlaceholderText("nickname")
        self.winner_entry.setFixedWidth(180)
        self.winner_entry.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 9999px;
                color: {TEXT_MAIN};
                font-size: 12px;
                padding: 6px 14px;
                font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
            }}
            QLineEdit:focus {{  border-color: {ACCENT_LIME}; }}
        """)
        winner_row_layout.addWidget(self.winner_entry)
        wheel_layout.addWidget(winner_row, 0, Qt.AlignmentFlag.AlignCenter)

        self.confirm_prize_btn = GlowButton("CONFIRM PRIZE", "lime")
        self.confirm_prize_btn.clicked.connect(self._confirm_prize)
        self.confirm_prize_btn.setVisible(False)
        wheel_layout.addWidget(self.confirm_prize_btn, 0, Qt.AlignmentFlag.AlignCenter)

        # Add cards container to the sidebar
        side_layout = wheel_panel.side_layout

        self.cards_scroll = QScrollArea()
        self.cards_scroll.setWidgetResizable(True)
        self.cards_scroll.setStyleSheet(f"""
            QScrollArea {{  background-color: transparent; border: none; }}
            QScrollBar:vertical {{
                background: transparent;
                width: 10px;
                border-radius: 9999px;
                margin: 0;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background: #8E8E93;
                border-radius: 9999px;
                min-height: 30px;
                margin: 2px;
                border: none;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #CCFF00;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0;
                background: transparent;
                border: none;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: transparent;
                border: none;
            }}
        """)
        self.cards_container = DropContainer()
        self.cards_container.setStyleSheet("background-color: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.cards_scroll.setWidget(self.cards_container)
        side_layout.addWidget(self.cards_scroll, 1)
        self.cards_container.item_dropped.connect(self._on_reorder_drop)

        self.refresh_wheels_list()

        case_panel = QWidget()

        case_panel.setStyleSheet(f"background: transparent;")

        case_main_layout = QHBoxLayout(case_panel)

        case_main_layout.setContentsMargins(0, 0, 0, 0)

        case_splitter = QSplitter(Qt.Orientation.Horizontal)

        case_splitter.setHandleWidth(5)

        case_splitter.setChildrenCollapsible(False)

        case_main_layout.addWidget(case_splitter)

        case_area = QWidget()
        case_area.setMinimumWidth(400)

        case_layout = QVBoxLayout(case_area)

        case_layout.setContentsMargins(20, 20, 20, 20)

        case_layout.setSpacing(0)

        case_splitter.addWidget(case_area)

        case_header = QHBoxLayout()

        case_layout.addLayout(case_header)

        self.case_combo = WheelDropdown()

        self.case_combo.setPlaceholderText("Select case...")

        self.case_combo.currentIndexChanged.connect(self._on_case_selected)

        case_header.addWidget(self.case_combo, 1)

        case_btn_frame = QHBoxLayout()

        case_btn_frame.setSpacing(4)

        case_header.addLayout(case_btn_frame)

        add_case_btn = HoverIconButton(PLUS_PATH, PLUS_PATH)

        add_case_btn.setFixedSize(36, 36)

        add_case_btn.setIconSize(add_case_btn.size())

        add_case_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        add_case_btn.setStyleSheet("""

            QPushButton {

                background-color: transparent;

                border: none;

                padding: 0;

            }

            QPushButton:hover {

                background-color: rgba(255, 255, 255, 12);

                border-radius: 18px;

            }

        """)

        add_case_btn.clicked.connect(self._case_add_case)

        case_btn_frame.addWidget(add_case_btn)

        self.del_case_btn = GlowButton("DELETE", "ghost")

        self.del_case_btn.clicked.connect(self._case_delete_case)

        case_btn_frame.addWidget(self.del_case_btn)

        self.rename_case_btn = GlowButton("RENAME", "ghost")

        self.rename_case_btn.clicked.connect(self._case_rename_case)

        case_btn_frame.addWidget(self.rename_case_btn)

        self.manage_case_btn = GlowButton("MANAGE", "ghost")

        self.manage_case_btn.clicked.connect(self._manage_case)

        case_btn_frame.addWidget(self.manage_case_btn)

        prev_case_btn = HoverIconButton(LEFT_ARROW_PATH, LEFT_ARROW_PATH)

        prev_case_btn.setFixedSize(36, 36)

        prev_case_btn.setIconSize(prev_case_btn.size())

        prev_case_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        prev_case_btn.setStyleSheet("""

            QPushButton {

                background-color: transparent;

                border: none;

                padding: 0;

            }

            QPushButton:hover {

                background-color: rgba(255, 255, 255, 12);

                border-radius: 18px;

            }

        """)

        prev_case_btn.clicked.connect(self._prev_case)

        case_btn_frame.addWidget(prev_case_btn)

        next_case_btn = HoverIconButton(RIGHT_ARROW_PATH, RIGHT_ARROW_PATH)

        next_case_btn.setFixedSize(36, 36)

        next_case_btn.setIconSize(next_case_btn.size())

        next_case_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        next_case_btn.setStyleSheet("""

            QPushButton {

                background-color: transparent;

                border: none;

                padding: 0;

            }

            QPushButton:hover {

                background-color: rgba(255, 255, 255, 12);

                border-radius: 18px;

            }

        """)

        next_case_btn.clicked.connect(self._next_case)

        case_btn_frame.addWidget(next_case_btn)

        self._case_opened = False

        self._case_is_spinning = False

        self._case_random_color_mode = False

        self._case_general_color_mode = False

        self._case_general_color_value = '#00F5FF'

        self._case_auto_color_var = True

        CLOSED_PATH = APP_DIR / "resources" / "case_closed.png"

        OPEN_PATH = APP_DIR / "resources" / "case_open.png"

        self._case_closed_pix_orig = QPixmap(str(CLOSED_PATH))

        self._case_open_pix_orig = QPixmap(str(OPEN_PATH))

        self._case_closed_pix = self._case_closed_pix_orig

        self._case_open_pix = self._case_open_pix_orig

        if not self._case_closed_pix_orig.isNull():

            self._case_closed_pix = self._case_closed_pix_orig.scaled(600, 420, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        if not self._case_open_pix_orig.isNull():

            self._case_open_pix = self._case_open_pix_orig.scaled(600, 420, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        case_overlay = QWidget()

        case_overlay.setObjectName("caseOverlay")

        case_overlay.setStyleSheet("background: transparent;")

        case_overlay.setMinimumSize(500, 380)

        case_overlay.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        overlay_layout = QVBoxLayout(case_overlay)

        overlay_layout.setContentsMargins(0, 0, 0, 0)

        overlay_layout.setSpacing(0)

        self._case_glow = QFrame(case_overlay)

        self._case_glow.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        glow_blur = QGraphicsBlurEffect()

        glow_blur.setBlurRadius(50)

        self._case_glow.setGraphicsEffect(glow_blur)

        self._case_glow.hide()

        self._case_img = QPushButton()

        self._case_img.setMinimumSize(400, 280)

        self._case_img.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        if not self._case_closed_pix.isNull():

            self._case_img.setIcon(QIcon(self._case_closed_pix))

            self._case_img.setIconSize(QSize(400, 280))

        else:

            self._case_img.setText("\U0001F4E6")

            self._case_img.setFont(QFont(str(FONT_FAMILY), 60))

        self._case_img.setStyleSheet(f"""

            QPushButton {{  background: transparent; border: none; color: {TEXT_SEC}; }}

        """)

        self._case_img.setCursor(Qt.CursorShape.PointingHandCursor)

        self._case_img.clicked.connect(self._case_toggle)

        overlay_layout.addWidget(self._case_img)

        self._case_glow.raise_()

        self._case_strip_wrapper = QFrame(case_overlay)

        self._case_strip_wrapper.setObjectName("caseStrip")

        self._case_strip_wrapper.setFixedHeight(110)

        self._case_strip_wrapper.setStyleSheet(f"""

            QFrame#caseStrip {{  background-color: {CARD_COLOR}; border: 1px solid {BORDER_COLOR};

                border-radius: 0px; }}

        """)

        self._case_strip_wrapper.hide()

        strip_wrap_layout = QVBoxLayout(self._case_strip_wrapper)

        strip_wrap_layout.setContentsMargins(0, 0, 0, 0)

        self._case_strip = _CaseStripWidget([], self)

        self._case_strip.setFixedHeight(110)

        strip_wrap_layout.addWidget(self._case_strip)

        case_overlay.installEventFilter(self)

        self._case_overlay = case_overlay

        case_layout.addWidget(case_overlay, 1)

        self._case_result = QLabel("\u2014")

        self._case_result.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._case_result.hide()

        case_layout.addWidget(self._case_result)

        self._case_btn_spacer = QWidget()

        self._case_btn_spacer.setFixedHeight(0)

        self._case_btn_spacer.setStyleSheet("background: transparent;")

        case_layout.addWidget(self._case_btn_spacer)

        self._case_spin_btn = GlowButton("OPEN", "lime")

        self._case_spin_btn.clicked.connect(self._case_spin)

        case_layout.addWidget(self._case_spin_btn, 0, Qt.AlignmentFlag.AlignCenter)

        self._case_winner_row = QWidget()

        self._case_winner_row.setStyleSheet("background: transparent;")

        winner_row_layout = QHBoxLayout(self._case_winner_row)

        winner_row_layout.setContentsMargins(0, 5, 0, 0)

        winner_row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        winner_lbl = QLabel("Winner:")

        winner_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px;")

        winner_row_layout.addWidget(winner_lbl)

        self._case_winner_entry = QLineEdit()

        self._case_winner_entry.setPlaceholderText("nickname")

        self._case_winner_entry.setFixedWidth(180)

        self._case_winner_entry.setStyleSheet(f"""

            QLineEdit {{

                background-color: {BG_COLOR};

                border: 1px solid {BORDER_COLOR};

                border-radius: 9999px;

                color: {TEXT_MAIN};

                font-size: 12px;

                padding: 6px 14px;

                font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

            }}

            QLineEdit:focus {{  border-color: {ACCENT_LIME}; }}

        """)

        winner_row_layout.addWidget(self._case_winner_entry)

        case_layout.addWidget(self._case_winner_row, 0, Qt.AlignmentFlag.AlignCenter)

        self._case_confirm_btn = GlowButton("CONFIRM PRIZE", "lime")

        self._case_confirm_btn.clicked.connect(self._case_confirm_prize)

        self._case_confirm_btn.setVisible(False)

        _confirm_spacer = QWidget()

        _confirm_spacer.setFixedHeight(8)

        _confirm_spacer.setStyleSheet("background: transparent;")

        case_layout.addWidget(_confirm_spacer)

        case_layout.addWidget(self._case_confirm_btn, 0, Qt.AlignmentFlag.AlignCenter)

        case_layout.addStretch(1)

        case_sidebar = QFrame()
        case_sidebar.setMinimumWidth(280)
        case_sidebar.setObjectName("sidebarFrame")
        case_sidebar.setStyleSheet("QFrame#sidebarFrame { background-color: transparent; border: 1px solid #232326; border-radius: 20px; }")

        case_sidebar_layout = QVBoxLayout(case_sidebar)

        case_sidebar_layout.setContentsMargins(0, 0, 0, 0)

        case_splitter.addWidget(case_sidebar)

        case_splitter.setStretchFactor(0, 3)

        case_splitter.setStretchFactor(1, 2)

        case_splitter.setSizes([700, 400])

        case_side_scroll = QScrollArea()

        case_side_scroll.setWidgetResizable(True)

        case_side_scroll.setStyleSheet(f"""

            QScrollArea {{  background-color: transparent; border: none; }}

        """)

        case_side_content = QWidget()

        case_side_content.setStyleSheet("background-color: transparent;")

        case_side_layout = QVBoxLayout(case_side_content)

        case_side_layout.setContentsMargins(30, 40, 30, 40)

        case_side_scroll.setWidget(case_side_content)

        case_sidebar_layout.addWidget(case_side_scroll)

        case_config_title = QLabel("CASE CONFIGURATOR")

        case_config_title.setStyleSheet("font-size: 16px; font-weight: bold;")

        case_config_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        case_side_layout.addWidget(case_config_title)

        self._case_auto_color_row = QWidget()

        self._case_auto_color_row.setStyleSheet("background: transparent;")

        auto_toggle_row = QHBoxLayout(self._case_auto_color_row)

        auto_toggle_row.setContentsMargins(0, 0, 0, 0)

        case_side_layout.addWidget(self._case_auto_color_row)

        auto_label = QLabel("Auto Color Gradient")

        auto_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px;")

        auto_toggle_row.addWidget(auto_label)

        auto_toggle_row.addStretch()

        self._case_auto_toggle = ToggleSwitch(initial=True)

        self._case_auto_toggle.toggled.connect(self._case_on_auto_color_toggle)

        auto_toggle_row.addWidget(self._case_auto_toggle)

        self._case_random_color_row = QWidget()

        self._case_random_color_row.setStyleSheet("background: transparent;")

        random_toggle_row = QHBoxLayout(self._case_random_color_row)

        random_toggle_row.setContentsMargins(0, 0, 0, 0)

        case_side_layout.addWidget(self._case_random_color_row)

        random_label = QLabel("Random Colors")

        random_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px;")

        random_toggle_row.addWidget(random_label)

        random_toggle_row.addStretch()

        self._case_random_toggle = ToggleSwitch(initial=False)

        self._case_random_toggle.toggled.connect(self._case_on_random_toggle)

        random_toggle_row.addWidget(self._case_random_toggle)

        self._case_general_color_row = QWidget()

        self._case_general_color_row.setStyleSheet("background: transparent;")

        general_toggle_row = QHBoxLayout(self._case_general_color_row)

        general_toggle_row.setContentsMargins(0, 0, 0, 0)

        case_side_layout.addWidget(self._case_general_color_row)

        general_label = QLabel("General Color")

        general_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px;")

        general_toggle_row.addWidget(general_label)

        general_toggle_row.addStretch()

        self._case_general_toggle = ToggleSwitch(initial=False)

        self._case_general_toggle.toggled.connect(self._case_on_general_toggle)

        general_toggle_row.addWidget(self._case_general_toggle)

        case_btn_row = QHBoxLayout()

        case_side_layout.addLayout(case_btn_row)

        self._case_add_prize_btn = GlowButton("ADD PRIZE", "outline")

        self._case_add_prize_btn.clicked.connect(self._case_add_prize)

        case_btn_row.addWidget(self._case_add_prize_btn)

        self._case_equalize_btn = GlowButton("EQUALIZE", "outline")

        self._case_equalize_btn.clicked.connect(self._case_equalize)

        case_btn_row.addWidget(self._case_equalize_btn)

        case_side_layout.addSpacing(10)

        self._case_cards_scroll = QScrollArea()

        self._case_cards_scroll.setWidgetResizable(True)

        self._case_cards_scroll.setStyleSheet(f"""

            QScrollArea {{  background-color: transparent; border: none; }}

            QScrollBar:vertical {{

                background: transparent;

                width: 10px;

                border-radius: 9999px;

                margin: 0;

                border: none;

            }}

            QScrollBar::handle:vertical {{

                background: #8E8E93;

                border-radius: 9999px;

                min-height: 30px;

                margin: 2px;

                border: none;

            }}

            QScrollBar::handle:vertical:hover {{

                background: #CCFF00;

            }}

            QScrollBar::add-line:vertical,

            QScrollBar::sub-line:vertical {{

                height: 0;

                background: transparent;

                border: none;

            }}

            QScrollBar::add-page:vertical,

            QScrollBar::sub-page:vertical {{

                background: transparent;

                border: none;

            }}

        """)

        self._case_cards_container = DropContainer()

        self._case_cards_container.setStyleSheet("background-color: transparent;")

        self._case_cards_layout = QVBoxLayout(self._case_cards_container)

        self._case_cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._case_cards_scroll.setWidget(self._case_cards_container)

        case_side_layout.addWidget(self._case_cards_scroll, 1)

        self.refresh_cases_list()

        dice_panel = DicePanel()

        dice_panel.setStyleSheet(f"background: transparent;")

        cards_panel = QWidget()

        cards_layout = QVBoxLayout(cards_panel)

        cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        cards_label = QLabel("CARDS - COMING SOON")

        cards_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 18px; letter-spacing: 1px;")

        cards_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        cards_layout.addWidget(cards_label)

        self.wheel_subsection = DetachableSection(wheel_panel, "WHEEL")

        self.case_subsection = DetachableSection(case_panel, "CASE")

        self.dice_subsection = DetachableSection(dice_panel, "DICE")

        self.cards_subsection = DetachableSection(cards_panel, "CARDS")

        self._sub_sections = [self.wheel_subsection, self.case_subsection,

                              self.dice_subsection, self.cards_subsection]

        self._panels_stack.addWidget(self.wheel_subsection)

        self._panels_stack.addWidget(self.case_subsection)

        self._panels_stack.addWidget(self.dice_subsection)

        self._panels_stack.addWidget(self.cards_subsection)

        self._panels_stack.setCurrentIndex(0)

        self.sub_nav = QFrame(page)

        self.sub_nav.setObjectName("subNav")

        self.sub_nav.setStyleSheet(f"""

            QFrame#subNav {{

                background-color: {BG_COLOR};

                border-bottom: 1px solid {BORDER_COLOR};

            }}

        """)

        self.sub_nav.setFixedHeight(32)

        self.sub_nav.hide()

        sub_nav_layout = QHBoxLayout(self.sub_nav)

        sub_nav_layout.setContentsMargins(0, 0, 0, 0)

        sub_nav_layout.setSpacing(0)

        self.sub_nav_btns = []

        sub_nav_items = ["WHEEL", "CASE", "DICE", "CARDS"]

        for i, text in enumerate(sub_nav_items):

            btn = QPushButton(text, self.sub_nav)

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

            btn.clicked.connect(lambda checked, p=i: self._switch_sub_panel(p))

            sub_nav_layout.addWidget(btn, 1)

            self.sub_nav_btns.append(btn)

        self._update_sub_nav_active(0)

        self.tab_btns[1].installEventFilter(self)

        self.sub_nav.installEventFilter(self)

        self._sub_nav_visible = False

        self._sub_nav_hover_timer = QTimer(self)

        self._sub_nav_hover_timer.setSingleShot(True)

        self._sub_nav_hover_timer.timeout.connect(self._check_sub_nav_hide)