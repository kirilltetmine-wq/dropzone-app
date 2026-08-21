import math

from PyQt6.QtCore import Qt, QRectF, QPointF

from PyQt6.QtGui import QColor, QPainter, QPen, QPainterPath, QPixmap

from PyQt6.QtWidgets import QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget

from core.theme import (

    BG_COLOR, CARD_COLOR, CARD_LIGHT, ACCENT_CYAN, ACCENT_LIME,

    TEXT_MAIN, TEXT_SEC, BORDER_COLOR, DANGER_COLOR, FONT_FAMILY

)

from gui.widgets.widgets import GlowButton, ModernSlider

from core.utils import _dialog_adaptive, _add_drag_handle, _get_cached_pixmap

class ImageEditorDialog(QDialog):

    def __init__(self, parent, image_path, cell_type="wheel",

                 initial_ox=0, initial_oy=0, initial_sx=1.0, initial_sy=1.0):

        super().__init__(parent, Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)

        self.setWindowTitle("IMAGE EDITOR")

        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        _dialog_adaptive(self, parent, 0.55, 0.7, 580, 680)

        self.image_path = image_path

        self.cell_type = cell_type

        self.pix = _get_cached_pixmap(image_path)

        self.ox = initial_ox

        self.oy = initial_oy

        self.sx = initial_sx

        self.sy = initial_sy

        self.result_params = None

        layout = QVBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)

        card = QFrame(self)

        card.setObjectName("card")

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(30, 25, 30, 25)

        card_layout.setSpacing(10)

        layout.addWidget(card)

        _add_drag_handle(card_layout, self)

        title = QLabel("IMAGE EDITOR", card)

        title.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 16px; font-weight: bold;")

        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(title)

        subtitle = QLabel("Drag to move · Scroll to zoom · Adjust sliders", card)

        subtitle.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px;")

        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(subtitle)

        self._preview = _ImageEditorPreview(card, self.pix, cell_type, self._get_params)

        self._preview.setMinimumSize(500, 400)

        self._preview.setStyleSheet(f"""

            background-color: {BG_COLOR}; border: 1px solid {BORDER_COLOR};

            border-radius: 12px;

        """)

        card_layout.addWidget(self._preview, 1)

        scale_row = QHBoxLayout()

        scale_row.setSpacing(8)

        scale_lbl = QLabel("SCALE", card)

        scale_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px; font-weight: bold;")

        scale_lbl.setFixedWidth(50)

        scale_row.addWidget(scale_lbl)

        self._scale_slider = ModernSlider(card)

        self._scale_slider.setRange(20, 400)

        self._scale_slider.setValue(int(initial_sx * 100))

        self._scale_slider.valueChanged.connect(self._on_scale_slider)

        scale_row.addWidget(self._scale_slider, 1)

        self._scale_val_label = QLabel(f"{initial_sx:.1f}x", card)

        self._scale_val_label.setFixedWidth(45)

        self._scale_val_label.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 12px; font-weight: bold;")

        self._scale_val_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        scale_row.addWidget(self._scale_val_label)

        card_layout.addLayout(scale_row)

        info_row = QHBoxLayout()

        info_row.setSpacing(15)

        self._ox_label = QLabel(f"OX: {initial_ox:+.0f}", card)

        self._ox_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px;")

        info_row.addWidget(self._ox_label)

        self._oy_label = QLabel(f"OY: {initial_oy:+.0f}", card)

        self._oy_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px;")

        info_row.addWidget(self._oy_label)

        self._sx_label = QLabel(f"SX: {initial_sx:.2f}", card)

        self._sx_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px;")

        info_row.addWidget(self._sx_label)

        self._sy_label = QLabel(f"SY: {initial_sy:.2f}", card)

        self._sy_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px;")

        info_row.addWidget(self._sy_label)

        info_row.addStretch(1)

        card_layout.addLayout(info_row)

        btn_row = QHBoxLayout()

        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_row.setSpacing(12)

        confirm_btn = GlowButton("CONFIRM", "lime", card)

        confirm_btn.setFixedSize(120, 45)

        confirm_btn.clicked.connect(self._on_confirm)

        btn_row.addWidget(confirm_btn)

        cancel_btn = GlowButton("CANCEL", "ghost", card)

        cancel_btn.setFixedSize(120, 45)

        cancel_btn.clicked.connect(self.reject)

        btn_row.addWidget(cancel_btn)

        reset_btn = GlowButton("RESET", "outline", card)

        reset_btn.setFixedSize(120, 45)

        reset_btn.clicked.connect(self._on_reset)

        btn_row.addWidget(reset_btn)

        card_layout.addLayout(btn_row)

    def _get_params(self):

        return self.ox, self.oy, self.sx, self.sy

    def _on_scale_slider(self, val):

        scale = val / 100.0

        self.sx = scale

        self.sy = scale

        self._scale_val_label.setText(f"{scale:.1f}x")

        self._update_info()

        self._preview.update()

    def _on_reset(self):

        self.ox = 0

        self.oy = 0

        self.sx = 1.0

        self.sy = 1.0

        self._scale_slider.setValue(100)

        self._scale_val_label.setText("1.0x")

        self._update_info()

        self._preview.update()

    def _update_info(self):

        self._ox_label.setText(f"OX: {self.ox:+.0f}")

        self._oy_label.setText(f"OY: {self.oy:+.0f}")

        self._sx_label.setText(f"SX: {self.sx:.2f}")

        self._sy_label.setText(f"SY: {self.sy:.2f}")

    def _on_confirm(self):

        self.result_params = (self.ox, self.oy, self.sx, self.sy)

        self.accept()

