import re
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QPushButton, QStackedWidget
from core.theme import BG_COLOR, CARD_LIGHT, ACCENT_CYAN, ACCENT_LIME, TEXT_SEC, BORDER_COLOR, SUCCESS_COLOR, DANGER_COLOR
from gui.widgets.widgets import GlowButton, RoundedLineEdit, ModernSlider
from core.utils import _dialog_adaptive, _add_drag_handle, _get_cached_pixmap
from gui.dialogs.primitives import _add_card_mask

class ModernItemPicker(QDialog):
    def __init__(self, parent, initial_color, initial_image=None, cell_type="wheel"):
        super().__init__(parent, Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("PICK COLOR / IMAGE")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        _dialog_adaptive(self, parent, 0.45, 0.6, 440, 540)
        self.result = ("color", initial_color)
        self._chosen_image_path = initial_image
        self._cell_type = cell_type
        self.editor_params = {"ox": 0, "oy": 0, "sx": 1.0, "sy": 1.0}
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
        card_layout.setContentsMargins(30, 25, 30, 40)
        card_layout.setSpacing(10)
        layout.addWidget(card)
        _add_card_mask(card)
        _add_drag_handle(card_layout, self)
        title = QLabel("PICK COLOR / IMAGE", card)
        title.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 16px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)
        mode_row = QHBoxLayout()
        mode_row.setSpacing(8)
        self._color_mode_btn = QPushButton("COLOR", card)
        self._color_mode_btn.setCheckable(True)
        self._color_mode_btn.setChecked(True)
        self._color_mode_btn.setFixedHeight(36)
        self._color_mode_btn.setStyleSheet(f"""
            QPushButton {{  background: {CARD_LIGHT}; color: {TEXT_SEC};
                           border: 1px solid {BORDER_COLOR}; border-radius: 18px;
                           font-size: 13px; font-weight: bold; }}
            QPushButton:checked {{  background: {ACCENT_CYAN}; color: {BG_COLOR};
                                   border: 1px solid {ACCENT_CYAN}; }}
        """)
        self._img_mode_btn = QPushButton("IMAGE", card)
        self._img_mode_btn.setCheckable(True)
        self._img_mode_btn.setFixedHeight(36)
        self._img_mode_btn.setStyleSheet(f"""
            QPushButton {{  background: {CARD_LIGHT}; color: {TEXT_SEC};
                           border: 1px solid {BORDER_COLOR}; border-radius: 18px;
                           font-size: 13px; font-weight: bold; }}
            QPushButton:checked {{  background: {ACCENT_CYAN}; color: {BG_COLOR};
                                   border: 1px solid {ACCENT_CYAN}; }}
        """)
        def _switch_to_color():
            self._color_mode_btn.setChecked(True)
            self._img_mode_btn.setChecked(False)
            self._stack.setCurrentIndex(0)
        def _switch_to_image():
            self._color_mode_btn.setChecked(False)
            self._img_mode_btn.setChecked(True)
            self._stack.setCurrentIndex(1)
        self._color_mode_btn.clicked.connect(_switch_to_color)
        self._img_mode_btn.clicked.connect(_switch_to_image)
        mode_row.addWidget(self._color_mode_btn)
        mode_row.addWidget(self._img_mode_btn)
        card_layout.addLayout(mode_row)
        self._stack = QStackedWidget(card)
        card_layout.addWidget(self._stack, 1)
        color_panel = QWidget()
        color_panel.setStyleSheet("background: transparent;")
        cp_layout = QVBoxLayout(color_panel)
        cp_layout.setContentsMargins(0, 0, 0, 0)
        cp_layout.setSpacing(10)
        self.preview = QFrame(color_panel)
        self.preview.setFixedSize(200, 50)
        self.preview.setStyleSheet(
            f"background-color: {initial_color}; border-radius: 12px; border: 1px solid {BORDER_COLOR};"
        )
        self.preview.setCursor(Qt.CursorShape.PointingHandCursor)
        cp_layout.addWidget(self.preview, alignment=Qt.AlignmentFlag.AlignCenter)
        def make_slider_row(label, val):
            row = QHBoxLayout()
            row.setSpacing(6)
            lbl = QLabel(label, color_panel)
            lbl.setFixedWidth(18)
            lbl.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 13px;")
            row.addWidget(lbl)
            sl = ModernSlider(color_panel)
            sl.setRange(0, 255)
            sl.setValue(val)
            row.addWidget(sl, 1)
            vl = QLabel(str(val), color_panel)
            vl.setFixedWidth(30)
            vl.setStyleSheet("color: #8E8E93; font-size: 12px;")
            vl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row.addWidget(vl)
            cp_layout.addLayout(row)
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
                f"background-color: {hex_str}; border-radius: 12px; border: 1px solid {BORDER_COLOR};"
            )
            self.hex_entry.setText(hex_str)
            self.r_val.setText(str(cr))
            self.g_val.setText(str(cg))
            self.b_val.setText(str(cb))
        self.r_slider.valueChanged.connect(lambda v: update_preview())
        self.g_slider.valueChanged.connect(lambda v: update_preview())
        self.b_slider.valueChanged.connect(lambda v: update_preview())
        self.hex_entry = RoundedLineEdit(color_panel)
        self.hex_entry.setText(initial_color)
        cp_layout.addWidget(self.hex_entry)
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(6)
        for c in [ACCENT_CYAN, ACCENT_LIME, SUCCESS_COLOR, DANGER_COLOR,
                  "#FF9500", "#AF52DE", "#5856D6", "#007AFF"]:
            btn = QPushButton(color_panel)
            btn.setFixedSize(28, 28)
            btn.setStyleSheet(
                f"background-color: {c}; border-radius: 14px; border: 2px solid {BORDER_COLOR};"
            )
            btn.clicked.connect(lambda checked, col=c: self._apply_preset(col))
            preset_layout.addWidget(btn)
        cp_layout.addLayout(preset_layout)
        self._stack.addWidget(color_panel)
        img_panel = QWidget()
        img_panel.setStyleSheet("background: transparent;")
        ip_layout = QVBoxLayout(img_panel)
        ip_layout.setContentsMargins(0, 0, 0, 0)
        ip_layout.setSpacing(10)
        ip_layout.addStretch(1)
        self._img_preview = QLabel(img_panel)
        self._img_preview.setFixedSize(200, 150)
        self._img_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._img_preview.setStyleSheet(
            f"background-color: {CARD_LIGHT}; border: 1px solid {BORDER_COLOR}; border-radius: 12px; color: {TEXT_SEC}; font-size: 12px;"
        )
        self._img_preview.setText("NO IMAGE SELECTED")
        ip_layout.addWidget(self._img_preview, alignment=Qt.AlignmentFlag.AlignCenter)
        self._img_path_label = QLabel("", img_panel)
        self._img_path_label.setWordWrap(True)
        self._img_path_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px; background: transparent;")
        self._img_path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._img_path_label.setMaximumWidth(400)
        ip_layout.addWidget(self._img_path_label, alignment=Qt.AlignmentFlag.AlignCenter)
        btn_row2 = QHBoxLayout()
        btn_row2.setSpacing(10)
        btn_row2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        browse_btn = GlowButton("BROWSE", "outline", img_panel)
        browse_btn.setFixedSize(130, 40)
        browse_btn.clicked.connect(self._on_browse_image)
        btn_row2.addWidget(browse_btn)
        clear_img_btn = GlowButton("CLEAR", "ghost", img_panel)
        clear_img_btn.setFixedSize(130, 40)
        clear_img_btn.clicked.connect(self._on_clear_image)
        btn_row2.addWidget(clear_img_btn)
        ip_layout.addLayout(btn_row2)
        ip_layout.addStretch(1)
        self._stack.addWidget(img_panel)
        if initial_image and Path(initial_image).exists():
            self._chosen_image_path = initial_image
            self._show_image_preview(initial_image)
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
    def _show_image_preview(self, path):
        pix = _get_cached_pixmap(path)
        if pix and not pix.isNull():
            scaled = pix.scaled(200, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self._img_preview.setPixmap(scaled)
            self._img_path_label.setText(path)
        else:
            self._img_preview.setText("INVALID IMAGE")
            self._img_preview.setPixmap(QPixmap())
            self._img_path_label.setText("")
    def _on_browse_image(self):
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Images (*.png *.jpg *.jpeg *.webp);;All Files (*)",
            options=QFileDialog.Option.DontUseNativeDialog
        )
        if path:
            self._chosen_image_path = path
            self._show_image_preview(path)
    def _on_clear_image(self):
        self._chosen_image_path = None
        self._img_preview.setPixmap(QPixmap())
        self._img_preview.setText("NO IMAGE SELECTED")
        self._img_path_label.setText("")
        self.editor_params = {"ox": 0, "oy": 0, "sx": 1.0, "sy": 1.0}
    def _on_ok(self):
        if self._color_mode_btn.isChecked():
            val = self.hex_entry.text()
            if re.match(r'^#[0-9A-Fa-f]{6}$', val):
                self.result = ("color", val)
                self.accept()
        else:
            if self._chosen_image_path and Path(self._chosen_image_path).exists():
                self.result = ("image", self._chosen_image_path)
                self.accept()
            else:
                val = self.hex_entry.text()
                if re.match(r'^#[0-9A-Fa-f]{6}$', val):
                    self.result = ("color", val)
                    self.accept()