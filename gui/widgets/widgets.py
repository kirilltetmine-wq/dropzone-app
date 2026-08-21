from PyQt6.QtCore import Qt, QRectF, QTimer, QSize, pyqtSignal

from PyQt6.QtGui import (

    QFont, QColor, QPainter, QBrush, QPen,

    QFontMetrics, QIcon, QPainterPath, QRegion,

    QLinearGradient, QTransform, QPixmap, QImage,

)

from PyQt6.QtWidgets import (

    QPushButton, QLineEdit, QFrame, QListView,

    QWidget, QVBoxLayout, QHBoxLayout, QLabel,

    QSizePolicy,

    QGraphicsDropShadowEffect,

)

from core.theme import (

    BG_COLOR, CARD_COLOR, CARD_LIGHT, ACCENT_CYAN, ACCENT_LIME,

    TEXT_MAIN, TEXT_SEC, BORDER_COLOR, DANGER_COLOR, FONT_FAMILY

)

from core.storage import Storage

class RoundedButton(QPushButton):

    def __init__(self, text="", parent=None):

        super().__init__(text, parent)

        self._bg_color = QColor("transparent")

        self._text_color = QColor(TEXT_MAIN)

        self._border_color = QColor("transparent")

        self._border_width = 2

        self._radius = 9999

        self._hover_bg = None

        self._hover_text = None

        self._hover_border = None

        self._hovered = False

        self._pressed = False

        self.setMouseTracking(True)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # ЗАЩИТА ОТ НАТИВНОЙ РАМКИ: перекрываем любой внешний border
        self.setStyleSheet("""
            QPushButton {
                border: none;
                outline: none;
                background: transparent;
            }
        """)
        self.setFlat(True)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setAutoFillBackground(False)

    def set_colors(self, bg=None, text=None, border=None, hover_bg=None, hover_text=None, hover_border=None):

        if bg is not None: self._bg_color = QColor(bg)

        if text is not None: self._text_color = QColor(text)

        if border is not None: self._border_color = QColor(border)

        if hover_bg is not None: self._hover_bg = QColor(hover_bg)

        if hover_text is not None: self._hover_text = QColor(hover_text)

        if hover_border is not None: self._hover_border = QColor(hover_border)

        self.update()

    def enterEvent(self, event):

        self._hovered = True

        self.update()

        return super().enterEvent(event)

    def leaveEvent(self, event):

        self._hovered = False

        self.update()

        return super().leaveEvent(event)

    def mousePressEvent(self, event):

        self._pressed = True

        self.update()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):

        self._pressed = False

        self.update()

        super().mouseReleaseEvent(event)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        radius = min(self._radius, h / 2)

        if self._hovered and self._hover_bg is not None:

            bg = self._hover_bg

        else:

            bg = self._bg_color

        if self._hovered and self._hover_text is not None:

            text_col = self._hover_text

        else:

            text_col = self._text_color

        if self._hovered and self._hover_border is not None:

            border_col = self._hover_border

        else:

            border_col = self._border_color

        if not self.isEnabled():

            painter.setOpacity(0.35)

        rect = QRectF(self._border_width / 2, self._border_width / 2,

                       w - self._border_width, h - self._border_width)

        if bg.alpha() > 0:

            painter.setPen(Qt.PenStyle.NoPen)

            painter.setBrush(bg)

            painter.drawRoundedRect(rect, radius, radius)

        if border_col.alpha() > 0 and self._border_width > 0:

            painter.setPen(QPen(border_col, self._border_width))

            painter.setBrush(Qt.BrushStyle.NoBrush)

            painter.drawRoundedRect(rect, radius, radius)

        painter.setPen(text_col)

        font = self.font()

        font.setBold(True)

        font.setPixelSize(13)

        painter.setFont(font)

        painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, self.text())

        painter.end()

    def sizeHint(self):

        fm = QFontMetrics(self.font())

        text_w = fm.horizontalAdvance(self.text())

        return QSize(text_w + 48, 45)

