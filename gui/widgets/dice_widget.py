import math

import random

from pathlib import Path

from PyQt6.QtCore import Qt, QRectF, QTimer, QSize, QPointF

from PyQt6.QtGui import (

    QFont, QColor, QPainter, QPen, QBrush, QFontMetrics, QPixmap, QIcon, QPainterPath,

    QPolygonF, QTransform, QLinearGradient

)

from PyQt6.QtWidgets import (

    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,

    QSplitter, QLineEdit, QSizePolicy, QMessageBox, QDialog

)

from core.theme import (

    BG_COLOR, CARD_COLOR, CARD_LIGHT, ACCENT_CYAN, ACCENT_LIME,

    TEXT_MAIN, TEXT_SEC, BORDER_COLOR, DANGER_COLOR, FONT_FAMILY,

    PLUS_PATH, LEFT_ARROW_PATH, RIGHT_ARROW_PATH

)

from gui.widgets.widgets import (

    GlowButton, HoverIconButton, RoundedButton, RoundedLineEdit,

    WheelDropdown, ToggleSwitch, ModernSlider

)

from gui.dialogs.primitives import DragHandle, DropContainer
from gui.dialogs.modern_dialog import ModernDialog, ask_string
from gui.dialogs.color_picker import ModernColorPicker
from gui.dialogs.item_picker import ModernItemPicker

from core.utils import _get_cached_pixmap

