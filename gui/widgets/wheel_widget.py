import math

import random

from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer, QSize, pyqtSignal

from PyQt6.QtGui import (

    QFont, QColor, QPainter, QBrush, QPen,

    QFontMetrics, QPainterPath, QPolygonF

)

from PyQt6.QtWidgets import QWidget, QSizePolicy

from core.theme import (

    BG_COLOR, CARD_COLOR, CARD_LIGHT, ACCENT_CYAN, ACCENT_LIME,

    TEXT_MAIN, TEXT_SEC, BORDER_COLOR, FONT_FAMILY

)

from core.utils import _get_cached_pixmap

class WheelWidget(QWidget):

    segment_clicked = pyqtSignal(int, str, float)

    selection_changed = pyqtSignal()

    def __init__(self, parent=None):

        super().__init__(parent)

        self._segments = []

        self._rotation = 0.0

        self._anim_timer = None

        self._is_spinning = False

        self._speed = 0.0

        self._show_labels = True

        self._hovered_idx = -1

        self._drag_idx = -1

        self._selected_indices = set()

        self._rotating = False

        self._rot_start_angle = 0.0

        self._rot_start_rotation = 0.0

        self._press_pos = None

        self._press_idx = -1

        self._press_ctrl = False

        self._drag_rect_origin = None

        self._drag_rect_current = None

        self._drag_rect_active = False

        self._skip_gradients = False

        self._truncation_ratio = 1.0

        self.setMouseTracking(True)

        self.setMinimumSize(400, 400)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_show_labels(self, show):

        self._show_labels = show

        self.update()

    def set_truncation_ratio(self, ratio):

        self._truncation_ratio = max(0.1, min(5.0, ratio))

        self.update()

    def set_segments(self, segments):

        self._segments = segments

        self._hovered_idx = -1

        self._drag_idx = -1

        self._rotation = 0.0

        self._selected_indices.clear()

        self.update()

    def selected_indices(self):

        return self._selected_indices.copy()

    def set_selected_indices(self, indices):

        self._selected_indices = set(indices)

        self.update()

        self.selection_changed.emit()

    def set_drag_idx(self, idx):

        self._drag_idx = idx

        self.update()

    def _hit_test(self, pos):

        if not self._segments:

            return -1

        w, h = self.width(), self.height()

        cx, cy = w / 2, h / 2

        radius = min(w, h) / 2 - 30

        if radius <= 0:

            return -1

        dx = pos.x() - cx

        dy = pos.y() - cy

        dist = math.sqrt(dx * dx + dy * dy)

        if dist > radius or dist < radius * 0.15:

            return -1

        qt_angle = (360 - math.degrees(math.atan2(dy, dx))) % 360

        unrotated = (qt_angle + self._rotation) % 360

        rel = (90 - unrotated) % 360

        total = sum(s['chance'] for s in self._segments)

        if total == 0: total = 1

        cum = 0

        for i, s in enumerate(self._segments):

            extent = (s['chance'] / total) * 360

            if cum <= rel < cum + extent:

                return i

            cum += extent

        return -1

    def mouseMoveEvent(self, event):

        pos = event.position()

        if self._is_spinning:

            return

        if self._rotating:

            dx = pos.x() - self.width() / 2

            dy = pos.y() - self.height() / 2

            current_angle = (360 - math.degrees(math.atan2(dy, dx))) % 360

            delta = (current_angle - self._rot_start_angle) % 360

            if delta > 180:

                delta -= 360

            self._rotation = (self._rot_start_rotation - delta) % 360

            self.update()

            return

        idx = self._hit_test(pos)

        if idx != self._hovered_idx:

            self._hovered_idx = idx

            self.update()

        if event.buttons() & Qt.MouseButton.LeftButton and self._press_pos is not None:

            if not self._drag_rect_active:

                dx = pos.x() - self._press_pos.x()

                dy = pos.y() - self._press_pos.y()

                if dx * dx + dy * dy > 25:

                    self._drag_rect_active = True

                    self._skip_gradients = True

                    self._drag_rect_origin = self._press_pos

                    self._drag_rect_current = pos

                    if not self._press_ctrl:

                        self._selected_indices.clear()

                    self.update()

                    self.selection_changed.emit()

            else:

                self._drag_rect_current = pos

                self.update()

                rect = QRectF(self._drag_rect_origin, self._drag_rect_current).normalized()

                new_set = self._rect_hit_test(rect)

                if self._press_ctrl:

                    new_set = self._selected_indices | new_set

                if new_set != self._selected_indices:

                    self._selected_indices = new_set

                    self.selection_changed.emit()

    def leaveEvent(self, event):

        if self._hovered_idx != -1:

            self._hovered_idx = -1

            self.update()

        super().leaveEvent(event)

    def _rect_hit_test(self, rect):

        if not self._segments:

            return set()

        cx = self.width() / 2

        cy = self.height() / 2

        wheel_radius = min(cx, cy) - 30

        total = sum(s['chance'] for s in self._segments)

        if total == 0:

            total = 1

        test_radii = [wheel_radius * 0.3, wheel_radius * 0.5, wheel_radius * 0.7, wheel_radius * 0.85]

        selected = set()

        cum = 0.0

        for i, s in enumerate(self._segments):

            extent = (s['chance'] / total) * 360

            found = False

            for frac in [0.15, 0.5, 0.85]:

                if found:

                    break

                rel_angle = cum + extent * frac

                unrotated = (90 - rel_angle) % 360

                qt_angle = (unrotated - self._rotation) % 360

                rad = math.radians(qt_angle)

                for test_r in test_radii:

                    px = cx + test_r * math.cos(rad)

                    py = cy - test_r * math.sin(rad)

                    if rect.contains(QPointF(px, py)):

                        selected.add(i)

                        found = True

                        break

            cum += extent

        return selected

    def mousePressEvent(self, event):

        if self._is_spinning:

            return

        if event.button() == Qt.MouseButton.MiddleButton:

            pos = event.position()

            dx = pos.x() - self.width() / 2

            dy = pos.y() - self.height() / 2

            self._rot_start_angle = (360 - math.degrees(math.atan2(dy, dx))) % 360

            self._rot_start_rotation = self._rotation

            self._rotating = True

            self.setCursor(Qt.CursorShape.ClosedHandCursor)

            return

        if event.button() != Qt.MouseButton.LeftButton:

            return

        self._press_pos = event.position()

        self._press_idx = self._hit_test(self._press_pos)

        self._press_ctrl = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)

        if self._press_ctrl and self._press_idx >= 0:

            if self._press_idx in self._selected_indices:

                self._selected_indices.discard(self._press_idx)

            else:

                self._selected_indices.add(self._press_idx)

            self.update()

            self.selection_changed.emit()

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MouseButton.MiddleButton:

            self._rotating = False

            self.setCursor(Qt.CursorShape.ArrowCursor)

        elif event.button() == Qt.MouseButton.LeftButton:

            if self._drag_rect_active:

                self._drag_rect_active = False

                self._skip_gradients = False

                self._drag_rect_origin = None

                self._drag_rect_current = None

                self.update()

            elif self._press_pos is not None and not self._press_ctrl:

                if self._press_idx >= 0:

                    if self._press_idx in self._selected_indices and len(self._selected_indices) == 1:

                        s = self._segments[self._press_idx]

                        self.segment_clicked.emit(self._press_idx, s['prize'], s['chance'])

                    else:

                        self._selected_indices = {self._press_idx}

                        self.update()

                        self.selection_changed.emit()

                else:

                    if self._selected_indices:

                        self._selected_indices.clear()

                        self.update()

                        self.selection_changed.emit()

            self._press_pos = None

            self._press_idx = -1

            self._press_ctrl = False

        super().mouseReleaseEvent(event)

    def start_spin(self, callback=None):

        if self._is_spinning or not self._segments:

            return

        self._is_spinning = True

        self._speed = random.uniform(30, 50)

        self._callback = callback

        self._spin_step()

    def _spin_step(self):

        if self._speed < 0.05:

            self._is_spinning = False

            self._speed = 0.0

            if self._callback:

                self._callback()

            return

        self._rotation = (self._rotation + self._speed) % 360

        self._speed *= 0.990

        self.update()

        if self._anim_timer:

            self._anim_timer.stop()

        self._anim_timer = QTimer.singleShot(16, self._spin_step)

    def get_winner(self):

        if not self._segments:

            return None

        total = sum(s['chance'] for s in self._segments)

        target = (-self._rotation) % 360

        cum = 0

        for s in self._segments:

            extent = (s['chance'] / total) * 360

            if cum <= target < cum + extent:

                return s['prize']

            cum += extent

        return self._segments[-1]['prize']

    def _generate_gradient(self, base_color, factor=0.4):

        hex_c = base_color.lstrip('#')

        rgb = [int(hex_c[i:i+2], 16) for i in (0, 2, 4)]

        new_rgb = [

            min(255, int(rgb[0] * (1 + factor))),

            min(255, int(rgb[1] * (1 + factor * 0.7))),

            max(0, int(rgb[2] * (1 - factor)))

        ]

        return QColor(new_rgb[0], new_rgb[1], new_rgb[2])

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        cx, cy = w / 2, h / 2

        radius = min(w, h) / 2 - 30

        if radius <= 0: return

        painter.translate(cx, cy)

        painter.rotate(self._rotation)

        painter.translate(-cx, -cy)

        if not self._segments:

            painter.setPen(Qt.PenStyle.NoPen)

            painter.setBrush(QColor(CARD_LIGHT))

            painter.drawEllipse(QRectF(cx - radius, cy - radius, radius*2, radius*2))

            painter.setPen(QColor(TEXT_SEC))

            painter.setFont(QFont(str(FONT_FAMILY), 14))

            painter.drawText(QRectF(cx - radius, cy - radius, radius*2, radius*2),

                           Qt.AlignmentFlag.AlignCenter, "EMPTY WHEEL")

            _total = 1

        else:

            total = sum(s['chance'] for s in self._segments)

            _total = total

            if total == 0: total = 1

            start_angle = 90 * 16

            for i, s in enumerate(self._segments):

                extent = -(s['chance'] / total) * 360 * 16

                if extent >= 0: continue

                is_hovered = (i == self._hovered_idx)

                is_dragged = (i == self._drag_idx)

                is_selected = (i in self._selected_indices)

                base_color = QColor(s.get('color', ACCENT_CYAN))

                grad_color = self._generate_gradient(s.get('color', ACCENT_CYAN), 0.4)

                if self._skip_gradients:

                    r = base_color.red()

                    g = base_color.green()

                    b = base_color.blue()

                    if is_hovered:

                        r = min(255, int(r * 1.3))

                        g = min(255, int(g * 1.3))

                        b = min(255, int(b * 1.3))

                    if is_dragged:

                        r = min(255, int(r * 0.8 + 0))

                        g = min(255, int(g * 0.8 + 60))

                        b = min(255, int(b * 0.8 + 180))

                    painter.setBrush(QColor(r, g, b))

                    painter.setPen(Qt.PenStyle.NoPen)

                    painter.drawPie(QRectF(cx - radius, cy - radius, radius*2, radius*2),

                                  int(start_angle), int(extent))

                else:

                    layers = 24

                    for layer in range(layers):

                        f = layer / (layers - 1)

                        r = int(grad_color.red() + (base_color.red() - grad_color.red()) * f)

                        g = int(grad_color.green() + (base_color.green() - grad_color.green()) * f)

                        b = int(grad_color.blue() + (base_color.blue() - grad_color.blue()) * f)

                        if is_hovered:

                            r = min(255, int(r * 1.3))

                            g = min(255, int(g * 1.3))

                            b = min(255, int(b * 1.3))

                        if is_dragged:

                            r = min(255, int(r * 0.8 + 0))

                            g = min(255, int(g * 0.8 + 60))

                            b = min(255, int(b * 0.8 + 180))

                        shrink = f * (radius * 0.85)

                        cur_r = radius - shrink

                        painter.setBrush(QColor(r, g, b))

                        painter.setPen(Qt.PenStyle.NoPen)

                        painter.drawPie(QRectF(cx - cur_r, cy - cur_r, cur_r*2, cur_r*2),

                                      int(start_angle), int(extent))

                img_path = s.get('image', None)

                if img_path:

                    pix = _get_cached_pixmap(img_path)

                    if pix and not pix.isNull():

                        painter.save()

                        clip_path = QPainterPath()

                        clip_path.moveTo(cx, cy)

                        clip_path.arcTo(QRectF(cx - radius, cy - radius, radius*2, radius*2),

                                        start_angle / 16, extent / 16)

                        clip_path.closeSubpath()

                        painter.setClipPath(clip_path)

                        mid_angle = start_angle + extent / 2

                        mid_deg = mid_angle / 16

                        mid_rad = math.radians(mid_deg)

                        extent_deg = extent / 16

                        extent_rad = math.radians(abs(extent_deg))

                        img_r = radius * 0.55

                        img_cx = cx + img_r * math.cos(mid_rad)

                        img_cy = cy - img_r * math.sin(mid_rad)

                        seg_w = 2 * radius * math.sin(extent_rad / 2) * 1.6

                        seg_h = radius * 1.2

                        pw = max(pix.width(), 1)

                        ph = max(pix.height(), 1)

                        img_ox = s.get('img_ox', 0)

                        img_oy = s.get('img_oy', 0)

                        img_sx = s.get('img_sx', 1.0)

                        img_sy = s.get('img_sy', 1.0)

                        iw = seg_w * img_sx

                        ih = seg_h * img_sy

                        painter.drawPixmap(

                            QRectF(img_cx - iw/2 + img_ox, img_cy - ih/2 + img_oy, iw, ih),

                            pix, QRectF(0, 0, pw, ph))

                        painter.restore()

                if is_dragged:

                    border_width = 4

                    border_color = QColor(ACCENT_CYAN)

                elif is_selected:

                    border_width = 3

                    border_color = QColor(ACCENT_LIME)

                elif is_hovered:

                    border_width = 3

                    border_color = QColor(ACCENT_LIME)

                else:

                    border_width = 2

                    border_color = QColor(BG_COLOR)

                painter.setPen(QPen(border_color, border_width))

                painter.setBrush(Qt.BrushStyle.NoBrush)

                painter.drawPie(QRectF(cx - radius, cy - radius, radius*2, radius*2),

                              int(start_angle), int(extent))

                if self._show_labels:

                    mid_angle = start_angle + extent / 2

                    mid_deg = mid_angle / 16

                    rad = math.radians(mid_deg)

                    extent_deg = extent / 16

                    extent_rad = math.radians(abs(extent_deg))

                    text_r = radius * 0.60

                    orig_mid_deg = mid_deg - self._rotation

                    orig_rad = math.radians(orig_mid_deg)

                    tx_orig = cx + text_r * math.cos(orig_rad)

                    ty_orig = cy - text_r * math.sin(orig_rad)

                    painter.save()

                    painter.resetTransform()

                    painter.translate(tx_orig, ty_orig)

                    painter.setPen(QColor(TEXT_MAIN))

                    font = QFont(str(FONT_FAMILY), 9)

                    painter.setFont(font)

                    fm = QFontMetrics(font)

                    text = s['prize']

                    text_w = fm.horizontalAdvance(text)

                    text_h = fm.height()

                    chord_w = 2 * text_r * math.sin(extent_rad / 2)

                    max_text_w = max(chord_w * self._truncation_ratio, 20)

                    while text_w > max_text_w and len(text) > 3:

                        text = text[:-3] + ".."

                        text_w = fm.horizontalAdvance(text)

                    painter.drawText(QRectF(-text_w/2, -text_h/2, text_w, text_h),

                                   Qt.AlignmentFlag.AlignCenter, text)

                    painter.restore()

                start_angle += extent

        painter.resetTransform()

        ptr_size = 25

        ptr_points = QPolygonF([

            QPointF(cx - ptr_size, cy - radius - ptr_size),

            QPointF(cx + ptr_size, cy - radius - ptr_size),

            QPointF(cx, cy - radius + ptr_size)

        ])

        painter.setPen(QPen(QColor("#FFFFFF"), 2))

        painter.setBrush(QColor(ACCENT_LIME))

        painter.drawPolygon(ptr_points)

        painter.setPen(QPen(QColor(ACCENT_LIME), 5))

        painter.setBrush(QColor(CARD_LIGHT))

        painter.drawEllipse(QRectF(cx - 35, cy - 35, 70, 70))

        if self._drag_rect_active and self._drag_rect_origin and self._drag_rect_current:

            painter.setPen(QPen(QColor(ACCENT_CYAN), 1.5))

            painter.setBrush(QColor(0, 245, 255, 25))

            rect = QRectF(self._drag_rect_origin, self._drag_rect_current).normalized()

            painter.drawRect(rect)

        painter.end()