class RoundedLineEdit(QLineEdit):

    def __init__(self, parent=None):

        super().__init__(parent)

        self._bg_color = QColor(BG_COLOR)

        self._border_color = QColor(BORDER_COLOR)

        self._focus_border = QColor(ACCENT_CYAN)

        self._radius = 9999

        self._border_width = 1

        self.setFrame(False)

        self.setTextMargins(18, 0, 18, 0)

        self.setStyleSheet(f"""

            QLineEdit {{

                background: transparent;

                border: none;

                color: {TEXT_MAIN};

                font-size: 14px;

                font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;

                padding: 14px 0px;

                selection-background-color: {ACCENT_CYAN};

                selection-color: {BG_COLOR};

            }}

        """)

    def set_colors(self, bg=None, border=None, focus_border=None):

        if bg is not None: self._bg_color = QColor(bg)

        if border is not None: self._border_color = QColor(border)

        if focus_border is not None: self._focus_border = QColor(focus_border)

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        radius = min(self._radius, h / 2)

        border_col = self._focus_border if self.hasFocus() else self._border_color

        rect = QRectF(self._border_width / 2, self._border_width / 2,

                       w - self._border_width, h - self._border_width)

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(self._bg_color)

        painter.drawRoundedRect(rect, radius, radius)

        painter.setPen(QPen(border_col, self._border_width))

        painter.setBrush(Qt.BrushStyle.NoBrush)

        painter.drawRoundedRect(rect, radius, radius)

        painter.end()

        super().paintEvent(event)

class RoundedFrame(QFrame):

    def __init__(self, parent=None, bg_color=None, border_color=None, radius=30):

        super().__init__(parent)

        # ЗАЩИТА ОТ НАТИВНОЙ РАМКИ: перекрываем любой внешний border
        self.setStyleSheet("QFrame { border: none; background: transparent; }")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setAutoFillBackground(False)

        self._bg = QColor(bg_color) if bg_color else QColor(CARD_COLOR)

        self._border = QColor(border_color) if border_color else QColor(BORDER_COLOR)

        self._radius = radius

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        rect = QRectF(0.5, 0.5, w - 1, h - 1)

        painter.setPen(QPen(self._border, 1))

        painter.setBrush(self._bg)

        painter.drawRoundedRect(rect, self._radius, self._radius)

        painter.end()

class RoundedListView(QListView):

    def __init__(self, parent=None, radius=20):

        super().__init__(parent)

        self._radius = radius

        self._bg = QColor(CARD_COLOR)

        self._border = QColor(BORDER_COLOR)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setAutoFillBackground(False)

        self.setFrameShape(QFrame.Shape.NoFrame)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def paintEvent(self, event):

        painter = QPainter(self.viewport())

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.viewport().width(), self.viewport().height()

        rect = QRectF(0.5, 0.5, w - 1, h - 1)

        painter.setPen(QPen(self._border, 1))

        painter.setBrush(self._bg)

        painter.drawRoundedRect(rect, self._radius, self._radius)

        painter.end()

        super().paintEvent(event)