class _ImageEditorPreview(QWidget):

    def __init__(self, parent, pixmap, cell_type, get_params_fn):

        super().__init__(parent)

        self.pixmap = pixmap

        self.cell_type = cell_type

        self._get_params = get_params_fn

        self._dragging = False

        self._drag_start_pos = None

        self._drag_start_ox = 0

        self._drag_start_oy = 0

        self.setMouseTracking(True)

        self.setMinimumSize(400, 300)

    def _get_mask_shape(self, w, h):

        cx, cy = w / 2, h / 2

        if self.cell_type == "wheel":

            extent_deg = 60

            extent_rad = math.radians(extent_deg)

            radius = min(w, h) / 2 - 40

            mid_rad = math.radians(90)

            img_r = radius * 0.55

            seg_cx = cx + img_r * math.cos(mid_rad)

            seg_cy = cy - img_r * math.sin(mid_rad)

            seg_w = 2 * radius * math.sin(extent_rad / 2) * 1.0

            seg_h = radius * 0.85

            clip_path = QPainterPath()

            clip_path.moveTo(cx, cy)

            start_angle = 90 - extent_deg / 2

            clip_path.arcTo(QRectF(cx - radius, cy - radius, radius * 2, radius * 2),

                           start_angle, extent_deg)

            clip_path.closeSubpath()

            return clip_path, cx, cy, seg_cx, seg_cy, seg_w, seg_h

        else:

            slot_w = 110

            slot_h = 56

            seg_cx = cx

            seg_cy = cy

            seg_w = slot_w * 1.5

            seg_h = slot_h * 1.5

            clip_path = QPainterPath()

            clip_path.addRoundedRect(QRectF(cx - seg_w / 2, cy - seg_h / 2, seg_w, seg_h), 12, 12)

            return clip_path, cx, cy, seg_cx, seg_cy, seg_w, seg_h

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w, h = self.width(), self.height()

        if not self.pixmap or self.pixmap.isNull():

            painter.setPen(QColor(TEXT_SEC))

            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "NO IMAGE")

            return

        ox, oy, sx, sy = self._get_params()

        clip_path, cx, cy, seg_cx, seg_cy, seg_w, seg_h = self._get_mask_shape(w, h)

        pw = max(self.pixmap.width(), 1)

        ph = max(self.pixmap.height(), 1)

        iw = seg_w * sx

        ih = seg_h * sy

        img_x = seg_cx - iw / 2 + ox

        img_y = seg_cy - ih / 2 + oy

        painter.fillRect(self.rect(), QColor(BG_COLOR))

        painter.save()

        painter.setClipPath(clip_path)

        painter.drawPixmap(QRectF(img_x, img_y, iw, ih),

                          self.pixmap, QRectF(0, 0, pw, ph))

        painter.restore()

        outer_path = QPainterPath()

        outer_path.addRect(self.rect())

        overlay_path = outer_path.subtracted(clip_path)

        painter.setBrush(QColor(0, 0, 0, 160))

        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawPath(overlay_path)

        if self.cell_type == "wheel":

            extent_deg = 60

            radius = min(w, h) / 2 - 40

            start_angle = 90 - extent_deg / 2

            painter.setPen(QPen(QColor(ACCENT_CYAN), 2))

            painter.setBrush(Qt.BrushStyle.NoBrush)

            painter.drawPie(QRectF(cx - radius, cy - radius, radius * 2, radius * 2),

                           int(start_angle * 16), int(extent_deg * 16))

            painter.setPen(QPen(QColor(ACCENT_CYAN), 1, Qt.PenStyle.DashLine))

            painter.drawLine(QPointF(cx, cy), QPointF(seg_cx, seg_cy))

        else:

            painter.setPen(QPen(QColor(ACCENT_CYAN), 2))

            painter.setBrush(Qt.BrushStyle.NoBrush)

            painter.drawRoundedRect(QRectF(cx - seg_w / 2, cy - seg_h / 2, seg_w, seg_h), 12, 12)

        painter.setPen(QPen(QColor(255, 255, 255, 80), 1))

        painter.drawLine(QPointF(seg_cx - 8, seg_cy), QPointF(seg_cx + 8, seg_cy))

        painter.drawLine(QPointF(seg_cx, seg_cy - 8), QPointF(seg_cx, seg_cy + 8))

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton and self.pixmap and not self.pixmap.isNull():

            self._dragging = True

            self._drag_start_pos = event.position()

            ox, oy, sx, sy = self._get_params()

            self._drag_start_ox = ox

            self._drag_start_oy = oy

            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):

        if self._dragging and self._drag_start_pos:

            dx = event.position().x() - self._drag_start_pos.x()

            dy = event.position().y() - self._drag_start_pos.y()

            parent_dialog = self.window()

            if isinstance(parent_dialog, ImageEditorDialog):

                parent_dialog.ox = self._drag_start_ox + dx

                parent_dialog.oy = self._drag_start_oy + dy

                parent_dialog._update_info()

                self.update()

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton and self._dragging:

            self._dragging = False

            self._drag_start_pos = None

            self.setCursor(Qt.CursorShape.ArrowCursor)

    def wheelEvent(self, event):

        if not self.pixmap or self.pixmap.isNull():

            return

        delta = event.angleDelta().y()

        parent_dialog = self.window()

        if isinstance(parent_dialog, ImageEditorDialog):

            step = 0.1 if delta > 0 else -0.1

            new_scale = max(0.2, min(4.0, parent_dialog.sx + step))

            parent_dialog.sx = new_scale

            parent_dialog.sy = new_scale

            parent_dialog._scale_slider.setValue(int(new_scale * 100))

            parent_dialog._scale_val_label.setText(f"{new_scale:.1f}x")

            parent_dialog._update_info()

            self.update()
