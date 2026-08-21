import re
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from core.theme import CARD_LIGHT, ACCENT_CYAN, BORDER_COLOR, SUCCESS_COLOR, DANGER_COLOR, ACCENT_LIME
from gui.widgets.widgets import GlowButton, RoundedLineEdit, ModernSlider
from core.utils import _dialog_adaptive, _add_drag_handle
from gui.dialogs.primitives import _add_card_mask

class ModernColorPicker(QDialog):
    def __init__(self, parent, initial_color):
        super().__init__(parent, Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("SELECT COLOR")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        _dialog_adaptive(self, parent, 0.35, 0.55, 380, 480)
        self.result = initial_color
        try:
            r = int(initial_color[1:3], 16)
            g = int(initial_color[3:5], 16)
            b = int(initial_color[5:7], 16)
        except:
            r, g, b = 0, 255, 255
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        card = QFrame(self)
        card.setObjectName("card")
        card.setStyleSheet(f"background-color: {CARD_LIGHT}; border-radius: 30px;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 40)
        card_layout.setSpacing(14)
        layout.addWidget(card)
        _add_card_mask(card)
        _add_drag_handle(card_layout, self)
        title = QLabel("COLOR PICKER", card)
        title.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 16px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)
        self.preview = QFrame(card)
        self.preview.setFixedSize(200, 60)
        self.preview.setStyleSheet(
            f"background-color: {initial_color}; border-radius: 15px; border: 1px solid {BORDER_COLOR};"
        )
        self.preview.setCursor(Qt.CursorShape.PointingHandCursor)
        card_layout.addWidget(self.preview, alignment=Qt.AlignmentFlag.AlignCenter)
        def make_slider_row(label, val):
            row = QHBoxLayout()
            row.setSpacing(8)
            lbl = QLabel(label, card)
            lbl.setFixedWidth(20)
            lbl.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 14px;")
            row.addWidget(lbl)
            sl = ModernSlider(card)
            sl.setRange(0, 255)
            sl.setValue(val)
            row.addWidget(sl, 1)
            vl = QLabel(str(val), card)
            vl.setFixedWidth(35)
            vl.setStyleSheet("color: #8E8E93; font-size: 13px;")
            vl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row.addWidget(vl)
            card_layout.addLayout(row)
            return sl, vl
        self.r_slider, self.r_val = make_slider_row("R", r)
        self.g_slider, self.g_val = make_slider_row("G", g)
        self.b_slider, self.b_val = make_slider_row("B", b)
        def update_preview():
            cr = int(self.r_slider.value())
            cg = int(self.g_slider.value())
            cb = int(self.b_slider.value())
            hex_str = f"#{cr:02X}{cg:02X}{cb:02X}"
            self.preview.setStyleSheet(
                f"background-color: {hex_str}; border-radius: 15px; border: 1px solid {BORDER_COLOR};"
            )
            self.hex_entry.setText(hex_str)
            self.r_val.setText(str(cr))
            self.g_val.setText(str(cg))
            self.b_val.setText(str(cb))
        self.r_slider.valueChanged.connect(lambda v: update_preview())
        self.g_slider.valueChanged.connect(lambda v: update_preview())
        self.b_slider.valueChanged.connect(lambda v: update_preview())
        self.hex_entry = RoundedLineEdit(card)
        self.hex_entry.setText(initial_color)
        card_layout.addWidget(self.hex_entry)
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(8)
        for c in [ACCENT_CYAN, ACCENT_LIME, SUCCESS_COLOR, DANGER_COLOR,
                  "#FF9500", "#AF52DE", "#5856D6", "#007AFF"]:
            btn = QPushButton(card)
            btn.setFixedSize(32, 32)
            btn.setStyleSheet(
                f"background-color: {c}; border-radius: 16px; border: 2px solid {BORDER_COLOR};"
            )
            btn.clicked.connect(lambda checked, col=c: self._apply_preset(col))
            preset_layout.addWidget(btn)
        card_layout.addLayout(preset_layout)
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_row.setSpacing(12)
        select_btn = GlowButton("SELECT", "lime", card)
        select_btn.setFixedSize(120, 45)
        select_btn.set_glow_enabled(False)
        select_btn.clicked.connect(self._on_ok)
        btn_row.addWidget(select_btn)
        close_btn = GlowButton("CLOSE", "ghost", card)
        close_btn.setFixedSize(120, 45)
        close_btn.set_glow_enabled(False)
        close_btn.clicked.connect(self.reject)
        btn_row.addWidget(close_btn)
        card_layout.addLayout(btn_row)
    def _apply_preset(self, color):
        self.hex_entry.setText(color)
        try:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            self.r_slider.setValue(r)
            self.g_slider.setValue(g)
            self.b_slider.setValue(b)
        except:
            pass
    def _on_ok(self):
        val = self.hex_entry.text()
        if re.match(r'^#[0-9A-Fa-f]{6}$', val):
            self.result = val
            self.accept()