class WheelDropdown(QWidget):

    currentIndexChanged = pyqtSignal(int)

    def __init__(self, parent=None):

        super().__init__(parent)

        self._items = []

        self._wheels_data = {}

        self._current_index = -1

        self._placeholder_text = "Select wheel..."

        self._signals_blocked = False

        self._popup = None

        self._hovered = False

        self._pressed = False

        self.setFixedHeight(48)
        self.setMinimumWidth(150)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.setMouseTracking(True)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        radius = min(9999, h / 2)

        border_w = 2

        pad = border_w / 2

        bg = QColor(CARD_LIGHT)

        text_col = QColor(TEXT_MAIN)

        border_col = QColor(BORDER_COLOR)

        if self._hovered:

            border_col = QColor(ACCENT_CYAN)

        rect = QRectF(pad, pad, w - border_w, h - border_w)

        path = QPainterPath()

        path.addRoundedRect(rect, radius, radius)

        painter.setBrush(bg)

        pen = QPen(border_col, border_w)

        pen.setStyle(Qt.PenStyle.SolidLine)

        painter.setPen(pen)

        painter.drawPath(path)

        painter.setClipPath(path)

        if 0 <= self._current_index < len(self._items):

            txt = self._items[self._current_index]

        else:

            txt = self._placeholder_text

        font = painter.font()

        font.setPointSize(11)

        font.setBold(True)

        painter.setFont(font)

        painter.setPen(text_col)

        painter.drawText(QRectF(20, 0, w - 20 - 40, h), Qt.AlignmentFlag.AlignVCenter, txt)

        chevron_rect = QRectF(w - 36, 0, 20, h)

        painter.setPen(QColor("#888888"))

        chevron_font = painter.font()

        chevron_font.setPointSize(9)

        painter.setFont(chevron_font)

        painter.drawText(chevron_rect, Qt.AlignmentFlag.AlignVCenter, "▼")

    def enterEvent(self, event):

        self._hovered = True

        self.update()

        super().enterEvent(event)

    def leaveEvent(self, event):

        self._hovered = False

        self.update()

        super().leaveEvent(event)

    def mousePressEvent(self, event):

        self._pressed = True

        self.update()

        self._toggle_popup()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):

        self._pressed = False

        self.update()

        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):

        if not self._items:

            return

        delta = event.angleDelta().y()

        if delta > 0:

            self._current_index = (self._current_index - 1) % len(self._items)

        else:

            self._current_index = (self._current_index + 1) % len(self._items)

        self._update_btn_text()

        if not self._signals_blocked:

            self.currentIndexChanged.emit(self._current_index)

        event.accept()

    def _update_btn_text(self):

        self.update()

    def _toggle_popup(self):

        if self._popup and self._popup.isVisible():

            self._popup.close()

            return

        self._popup = WheelPopup(

            self._items, self._wheels_data, self._current_index, self

        )

        self._popup.item_selected.connect(self._on_item_selected)

        btn_rect = self.rect()

        global_pos = self.mapToGlobal(btn_rect.bottomLeft())

        popup_width = self.width()

        self._popup.setFixedWidth(popup_width)

        self._popup.move(global_pos)

        self._popup.show()

    def _on_item_selected(self, index):

        if self._popup:

            self._popup.close()

            self._popup = None

        if index != self._current_index:

            self._current_index = index

            self._update_btn_text()

            if not self._signals_blocked:

                self.currentIndexChanged.emit(index)

    def currentText(self):

        if 0 <= self._current_index < len(self._items):

            return self._items[self._current_index]

        return ""

    def currentIndex(self):

        return self._current_index

    def setCurrentIndex(self, idx):

        if 0 <= idx < len(self._items):

            self._current_index = idx

            self._update_btn_text()

            if not self._signals_blocked:

                self.currentIndexChanged.emit(idx)

    def setCurrentText(self, text):

        if text in self._items:

            self.setCurrentIndex(self._items.index(text))

    def count(self):

        return len(self._items)

    def clear(self):

        self._items = []

        self._wheels_data = {}

        self._current_index = -1

        self._update_btn_text()

    def addItems(self, items):

        self._items = list(items)

        if not self._wheels_data:

            self._wheels_data = Storage.get_wheels()

        if self._items and self._current_index == -1:

            self._current_index = 0

            self._update_btn_text()

    def setPopupData(self, data):

        self._wheels_data = data

    def blockSignals(self, block):

        self._signals_blocked = block

    def setPlaceholderText(self, text):

        self._placeholder_text = text

        self._update_btn_text()

