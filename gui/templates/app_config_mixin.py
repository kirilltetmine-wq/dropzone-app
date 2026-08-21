import json

from PyQt6.QtWidgets import (

    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,

    QFrame, QLineEdit, QScrollArea, QSizePolicy, QCheckBox,

    QSlider, QSpinBox, QComboBox, QFileDialog, QMessageBox,

    QGraphicsDropShadowEffect, QDialog,

)

from PyQt6.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve

from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor, QPainter, QBrush, QPen

from core.theme import (
    BG_COLOR, CARD_COLOR, CARD_LIGHT, TEXT_MAIN, TEXT_SEC,
    BORDER_COLOR, ACCENT_LIME, FONT_FAMILY,
    ACCENT_CYAN, get_stylesheet, DANGER_COLOR,
    SUCCESS_COLOR, QUESTION_PATH,
)

from core.config import ConfigManager

from ui_kit import show_info, ModernDialog

from ui_kit import RoundedButton, GlowButton, ToggleSwitch
from ui_kit.ui_kit_pages import ConfigTabTemplate


class HintIcon(QWidget):
    """Question-mark icon that shows a tooltip popup on hover."""

    def __init__(self, hint_text, parent=None):
        super().__init__(parent)
        self._hint_text = hint_text
        self._popup = None
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._show_popup)

        self.setFixedSize(16, 16)
        self.setCursor(Qt.CursorShape.WhatsThisCursor)
        self.setToolTip("")

        self._pixmap = QIcon(str(QUESTION_PATH)).pixmap(16, 16)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawPixmap(0, 0, self._pixmap)

    def enterEvent(self, event):
        self._timer.start(400)

    def leaveEvent(self, event):
        self._timer.stop()
        self._hide_popup()

    def _show_popup(self):
        if self._popup:
            self._popup.close()

        self._popup = QFrame(None)
        self._popup.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.NoDropShadowWindowHint
        )
        self._popup.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self._popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._popup.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
            }}
        """)

        layout = QVBoxLayout(self._popup)
        layout.setContentsMargins(12, 8, 12, 8)

        lbl = QLabel(self._hint_text)
        lbl.setWordWrap(True)
        lbl.setMaximumWidth(260)
        lbl.setStyleSheet(f"""
            color: {TEXT_MAIN};
            font-size: 11px;
            font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
            background: transparent;
            line-height: 1.4;
        """)
        layout.addWidget(lbl)

        self._popup.adjustSize()

        # Position near the icon
        global_pos = self.mapToGlobal(self.rect().topRight())
        x = global_pos.x() + 6
        y = global_pos.y() - 4

        screen = self.screen()
        if screen:
            sg = screen.availableGeometry()
            pw = self._popup.width()
            ph = self._popup.height()
            if x + pw > sg.right():
                x = global_pos.x() - pw - 6
            if y + ph > sg.bottom():
                y = sg.bottom() - ph
            if y < sg.top():
                y = sg.top()

        self._popup.move(int(x), int(y))
        self._popup.show()

    def _hide_popup(self):
        if self._popup:
            self._popup.close()
            self._popup = None


class ConfigMixin:

    def _setup_config_tab(self):

        page = self.config_page

        # Use ConfigTabTemplate as the base layout (sidebar + content stack)
        template = ConfigTabTemplate()

        # Clear template's default sidebar content
        sidebar = template.layout().itemAt(0).widget()
        sidebar_layout = sidebar.layout()
        while sidebar_layout.count():
            item = sidebar_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Clear template's default content stack pages
        self._content_stack = template._content_stack
        while self._content_stack.count():
            w = self._content_stack.widget(0)
            self._content_stack.removeWidget(w)
            w.deleteLater()

        # Add template to page
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(template)

        self._config_nav_btns = {}
        self._config_section_widgets = {}

        def add_section_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"""
                color: {TEXT_MAIN};
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1.2px;
                padding: 10px 20px 4px;
                font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
            """)
            lbl.setGraphicsEffect(None)
            sidebar_layout.addWidget(lbl)

        def add_nav_btn(section_id, text, is_sub=False):
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            pl = '36px' if is_sub else '20px'
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-left: 2px solid transparent;
                    color: {TEXT_SEC};
                    font-size: {'11px' if is_sub else '12px'};
                    font-weight: {'500' if is_sub else '600'};
                    letter-spacing: 0.3px;
                    padding: 8px 0;
                    text-align: left;
                    padding-left: {pl};
                    font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
                }}
                QPushButton:hover {{
                    color: {TEXT_MAIN};
                    background: rgba(255,255,255,0.02);
                }}
            """)
            btn.clicked.connect(lambda checked, sid=section_id: self._show_config_section(sid))
            self._config_nav_btns[section_id] = (btn, is_sub)
            sidebar_layout.addWidget(btn)

        add_section_label("GENERAL")
        add_nav_btn("general", "General")
        add_nav_btn("appearance", "Appearance")
        add_nav_btn("api", "API & Connection")

        add_section_label("TABS")
        add_nav_btn("lottery", "Lottery")
        add_nav_btn("lottery-keyword", "Keyword", is_sub=True)
        add_nav_btn("lottery-participants", "Participants", is_sub=True)
        add_nav_btn("chat", "Chat")
        add_nav_btn("wheels", "Wheels")
        add_nav_btn("case", "Case")
        add_nav_btn("dice", "Dice")
        add_nav_btn("logs", "Logs")

        add_section_label("FEATURES")
        add_nav_btn("notifications", "Notifications")

        add_section_label("DATA")
        add_nav_btn("export", "Export / Import")
        add_nav_btn("reset", "Reset")

        add_section_label("HELP")
        add_nav_btn("how_to_use", "How to use")

        sidebar_layout.addStretch()

        self._build_config_general()
        self._build_config_appearance()
        self._build_config_api()
        self._build_config_chat()
        self._build_config_dice()
        self._build_config_notifications()
        self._build_config_lottery()
        self._build_config_wheels()
        self._build_config_case()
        self._build_config_logs()
        self._build_config_export()
        self._build_config_reset()
        self._build_config_how_to_use()

        self._show_config_section("general")

    def _build_config_how_to_use(self):

        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(24, 24, 24, 24)
        section_layout.setSpacing(16)
        section_layout.addWidget(self._config_section_title("HOW TO USE"))

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_COLOR};
                border-radius: 20px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(12)

        intro = QLabel("Welcome to Dropzone! This guide will help you get started with the main features.")
        intro.setWordWrap(True)
        intro.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 13px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif; background: transparent;")
        card_layout.addWidget(intro)

        # Quick tips
        tips = [
            ("Connect YouTube", "Authorize your Google account in Config → API & Connection → YouTube Channel, then bind a channel."),
            ("Connect Twitch", "Authorize Twitch in Config → API & Connection → Twitch, or just enter a channel name for anonymous mode."),
            ("Run a Lottery", "Go to Main → Lottery, set a keyword (e.g. !join), start tracking, and click Pick Winner."),
            ("Moderate Chat", "Right-click on any username in chat to ban, timeout, or delete messages."),
            ("Customize Wheels", "Go to the Wheel tab to create, edit, and spin prize wheels with custom sectors."),
            ("Detach Tabs", "Click the detach button on any tab to pop it out as a separate window."),
        ]

        for title, desc in tips:
            tip_row = QWidget()
            tip_row.setStyleSheet("background: transparent;")
            tip_layout = QHBoxLayout(tip_row)
            tip_layout.setContentsMargins(0, 4, 0, 4)
            tip_layout.setSpacing(12)

            dot = QLabel("•")
            dot.setStyleSheet(f"color: {ACCENT_LIME}; font-size: 16px; font-weight: 700; background: transparent;")
            dot.setFixedWidth(12)
            tip_layout.addWidget(dot)

            text_w = QWidget()
            text_w.setStyleSheet("background: transparent;")
            text_layout = QVBoxLayout(text_w)
            text_layout.setContentsMargins(0, 0, 0, 0)
            text_layout.setSpacing(2)

            ttl = QLabel(title)
            ttl.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 12px; font-weight: 600; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif; background: transparent;")
            text_layout.addWidget(ttl)

            desc_lbl = QLabel(desc)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif; background: transparent;")
            text_layout.addWidget(desc_lbl)

            tip_layout.addWidget(text_w, 1)
            card_layout.addWidget(tip_row)

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addWidget(card)
        section_layout.addWidget(wrapper)

        # Replay button
        replay_row = QWidget()
        replay_row.setStyleSheet("background: transparent;")
        replay_layout = QHBoxLayout(replay_row)
        replay_layout.setContentsMargins(0, 8, 0, 8)
        replay_layout.setSpacing(0)

        replay_btn = QPushButton("REPLAY TUTORIAL")
        replay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        replay_btn.setFixedHeight(40)
        replay_btn.setFixedWidth(220)
        replay_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_LIME};
                color: {BG_COLOR};
                border: none;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 1px;
                padding: 0;
                font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
            }}
            QPushButton:hover {{
                background: transparent;
                color: {ACCENT_LIME};
                border: 2px solid {ACCENT_LIME};
            }}
        """)
        replay_btn.clicked.connect(self._replay_tutorial)
        replay_layout.addWidget(replay_btn)
        replay_layout.addStretch()
        section_layout.addWidget(replay_row)

        section_layout.addStretch()
        self._content_stack.addWidget(section)
        self._config_section_widgets["how_to_use"] = section

    def _replay_tutorial(self):
        if hasattr(self, '_show_tutorial'):
            self._show_tutorial()

    def _show_config_section(self, section_id):

        for sid, (btn, is_sub) in self._config_nav_btns.items():

            pl = '36px' if is_sub else '20px'

            fs = '11px' if is_sub else '12px'

            fw = '500' if is_sub else '600'

            is_active = (sid == section_id or sid.startswith(section_id + '-'))

            active_color = ACCENT_LIME if is_active else TEXT_SEC

            border_color = ACCENT_LIME if is_active else "transparent"

            bg_color = "rgba(204,255,0,0.03)" if is_active else "rgba(255,255,255,0.02)"

            btn.setStyleSheet(f"""

                QPushButton {{

                    background: transparent;

                    border: none;

                    border-left: 2px solid {border_color};

                    color: {active_color};

                    font-size: {fs};

                    font-weight: {fw};

                    letter-spacing: 0.3px;

                    padding: 8px 0;

                    text-align: left;

                    padding-left: {pl};

                    font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

                }}

                QPushButton:hover {{

                    color: {TEXT_MAIN};

                    background: {bg_color};

                }}

            """)

        parent_id = section_id.split('-')[0]

        if parent_id in ("lottery",):

            if parent_id in self._config_section_widgets:

                widget = self._config_section_widgets[parent_id]

                idx = self._content_stack.indexOf(widget)

                if idx >= 0:

                    self._content_stack.setCurrentIndex(idx)

            anchor_id = f"config-anchor-{section_id}"

            # For lottery, the widget is a QScrollArea wrapping the content
            lottery_widget = self._config_section_widgets.get(parent_id)
            if lottery_widget:
                anchor = lottery_widget.widget().findChild(QWidget, anchor_id)
                if anchor:
                    lottery_widget.ensureWidgetVisible(anchor, 0, 50)

        else:

            if section_id in self._config_section_widgets:

                widget = self._config_section_widgets[section_id]

                idx = self._content_stack.indexOf(widget)

                if idx >= 0:

                    self._content_stack.setCurrentIndex(idx)

    def _config_section_title(self, text):

        lbl = QLabel(text)

        lbl.setStyleSheet(f"""

            color: {ACCENT_CYAN};

            font-size: 14px;

            font-weight: 700;

            letter-spacing: 0.5px;

            margin-bottom: 8px;

            font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

        """)

        return lbl

    def _config_group(self, title, rows):

        card = QFrame()

        card.setStyleSheet(f"""

            QFrame {{

                background-color: {CARD_COLOR};

                border-radius: 20px;

            }}

        """)

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(20, 16, 20, 16)

        card_layout.setSpacing(0)

        title_lbl = QLabel(title)

        title_lbl.setStyleSheet(f"""

            color: {TEXT_MAIN};

            font-size: 12px;

            font-weight: 700;

            letter-spacing: 0.4px;

            margin-bottom: 8px;

            font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

        """)

        card_layout.addWidget(title_lbl)

        for row in rows:

            card_layout.addWidget(row)

        wrapper = QWidget()

        wrapper_layout = QVBoxLayout(wrapper)

        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        wrapper_layout.addWidget(card)

        return wrapper

    def _config_toggle_row(self, label_text, desc_text, section, key, checked=True, hint=None):

        row = QWidget()

        row.setStyleSheet("background: transparent;")

        row_layout = QHBoxLayout(row)

        row_layout.setContentsMargins(0, 8, 0, 8)

        row_layout.setSpacing(0)

        left = QWidget()

        left.setStyleSheet("background: transparent;")

        left_layout = QVBoxLayout(left)

        left_layout.setContentsMargins(0, 0, 0, 0)

        left_layout.setSpacing(2)

        label_row = QWidget()
        label_row.setStyleSheet("background: transparent;")
        label_row_layout = QHBoxLayout(label_row)
        label_row_layout.setContentsMargins(0, 0, 0, 0)
        label_row_layout.setSpacing(4)

        lbl = QLabel(label_text)

        lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

        label_row_layout.addWidget(lbl)

        if hint:
            hint_icon = HintIcon(hint)
            label_row_layout.addWidget(hint_icon)

        label_row_layout.addStretch()
        left_layout.addWidget(label_row)

        if desc_text:

            desc = QLabel(desc_text)

            desc.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; opacity: 0.6; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

            left_layout.addWidget(desc)

        row_layout.addWidget(left, 1)

        toggle = ToggleSwitch(initial=checked)

        toggle.toggled.connect(lambda v: self.config_mgr.set(section, key, v))

        row_layout.addWidget(toggle)

        sep = QFrame()

        sep.setStyleSheet(f"background: rgba(255,255,255,0.03);")

        sep.setFixedHeight(1)

        container = QWidget()

        container.setStyleSheet("background: transparent;")

        cont_layout = QVBoxLayout(container)

        cont_layout.setContentsMargins(0, 0, 0, 0)

        cont_layout.setSpacing(0)

        cont_layout.addWidget(row)

        cont_layout.addWidget(sep)

        return container

    def _config_input_row(self, label_text, section, key, default_value="", on_change=None, hint=None):

        row = QWidget()

        row.setStyleSheet("background: transparent;")

        row_layout = QHBoxLayout(row)

        row_layout.setContentsMargins(0, 8, 0, 8)

        row_layout.setSpacing(0)

        label_widget = QWidget()
        label_widget.setStyleSheet("background: transparent;")
        label_widget_layout = QHBoxLayout(label_widget)
        label_widget_layout.setContentsMargins(0, 0, 0, 0)
        label_widget_layout.setSpacing(4)

        lbl = QLabel(label_text)

        lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

        label_widget_layout.addWidget(lbl)

        if hint:
            hint_icon = HintIcon(hint)
            label_widget_layout.addWidget(hint_icon)

        label_widget_layout.addStretch()
        row_layout.addWidget(label_widget, 1)

        inp = QLineEdit()

        inp.setText(str(default_value))

        inp.setFixedWidth(120)

        inp.setAlignment(Qt.AlignmentFlag.AlignCenter)

        inp.setStyleSheet(f"""

            QLineEdit {{

                background-color: {BG_COLOR};

                border: 1px solid {BORDER_COLOR};

                border-radius: 9999px;

                color: {TEXT_MAIN};

                font-size: 12px;

                padding: 6px 12px;

                font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

            }}

            QLineEdit:focus {{

                border-color: {ACCENT_CYAN};

            }}

        """)

        def _on_edit():

            self.config_mgr.set(section, key, inp.text())

            if on_change:

                on_change(inp.text())

        inp.editingFinished.connect(_on_edit)

        row_layout.addWidget(inp)

        sep = QFrame()

        sep.setStyleSheet(f"background: rgba(255,255,255,0.03);")

        sep.setFixedHeight(1)

        container = QWidget()

        container.setStyleSheet("background: transparent;")

        cont_layout = QVBoxLayout(container)

        cont_layout.setContentsMargins(0, 0, 0, 0)

        cont_layout.setSpacing(0)

        cont_layout.addWidget(row)

        cont_layout.addWidget(sep)

        return container

    def _config_anchor(self, anchor_id):

        anchor = QWidget()

        anchor.setObjectName(anchor_id)

        anchor.setFixedHeight(0)

        return anchor

    def _build_config_general(self):

        section = QWidget()

        section.setObjectName("config-section-general")

        section_layout = QVBoxLayout(section)

        section_layout.setContentsMargins(24, 24, 24, 24)

        section_layout.setSpacing(16)

        section_layout.addWidget(self._config_section_title("GENERAL"))

        cfg = self.config_mgr

        section_layout.addWidget(self._config_group("WINDOW", [

            self._config_toggle_row("Always on Top", None, "general", "always_on_top", cfg.get("general", "always_on_top"),
                                    hint="Keeps the application window always on top of other windows"),

            self._config_toggle_row("Start Minimized", None, "general", "start_minimized", cfg.get("general", "start_minimized"),
                                    hint="Launch the application minimized to the system tray"),

            self._config_input_row("Transparency (%)", "general", "transparency", cfg.get("general", "transparency"),
                                   on_change=lambda v: self._apply_transparency(int(v)),
                                   hint="Adjust the opacity of the window from 0 (invisible) to 100 (fully opaque)"),

        ]))

        section_layout.addWidget(self._config_group("BEHAVIOR", [

            self._config_input_row("Auto-save interval (min)", "general", "auto_save_interval", cfg.get("general", "auto_save_interval"),
                                   hint="Automatically save configuration every N minutes"),

            self._config_toggle_row("Confirm before delete", None, "general", "confirm_before_delete", cfg.get("general", "confirm_before_delete"),
                                    hint="Show a confirmation dialog before deleting items"),

        ]))

        section_layout.addStretch()

        self._content_stack.addWidget(section)

        self._config_section_widgets["general"] = section

    def _build_config_appearance(self):

        section = QWidget()

        section_layout = QVBoxLayout(section)

        section_layout.setContentsMargins(24, 24, 24, 24)

        section_layout.setSpacing(16)

        section_layout.addWidget(self._config_section_title("APPEARANCE"))

        cfg = self.config_mgr

        section_layout.addWidget(self._config_group("THEME", [

            self._config_toggle_row("Dark Mode", None, "appearance", "dark_mode", cfg.get("appearance", "dark_mode"),
                                    hint="Toggle between dark and light color scheme"),

            self._config_input_row("Accent Color", "appearance", "accent_color", cfg.get("appearance", "accent_color"),
                                   hint="Set a custom accent color as a hex value (e.g. #CCFF00)"),

        ]))

        section_layout.addStretch()

        self._content_stack.addWidget(section)

        self._config_section_widgets["appearance"] = section

    def _build_config_api(self):

        section = QWidget()

        section_layout = QVBoxLayout(section)

        section_layout.setContentsMargins(24, 24, 24, 24)

        section_layout.setSpacing(16)

        section_layout.addWidget(self._config_section_title("API & CONNECTION"))

        cfg = self.config_mgr

        channel_card = QFrame()

        channel_card.setStyleSheet(f"""

            QFrame {{

                background-color: {CARD_COLOR};

                border-radius: 20px;

            }}

        """)

        channel_card_layout = QVBoxLayout(channel_card)

        channel_card_layout.setContentsMargins(20, 16, 20, 16)

        channel_card_layout.setSpacing(0)

        channel_title = QLabel("YOUTUBE CHANNEL")

        channel_title.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 12px; font-weight: 700; letter-spacing: 0.4px; margin-bottom: 8px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

        channel_card_layout.addWidget(channel_title)

        # Status row (CONNECTED / DISCONNECTED)
        yt_status_row = QWidget()
        yt_status_row.setStyleSheet("background: transparent;")
        yt_status_layout = QHBoxLayout(yt_status_row)
        yt_status_layout.setContentsMargins(0, 8, 0, 4)
        yt_status_layout.setSpacing(0)

        yt_status_lbl = QLabel("Status")
        yt_status_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")
        yt_status_layout.addWidget(yt_status_lbl, 1)

        yt_connected = (getattr(self, 'bot', None) is not None
                        and hasattr(self.bot, 'youtube')
                        and self.bot.youtube is not None
                        and bool(self.config_mgr.get('youtube', 'bound_channel', '')))

        self._yt_status_dot = QLabel()
        self._yt_status_dot.setFixedSize(8, 8)
        self._yt_status_dot.setStyleSheet(f"""
            background-color: {SUCCESS_COLOR if yt_connected else DANGER_COLOR};
            border-radius: 4px;
        """)
        yt_status_layout.addWidget(self._yt_status_dot)
        yt_status_layout.addSpacing(6)

        self._yt_status_text = QLabel("CONNECTED" if yt_connected else "DISCONNECTED")
        self._yt_status_text.setStyleSheet(
            f"color: {SUCCESS_COLOR if yt_connected else DANGER_COLOR}; font-size: 13px; font-weight: 700;"
            f" font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;"
        )
        yt_status_layout.addWidget(self._yt_status_text)

        channel_card_layout.addWidget(yt_status_row)

        # Google Auth button (like Twitch's AUTHORIZE TWITCH)
        yt_auth_row = QWidget()
        yt_auth_row.setStyleSheet("background: transparent;")
        yt_auth_layout = QHBoxLayout(yt_auth_row)
        yt_auth_layout.setContentsMargins(0, 8, 0, 8)
        yt_auth_layout.setSpacing(0)

        self._yt_auth_btn = GlowButton("AUTHORIZE YOUTUBE", "lime")
        self._yt_auth_btn.clicked.connect(self.run_oauth)
        yt_auth_layout.addWidget(self._yt_auth_btn, 0, Qt.AlignmentFlag.AlignLeft)
        yt_auth_layout.addStretch()
        channel_card_layout.addWidget(yt_auth_row)

        channel_input_row = QWidget()

        channel_input_row.setStyleSheet("background: transparent;")

        channel_input_layout = QHBoxLayout(channel_input_row)

        channel_input_layout.setContentsMargins(0, 8, 0, 8)

        channel_input_layout.setSpacing(0)

        channel_lbl = QLabel("Channel URL / ID")

        channel_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

        channel_input_layout.addWidget(channel_lbl)
        channel_input_layout.addWidget(HintIcon("Enter your YouTube channel URL or ID to bind it. Messages from this channel's live streams will be tracked."))
        channel_input_layout.addStretch()

        self._channel_entry = QLineEdit()

        self._channel_entry.setText(cfg.get('youtube', 'bound_channel', ''))

        self._channel_entry.setFixedWidth(200)

        self._channel_entry.setPlaceholderText("https://youtube.com/@...")

        self._channel_entry.setStyleSheet(f"""

            QLineEdit {{

                background-color: {BG_COLOR};

                border: 1px solid {BORDER_COLOR};

                border-radius: 9999px;

                color: {TEXT_MAIN};

                font-size: 12px;

                padding: 6px 12px;

                font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

            }}

            QLineEdit:focus {{

                border-color: {ACCENT_CYAN};

            }}

        """)

        channel_input_layout.addWidget(self._channel_entry)
        self._channel_entry.returnPressed.connect(self._bind_youtube_channel)

        channel_card_layout.addWidget(channel_input_row)

        channel_btn_row = QWidget()

        channel_btn_row.setStyleSheet("background: transparent;")

        channel_btn_layout = QHBoxLayout(channel_btn_row)

        channel_btn_layout.setContentsMargins(0, 12, 0, 0)

        channel_btn_layout.setSpacing(12)

        self._bind_channel_btn = GlowButton("BIND CHANNEL", "outline")

        self._bind_channel_btn.clicked.connect(self._bind_youtube_channel)

        channel_btn_layout.addWidget(self._bind_channel_btn, 0, Qt.AlignmentFlag.AlignLeft)

        self._unbind_channel_btn = GlowButton("UNBIND", "ghost")

        self._unbind_channel_btn.clicked.connect(self._unbind_youtube_channel)

        self._unbind_channel_btn.setVisible(False)

        channel_btn_layout.addWidget(self._unbind_channel_btn, 0, Qt.AlignmentFlag.AlignLeft)

        channel_btn_layout.addStretch()

        self._channel_status_label = QLabel()

        self._channel_status_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

        channel_btn_layout.addWidget(self._channel_status_label)

        channel_card_layout.addWidget(channel_btn_row)

        auto_track_row = QWidget()

        auto_track_row.setStyleSheet("background: transparent;")

        auto_track_layout = QHBoxLayout(auto_track_row)

        auto_track_layout.setContentsMargins(0, 8, 0, 8)

        auto_track_layout.setSpacing(0)

        auto_track_lbl = QLabel("Auto-track live streams")

        auto_track_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

        auto_track_layout.addWidget(auto_track_lbl)
        auto_track_layout.addWidget(HintIcon("When enabled, the app will automatically connect to chat when a new live stream starts on the bound channel"))

        auto_track_layout.addStretch()

        self._auto_track_switch = ToggleSwitch(initial=cfg.get('youtube', 'auto_track', False))

        self._auto_track_switch.toggled.connect(self._on_auto_track_toggle)

        auto_track_layout.addWidget(self._auto_track_switch)

        channel_card_layout.addWidget(auto_track_row)

        bound_channel = cfg.get('youtube', 'bound_channel', '')

        if bound_channel:

            channel_name = cfg.get('youtube', 'channel_name', '') or bound_channel

            self._channel_entry.setText(bound_channel)

            self._channel_entry.setReadOnly(True)

            self._channel_status_label.setText(f"Bound: {channel_name}")

            self._channel_status_label.setStyleSheet(f"color: {SUCCESS_COLOR}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

            self._bind_channel_btn.setVisible(False)

            self._unbind_channel_btn.setVisible(True)

        twitch_card = QFrame()

        twitch_card.setStyleSheet(f"""

            QFrame {{

                background-color: {CARD_COLOR};

                border-radius: 20px;

            }}

        """)

        twitch_card_layout = QVBoxLayout(twitch_card)

        twitch_card_layout.setContentsMargins(20, 16, 20, 16)

        twitch_card_layout.setSpacing(0)

        twitch_title = QLabel("TWITCH")

        twitch_title.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 12px; font-weight: 700; letter-spacing: 0.4px; margin-bottom: 8px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

        twitch_card_layout.addWidget(twitch_title)

        twitch_status_row = QWidget()

        twitch_status_row.setStyleSheet("background: transparent;")

        twitch_status_layout = QHBoxLayout(twitch_status_row)

        twitch_status_layout.setContentsMargins(0, 0, 0, 0)

        twitch_status_layout.setSpacing(0)

        twitch_status_lbl = QLabel("Status")

        twitch_status_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

        twitch_status_layout.addWidget(twitch_status_lbl, 1)

        self._twitch_status_dot = QLabel()

        self._twitch_status_dot.setFixedSize(8, 8)

        self._twitch_status_dot.setStyleSheet(f"""

            background-color: {DANGER_COLOR};

            border-radius: 4px;

        """)

        twitch_status_layout.addWidget(self._twitch_status_dot)

        twitch_status_layout.addSpacing(6)

        self._twitch_status_text = QLabel("DISCONNECTED")

        self._twitch_status_text.setStyleSheet(f"color: {DANGER_COLOR}; font-size: 13px; font-weight: 700; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

        twitch_status_layout.addWidget(self._twitch_status_text)

        twitch_card_layout.addWidget(twitch_status_row)

        oauth_row = QWidget()
        oauth_row.setStyleSheet("background: transparent;")
        oauth_layout = QHBoxLayout(oauth_row)
        oauth_layout.setContentsMargins(0, 8, 0, 8)
        oauth_layout.setSpacing(0)

        self._twitch_auth_btn = GlowButton("AUTHORIZE TWITCH", "lime")
        self._twitch_auth_btn.clicked.connect(self._twitch_oauth)
        oauth_layout.addWidget(self._twitch_auth_btn, 0, Qt.AlignmentFlag.AlignLeft)
        oauth_layout.addStretch()
        twitch_card_layout.addWidget(oauth_row)

        tchan_row = QWidget()
        tchan_row.setStyleSheet("background: transparent;")
        tchan_layout = QHBoxLayout(tchan_row)
        tchan_layout.setContentsMargins(0, 8, 0, 8)
        tchan_layout.setSpacing(0)

        tchan_lbl = QLabel("Channel name")
        tchan_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")
        tchan_layout.addWidget(tchan_lbl)
        tchan_layout.addWidget(HintIcon("Enter a Twitch streamer's name to connect to their chat. Supports both OAuth (API) and anonymous connection."))
        tchan_layout.addStretch()

        self._twitch_channel_entry = QLineEdit()
        self._twitch_channel_entry.setText(cfg.get('twitch', 'channel_name', ''))
        self._twitch_channel_entry.setFixedWidth(200)
        self._twitch_channel_entry.setPlaceholderText("streamer name")
        self._twitch_channel_entry.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 9999px;
                color: {TEXT_MAIN};
                font-size: 12px;
                padding: 6px 12px;
                font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
            }}
            QLineEdit:focus {{
                border-color: {ACCENT_CYAN};
            }}
        """)
        tchan_layout.addWidget(self._twitch_channel_entry)
        twitch_card_layout.addWidget(tchan_row)

        twitch_btn_row = QWidget()
        twitch_btn_row.setStyleSheet("background: transparent;")
        twitch_btn_layout = QHBoxLayout(twitch_btn_row)
        twitch_btn_layout.setContentsMargins(0, 12, 0, 0)
        twitch_btn_layout.setSpacing(12)

        self._twitch_bind_btn = GlowButton("BIND TWITCH CHANNEL", "outline")
        self._twitch_bind_btn.clicked.connect(self._bind_twitch_channel)
        twitch_btn_layout.addWidget(self._twitch_bind_btn, 0, Qt.AlignmentFlag.AlignLeft)

        self._twitch_unbind_btn = GlowButton("UNBIND", "ghost")
        self._twitch_unbind_btn.clicked.connect(self._unbind_twitch_channel)
        self._twitch_unbind_btn.setVisible(False)
        twitch_btn_layout.addWidget(self._twitch_unbind_btn, 0, Qt.AlignmentFlag.AlignLeft)

        twitch_btn_layout.addStretch()

        self._twitch_status_label = QLabel()
        self._twitch_status_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")
        twitch_btn_layout.addWidget(self._twitch_status_label)

        twitch_card_layout.addWidget(twitch_btn_row)

        # Auto-connect on Enter in channel field
        self._twitch_channel_entry.returnPressed.connect(self._connect_twitch)

        twitch_auto_row = QWidget()
        twitch_auto_row.setStyleSheet("background: transparent;")
        twitch_auto_layout = QHBoxLayout(twitch_auto_row)
        twitch_auto_layout.setContentsMargins(0, 8, 0, 8)
        twitch_auto_layout.setSpacing(0)

        twitch_auto_lbl = QLabel("Auto-track Twitch streams")
        twitch_auto_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")
        twitch_auto_layout.addWidget(twitch_auto_lbl)
        twitch_auto_layout.addWidget(HintIcon("When enabled, the app will automatically connect to Twitch chat when the bound streamer goes live"))
        twitch_auto_layout.addStretch()

        self._twitch_auto_track_switch = ToggleSwitch(initial=cfg.get('twitch', 'auto_track', False))
        self._twitch_auto_track_switch.toggled.connect(self._on_twitch_auto_track)
        twitch_auto_layout.addWidget(self._twitch_auto_track_switch)

        twitch_card_layout.addWidget(twitch_auto_row)

        tchan = cfg.get('twitch', 'channel_name', '')
        if tchan:
            self._twitch_channel_entry.setText(tchan)
            self._twitch_channel_entry.setReadOnly(True)
            self._twitch_bind_btn.setVisible(False)
            self._twitch_unbind_btn.setVisible(True)
            channel_name = cfg.get('twitch', 'channel_name', '') or tchan
            self._twitch_status_label.setText(f"Bound: {channel_name}")
            self._twitch_status_label.setStyleSheet(f"color: {SUCCESS_COLOR}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")
        self._update_twitch_status()

        wrapper = QWidget()

        wrapper_layout = QVBoxLayout(wrapper)

        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        wrapper_layout.addWidget(channel_card)

        wrapper_layout.addWidget(twitch_card)

        section_layout.addWidget(wrapper)

        section_layout.addStretch()

        self._content_stack.addWidget(section)

        self._config_section_widgets["api"] = section

    def _build_config_chat(self):

        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(24, 24, 24, 24)
        section_layout.setSpacing(16)
        section_layout.addWidget(self._config_section_title("CHAT"))

        cfg = self.config_mgr

        section_layout.addWidget(self._config_group("DISPLAY", [

            self._config_input_row("Max messages", "chat", "max_messages", cfg.get("chat", "max_messages"),
                                   hint="Maximum number of messages shown in chat before older ones are removed"),

            self._config_toggle_row("Show timestamps", None, "chat", "show_timestamps", cfg.get("chat", "show_timestamps"),
                                    hint="Display timestamps next to chat messages"),

            self._config_toggle_row("Show badges", None, "chat", "show_badges", cfg.get("chat", "show_badges"),
                                    hint="Show user badges (mod, VIP, etc.) in chat"),

            self._config_toggle_row("Show platform icons", None, "chat", "show_platform_icons", cfg.get("chat", "show_platform_icons"),
                                    hint="Show YouTube / Twitch platform icons next to usernames"),

        ]))

        section_layout.addWidget(self._config_group("MODERATION", [

            self._config_input_row("Default timeout (sec)", "chat", "mod_default_timeout",
                                   cfg.get("chat", "mod_default_timeout"),
                                   hint="Default timeout duration in seconds when moderating a user"),

        ]))

        section_layout.addStretch()

        self._content_stack.addWidget(section)
        self._config_section_widgets["chat"] = section

    def _build_config_dice(self):

        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(24, 24, 24, 24)
        section_layout.setSpacing(16)
        section_layout.addWidget(self._config_section_title("DICE"))

        cfg = self.config_mgr

        section_layout.addWidget(self._config_group("ANIMATION", [

            self._config_toggle_row("Enable animation", None, "dice", "animation_enabled", cfg.get("dice", "animation_enabled"),
                                    hint="Play rolling animation when dice are thrown"),

            self._config_toggle_row("Auto-roll on start", None, "dice", "auto_roll", cfg.get("dice", "auto_roll"),
                                    hint="Automatically roll dice when the dice tab is opened"),

        ]))

        section_layout.addStretch()

        self._content_stack.addWidget(section)
        self._config_section_widgets["dice"] = section

    def _build_config_notifications(self):

        section = QWidget()
        section_layout = QVBoxLayout(section)
        section_layout.setContentsMargins(24, 24, 24, 24)
        section_layout.setSpacing(16)
        section_layout.addWidget(self._config_section_title("NOTIFICATIONS"))

        cfg = self.config_mgr

        section_layout.addWidget(self._config_group("SYSTEM", [

            self._config_toggle_row("System notifications", None, "notifications", "system_notifications",
                                    cfg.get("notifications", "system_notifications"),
                                    hint="Show native OS notifications for lottery events (wins, draws)"),

        ]))

        section_layout.addStretch()

        self._content_stack.addWidget(section)
        self._config_section_widgets["notifications"] = section

    def _build_config_lottery(self):

        section = QWidget()

        section_layout = QVBoxLayout(section)

        section_layout.setContentsMargins(24, 24, 24, 24)

        section_layout.setSpacing(16)

        section_layout.addWidget(self._config_section_title("LOTTERY"))

        cfg = self.config_mgr

        section_layout.addWidget(self._config_anchor("config-anchor-lottery-keyword"))

        section_layout.addWidget(self._config_group("KEYWORD", [

            self._config_input_row("Default keyword", "lottery", "default_keyword", cfg.get("lottery", "default_keyword"),
                                   hint="The keyword viewers must type in chat to enter the giveaway"),

            self._config_toggle_row("Case sensitive", None, "lottery", "case_sensitive", cfg.get("lottery", "case_sensitive"),
                                    hint="If enabled, 'Join' and 'join' are treated as different keywords"),

        ]))

        section_layout.addWidget(self._config_anchor("config-anchor-lottery-participants"))

        section_layout.addWidget(self._config_group("PARTICIPANTS", [

            self._config_toggle_row("SHOW AUTO-DELETE WINNERS", None, "lottery", "auto_delete_winners", cfg.get("lottery", "auto_delete_winners"),
                                    hint="Automatically remove winners from the participant list after drawing"),

            self._config_toggle_row("SHOW AUTO WHEEL", None, "lottery", "auto_wheel", cfg.get("lottery", "auto_wheel"),
                                    hint="Automatically spin the wheel when a winner is picked"),

            self._config_toggle_row("SHOW MANUAL ADD FIELD", None, "lottery", "show_manual_add", cfg.get("lottery", "show_manual_add"),
                                    hint="Show the manual participant entry field in the lottery tab"),

            self._config_toggle_row("SHOW DUPLICATE CHECK", None, "lottery", "duplicate_check", cfg.get("lottery", "duplicate_check"),
                                    hint="Prevent the same user from being added multiple times"),

        ]))

        section_layout.addWidget(self._build_blacklist_whitelist())

        section_layout.addStretch()

        # Wrap in QScrollArea for anchor scrolling support
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(section)
        scroll.setStyleSheet(f"""
            QScrollArea {{  border: none; background: {BG_COLOR}; }}
            QScrollBar:vertical {{  width: 6px; background: transparent; }}
            QScrollBar::handle:vertical {{  background: {BORDER_COLOR}; border-radius: 3px; min-height: 30px; }}
            QScrollBar::add-line:vertical {{  height: 0px; background: transparent; }}
            QScrollBar::sub-line:vertical {{  height: 0px; background: transparent; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{  background: transparent; }}
        """)

        self._content_stack.addWidget(scroll)

        self._config_section_widgets["lottery"] = scroll

    def _build_blacklist_whitelist(self):

        card = QFrame()

        card.setStyleSheet(f"""

            QFrame {{

                background-color: {CARD_COLOR};

                border-radius: 20px;

            }}

        """)

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(20, 16, 20, 16)

        card_layout.setSpacing(0)

        title = QLabel("BLACKLIST / WHITELIST")

        title.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 12px; font-weight: 700; letter-spacing: 0.4px; margin-bottom: 8px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

        card_layout.addWidget(title)

        cfg = self.config_mgr

        def _sep():

            s = QFrame()

            s.setStyleSheet(f"background: rgba(255,255,255,0.03);")

            s.setFixedHeight(1)

            return s

        def _make_tag_list(section, list_key):

            container = QWidget()

            container.setStyleSheet("background: transparent;")

            container_layout = QVBoxLayout(container)

            container_layout.setContentsMargins(0, 0, 0, 0)

            container_layout.setSpacing(4)

            tags_flow = QWidget()

            tags_flow.setStyleSheet("background: transparent;")

            tags_flow_layout = QHBoxLayout(tags_flow)

            tags_flow_layout.setContentsMargins(0, 0, 0, 0)

            tags_flow_layout.setSpacing(4)

            tags_flow_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            def add_tag(name):

                tag = QFrame()

                tag.setStyleSheet(f"background-color: {CARD_LIGHT}; border: 1px solid {BORDER_COLOR}; border-radius: 9999px;")

                tag_layout = QHBoxLayout(tag)

                tag_layout.setContentsMargins(10, 3, 6, 3)

                tag_layout.setSpacing(4)

                tag_lbl = QLabel(name)

                tag_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif; border: none;")

                tag_layout.addWidget(tag_lbl)

                remove_btn = QPushButton("x")

                remove_btn.setFixedSize(16, 16)

                remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)

                remove_btn.setStyleSheet(f"""

                    QPushButton {{

                        background: transparent;

                        border: none;

                        color: {DANGER_COLOR};

                        font-size: 10px;

                        font-weight: 700;

                        padding: 0;

                    }}

                """)

                remove_btn.clicked.connect(lambda: (

                    (cfg.remove_blacklist_user if list_key == 'blacklist' else cfg.remove_whitelist_user)(name),

                    tag.deleteLater()

                ))

                tag_layout.addWidget(remove_btn)

                tags_flow_layout.addWidget(tag)

            def add_user_dialog():

                dialog = QDialog(self)

                dialog.setWindowTitle("Add User")

                dialog.setFixedSize(300, 120)

                dialog.setStyleSheet(f"background-color: {CARD_COLOR};")

                d_layout = QVBoxLayout(dialog)

                d_label = QLabel("Enter username:")

                d_label.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

                d_layout.addWidget(d_label)

                d_input = QLineEdit()

                d_input.setStyleSheet(f"""

                    QLineEdit {{

                        background-color: {BG_COLOR};

                        border: 1px solid {BORDER_COLOR};

                        border-radius: 8px;

                        color: {TEXT_MAIN};

                        padding: 8px 12px;

                        font-size: 12px;

                        font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

                    }}

                    QLineEdit:focus {{  border-color: {ACCENT_LIME}; }}

                """)

                d_layout.addWidget(d_input)

                btn_layout = QHBoxLayout()

                cancel_btn = QPushButton("Cancel")

                cancel_btn.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; padding: 6px 16px; border: 1px solid {BORDER_COLOR}; border-radius: 9999px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

                cancel_btn.clicked.connect(dialog.reject)

                btn_layout.addWidget(cancel_btn)

                add_btn = QPushButton("Add")

                add_btn.setStyleSheet(f"color: {ACCENT_LIME}; font-size: 12px; padding: 6px 16px; border: 1px solid {ACCENT_LIME}; border-radius: 9999px; font-weight: 700; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

                add_btn.clicked.connect(dialog.accept)

                btn_layout.addWidget(add_btn)

                d_layout.addLayout(btn_layout)

                if dialog.exec() == QDialog.DialogCode.Accepted:

                    name = d_input.text().strip()

                    if name:

                        if list_key == 'blacklist':

                            cfg.add_blacklist_user(name)

                        else:

                            cfg.add_whitelist_user(name)

                        add_tag(name)

            users = cfg.get("lottery", list_key)

            for user in users:

                add_tag(user)

            add_btn = QPushButton("+ Add")

            add_btn.setCursor(Qt.CursorShape.PointingHandCursor)

            add_btn.setStyleSheet(f"""

                QPushButton {{

                    background: transparent;

                    border: 1px dashed {BORDER_COLOR};

                    border-radius: 9999px;

                    color: {TEXT_SEC};

                    font-size: 10px;

                    padding: 3px 10px;

                    font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

                }}

                QPushButton:hover {{

                    border-color: {ACCENT_LIME};

                    color: {ACCENT_LIME};

                }}

            """)

            add_btn.clicked.connect(add_user_dialog)

            tags_flow_layout.addWidget(add_btn)

            container_layout.addWidget(tags_flow)

            return container

        bl_row = QWidget()

        bl_row.setStyleSheet("background: transparent;")

        bl_layout = QHBoxLayout(bl_row)

        bl_layout.setContentsMargins(0, 8, 0, 8)

        bl_layout.setSpacing(0)

        bl_lbl = QLabel("Enable Blacklist")

        bl_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

        bl_layout.addWidget(bl_lbl, 1)

        bl_toggle = ToggleSwitch(initial=cfg.get("lottery", "blacklist_enabled"))

        bl_toggle.toggled.connect(lambda v: cfg.set("lottery", "blacklist_enabled", v))

        bl_layout.addWidget(bl_toggle)

        card_layout.addWidget(bl_row)

        card_layout.addWidget(_sep())

        card_layout.addSpacing(6)

        bl_label = QLabel("Blacklisted users")

        bl_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

        card_layout.addWidget(bl_label)

        card_layout.addWidget(_make_tag_list("lottery", "blacklist"))

        card_layout.addSpacing(10)

        wl_row = QWidget()

        wl_row.setStyleSheet("background: transparent;")

        wl_layout = QHBoxLayout(wl_row)

        wl_layout.setContentsMargins(0, 8, 0, 8)

        wl_layout.setSpacing(0)

        wl_lbl = QLabel("Enable Whitelist")

        wl_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

        wl_layout.addWidget(wl_lbl, 1)

        wl_toggle = ToggleSwitch(initial=cfg.get("lottery", "whitelist_enabled"))

        wl_toggle.toggled.connect(lambda v: cfg.set("lottery", "whitelist_enabled", v))

        wl_layout.addWidget(wl_toggle)

        card_layout.addWidget(wl_row)

        card_layout.addWidget(_sep())

        card_layout.addSpacing(6)

        wl_label = QLabel("Whitelisted users")

        wl_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

        card_layout.addWidget(wl_label)

        card_layout.addWidget(_make_tag_list("lottery", "whitelist"))

        wrapper = QWidget()

        wrapper_layout = QVBoxLayout(wrapper)

        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        wrapper_layout.addWidget(card)

        return wrapper

    def _build_config_wheels(self):

        section = QWidget()

        section_layout = QVBoxLayout(section)

        section_layout.setContentsMargins(24, 24, 24, 24)

        section_layout.setSpacing(16)

        section_layout.addWidget(self._config_section_title("WHEELS"))

        cfg = self.config_mgr

        section_layout.addWidget(self._config_group("INTERFACE", [

            self._config_toggle_row("Show ADD SECTOR button", None, "wheels", "show_add_sector", cfg.get("wheels", "show_add_sector"),
                                    hint="Show the button to add a new sector to the current wheel"),

            self._config_toggle_row("Show EQUALIZE button", None, "wheels", "show_equalize", cfg.get("wheels", "show_equalize"),
                                    hint="Show the button to equalize all sector sizes"),

            self._config_toggle_row("Show DELETE button", None, "wheels", "show_delete", cfg.get("wheels", "show_delete"),
                                    hint="Show the delete button for sectors"),

            self._config_toggle_row("Show RENAME button", None, "wheels", "show_rename", cfg.get("wheels", "show_rename"),
                                    hint="Show the rename button for sectors"),

            self._config_toggle_row("Show AUTO COLOR toggle", None, "wheels", "show_auto_color", cfg.get("wheels", "show_auto_color"),
                                    hint="Show the auto-color toggle for wheel sectors"),

            self._config_toggle_row("Show RANDOM COLOR toggle", None, "wheels", "show_random_color", cfg.get("wheels", "show_random_color"),
                                    hint="Show the random color toggle for wheel sectors"),

            self._config_toggle_row("Show GENERAL COLOR toggle", None, "wheels", "show_general_color", cfg.get("wheels", "show_general_color"),
                                    hint="Show the general color picker for all sectors"),

        ]))

        section_layout.addWidget(self._config_group("LABELS", [

            self._config_input_row("Max name length", "wheels", "max_name_length", cfg.get("wheels", "max_name_length", "16"),
                                   hint="Maximum number of characters allowed for sector names"),

            self._config_input_row("Text truncation (%)", "wheels", "truncation_threshold", cfg.get("wheels", "truncation_threshold", "100"),

                                   on_change=lambda v: self._apply_truncation_config(v),
                                   hint="Percentage threshold after which sector text is truncated"),

        ]))

        section_layout.addStretch()

        self._content_stack.addWidget(section)

        self._config_section_widgets["wheels"] = section

    def _build_config_case(self):

        section = QWidget()

        section_layout = QVBoxLayout(section)

        section_layout.setContentsMargins(24, 24, 24, 24)

        section_layout.setSpacing(16)

        section_layout.addWidget(self._config_section_title("CASE"))

        cfg = self.config_mgr

        section_layout.addWidget(self._config_group("INTERFACE", [

            self._config_toggle_row("Show ADD PRIZE button", None, "case", "show_add_prize", cfg.get("case", "show_add_prize"),
                                    hint="Show the button to add a new prize row"),

            self._config_toggle_row("Show EQUALIZE button", None, "case", "show_equalize", cfg.get("case", "show_equalize"),
                                    hint="Show the button to equalize all prize values"),

            self._config_toggle_row("Show AUTO COLOR toggle", None, "case", "show_auto_color", cfg.get("case", "show_auto_color"),
                                    hint="Show the auto-color toggle for case prizes"),

            self._config_toggle_row("Show RANDOM COLOR toggle", None, "case", "show_random_color", cfg.get("case", "show_random_color"),
                                    hint="Show the random color toggle for case prizes"),

            self._config_toggle_row("Show GENERAL COLOR toggle", None, "case", "show_general_color", cfg.get("case", "show_general_color"),
                                    hint="Show the general color picker for all case prizes"),

        ]))

        section_layout.addStretch()

        self._content_stack.addWidget(section)

        self._config_section_widgets["case"] = section

    def _build_config_logs(self):

        section = QWidget()

        section_layout = QVBoxLayout(section)

        section_layout.setContentsMargins(24, 24, 24, 24)

        section_layout.setSpacing(16)

        section_layout.addWidget(self._config_section_title("LOGS"))

        cfg = self.config_mgr

        section_layout.addWidget(self._config_group("HISTORY", [

            self._config_input_row("Auto-clear after (entries)", "logs", "auto_clear_entries", cfg.get("logs", "auto_clear_entries"),
                                   hint="Automatically clear the log history when it exceeds this number of entries"),

            self._config_toggle_row("Show timestamps", None, "logs", "show_timestamps", cfg.get("logs", "show_timestamps"),
                                    hint="Display timestamps next to each log entry"),

        ]))

        section_layout.addStretch()

        self._content_stack.addWidget(section)

        self._config_section_widgets["logs"] = section

    def _build_config_export(self):

        section = QWidget()

        section_layout = QVBoxLayout(section)

        section_layout.setContentsMargins(24, 24, 24, 24)

        section_layout.setSpacing(16)

        section_layout.addWidget(self._config_section_title("EXPORT / IMPORT"))

        card = QFrame()

        card.setStyleSheet(f"""

            QFrame {{

                background-color: {CARD_COLOR};

                border-radius: 20px;

            }}

        """)

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(20, 16, 20, 16)

        card_layout.setSpacing(0)

        title = QLabel("DATA")

        title.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 12px; font-weight: 700; letter-spacing: 0.4px; margin-bottom: 8px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

        card_layout.addWidget(title)

        def _btn_row(label_text, callback):

            row = QWidget()

            row.setStyleSheet("background: transparent;")

            row_layout = QHBoxLayout(row)

            row_layout.setContentsMargins(0, 8, 0, 8)

            row_layout.setSpacing(0)

            lbl = QLabel(label_text)

            lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

            row_layout.addWidget(lbl, 1)

            btn_text = label_text.split()[-1]

            btn = QPushButton(btn_text)

            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            btn.setStyleSheet(f"""

                QPushButton {{

                    background: transparent;

                    border: 1px dashed {BORDER_COLOR};

                    border-radius: 9999px;

                    color: {TEXT_SEC};

                    font-size: 11px;

                    padding: 6px 14px;

                    font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

                }}

                QPushButton:hover {{

                    border-color: {ACCENT_LIME};

                    color: {ACCENT_LIME};

                }}

            """)

            btn.clicked.connect(callback)

            row_layout.addWidget(btn)

            sep = QFrame()

            sep.setStyleSheet(f"background: rgba(255,255,255,0.03);")

            sep.setFixedHeight(1)

            container = QWidget()

            container.setStyleSheet("background: transparent;")

            cont_layout = QVBoxLayout(container)

            cont_layout.setContentsMargins(0, 0, 0, 0)

            cont_layout.setSpacing(0)

            cont_layout.addWidget(row)

            cont_layout.addWidget(sep)

            return container

        card_layout.addWidget(_btn_row("Export settings (JSON)", self._export_config))

        card_layout.addWidget(_btn_row("Import settings (JSON)", self._import_config))

        wrapper = QWidget()

        wrapper_layout = QVBoxLayout(wrapper)

        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        wrapper_layout.addWidget(card)

        section_layout.addWidget(wrapper)

        section_layout.addStretch()

        self._content_stack.addWidget(section)

        self._config_section_widgets["export"] = section

    def _build_config_reset(self):

        section = QWidget()

        section_layout = QVBoxLayout(section)

        section_layout.setContentsMargins(24, 24, 24, 24)

        section_layout.setSpacing(16)

        section_layout.addWidget(self._config_section_title("RESET"))

        card = QFrame()

        card.setStyleSheet(f"""

            QFrame {{

                background-color: {CARD_COLOR};

                border-radius: 20px;

            }}

        """)

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(20, 16, 20, 16)

        card_layout.setSpacing(0)

        row = QWidget()

        row.setStyleSheet("background: transparent;")

        row_layout = QHBoxLayout(row)

        row_layout.setContentsMargins(0, 8, 0, 8)

        row_layout.setSpacing(0)

        left = QWidget()

        left.setStyleSheet("background: transparent;")

        left_layout = QVBoxLayout(left)

        left_layout.setContentsMargins(0, 0, 0, 0)

        left_layout.setSpacing(2)

        lbl = QLabel("Reset all settings")

        lbl.setStyleSheet(f"color: {DANGER_COLOR}; font-size: 12px; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

        left_layout.addWidget(lbl)

        desc = QLabel("Restore default configuration")

        desc.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; opacity: 0.6; font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;")

        left_layout.addWidget(desc)

        row_layout.addWidget(left, 1)

        reset_btn = QPushButton("Reset")

        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.setFixedHeight(36)
        reset_btn.setFixedWidth(90)
        reset_btn.setStyleSheet(f"""

            QPushButton {{

                background: transparent;

                border: 1px solid {DANGER_COLOR};

                border-radius: 18px;

                color: {DANGER_COLOR};

                font-size: 11px;

                font-weight: 700;

                padding: 0;

                font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

            }}

            QPushButton:hover {{

                background: {DANGER_COLOR};

                color: {TEXT_MAIN};

            }}

        """)

        reset_btn.clicked.connect(self._reset_config)

        row_layout.addWidget(reset_btn)

        card_layout.addWidget(row)

        wrapper = QWidget()

        wrapper_layout = QVBoxLayout(wrapper)

        wrapper_layout.setContentsMargins(0, 0, 0, 0)

        wrapper_layout.addWidget(card)

        section_layout.addWidget(wrapper)

        section_layout.addStretch()

        self._content_stack.addWidget(section)

        self._config_section_widgets["reset"] = section

    def _export_config(self):

        from PyQt6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getSaveFileName(self, "Export Config", "config_export.json", "JSON (*.json)")

        if path:

            try:

                with open(path, 'w', encoding='utf-8') as f:

                    json.dump(self.config_mgr.export_data(), f, ensure_ascii=False, indent=4)

                show_info(self, "Success", f"Config exported to {path}")

            except Exception as e:

                show_info(self, "Error", str(e))

    def _import_config(self):

        from PyQt6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getOpenFileName(self, "Import Config", "", "JSON (*.json)")

        if path:

            try:

                with open(path, 'r', encoding='utf-8') as f:

                    data = json.load(f)

                if self.config_mgr.import_data(data):

                    show_info(self, "Success", "Config imported. Restart for full effect.")

                    self._refresh_config_ui()

                else:

                    show_info(self, "Error", "Invalid config format")

            except Exception as e:

                show_info(self, "Error", str(e))

    def _export_all_data(self):

        from core.storage import Storage

        data = {

            "config": self.config_mgr.export_data(),

            "wheels": Storage.get_wheels(),

            "cases": Storage.get_cases(),

            "logs": Storage.get_logs(),

            "export_type": "full"

        }

        path, _ = QFileDialog.getSaveFileName(self, "Export All Data", "dropzone_export.json", "JSON (*.json)")

        if path:

            try:

                with open(path, 'w', encoding='utf-8') as f:

                    json.dump(data, f, ensure_ascii=False, indent=4)

                show_info(self, "Success", f"All data exported to {path}")

            except Exception as e:

                show_info(self, "Error", str(e))

    def _import_all_data(self):

        from core.storage import Storage

        path, _ = QFileDialog.getOpenFileName(self, "Import All Data", "", "JSON (*.json)")

        if path:

            try:

                with open(path, 'r', encoding='utf-8') as f:

                    data = json.load(f)

                if not isinstance(data, dict) or data.get("export_type") != "full":

                    show_info(self, "Error", "Invalid full export file format")

                    return

                if "config" in data and isinstance(data["config"], dict):

                    self.config_mgr.import_data(data["config"])

                if "wheels" in data and isinstance(data["wheels"], dict):

                    Storage.save_wheels(data["wheels"])

                if "cases" in data and isinstance(data["cases"], dict):

                    Storage.save_cases(data["cases"])

                if "logs" in data and isinstance(data["logs"], list):

                    with open(Storage.LOGS_FILE, 'w', encoding='utf-8') as f:

                        json.dump(data["logs"], f, ensure_ascii=False, indent=4)

                show_info(self, "Success", "All data imported. Restart for full effect.")

                self._refresh_config_ui()

                self.refresh_wheels_list()

                self.refresh_cases_list()

            except Exception as e:

                show_info(self, "Error", str(e))

    def _export_wheels(self):

        from core.storage import Storage

        data = {

            "wheels": Storage.get_wheels(),

            "cases": Storage.get_cases(),

            "export_type": "wheels"

        }

        path, _ = QFileDialog.getSaveFileName(self, "Export Wheels", "wheels_export.json", "JSON (*.json)")

        if path:

            try:

                with open(path, 'w', encoding='utf-8') as f:

                    json.dump(data, f, ensure_ascii=False, indent=4)

                show_info(self, "Success", f"Wheels exported to {path}")

            except Exception as e:

                show_info(self, "Error", str(e))

    def _import_wheels(self):

        from core.storage import Storage

        path, _ = QFileDialog.getOpenFileName(self, "Import Wheels", "", "JSON (*.json)")

        if path:

            try:

                with open(path, 'r', encoding='utf-8') as f:

                    data = json.load(f)

                if not isinstance(data, dict):

                    show_info(self, "Error", "Invalid file format")

                    return

                imported_wheels = data.get("wheels", {})

                imported_cases = data.get("cases", {})

                if not isinstance(imported_wheels, dict) or not isinstance(imported_cases, dict):

                    show_info(self, "Error", "Invalid wheels data format")

                    return

                current_wheels = Storage.get_wheels()

                current_wheels.update(imported_wheels)

                Storage.save_wheels(current_wheels)

                current_cases = Storage.get_cases()

                current_cases.update(imported_cases)

                Storage.save_cases(current_cases)

                show_info(self, "Success", f"Imported {len(imported_wheels)} wheel(s) and {len(imported_cases)} case(s)")

                self.refresh_wheels_list()

                self.refresh_cases_list()

            except Exception as e:

                show_info(self, "Error", str(e))

    def _export_logs(self):

        from core.storage import Storage

        logs = Storage.get_logs()

        path, _ = QFileDialog.getSaveFileName(self, "Export Logs", "logs_export.json", "JSON (*.json)")

        if path:

            try:

                with open(path, 'w', encoding='utf-8') as f:

                    json.dump(logs, f, ensure_ascii=False, indent=4)

                show_info(self, "Success", f"Exported {len(logs)} log entries to {path}")

            except Exception as e:

                show_info(self, "Error", str(e))

    def _reset_config(self):

        dialog = ModernDialog(self, "RESET CONFIG", "This will delete all settings and restore defaults. Continue?")

        if dialog.exec() == QDialog.DialogCode.Accepted:

            self.config_mgr.reset_all()

            self._refresh_config_ui()

            show_info(self, "Success", "All settings reset to defaults")

    def _refresh_config_ui(self):

        self._apply_transparency()

        while self._content_stack.count():

            w = self._content_stack.widget(0)

            self._content_stack.removeWidget(w)

            w.deleteLater()

        self._config_section_widgets.clear()

        self._build_config_general()

        self._build_config_appearance()

        self._build_config_api()

        self._build_config_lottery()

        self._build_config_wheels()

        self._build_config_case()

        self._build_config_logs()

        self._build_config_export()

        self._build_config_reset()
        self._build_config_how_to_use()

        self._show_config_section("general")