class DiceCubeWidget(QWidget):

    FACE_COLORS = ["#FF3B30", "#FF9500", "#CCFF00", "#00F5FF", "#AF52DE", "#007AFF"]

    def __init__(self, parent=None):

        super().__init__(parent)

        self._faces = ["Да", "Нет", "Возможно", "Пропуск", "Повторить", "Скидка"]

        self._face_colors = list(self.FACE_COLORS)

        self._face_images = [None] * 6

        self._base_angle_x = 15.0

        self._base_angle_y = 15.0

        self._base_angle_z = 0.0

        self._drag_offset_x = 0.0

        self._drag_offset_y = 0.0

        self._drag_offset_z = 0.0

        self._angle_x = 15.0

        self._angle_y = 15.0

        self._angle_z = 0.0

        self._is_rolling = False

        self._anim_progress = 0.0

        self._anim_timer = None

        self._on_finish = None

        self._target_rx = 0.0

        self._target_ry = 0.0

        self._target_rz = 0.0

        self._start_rx = 0.0

        self._start_ry = 0.0

        self._start_rz = 0.0

        self._tilt_rx = 0.0

        self._tilt_ry = 0.0

        self._tilt_rz = 0.0

        self._is_dragging = False

        self._drag_start_x = 0

        self._drag_start_y = 0

        self._drag_ox = 0.0

        self._drag_oy = 0.0

        self.setMinimumSize(180, 180)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.setMouseTracking(True)

        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def _update_angle(self):

        self._angle_x = self._base_angle_x + self._drag_offset_x

        self._angle_y = self._base_angle_y + self._drag_offset_y

        self._angle_z = self._base_angle_z + self._drag_offset_z

    def mousePressEvent(self, event):

        if self._is_rolling:

            event.ignore()

            return

        if event.button() in (Qt.MouseButton.MiddleButton, Qt.MouseButton.LeftButton):

            self._is_dragging = True

            self._drag_start_x = event.position().x()

            self._drag_start_y = event.position().y()

            self._drag_ox = self._drag_offset_x

            self._drag_oy = self._drag_offset_y

            self.setCursor(Qt.CursorShape.ClosedHandCursor)

            event.accept()

        else:

            event.ignore()

    def mouseMoveEvent(self, event):

        if not self._is_dragging:

            return

        dx = event.position().x() - self._drag_start_x

        dy = event.position().y() - self._drag_start_y

        self._drag_offset_x = self._drag_ox + dy * 0.5

        self._drag_offset_y = self._drag_oy - dx * 0.5

        self._update_angle()

        self.update()

        event.accept()

    def mouseReleaseEvent(self, event):

        if event.button() in (Qt.MouseButton.MiddleButton, Qt.MouseButton.LeftButton) and self._is_dragging:

            self._is_dragging = False

            self._base_angle_x += self._drag_offset_x

            self._base_angle_y += self._drag_offset_y

            self._base_angle_z += self._drag_offset_z

            self._drag_offset_x = 0.0

            self._drag_offset_y = 0.0

            self._drag_offset_z = 0.0

            self._update_angle()

            self.setCursor(Qt.CursorShape.OpenHandCursor)

            event.accept()

        else:

            event.ignore()

    def set_faces(self, faces: list[str]):

        if len(faces) >= 6:

            self._faces = [str(f) for f in faces[:6]]

            self.update()

    def set_face_data(self, faces, colors, images):

        if len(faces) >= 6:

            self._faces = [str(f) for f in faces[:6]]

            self._face_colors = list(colors[:6])

            self._face_images = [None] * 6

            for i, img in enumerate(images[:6]):

                if img and Path(str(img)).exists():

                    self._face_images[i] = str(img)

            self.update()

    def _draw_projected_text(self, painter: QPainter, pts: list[QPointF], text: str):

        face_sz = 200.0

        src_quad = QPolygonF([

            QPointF(0, 0), QPointF(face_sz, 0),

            QPointF(face_sz, face_sz), QPointF(0, face_sz)

        ])

        dst_quad = QPolygonF(pts)

        transform = QTransform()

        if not QTransform.quadToQuad(src_quad, dst_quad, transform):

            return

        painter.save()

        painter.setTransform(transform, combine=True)

        local_rect = QRectF(10, 10, face_sz - 20, face_sz - 20)

        base_font_size = 36

        font = QFont(str(FONT_FAMILY), base_font_size, QFont.Weight.Bold)

        fm = QFontMetrics(font)

        text_width = fm.horizontalAdvance(text)

        max_allowed_width = local_rect.width() * 0.85

        if text_width > max_allowed_width and text_width > 0:

            new_size = int(base_font_size * (max_allowed_width / text_width))

            font.setPointSize(max(10, new_size))

        painter.setPen(QColor(TEXT_MAIN))

        painter.setFont(font)

        painter.drawText(local_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, text)

        painter.restore()

    def roll(self, value_index, on_finish=None):

        if self._is_rolling:

            return

        self._is_rolling = True

        self._on_finish = on_finish

        face_angles = {

            0: (0, 0),

            1: (0, 180),

            2: (0, 90),

            3: (0, -90),

            4: (90, 0),

            5: (-90, 0),

        }

        rx, ry = face_angles[value_index]

        full_spins = (2 + random.randint(0, 1)) * 360

        self._tilt_rx = random.uniform(10, 30) * random.choice([-1, 1])

        self._tilt_ry = random.uniform(10, 30) * random.choice([-1, 1])

        self._tilt_rz = random.uniform(10, 30) * random.choice([-1, 1])

        self._target_rx = rx + full_spins

        self._target_ry = ry + full_spins

        self._target_rz = random.randint(0, 3) * 90

        self._start_rx = self._base_angle_x

        self._start_ry = self._base_angle_y

        self._start_rz = self._base_angle_z

        self._drag_offset_x = 0.0

        self._drag_offset_y = 0.0

        self._drag_offset_z = 0.0

        self._anim_progress = 0.0

        self._anim_timer = QTimer(self)

        self._anim_timer.timeout.connect(self._anim_step)

        self._anim_timer.start(16)

    def _anim_step(self):

        self._anim_progress += 0.011

        if self._anim_progress >= 1.0:

            self._anim_progress = 1.0

            self._anim_timer.stop()

            self._anim_timer = None

            self._is_rolling = False

            self._base_angle_x = (self._target_rx % 360) + self._tilt_rx

            self._base_angle_y = (self._target_ry % 360) + self._tilt_ry

            self._base_angle_z = (self._target_rz % 360) + self._tilt_rz

            self._update_angle()

            if self._on_finish:

                self._on_finish()

            self.update()

            return

        t = self._anim_progress

        e = 1 - math.pow(1 - t, 3)

        self._base_angle_x = self._start_rx + (self._target_rx - self._start_rx) * e

        self._base_angle_y = self._start_ry + (self._target_ry - self._start_ry) * e

        self._base_angle_z = self._start_rz + (self._target_rz - self._start_rz) * e

        self._update_angle()

        self.update()

    def _rounded_quad_path(self, pts, radius):

        path = QPainterPath()

        n = len(pts)

        if n < 4:

            path.moveTo(pts[0])

            for pt in pts[1:]:

                path.lineTo(pt)

            path.closeSubpath()

            return path

        edge_starts, edge_ends, corners = [], [], []

        for i in range(n):

            p0, p1 = pts[i], pts[(i + 1) % n]

            dx, dy = p1.x() - p0.x(), p1.y() - p0.y()

            length = math.sqrt(dx*dx + dy*dy)

            if length < 1:

                return None

            ux, uy = dx / length, dy / length

            r = min(radius, length * 0.4)

            edge_starts.append(QPointF(p0.x() + ux * r, p0.y() + uy * r))

            edge_ends.append(QPointF(p1.x() - ux * r, p1.y() - uy * r))

            corners.append(p1)

        path.moveTo(edge_starts[0])

        for i in range(n):

            path.lineTo(edge_ends[i])

            path.quadTo(corners[i], edge_starts[(i + 1) % n])

        path.closeSubpath()

        return path

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        size = min(w, h) * 0.5

        cx, cy = w / 2, h / 2

        half = size / 2

        light_dir = (0.5, -0.5, -0.7)

        ld_len = math.sqrt(sum(v*v for v in light_dir))

        light_dir = (light_dir[0]/ld_len, light_dir[1]/ld_len, light_dir[2]/ld_len)

        vertices = [

            (-half, -half, -half), (half, -half, -half),

            (half, half, -half), (-half, half, -half),

            (-half, -half, half), (half, -half, half),

            (half, half, half), (-half, half, half),

        ]

        face_indices = [

            (0, 1, 2, 3),

            (4, 5, 6, 7),

            (1, 5, 6, 2),

            (0, 4, 7, 3),

            (4, 5, 1, 0),

            (3, 2, 6, 7),

        ]

        face_normals = [

            (0, 0, -1),

            (0, 0, 1),

            (1, 0, 0),

            (-1, 0, 0),

            (0, -1, 0),

            (0, 1, 0),

        ]

        rx = math.radians(self._angle_x)

        ry = math.radians(self._angle_y)

        rz = math.radians(self._angle_z)

        def rotate_point(pt):

            x, y, z = pt

            y1 = y * math.cos(rx) - z * math.sin(rx)

            z1 = y * math.sin(rx) + z * math.cos(rx)

            x2 = x * math.cos(ry) + z1 * math.sin(ry)

            z2 = -x * math.sin(ry) + z1 * math.cos(ry)

            x3 = x2 * math.cos(rz) - y1 * math.sin(rz)

            y3 = x2 * math.sin(rz) + y1 * math.cos(rz)

            return x3, y3, z2

        rotated = [rotate_point(v) for v in vertices]

        perspective = 200

        projected = []

        for v in rotated:

            x, y, z = v

            scale = perspective / (perspective + z + half)

            px = cx + x * scale

            py = cy + y * scale

            projected.append((px, py, z))

        shadow_center_x = cx + 6

        shadow_center_y = cy + 8

        shadow_radius_x = size * 0.55

        shadow_radius_y = size * 0.45

        shadow_steps = 16

        for i in range(shadow_steps, 0, -1):

            t = i / shadow_steps

            alpha = int(30 * (1 - t))

            r = t * 0.5

            painter.setPen(Qt.PenStyle.NoPen)

            painter.setBrush(QColor(0, 0, 0, alpha))

            painter.drawEllipse(QPointF(shadow_center_x, shadow_center_y),

                                shadow_radius_x * (0.3 + r * 0.7),

                                shadow_radius_y * (0.3 + r * 0.7))

        visible_faces = []

        for fi, norm in enumerate(face_normals):

            nx, ny, nz = rotate_point(norm)

            if nz >= 0:

                continue

            indices = face_indices[fi]

            avg_z = sum(rotated[idx][2] for idx in indices) / len(indices)

            dot = nx * light_dir[0] + ny * light_dir[1] + nz * light_dir[2]

            if dot < 0:

                dot = 0.0

            else:

                dot = pow(dot, 6)

            visible_faces.append((fi, avg_z, dot))

        visible_faces.sort(key=lambda item: item[1], reverse=True)

        FACE_GRAY = "#48484A"

        corner_radius = max(10, min(w, h) * 0.06)

        for fi, _, light in visible_faces:

            indices = face_indices[fi]

            pts = [QPointF(projected[i][0], projected[i][1]) for i in indices]

            val_idx = fi

            path = self._rounded_quad_path(pts, corner_radius)

            if path is None:

                continue

            img_path = self._face_images[val_idx]

            if img_path:

                pix = QPixmap(img_path)

                if not pix.isNull():

                    painter.save()

                    painter.setClipPath(path)

                    brect = path.boundingRect()

                    scaled = pix.scaled(int(brect.width()), int(brect.height()),

                                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,

                                        Qt.TransformationMode.SmoothTransformation)

                    ox = int(brect.x() - (scaled.width() - brect.width()) / 2)

                    oy = int(brect.y() - (scaled.height() - brect.height()) / 2)

                    painter.drawPixmap(ox, oy, scaled)

                    painter.setClipping(False)

                    overlay = QColor(0, 0, 0, int(120 * (1 - light * 0.5)))

                    painter.fillPath(path, overlay)

                    painter.restore()

                else:

                    painter.setBrush(QColor(FACE_GRAY))

                    painter.setPen(Qt.PenStyle.NoPen)

                    painter.drawPath(path)

            else:

                base_gray = QColor(FACE_GRAY)

                brightness = 0.50 + 0.75 * light

                r = min(255, int(base_gray.red() * brightness))

                g = min(255, int(base_gray.green() * brightness))

                b = min(255, int(base_gray.blue() * brightness))

                grad = QLinearGradient(pts[0], pts[2])

                grad.setColorAt(0.0, QColor(

                    min(255, r + int(15 * light)),

                    min(255, g + int(15 * light)),

                    min(255, b + int(15 * light)),

                    255

                ))

                grad.setColorAt(1.0, QColor(

                    max(0, r - int(20 * (1 - light * 0.5))),

                    max(0, g - int(20 * (1 - light * 0.5))),

                    max(0, b - int(20 * (1 - light * 0.5))),

                    255

                ))

                painter.setBrush(QBrush(grad))

                painter.setPen(Qt.PenStyle.NoPen)

                painter.drawPath(path)

            pen = QPen(QColor(self._face_colors[val_idx]), 4)

            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

            pen.setCapStyle(Qt.PenCapStyle.RoundCap)

            painter.setPen(pen)

            painter.setBrush(Qt.BrushStyle.NoBrush)

            painter.drawPath(path)

            if not img_path:

                if light > 0.05:

                    hl_pen = QPen(QColor(255, 255, 255, int(80 + 100 * light)), 1)

                    hl_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

                    painter.setPen(hl_pen)

                    painter.setBrush(Qt.BrushStyle.NoBrush)

                    inset = 2

                    hl_path = self._rounded_quad_path(

                        [QPointF(p.x() + inset, p.y() + inset) for p in pts],

                        max(4, corner_radius - 2)

                    )

                    if hl_path:

                        painter.drawPath(hl_path)

                face_text = str(self._faces[val_idx])

                self._draw_projected_text(painter, pts, face_text)

