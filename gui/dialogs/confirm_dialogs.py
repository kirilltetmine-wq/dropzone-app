from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel
from core.theme import CARD_COLOR, ACCENT_CYAN, ACCENT_LIME, TEXT_SEC, DANGER_COLOR
from gui.widgets.widgets import GlowButton
from core.utils import _dialog_adaptive, _add_drag_handle
from gui.dialogs.primitives import _add_card_mask

class SegmentInfoPopup(QDialog):
    def __init__(self, parent, prize, chance):
        super().__init__(parent, Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        _dialog_adaptive(self, parent, 0.18, 0.15, 180, 120)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        card = QFrame(self)
        card.setObjectName("card")
        card.setStyleSheet(f"""
            #card {{
                background-color: {CARD_COLOR};
                border-radius: 20px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(card)
        _add_card_mask(card)
        _add_drag_handle(card_layout, self)
        prize_label = QLabel(prize.upper(), card)
        prize_label.setStyleSheet(f"""
            color: {ACCENT_LIME}; font-size: 18px; font-weight: 700;
        """)
        prize_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prize_label.setWordWrap(True)
        card_layout.addWidget(prize_label)
        pct_label = QLabel(f"{chance:.1f}% chance", card)
        pct_label.setStyleSheet(f"""
            color: {TEXT_SEC}; font-size: 12px; font-weight: 500;
        """)
        pct_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(pct_label)
    def resizeEvent(self, event):
        super().resizeEvent(event)
    def mousePressEvent(self, event):
        self.close()

class DeleteConfirmDialog(QDialog):
    _skip_confirm = False
    def __init__(self, parent, count):
        super().__init__(parent, Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self._count = count
        self._countdown = 3
        self._confirmed = False
        self._cancelled = False
        self.setWindowTitle("DELETE")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        _dialog_adaptive(self, parent, 0.35, 0.3, 380, 240)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        card = QFrame(self)
        card.setObjectName("card")
        card.setStyleSheet(f"background-color: {CARD_COLOR}; border-radius: 30px;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 40)
        card_layout.setSpacing(16)
        layout.addWidget(card)
        _add_card_mask(card)
        _add_drag_handle(card_layout, self)
        self.title = QLabel("DELETE", card)
        self.title.setStyleSheet(f"color: {DANGER_COLOR}; font-size: 16px; font-weight: bold;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.title)
        self.msg = QLabel(
            f"Do you really want to delete {count} item{'s' if count > 1 else ''}?\n"
            "This action cannot be undone.",
            card
        )
        self.msg.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px;")
        self.msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg.setWordWrap(True)
        card_layout.addWidget(self.msg)
        self.dont_show_cb = QLabel("☐  Don't show me again", card)
        self.dont_show_cb.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; cursor: pointer;")
        self.dont_show_cb.setCursor(Qt.CursorShape.PointingHandCursor)
        card_layout.addWidget(self.dont_show_cb, alignment=Qt.AlignmentFlag.AlignCenter)
        self.btn_row = QHBoxLayout()
        self.btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_row.setSpacing(12)
        card_layout.addLayout(self.btn_row)
        self.confirm_btn = GlowButton("CONFIRM", "danger", card)
        self.confirm_btn.set_glow_enabled(False)
        self.confirm_btn.setFixedSize(140, 45)
        self.confirm_btn.clicked.connect(self._on_confirm)
        self.btn_row.addWidget(self.confirm_btn)
        self.cancel_btn = GlowButton("CANCEL", "ghost", card)
        self.cancel_btn.set_glow_enabled(False)
        self.cancel_btn.setFixedSize(140, 45)
        self.cancel_btn.clicked.connect(self.reject)
        self.btn_row.addWidget(self.cancel_btn)
        self._in_countdown = False
    def mousePressEvent(self, event):
        pos = event.position().toPoint()
        if self.dont_show_cb.geometry().contains(pos):
            self._toggle_dont_show()
        super().mousePressEvent(event)
    def _toggle_dont_show(self):
        if DeleteConfirmDialog._skip_confirm:
            DeleteConfirmDialog._skip_confirm = False
            self.dont_show_cb.setText("☐  Don't show me again")
        else:
            DeleteConfirmDialog._skip_confirm = True
            self.dont_show_cb.setText("☑  Don't show me again")
    def _on_confirm(self):
        if self._in_countdown:
            return
        self._in_countdown = True
        self._confirmed = True
        self._countdown = 3
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.setText("...")
        self._tick()
    def _tick(self):
        if self._countdown <= 0:
            self.accept()
            return
        self.msg.setText(
            f"You can cancel the action within\n{self._countdown}"
        )
        self.cancel_btn.setText(f"CANCEL ({self._countdown})")
        self._countdown -= 1
        QTimer.singleShot(1000, self._tick)

class BatchValueDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent, Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.dont_show_again = False
        self.setWindowTitle("BATCH VALUE")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        _dialog_adaptive(self, parent, 0.3, 0.25, 360, 200)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        card = QFrame(self)
        card.setObjectName("card")
        card.setStyleSheet(f"background-color: {CARD_COLOR}; border-radius: 30px;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 40)
        card_layout.setSpacing(14)
        layout.addWidget(card)
        _add_card_mask(card)
        _add_drag_handle(card_layout, self)
        title = QLabel("BATCH VALUE", card)
        title.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 16px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)
        msg = QLabel(
            "You are trying to change the value\nfor all objects.",
            card
        )
        msg.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px;")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setWordWrap(True)
        card_layout.addWidget(msg)
        self.dont_show_lbl = QLabel("☐  Don't show me again", card)
        self.dont_show_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; cursor: pointer;")
        self.dont_show_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dont_show_lbl.mousePressEvent = lambda e: self._toggle_dont_show()
        card_layout.addWidget(self.dont_show_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_row.setSpacing(12)
        card_layout.addLayout(btn_row)
        ok_btn = GlowButton("APPLY", "lime", card)
        ok_btn.set_glow_enabled(False)
        ok_btn.setFixedSize(120, 45)
        ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(ok_btn)
        cancel_btn = GlowButton("CANCEL", "ghost", card)
        cancel_btn.set_glow_enabled(False)
        cancel_btn.setFixedSize(120, 45)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
    def _toggle_dont_show(self):
        self.dont_show_again = not self.dont_show_again
        if self.dont_show_again:
            self.dont_show_lbl.setText("☑  Don't show me again")
        else:
            self.dont_show_lbl.setText("☐  Don't show me again")