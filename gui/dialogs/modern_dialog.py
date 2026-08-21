from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel
from core.theme import CARD_COLOR, ACCENT_CYAN, TEXT_SEC
from gui.widgets.widgets import GlowButton, RoundedLineEdit
from core.utils import _dialog_adaptive, _add_drag_handle
from gui.dialogs.primitives import _add_card_mask

class ModernDialog(QDialog):
    def __init__(self, parent, title, message, is_input=False, placeholder=""):
        super().__init__(parent, Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle(title)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        _dialog_adaptive(self, parent, 0.35, 0.3, 400, 260)
        self.result_data = None
        self.is_input = is_input
        self._drag_start = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        card = QFrame(self)
        card.setObjectName("card")
        card.setStyleSheet(f"background-color: {CARD_COLOR}; border-radius: 30px;")
        self._card = card
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 40)
        layout.addWidget(card)
        _add_drag_handle(card_layout, self)
        _add_card_mask(card)
        card.installEventFilter(self)
        title_label = QLabel(title, card)
        title_label.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 16px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title_label)
        msg_label = QLabel(message, card)
        msg_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px;")
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setWordWrap(True)
        card_layout.addWidget(msg_label)
        if self.is_input:
            self.entry = RoundedLineEdit(card)
            self.entry.setPlaceholderText(placeholder)
            card_layout.addWidget(self.entry)
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addLayout(btn_layout)
        confirm_btn = GlowButton("CONFIRM", "lime", card)
        confirm_btn.set_glow_enabled(False)
        confirm_btn.setFixedSize(140, 45)
        confirm_btn.clicked.connect(self._on_ok)
        btn_layout.addWidget(confirm_btn)
        cancel_btn = GlowButton("CANCEL", "ghost", card)
        cancel_btn.set_glow_enabled(False)
        cancel_btn.setFixedSize(140, 45)
        cancel_btn.clicked.connect(self._on_cancel)
        btn_layout.addWidget(cancel_btn)
    def eventFilter(self, obj, event):
        if obj is self._card:
            if event.type() == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    self._drag_start = event.globalPosition().toPoint()
                    return True
            elif event.type() == QEvent.Type.MouseMove:
                if self._drag_start and event.buttons() & Qt.MouseButton.LeftButton:
                    delta = event.globalPosition().toPoint() - self._drag_start
                    self._drag_start = event.globalPosition().toPoint()
                    self.move(self.pos() + delta)
                    return True
            elif event.type() == QEvent.Type.MouseButtonRelease:
                if event.button() == Qt.MouseButton.LeftButton:
                    self._drag_start = None
                    return True
        return super().eventFilter(obj, event)
    def _on_ok(self):
        if self.is_input:
            self.result_data = self.entry.text()
        else:
            self.result_data = True
        self.accept()
    def _on_cancel(self):
        self.result_data = None
        self.reject()

def show_info(parent, title, message):
    dialog = ModernDialog(parent, title, message)
    dialog.exec()

def ask_string(parent, title, message, placeholder=""):
    dialog = ModernDialog(parent, title, message, is_input=True, placeholder=placeholder)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.result_data
    return None