class DicePanel(QWidget):

    FACE_COLORS = ["#FF3B30", "#FF9500", "#CCFF00", "#00F5FF", "#AF52DE", "#007AFF"]

    DEFAULT_FACES = ["1", "2", "3", "4", "5", "6"]

    DEFAULT_CHANCE = 16.67

    def __init__(self, parent=None):

        super().__init__(parent)

        self._dice_data = {

            "Standard": {

                "faces": self.DEFAULT_FACES[:],

                "chances": [self.DEFAULT_CHANCE] * 6,

                "colors": self.FACE_COLORS[:],

                "images": [None] * 6

            }

        }

        self._active_dice = "Standard"

        self._history = []

        self._is_rolling = False

        self._setup_ui()

        self._update_faces()

        self._render_dice_combo()

        self._render_face_cards()

        self._apply_auto_colors()

    def _setup_ui(self):

        layout = QHBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)

        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        splitter.setHandleWidth(5)

        splitter.setChildrenCollapsible(False)

        layout.addWidget(splitter)

        dice_area = QWidget()
        dice_area.setMinimumWidth(400)

        dice_layout = QVBoxLayout(dice_area)

        dice_layout.setContentsMargins(30, 20, 20, 20)

        dice_layout.setSpacing(0)

        splitter.addWidget(dice_area)

        header = QHBoxLayout()

        dice_layout.addLayout(header)

        self._dice_combo = WheelDropdown()

        self._dice_combo.setPlaceholderText("Select dice...")

        self._dice_combo.currentIndexChanged.connect(self._on_combo_changed)

        header.addWidget(self._dice_combo, 1)

        dice_btn_frame = QHBoxLayout()

        dice_btn_frame.setSpacing(4)

        header.addLayout(dice_btn_frame)

        add_dice_btn = HoverIconButton(PLUS_PATH, PLUS_PATH)

        add_dice_btn.setFixedSize(36, 36)

        add_dice_btn.setIconSize(add_dice_btn.size())

        add_dice_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        add_dice_btn.setStyleSheet("""

            QPushButton {

                background-color: transparent;

                border: none;

                padding: 0;

            }

            QPushButton:hover {

                background-color: rgba(255, 255, 255, 12);

                border-radius: 18px;

            }

        """)

        add_dice_btn.clicked.connect(self._add_dice)

        dice_btn_frame.addWidget(add_dice_btn)

        self._del_dice_btn = GlowButton("DELETE", "ghost")

        self._del_dice_btn.clicked.connect(self._delete_dice)

        dice_btn_frame.addWidget(self._del_dice_btn)

        self.rename_dice_btn = GlowButton("RENAME", "ghost")

        self.rename_dice_btn.clicked.connect(self._dice_rename_dice)

        dice_btn_frame.addWidget(self.rename_dice_btn)

        prev_dice_btn = HoverIconButton(LEFT_ARROW_PATH, LEFT_ARROW_PATH)

        prev_dice_btn.setFixedSize(36, 36)

        prev_dice_btn.setIconSize(prev_dice_btn.size())

        prev_dice_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        prev_dice_btn.setStyleSheet("""

            QPushButton {

                background-color: transparent;

                border: none;

                padding: 0;

            }

            QPushButton:hover {

                background-color: rgba(255, 255, 255, 12);

                border-radius: 18px;

            }

        """)

        prev_dice_btn.clicked.connect(self._prev_dice)

        dice_btn_frame.addWidget(prev_dice_btn)

        next_dice_btn = HoverIconButton(RIGHT_ARROW_PATH, RIGHT_ARROW_PATH)

        next_dice_btn.setFixedSize(36, 36)

        next_dice_btn.setIconSize(next_dice_btn.size())

        next_dice_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        next_dice_btn.setStyleSheet("""

            QPushButton {

                background-color: transparent;

                border: none;

                padding: 0;

            }

            QPushButton:hover {

                background-color: rgba(255, 255, 255, 12);

                border-radius: 18px;

            }

        """)

        next_dice_btn.clicked.connect(self._next_dice)

        dice_btn_frame.addWidget(next_dice_btn)

        self._result_label = QLabel("—")

        self._result_label.setStyleSheet(f"color: {TEXT_MAIN}; font-size: 26px; font-weight: 900; letter-spacing: 1px;")

        self._result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        dice_layout.addWidget(self._result_label)

        self._cube_widget = DiceCubeWidget()

        self._cube_widget.setFixedSize(520, 520)

        dice_layout.addWidget(self._cube_widget, 0, Qt.AlignmentFlag.AlignCenter)

        self._roll_btn = GlowButton("ROLL", "lime")

        self._roll_btn.setFixedHeight(48)

        self._roll_btn.clicked.connect(self._roll_dice)

        dice_layout.addWidget(self._roll_btn, 0, Qt.AlignmentFlag.AlignCenter)

        winner_row = QWidget()

        winner_row.setStyleSheet("background: transparent;")

        winner_row_layout = QHBoxLayout(winner_row)

        winner_row_layout.setContentsMargins(0, 5, 0, 0)

        winner_row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        winner_lbl = QLabel("Winner:")

        winner_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 12px;")

        winner_row_layout.addWidget(winner_lbl)

        self._dice_winner_entry = QLineEdit()

        self._dice_winner_entry.setPlaceholderText("nickname")

        self._dice_winner_entry.setFixedWidth(180)

        self._dice_winner_entry.setStyleSheet(f"""

            QLineEdit {{

                background-color: {BG_COLOR};

                border: 1px solid {BORDER_COLOR};

                border-radius: 9999px;

                color: {TEXT_MAIN};

                font-size: 12px;

                padding: 6px 14px;

                font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

            }}

            QLineEdit:focus {{  border-color: {ACCENT_LIME}; }}

        """)

        winner_row_layout.addWidget(self._dice_winner_entry)

        dice_layout.addWidget(winner_row, 0, Qt.AlignmentFlag.AlignCenter)

        history_row = QWidget()

        history_layout_outer = QHBoxLayout(history_row)

        history_layout_outer.setContentsMargins(0, 0, 0, 0)

        history_layout_outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._history_widget = QWidget()

        self._history_layout = QHBoxLayout(self._history_widget)

        self._history_layout.setContentsMargins(0, 0, 0, 0)

        self._history_layout.setSpacing(6)

        history_layout_outer.addWidget(self._history_widget)

        clear_btn = GlowButton("CLEAR", "ghost")

        clear_btn.clicked.connect(self._clear_history)

        history_layout_outer.addWidget(clear_btn)

        dice_layout.addWidget(history_row, 0, Qt.AlignmentFlag.AlignCenter)

        dice_layout.addStretch(1)

        right_sidebar = QFrame()
        right_sidebar.setMinimumWidth(280)
        right_sidebar.setObjectName("sidebarFrame")
        right_sidebar.setStyleSheet(f"QFrame#sidebarFrame {{ background-color: transparent; border: 1px solid {BORDER_COLOR}; border-radius: 20px; }}")

        right_sidebar_layout = QVBoxLayout(right_sidebar)

        right_sidebar_layout.setContentsMargins(0, 0, 0, 0)

        splitter.addWidget(right_sidebar)

        splitter.setStretchFactor(0, 3)

        splitter.setStretchFactor(1, 2)

        splitter.setSizes([700, 400])

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setStyleSheet(f"""

            QScrollArea {{  background-color: transparent; border: none; }}

        """)

        editor_widget = QWidget()

        editor_widget.setStyleSheet("background-color: transparent;")

        editor_layout = QVBoxLayout(editor_widget)

        editor_layout.setContentsMargins(30, 40, 30, 40)

        editor_layout.setSpacing(14)

        title = QLabel("DICE CONFIGURATOR")

        title.setStyleSheet("font-size: 16px; font-weight: bold;")

        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        editor_layout.addWidget(title)

        self._auto_color_toggle_row = QWidget()

        self._auto_color_toggle_row.setStyleSheet("background: transparent;")

        ac_row = QHBoxLayout(self._auto_color_toggle_row)

        ac_row.setContentsMargins(0, 0, 0, 0)

        editor_layout.addWidget(self._auto_color_toggle_row)

        ac_label = QLabel("Auto Color Gradient")

        ac_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px;")

        ac_row.addWidget(ac_label)

        ac_row.addStretch()

        self._auto_color_toggle = ToggleSwitch(initial=True)

        self._auto_color_toggle.toggled.connect(self._on_auto_color_toggle)

        ac_row.addWidget(self._auto_color_toggle)

        self._random_color_toggle_row = QWidget()

        self._random_color_toggle_row.setStyleSheet("background: transparent;")

        rc_row = QHBoxLayout(self._random_color_toggle_row)

        rc_row.setContentsMargins(0, 0, 0, 0)

        editor_layout.addWidget(self._random_color_toggle_row)

        rc_label = QLabel("Random Colors")

        rc_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px;")

        rc_row.addWidget(rc_label)

        rc_row.addStretch()

        self._random_color_toggle = ToggleSwitch(initial=False)

        self._random_color_toggle.toggled.connect(self._on_random_color_toggle)

        rc_row.addWidget(self._random_color_toggle)

        self._general_color_toggle_row = QWidget()

        self._general_color_toggle_row.setStyleSheet("background: transparent;")

        gc_row = QHBoxLayout(self._general_color_toggle_row)

        gc_row.setContentsMargins(0, 0, 0, 0)

        editor_layout.addWidget(self._general_color_toggle_row)

        gc_label = QLabel("General Color")

        gc_label.setStyleSheet(f"color: {TEXT_SEC}; font-size: 13px;")

        gc_row.addWidget(gc_label)

        gc_row.addStretch()

        self._general_color_toggle = ToggleSwitch(initial=False)

        self._general_color_toggle.toggled.connect(self._on_general_color_toggle)

        gc_row.addWidget(self._general_color_toggle)

        equalize_btn = GlowButton("EQUALIZE", "outline")

        equalize_btn.clicked.connect(self._equalize_chances)

        editor_layout.addWidget(equalize_btn)

        self._face_cards_scroll = QScrollArea()

        self._face_cards_scroll.setWidgetResizable(True)

        self._face_cards_scroll.setStyleSheet("""

            QScrollArea { background-color: transparent; border: none; }

        """)

        self._face_cards_container = DropContainer()

        self._face_cards_container.setStyleSheet("background-color: transparent;")

        self._face_cards_layout = QVBoxLayout(self._face_cards_container)

        self._face_cards_layout.setSpacing(8)

        self._face_cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._face_cards_scroll.setWidget(self._face_cards_container)

        editor_layout.addWidget(self._face_cards_scroll, 1)

        scroll.setWidget(editor_widget)

        right_sidebar_layout.addWidget(scroll)

    def _render_dice_combo(self):

        self._dice_combo.blockSignals(True)

        self._dice_combo.clear()

        names = list(self._dice_data.keys())

        if names:

            display_items = [f"{n} ({len(self._dice_data[n]['faces'])})" for n in names]

            self._dice_combo.addItems(display_items)

            self._dice_combo.setCurrentIndex(names.index(self._active_dice))

            popup_data = {n: self._dice_data[n]['faces'] for n in names}

            self._dice_combo.setPopupData(popup_data)

        self._dice_combo.blockSignals(False)

    def _prev_dice(self):

        keys = list(self._dice_data.keys())

        idx = keys.index(self._active_dice)

        idx = (idx - 1) % len(keys)

        self._select_dice(keys[idx])

    def _next_dice(self):

        keys = list(self._dice_data.keys())

        idx = keys.index(self._active_dice)

        idx = (idx + 1) % len(keys)

        self._select_dice(keys[idx])

    def _on_combo_changed(self, idx):

        names = list(self._dice_data.keys())

        if 0 <= idx < len(names):

            self._select_dice(names[idx])

    def _render_face_cards(self):

        for i in reversed(range(self._face_cards_layout.count())):

            item = self._face_cards_layout.itemAt(i)

            if item.widget():

                item.widget().deleteLater()

        data = self._dice_data[self._active_dice]

        for i in range(6):

            self._create_face_card(i, data)

    def _create_face_card(self, index, data):

        card = QFrame()

        card.setObjectName("cardDark")

        card.setStyleSheet(

            f"QFrame#cardDark {{ background-color: {BG_COLOR}; border: 1px solid {BORDER_COLOR}; border-radius: 30px; }}"

        )

        card_layout = QHBoxLayout(card)

        card_layout.setContentsMargins(8, 20, 20, 20)

        card_layout.setSpacing(6)

        self._face_cards_layout.addWidget(card)

        handle = DragHandle(index)

        card_layout.addWidget(handle)

        content = QWidget()

        content.setStyleSheet("background-color: transparent;")

        content_layout = QVBoxLayout(content)

        content_layout.setContentsMargins(0, 0, 0, 0)

        card_layout.addWidget(content, 1)

        top_row = QHBoxLayout()

        content_layout.addLayout(top_row)

        name_entry = RoundedLineEdit()

        name_entry.setText(data["faces"][index])

        name_entry.set_colors(bg="transparent", border="transparent")

        name_entry.setMaxLength(16)

        name_entry.textChanged.connect(lambda text, idx=index: self._update_face(idx, text))

        top_row.addWidget(name_entry, 1)

        color_btn = RoundedButton("", card)

        color_btn.setFixedSize(40, 30)

        color_path = data["images"][index]

        if color_path and Path(str(color_path)).exists():

            pix = _get_cached_pixmap(color_path)

            if pix:

                icon = QIcon(pix.scaled(36, 26, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

                color_btn.setIcon(icon)

                color_btn.setIconSize(QSize(36, 26))

                color_btn.set_colors(bg="transparent", border=BORDER_COLOR, hover_border="#FFFFFF")

            else:

                color_btn.set_colors(bg=data["colors"][index], border=BORDER_COLOR, hover_border="#FFFFFF")

        else:

            color_btn.set_colors(bg=data["colors"][index], border=BORDER_COLOR, hover_border="#FFFFFF")

        color_btn.clicked.connect(lambda checked, idx=index, btn=color_btn: self._on_color_btn(idx, btn))

        top_row.addWidget(color_btn)

        bot_row = QHBoxLayout()

        content_layout.addLayout(bot_row)

        val_entry = RoundedLineEdit()

        val_entry.setText(str(round(data["chances"][index], 1)))

        val_entry.setMaximumWidth(80)

        val_entry.set_colors(bg="transparent", border="transparent")

        val_entry.textChanged.connect(lambda text, idx=index: self._on_chance_entry(idx, text))

        bot_row.addWidget(val_entry)

        slider = ModernSlider()

        slider.setValue(data["chances"][index])

        slider.valueChanged.connect(lambda v, idx=index, entry=val_entry: self._on_slider_change(idx, v, entry))

        slider.dragStarted.connect(lambda idx=index: None)

        slider.dragFinished.connect(lambda: None)

        bot_row.addWidget(slider, 1)

        del_btn = RoundedButton("X")

        del_btn.setFixedSize(40, 40)

        del_btn.set_colors(bg="transparent", text=DANGER_COLOR, border="transparent", hover_bg=CARD_LIGHT)

        del_btn.clicked.connect(lambda checked, idx=index: self._on_delete_face(idx))

        bot_row.addWidget(del_btn)

    def _on_color_btn(self, idx, btn):

        data = self._dice_data[self._active_dice]

        if idx >= len(data["faces"]):

            return

        initial = data["colors"][idx]

        initial_image = data["images"][idx]

        picker = ModernItemPicker(self, initial, initial_image, cell_type="case")

        if picker.exec() == QDialog.DialogCode.Accepted:

            ptype, pval = picker.result

            if ptype == 'color':

                data["colors"][idx] = pval

                data["images"][idx] = None

                btn.setIcon(QIcon())

                btn.set_colors(bg=pval, border=BORDER_COLOR, hover_border="#FFFFFF")

            elif ptype == 'image':

                data["images"][idx] = pval

                data["colors"][idx] = ACCENT_CYAN

                pix = _get_cached_pixmap(pval)

                if pix:

                    icon = QIcon(pix.scaled(36, 26, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

                    btn.setIcon(icon)

                    btn.setIconSize(QSize(36, 26))

                    btn.set_colors(bg="transparent", border=BORDER_COLOR, hover_border="#FFFFFF")

            self._update_faces()

    def _on_slider_change(self, idx, value, entry):

        data = self._dice_data[self._active_dice]

        if idx >= len(data["chances"]):

            return

        data["chances"][idx] = value

        entry.setText(str(round(value, 1)))

        self._normalize_chances(idx)

        self._render_face_cards()

        self._update_faces()

    def _on_chance_entry(self, idx, text):

        try:

            v = float(text)

            data = self._dice_data[self._active_dice]

            if idx < len(data["chances"]):

                data["chances"][idx] = v

                self._normalize_chances(idx)

                self._render_face_cards()

                self._update_faces()

        except ValueError:

            pass

    def _on_delete_face(self, idx):

        data = self._dice_data[self._active_dice]

        if len(data["faces"]) <= 1:

            return

        data["faces"].pop(idx)

        data["chances"].pop(idx)

        data["colors"].pop(idx)

        data["images"].pop(idx)

        self._normalize_chances(-1)

        self._render_face_cards()

        self._update_faces()

        self._render_dice_combo()

    def _normalize_chances(self, skip_idx=-1):

        data = self._dice_data[self._active_dice]

        total = sum(data["chances"])

        if abs(total - 100) < 0.01:

            return

        if total < 0.01:

            for i in range(len(data["chances"])):

                data["chances"][i] = 100.0 / len(data["chances"])

            return

        for i in range(len(data["chances"])):

            if i != skip_idx:

                data["chances"][i] = max(0.01, data["chances"][i] * 100 / total)

        new_total = sum(data["chances"])

        if abs(new_total - 100) > 0.01:

            diff = 100 - new_total

            for i in range(len(data["chances"])):

                if i != skip_idx:

                    data["chances"][i] = max(0.01, data["chances"][i] + diff / len(data["chances"]))

                    break

    def _random_colors(self):

        data = self._dice_data[self._active_dice]

        shuffled = self.FACE_COLORS[:]

        random.shuffle(shuffled)

        for i in range(len(data["colors"])):

            data["colors"][i] = shuffled[i % len(shuffled)]

            data["images"][i] = None

        self._render_face_cards()

        self._update_faces()

    def _equalize_chances(self):

        data = self._dice_data[self._active_dice]

        eq = 100.0 / len(data["chances"])

        for i in range(len(data["chances"])):

            data["chances"][i] = round(eq, 2)

        self._render_face_cards()

        self._update_faces()

    def _on_auto_color_toggle(self, checked):

        if checked:

            self._random_color_toggle.set_checked(False)

            self._general_color_toggle.set_checked(False)

            self._apply_auto_colors()

    def _apply_auto_colors(self):

        data = self._dice_data[self._active_dice]

        chances = data["chances"]

        if not chances:

            return

        max_ch = max(chances)

        for i in range(len(data["colors"])):

            ratio = chances[i] / max_ch if max_ch > 0 else 0.5

            r = int(0 + ratio * 204)

            g = int(245 * ratio + (1-ratio)*50)

            b = int(255 * (1-ratio))

            data["colors"][i] = f'#{r:02x}{g:02x}{b:02x}'

            data["images"][i] = None

        self._render_face_cards()

        self._update_faces()

    def _on_random_color_toggle(self, checked):

        if checked:

            self._general_color_toggle.set_checked(False)

            self._random_colors()

    def _on_general_color_toggle(self, checked):

        if checked:

            data = self._dice_data[self._active_dice]

            initial = data["colors"][0] if data["colors"] else ACCENT_CYAN

            picker = ModernColorPicker(self, initial)

            if picker.exec() == QDialog.DialogCode.Accepted and picker.result:

                self._random_color_toggle.set_checked(False)

                for i in range(len(data["colors"])):

                    data["colors"][i] = picker.result

                    data["images"][i] = None

                self._render_face_cards()

                self._update_faces()

            else:

                self._general_color_toggle.set_checked(False)

    def _update_faces(self):

        data = self._dice_data[self._active_dice]

        self._cube_widget.set_face_data(data["faces"], data["colors"], data["images"])

    def _select_dice(self, name):

        self._active_dice = name

        self._render_dice_combo()

        self._render_face_cards()

        self._update_faces()

    def _add_dice(self):

        name = f"Dice {len(self._dice_data) + 1}"

        self._dice_data[name] = {

            "faces": self.DEFAULT_FACES[:],

            "chances": [self.DEFAULT_CHANCE] * 6,

            "colors": self.FACE_COLORS[:],

            "images": [None] * 6

        }

        self._active_dice = name

        self._render_dice_combo()

        self._render_face_cards()

        self._update_faces()

    def _delete_dice(self):

        if len(self._dice_data) <= 1:

            return

        del self._dice_data[self._active_dice]

        self._active_dice = list(self._dice_data.keys())[0]

        self._render_dice_combo()

        self._render_face_cards()

        self._update_faces()

    def _dice_rename_dice(self):

        old_name = self._active_dice

        if not old_name:

            return

        new_name = ask_string(self, "RENAME DICE", "Enter new name:", placeholder=old_name)

        if new_name and new_name != old_name:

            if new_name in self._dice_data:

                QMessageBox.warning(self, "ERROR", f"Dice '{new_name}' already exists!")

                return

            self._dice_data[new_name] = self._dice_data.pop(old_name)

            self._active_dice = new_name

            self._render_dice_combo()

            self._render_face_cards()

            self._update_faces()

    def _update_face(self, index, value):

        if not value.strip():

            return

        data = self._dice_data[self._active_dice]

        if index < len(data["faces"]):

            data["faces"][index] = value.strip()

            self._update_faces()

            self._render_dice_combo()

    def _roll_dice(self):

        if self._is_rolling:

            return

        self._is_rolling = True

        self._roll_btn.setEnabled(False)

        self._result_label.setText("Rolling...")

        data = self._dice_data[self._active_dice]

        total = sum(data["chances"])

        r = random.uniform(0, total)

        cum = 0.0

        value_index = 0

        for i, c in enumerate(data["chances"]):

            cum += c

            if r <= cum:

                value_index = i

                break

        value = data["faces"][value_index]

        def on_finish():

            self._is_rolling = False

            self._roll_btn.setEnabled(True)

            color = data["colors"][value_index]

            self._result_label.setText(f"<span style='color:{color};'>{value}</span>")

            self._result_label.setStyleSheet(f"color: {color}; font-size: 26px; font-weight: 900; letter-spacing: 1px;")

            self._history.insert(0, value)

            if len(self._history) > 30:

                self._history.pop()

            self._render_history()

        self._cube_widget.roll(value_index, on_finish)

    def _render_history(self):

        for i in reversed(range(self._history_layout.count())):

            item = self._history_layout.itemAt(i)

            if item.widget():

                item.widget().deleteLater()

        data = self._dice_data[self._active_dice]

        for v in self._history:

            item_w = QWidget()

            item_w.setStyleSheet("background: transparent;")

            item_lay = QHBoxLayout(item_w)

            item_lay.setContentsMargins(0, 0, 0, 0)

            item_lay.setSpacing(2)

            lbl = QLabel(v)

            idx = data["faces"].index(v) if v in data["faces"] else -1

            color = data["colors"][idx] if idx >= 0 else TEXT_SEC

            lbl.setStyleSheet(f"""

                color: {color}; font-size: 14px; font-weight: 800;

                background: {CARD_COLOR}; border: 1px solid {BORDER_COLOR};

                border-radius: 10px; padding: 6px 10px;

            """)

            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            lbl.setFixedSize(40, 40)

            item_lay.addWidget(lbl)

            self._history_layout.addWidget(item_w)

    def _clear_history(self):

        self._history.clear()

        self._render_history()
