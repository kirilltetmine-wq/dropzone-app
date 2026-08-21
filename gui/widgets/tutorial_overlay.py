from PyQt6.QtCore import Qt, QTimer, QRect, QRectF, QEvent, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPainterPath
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

from core.theme import (
    BG_COLOR, CARD_COLOR, TEXT_MAIN, TEXT_SEC,
    BORDER_COLOR, ACCENT_LIME, FONT_FAMILY, DANGER_COLOR,
)


class TutorialOverlay(QWidget):
    """Full-screen onboarding overlay — sits as a child widget covering the entire parent."""

    finished = pyqtSignal()
    step_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        # No window flags — this is a plain child widget

        self._steps = []
        self._current_step = 0
        self._highlight_rect = QRect()
        self._target_widget = None
        self._anim_progress = 0.0
        self._animating = False
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._animate_step)

        # ── Text panel (floating card) ──
        self._panel = QWidget(self)
        self._panel.setStyleSheet(f"""
            background-color: {CARD_COLOR};
            border-radius: 20px;
        """)
        panel_layout = QVBoxLayout(self._panel)
        panel_layout.setContentsMargins(24, 20, 24, 20)
        panel_layout.setSpacing(8)

        self._title_label = QLabel()
        self._title_label.setStyleSheet(f"""
            color: {ACCENT_LIME}; font-size: 18px; font-weight: 700;
            font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
            background: transparent; letter-spacing: 0.5px;
        """)
        panel_layout.addWidget(self._title_label)

        self._text_label = QLabel()
        self._text_label.setWordWrap(True)
        self._text_label.setStyleSheet(f"""
            color: {TEXT_MAIN}; font-size: 14px;
            font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
            background: transparent;
        """)
        panel_layout.addWidget(self._text_label)
        panel_layout.addSpacing(4)

        self._step_counter = QLabel()
        self._step_counter.setStyleSheet(f"""
            color: {TEXT_SEC}; font-size: 11px;
            font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
            background: transparent;
        """)
        panel_layout.addWidget(self._step_counter)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self._prev_btn = QPushButton("BACK")
        self._prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._prev_btn.setFixedHeight(36)
        self._prev_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_SEC};
                border: 1px solid {BORDER_COLOR}; border-radius: 18px;
                font-size: 11px; font-weight: 700; letter-spacing: 1px;
                padding: 8px 20px;
                font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
            }}
            QPushButton:hover {{
                color: {TEXT_MAIN}; border-color: {TEXT_MAIN};
            }}
        """)
        self._prev_btn.clicked.connect(self._go_prev)
        btn_row.addWidget(self._prev_btn)

        self._next_btn = QPushButton("NEXT")
        self._next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._next_btn.setFixedHeight(36)
        self._next_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_LIME}; color: {BG_COLOR};
                border: none; border-radius: 18px;
                font-size: 11px; font-weight: 700; letter-spacing: 1px;
                padding: 8px 24px;
                font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
            }}
            QPushButton:hover {{
                background: transparent; color: {ACCENT_LIME};
                border: 2px solid {ACCENT_LIME};
            }}
        """)
        self._next_btn.clicked.connect(self._go_next)
        btn_row.addWidget(self._next_btn)

        btn_row.addStretch()

        self._skip_btn = QPushButton("SKIP")
        self._skip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._skip_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {TEXT_SEC};
                border: none; font-size: 10px; font-weight: 600;
                letter-spacing: 0.8px; padding: 6px 12px;
                font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;
            }}
            QPushButton:hover {{ color: {DANGER_COLOR}; }}
        """)
        self._skip_btn.clicked.connect(self._skip)
        btn_row.addWidget(self._skip_btn)

        panel_layout.addLayout(btn_row)

        # Dots
        self._dots_widget = QWidget()
        self._dots_widget.setStyleSheet("background: transparent;")
        self._dots_layout = QHBoxLayout(self._dots_widget)
        self._dots_layout.setContentsMargins(0, 0, 0, 0)
        self._dots_layout.setSpacing(6)
        self._dot_labels = []
        panel_layout.addWidget(self._dots_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        self.hide()

    def set_steps(self, steps):
        for lbl in self._dot_labels:
            lbl.deleteLater()
        self._dot_labels.clear()
        for i in range(len(steps)):
            lbl = QLabel()
            lbl.setFixedSize(8, 8)
            lbl.setStyleSheet(f"background-color: {TEXT_SEC}; border-radius: 4px;")
            self._dot_labels.append(lbl)
            self._dots_layout.addWidget(lbl)
        self._steps = steps
        self._current_step = 0
        self._update_step()

    def start(self):
        """Resize to parent, show, and begin."""
        if self.parent():
            self.setGeometry(self.parent().rect())
        self._current_step = 0
        self._update_step()
        self.show()
        self.raise_()

    def _update_step(self):
        if not self._steps or self._current_step >= len(self._steps):
            return
        step = self._steps[self._current_step]
        self._title_label.setText(step.get("title", ""))
        self._text_label.setText(step.get("text", ""))
        self._step_counter.setText(f"{self._current_step + 1} / {len(self._steps)}")
        self._target_widget = step.get("target")
        padding = step.get("padding", 12)

        # Update dots
        for i, lbl in enumerate(self._dot_labels):
            c = ACCENT_LIME if i == self._current_step else TEXT_SEC
            lbl.setStyleSheet(f"background-color: {c}; border-radius: 4px;")

        # Calculate highlight rect in overlay coordinates
        if self._target_widget and self._target_widget.isVisible():
            parent = self.parent()
            if parent:
                # Map from target to shared parent (overlay covers parent entirely)
                tl = self._target_widget.mapTo(parent, self._target_widget.rect().topLeft())
                self._highlight_rect = QRect(tl, self._target_widget.size()).adjusted(-padding, -padding, padding, padding)
            else:
                self._highlight_rect = QRect()
        else:
            self._highlight_rect = QRect()

        self._prev_btn.setVisible(self._current_step > 0)
        is_last = self._current_step == len(self._steps) - 1
        self._next_btn.setText("FINISH" if is_last else "NEXT")

        # Emit step changed for tab switching etc.
        self.step_changed.emit(self._current_step)

        # Animate
        self._anim_progress = 0.0
        self._animating = True
        self._anim_timer.start(16)

        self._position_panel()
        self.update()

    def _animate_step(self):
        self._anim_progress += 0.08
        if self._anim_progress >= 1.0:
            self._anim_progress = 1.0
            self._animating = False
            self._anim_timer.stop()
        self.update()

    def _go_next(self):
        if self._current_step < len(self._steps) - 1:
            self._current_step += 1
            self._update_step()
        else:
            self._skip()

    def _go_prev(self):
        if self._current_step > 0:
            self._current_step -= 1
            self._update_step()

    def _skip(self):
        self._anim_timer.stop()
        self.hide()
        self.finished.emit()

    def _position_panel(self):
        w = self.width()
        h = self.height()
        if w < 1 or h < 1:
            return
        panel_w = min(400, w - 40)
        self._panel.setFixedWidth(panel_w)
        self._panel.adjustSize()
        panel_h = self._panel.height()
        px = (w - panel_w) // 2
        py = h - panel_h - 40
        self._panel.setGeometry(px, py, panel_w, panel_h)

    def showEvent(self, event):
        super().showEvent(event)
        if self.parent():
            self.setGeometry(self.parent().rect())
        self._position_panel()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_panel()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        if w < 1 or h < 1:
            return

        overlay_color = QColor(0, 0, 0, 180)

        if self._highlight_rect.isValid():
            # Animated scale
            if self._animating:
                scale = 0.7 + 0.3 * self._anim_progress
                c = self._highlight_rect.center()
                rw = int(self._highlight_rect.width() * scale)
                rh = int(self._highlight_rect.height() * scale)
                hr = QRect(c.x() - rw // 2, c.y() - rh // 2, rw, rh)
            else:
                hr = self._highlight_rect

            # Clip highlight rect to overlay bounds (no border outside window)
            hr = hr.intersected(QRect(0, 0, w, h))

            # Cutout: fill everything EXCEPT the highlight rect
            path = QPainterPath()
            path.addRect(0, 0, w, h)
            hole = QPainterPath()
            hole.addRoundedRect(QRectF(hr), 12, 12)
            path = path.subtracted(hole)
            painter.fillPath(path, overlay_color)

            # Glow border
            pen = QPen(QColor(ACCENT_LIME), 2)
            painter.setPen(pen)
            painter.setBrush(QBrush())
            painter.drawRoundedRect(hr, 12, 12)

        else:
            painter.fillRect(0, 0, w, h, overlay_color)

    def mousePressEvent(self, event):
        if self._highlight_rect.contains(event.position().toPoint()):
            self._go_next()