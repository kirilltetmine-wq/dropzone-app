from pathlib import Path

from PyQt6.QtCore import Qt, QPoint, QPointF, QTimer

from PyQt6.QtGui import QPixmap, QColor, QPainter

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel

from core.theme import TEXT_SEC

_image_cache = {}

def _get_cached_pixmap(path):

    if not path:

        return None

    if path in _image_cache:

        return _image_cache[path]

    if not Path(path).exists():

        return None

    pix = QPixmap(path)

    if pix.isNull():

        return None

    _image_cache[path] = pix

    return pix

def _clear_image_cache():

    _image_cache.clear()

def _dialog_adaptive(dialog, parent, w_factor=0.5, h_factor=0.55, min_w=400, min_h=300):

    dialog._dialog_w_factor = w_factor
    dialog._dialog_h_factor = h_factor
    dialog._dialog_min_w = min_w
    dialog._dialog_min_h = min_h

    win = parent.window() if parent else None

    if win:
        geo = win.geometry()
        px, py = geo.x(), geo.y()
        pw, ph = geo.width(), geo.height()
    else:
        px, py, pw, ph = 0, 0, 1000, 700

    w = max(int(pw * w_factor), min_w)
    h = max(int(ph * h_factor), min_h)

    dialog.setMinimumSize(min_w, min_h)
    dialog.resize(w, h)
    dialog.move(px + (pw - w) // 2, py + (ph - h) // 2)

    # Delay position until after native window is fully created
    _orig_show = dialog.showEvent
    _win = win
    def _centered(event, d=dialog, w=_win, wf=w_factor, hf=h_factor,
                   mw=min_w, mh=min_h, orig=_orig_show):
        orig(event)
        QTimer.singleShot(0, lambda: _center_dialog(d, w, wf, hf, mw, mh))
    dialog.showEvent = _centered


def _center_dialog(d, win, wf, hf, mw, mh):
    if win:
        g = win.geometry()
        pw2, ph2 = g.width(), g.height()
        dx, dy = g.x(), g.y()
    else:
        dx = dy = 0
        pw2, ph2 = 1000, 700
    w2 = max(int(pw2 * wf), mw)
    h2 = max(int(ph2 * hf), mh)
    d.setMinimumSize(mw, mh)
    d.resize(w2, h2)
    d.move(dx + (pw2 - w2) // 2, dy + (ph2 - h2) // 2)


class _DragHandle(QWidget):

    def __init__(self, parent_dialog, dot_color="#8E8E93"):

        super().__init__(parent_dialog)

        self._dialog = parent_dialog

        self._dot_color = QColor(dot_color)

        self._dragging = False

        self._drag_start = None

        self.setFixedSize(36, 20)

        self.setCursor(Qt.CursorShape.OpenHandCursor)

        self.setToolTip("Drag to move")

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(self._dot_color)

        dot_r = 3

        y = self.height() / 2

        spacing = 9

        total_w = spacing * 2

        start_x = (self.width() - total_w) / 2

        for i in range(3):

            cx = start_x + i * spacing

            painter.drawEllipse(QPointF(cx, y), dot_r, dot_r)

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self._dragging = True

            self._drag_start = event.globalPosition().toPoint()

            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):

        if self._dragging and self._drag_start:

            delta = event.globalPosition().toPoint() - self._drag_start

            self._drag_start = event.globalPosition().toPoint()

            pos = self._dialog.pos()

            self._dialog.move(pos.x() + delta.x(), pos.y() + delta.y())

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton and self._dragging:

            self._dragging = False

            self._drag_start = None

            self.setCursor(Qt.CursorShape.OpenHandCursor)

def _add_drag_handle(card_layout, dialog):

    handle_row = QHBoxLayout()

    handle_row.setContentsMargins(0, 0, 0, 0)

    handle = _DragHandle(dialog)

    handle_row.addWidget(handle)

    handle_row.addStretch(1)

    card_layout.insertLayout(0, handle_row)