class WheelPopup(QFrame):

    item_selected = pyqtSignal(int)

    def __init__(self, items, wheels_data, current_index, parent=None):

        super().__init__(None, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setAutoFillBackground(False)

        container = QFrame(self)

        container.setObjectName("popupContainer")

        container.setStyleSheet(f"""

            #popupContainer {{

                background-color: {CARD_COLOR};

                border: 1px solid {BORDER_COLOR};

                border-radius: 20px;

            }}

        """)

        container_layout = QVBoxLayout(container)

        container_layout.setContentsMargins(6, 6, 6, 6)

        container_layout.setSpacing(2)

        for i, name in enumerate(items):

            prizes = wheels_data.get(name, [])

            item_widget = QFrame()

            item_widget.setCursor(Qt.CursorShape.PointingHandCursor)

            item_widget._idx = i

            is_active = (i == current_index)

            item_layout = QHBoxLayout(item_widget)

            item_layout.setContentsMargins(16, 10, 16, 10)

            item_layout.setSpacing(10)

            dot_color = "#CCFF00" if is_active else "#8E8E93"

            dot = QLabel()

            dot.setFixedSize(8, 8)

            dot.setStyleSheet(f"background-color: {dot_color}; border-radius: 4px;")

            dot.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

            item_layout.addWidget(dot)

            name_label = QLabel(name)

            name_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

            if is_active:

                name_label.setStyleSheet("color: #CCFF00; font-weight: 700; font-size: 13px;")

            else:

                name_label.setStyleSheet(f"color: {TEXT_MAIN}; font-weight: 500; font-size: 13px;")

            item_layout.addWidget(name_label, 1)

            if prizes:

                badge = QLabel(f"{len(prizes)} prizes")

                badge.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

                if is_active:

                    badge.setStyleSheet(f"""
                        font-size: 10px; font-weight: 700;
                        padding: 3px 10px; border-radius: 9999px;
                        background-color: rgba(204, 255, 0, 0.15);
                        color: {ACCENT_LIME};
                    """)

                else:

                    badge.setStyleSheet(f"""
                        font-size: 10px; font-weight: 700;
                        padding: 3px 10px; border-radius: 9999px;
                        background-color: {CARD_LIGHT}; color: {TEXT_SEC};
                    """)

                item_layout.addWidget(badge)

            item_widget.mousePressEvent = lambda e, idx=i: self._on_item_click(idx)

            def make_enter(w):

                def handler(e):

                    w.setStyleSheet(f"background-color: {CARD_LIGHT}; border-radius: 14px;")

                return handler

            def make_leave(w):

                def handler(e):

                    w.setStyleSheet("background-color: transparent; border-radius: 14px;")

                return handler

            item_widget.enterEvent = make_enter(item_widget)

            item_widget.leaveEvent = make_leave(item_widget)

            item_widget.setStyleSheet("background-color: transparent; border-radius: 14px;")

            container_layout.addWidget(item_widget)

        popup_layout = QVBoxLayout(self)

        popup_layout.setContentsMargins(0, 0, 0, 0)

        popup_layout.addWidget(container)

    def _on_item_click(self, index):

        self.item_selected.emit(index)

    def showEvent(self, event):
        super().showEvent(event)
        # Popup container has border-radius: 20px in stylesheet,
        # which handles anti-aliased visual clipping automatically.

class GlowButton(RoundedButton):

    STYLES = {

        "lime": {

            "bg": ACCENT_LIME, "text": BG_COLOR, "border": ACCENT_LIME,

            "hover_bg": "transparent", "hover_text": ACCENT_LIME, "hover_border": ACCENT_LIME,

        },

        "cyan": {

            "bg": ACCENT_CYAN, "text": BG_COLOR, "border": ACCENT_CYAN,

            "hover_bg": "transparent", "hover_text": ACCENT_CYAN, "hover_border": ACCENT_CYAN,

        },

        "danger": {

            "bg": DANGER_COLOR, "text": "#FFFFFF", "border": DANGER_COLOR,

            "hover_bg": "transparent", "hover_text": DANGER_COLOR, "hover_border": DANGER_COLOR,

        },

        "ghost": {

            "bg": CARD_LIGHT, "text": TEXT_MAIN, "border": BORDER_COLOR,

            "hover_bg": "transparent", "hover_text": TEXT_MAIN, "hover_border": TEXT_SEC,

        },

        "outline": {

            "bg": "transparent", "text": TEXT_MAIN, "border": BORDER_COLOR,

            "hover_bg": "transparent", "hover_text": ACCENT_LIME, "hover_border": ACCENT_LIME,

        },

    }

    def __init__(self, text="", style="lime", parent=None, use_paint_glow=False):

        super().__init__(text, parent)

        self._style = style

        self._glow_enabled = True

        self._use_paint_glow = use_paint_glow

        self.apply_style(style)

    def resizeEvent(self, event):

        super().resizeEvent(event)

    def apply_style(self, style):

        self._style = style

        colors = self.STYLES.get(style, self.STYLES["lime"])

        self.set_colors(**colors)

    def set_glow_enabled(self, enabled):

        self._glow_enabled = enabled

        if not enabled:

            self.setGraphicsEffect(None)

    def _get_glow_color(self):

        if self._style == "lime": return ACCENT_LIME

        elif self._style == "cyan": return ACCENT_CYAN

        elif self._style == "danger": return DANGER_COLOR

        return ACCENT_LIME

    def enterEvent(self, event):

        if not self._use_paint_glow and self._glow_enabled and self.isEnabled():

            effect = QGraphicsDropShadowEffect()

            effect.setOffset(0, 0)

            effect.setColor(QColor(self._get_glow_color()))

            effect.setBlurRadius(30)

            self.setGraphicsEffect(effect)

        return super().enterEvent(event)

    def leaveEvent(self, event):

        if not self._use_paint_glow and self._glow_enabled:

            self.setGraphicsEffect(None)

        return super().leaveEvent(event)

    def paintEvent(self, event):

        if self._use_paint_glow and self._hovered and self._glow_enabled and self.isEnabled():

            painter = QPainter(self)

            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            w, h = self.width(), self.height()

            bw = self._border_width

            glow = QColor(self._get_glow_color())

            for i in range(8, 0, -1):

                alpha = max(0, 48 - i * 6)

                glow.setAlpha(alpha)

                s = i * 1.5

                rect = QRectF(

                    bw / 2 - s, bw / 2 - s,

                    w - bw + 2 * s, h - bw + 2 * s

                )

                h2 = h - bw + 2 * s

                if h2 <= 0:

                    continue

                glow_radius = min(9999, h2 / 2)

                painter.setPen(Qt.PenStyle.NoPen)

                painter.setBrush(glow)

                painter.drawRoundedRect(rect, glow_radius, glow_radius)

            painter.end()

        super().paintEvent(event)

    def update_style(self):

        self.apply_style(self._style)

class ToggleSwitch(QWidget):

    toggled = pyqtSignal(bool)

    def __init__(self, parent=None, initial=True):

        super().__init__(parent)

        self._checked = initial

        self.setFixedSize(48, 28)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._anim_progress = 1.0 if initial else 0.0

    def is_checked(self):

        return self._checked

    def set_checked(self, checked):

        self._checked = checked

        self._anim_progress = 1.0 if checked else 0.0

        self.update()

    def toggle(self):

        self._checked = not self._checked

        target = 1.0 if self._checked else 0.0

        steps = 10

        start = self._anim_progress

        delta = (target - start) / steps

        self._anim_step = 0

        self._anim_steps = steps

        self._anim_start = start

        self._anim_delta = delta

        self._anim_target = target

        self._anim_timer = QTimer(self)

        self._anim_timer.timeout.connect(self._anim_step_func)

        self._anim_timer.start(16)

        self.toggled.emit(self._checked)

    def _anim_step_func(self):

        self._anim_step += 1

        self._anim_progress = self._anim_start + self._anim_delta * self._anim_step

        if self._anim_step >= self._anim_steps:

            self._anim_progress = self._anim_target

            self._anim_timer.stop()

            self._anim_timer.deleteLater()

        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        radius = h / 2

        if self._checked:

            col = QColor(ACCENT_LIME)

        else:

            col = QColor(BORDER_COLOR)

        painter.setBrush(col)

        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawRoundedRect(0, 0, w, h, radius, radius)

        thumb_size = 22

        thumb_radius = thumb_size / 2

        thumb_margin = 3

        track_start = thumb_margin

        track_end = w - thumb_size - thumb_margin

        thumb_x = track_start + (track_end - track_start) * self._anim_progress

        painter.setBrush(QColor("#FFFFFF"))

        painter.setPen(Qt.PenStyle.NoPen)

        shadow = QColor(0, 0, 0, 60)

        painter.setBrush(shadow)

        painter.drawEllipse(QRectF(thumb_x + 1, thumb_margin + 1, thumb_size, thumb_size))

        painter.setBrush(QColor("#FFFFFF"))

        painter.drawEllipse(QRectF(thumb_x, thumb_margin, thumb_size, thumb_size))

        painter.end()

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self.toggle()

class ModernSlider(QWidget):

    valueChanged = pyqtSignal(float)

    dragStarted = pyqtSignal()

    dragFinished = pyqtSignal()

    def __init__(self, parent=None):

        super().__init__(parent)

        self._value = 50.0

        self._min = 0.0

        self._max = 100.0

        self._hovered = False

        self._dragging = False

        self.setFixedHeight(32)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setMouseTracking(True)

    def setValue(self, v):

        self._value = max(self._min, min(self._max, v))

        self.valueChanged.emit(self._value)

        self.update()

    def value(self):

        return self._value

    def setRange(self, mn, mx):

        self._min, self._max = mn, mx

    def _pos_to_val(self, x):

        margin = 12

        track_w = self.width() - margin * 2

        if track_w <= 0: return self._value

        rel = (x - margin) / track_w

        rel = max(0, min(1, rel))

        return self._min + rel * (self._max - self._min)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()

        margin = 12

        track_h = 32

        track_r = 16

        thumb_w = 44

        thumb_h = 22

        thumb_r = 11

        border_w = 2

        y_center = h / 2

        track_rect = QRectF(margin, y_center - track_h/2, w - margin*2, track_h)

        painter.setPen(QPen(QColor("#FFFFFF"), border_w))

        painter.setBrush(QColor(CARD_COLOR))

        painter.drawRoundedRect(track_rect, track_r, track_r)

        track_w = w - margin * 2

        rel = (self._value - self._min) / (self._max - self._min)

        thumb_x = margin + rel * track_w

        tx1 = thumb_x - thumb_w / 2

        ty1 = y_center - thumb_h / 2

        tx2 = thumb_x + thumb_w / 2

        ty2 = y_center + thumb_h / 2

        if tx1 < margin + 4:

            diff = (margin + 4) - tx1

            tx1 += diff; tx2 += diff

        if tx2 > w - margin - 4:

            diff = tx2 - (w - margin - 4)

            tx1 -= diff; tx2 -= diff

        thumb_color = QColor(ACCENT_LIME) if self._hovered else QColor(TEXT_SEC)

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(thumb_color)

        painter.drawRoundedRect(QRectF(tx1, ty1, tx2 - tx1, ty2 - ty1), thumb_r, thumb_r)

        painter.end()

    def enterEvent(self, event):

        self._hovered = True

        self.update()

        return super().enterEvent(event)

    def leaveEvent(self, event):

        self._hovered = False

        self.update()

        return super().leaveEvent(event)

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self._dragging = True

            self.dragStarted.emit()

            self.setValue(self._pos_to_val(event.position().x()))

    def mouseMoveEvent(self, event):

        if event.buttons() & Qt.MouseButton.LeftButton:

            self.setValue(self._pos_to_val(event.position().x()))

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton and self._dragging:

            self._dragging = False

            self.dragFinished.emit()

class HoverIconButton(QPushButton):

    def __init__(self, normal_icon_path, hover_icon_path, parent=None):

        super().__init__(parent)

        self._normal = QIcon(str(normal_icon_path))

        self._hover = QIcon(str(hover_icon_path))

        self.setIcon(self._normal)

        self.setMouseTracking(True)

        self.setStyleSheet("""

            QPushButton {

                background-color: transparent;

                border: none;

                padding: 0;

            }

        """)

    def enterEvent(self, event):

        self.setIcon(self._hover)

        return super().enterEvent(event)

    def leaveEvent(self, event):

        self.setIcon(self._normal)

        return super().leaveEvent(event)

class TabButton(RoundedButton):

    def __init__(self, text, parent=None):

        super().__init__(text, parent)

        self.setCheckable(True)

        self._checked_bg = QColor(ACCENT_LIME)

        self._checked_text = QColor(BG_COLOR)

        self.set_colors(

            bg="transparent", text=TEXT_SEC, border="transparent",

            hover_bg="rgba(255,255,255,13)", hover_text=TEXT_MAIN, hover_border="transparent"

        )

    def paintEvent(self, event):

        if self.isChecked():

            old_bg = self._bg_color

            old_text = self._text_color

            self._bg_color = self._checked_bg

            self._text_color = self._checked_text

            super().paintEvent(event)

            self._bg_color = old_bg

            self._text_color = old_text

        else:

            super().paintEvent(event)
