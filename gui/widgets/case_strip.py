from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal

from PyQt6.QtGui import QPainter, QFont, QFontMetrics, QPen, QColor, QPainterPath, QLinearGradient, QBrush, QPolygonF

from PyQt6.QtWidgets import QWidget

from core.theme import (

    ACCENT_CYAN, ACCENT_LIME, CARD_COLOR, TEXT_MAIN, TEXT_SEC, BORDER_COLOR, FONT_FAMILY

)

from core.utils import _get_cached_pixmap

from gui.dialogs.confirm_dialogs import SegmentInfoPopup

class WheelTabPage(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)

class _CaseStripWidget(QWidget):

    SLOT_W = 110

    selection_changed = pyqtSignal()

    def __init__(self, prizes, parent=None):

        super().__init__(parent)

        self._prizes = prizes

        self._offset = 0

        self._dragging = False

        self._drag_start_x = 0

        self._drag_start_offset = 0

        self._app = parent

        self.setMouseTracking(True)

        self.setFixedHeight(110)

        self._selected_indices = set()

        self._press_pos = None

        self._press_idx = -1

        self._press_ctrl = False

    def _slot_at_pos(self, pos_x):

        if not self._prizes:

            return -1

        n = len(self._prizes)

        abs_x = self._offset + pos_x

        idx = int(abs_x / self.SLOT_W)

        return idx % n

    def set_prizes(self, prizes):

        self._prizes = prizes

        self._offset = 0

        self._selected_indices.clear()

        self.update()

    def get_winner(self, wrapper_width):

        if not self._prizes:

            return None

        center = self._offset + wrapper_width / 2

        idx = int(center / self.SLOT_W)

        return self._prizes[idx % len(self._prizes)]

    def scroll_to(self, offset):

        self._offset = offset

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()

        h = self.height()

        if not self._prizes:

            return

        n = len(self._prizes)

        cycle_w = n * self.SLOT_W

        left_idx = int(self._offset / self.SLOT_W)

        num_slots = int(w / self.SLOT_W) + 3

        for i_offset in range(-1, num_slots):

            i = left_idx + i_offset

            idx = i % n

            p = self._prizes[idx]

            x = i * self.SLOT_W - self._offset

            if x + self.SLOT_W < -2 or x > w + 2:

                continue

            if idx in self._selected_indices:

                sel_rect = QRectF(x, 0, self.SLOT_W, h)

                painter.setPen(QPen(QColor(ACCENT_LIME), 2))

                sel_color = QColor(ACCENT_LIME)

                sel_color.setAlpha(30)

                painter.setBrush(sel_color)

                painter.drawRoundedRect(sel_rect, 4, 4)

            color_rect = QRectF(x + (self.SLOT_W - 56) / 2, 8, 56, 56)

            painter.setPen(QPen(QColor(BORDER_COLOR), 1))

            img_path = p.get('image', None)

            if img_path:

                pix = _get_cached_pixmap(img_path)

                if pix and not pix.isNull():

                    painter.save()

                    clip_path = QPainterPath()

                    clip_path.addRoundedRect(color_rect, 12, 12)

                    painter.setClipPath(clip_path)

                    img_ox = p.get('img_ox', 0)

                    img_oy = p.get('img_oy', 0)

                    img_sx = p.get('img_sx', 1.0)

                    img_sy = p.get('img_sy', 1.0)

                    iw = 56 * img_sx

                    ih = 56 * img_sy

                    img_rect = QRectF(

                        color_rect.center().x() - iw/2 + img_ox,

                        color_rect.center().y() - ih/2 + img_oy,

                        iw, ih

                    )

                    painter.drawPixmap(img_rect, pix, QRectF(0, 0, pix.width(), pix.height()))

                    painter.restore()

                    painter.setBrush(Qt.BrushStyle.NoBrush)

                    painter.drawRoundedRect(color_rect, 12, 12)

                else:

                    painter.setBrush(QColor(p['color']))

                    painter.drawRoundedRect(color_rect, 12, 12)

            else:

                painter.setBrush(QColor(p['color']))

                painter.drawRoundedRect(color_rect, 12, 12)

            painter.setPen(QColor(TEXT_SEC))

            font = painter.font()

            font.setPointSize(9)

            font.setWeight(60)

            painter.setFont(font)

            painter.drawText(QRectF(x, 68, self.SLOT_W, 30), Qt.AlignmentFlag.AlignCenter, p['name'])

            sep_x = x + self.SLOT_W

            if 0 <= sep_x <= w:

                painter.setPen(QPen(QColor(BORDER_COLOR), 1))

                painter.drawLine(QPointF(sep_x, 4), QPointF(sep_x, h - 4))

        center_x = w / 2

        line_grad = QLinearGradient(center_x, 0, center_x, h)

        line_grad.setColorAt(0, QColor(255, 255, 255, 0))

        line_grad.setColorAt(0.4, QColor(255, 255, 255, 80))

        line_grad.setColorAt(0.5, QColor(255, 255, 255, 180))

        line_grad.setColorAt(0.6, QColor(255, 255, 255, 80))

        line_grad.setColorAt(1, QColor(255, 255, 255, 0))

        painter.setPen(QPen(QBrush(line_grad), 2))

        painter.drawLine(QPointF(center_x, 4), QPointF(center_x, h - 4))

        tri_size = 6

        painter.setBrush(QColor(255, 255, 255, 180))

        painter.setPen(Qt.PenStyle.NoPen)

        top_tri = QPolygonF([

            QPointF(center_x - tri_size, 0),

            QPointF(center_x + tri_size, 0),

            QPointF(center_x, tri_size),

        ])

        painter.drawPolygon(top_tri)

        bot_tri = QPolygonF([

            QPointF(center_x - tri_size, h),

            QPointF(center_x + tri_size, h),

            QPointF(center_x, h - tri_size),

        ])

        painter.drawPolygon(bot_tri)

    def wheelEvent(self, event):

        delta = event.angleDelta().y()

        self._offset += delta

        self.update()

        if self._app and hasattr(self._app, '_case_update_glow'):

            self._app._case_update_glow()

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self._dragging = True

            self._drag_start_x = event.position().x()

            self._drag_start_offset = self._offset

            self.setCursor(Qt.CursorShape.ClosedHandCursor)

            self._press_pos = event.position()

            self._press_idx = self._slot_at_pos(self._press_pos.x())

            self._press_ctrl = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)

            if self._press_ctrl and self._press_idx >= 0:

                if self._press_idx in self._selected_indices:

                    self._selected_indices.discard(self._press_idx)

                else:

                    self._selected_indices.add(self._press_idx)

                self.update()

                self.selection_changed.emit()

        elif event.button() == Qt.MouseButton.MiddleButton:

            self._dragging = True

            self._drag_start_x = event.position().x()

            self._drag_start_offset = self._offset

            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):

        if self._dragging:

            dx = event.position().x() - self._drag_start_x

            self._offset = self._drag_start_offset - dx

            self.update()

            if self._app and hasattr(self._app, '_case_update_glow'):

                self._app._case_update_glow()

    def mouseReleaseEvent(self, event):

        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.MiddleButton) and self._dragging:

            if event.button() == Qt.MouseButton.LeftButton and self._press_pos is not None:

                dx = abs(event.position().x() - self._press_pos.x())

                if dx < 5 and not self._press_ctrl:

                    idx = self._slot_at_pos(event.position().x())

                    if idx >= 0:

                        self._selected_indices = {idx}

                        self.update()

                        self.selection_changed.emit()

                    else:

                        self._selected_indices.clear()

                        self.update()

                        self.selection_changed.emit()

            self._dragging = False

            self.setCursor(Qt.CursorShape.ArrowCursor)

            self._press_pos = None

            self._press_idx = -1

            self._press_ctrl = False

    def mouseDoubleClickEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            idx = self._slot_at_pos(event.position().x())

            if idx >= 0 and idx < len(self._prizes):

                p = self._prizes[idx]

                popup = SegmentInfoPopup(self, p['name'], p['chance'])

                popup.show()
