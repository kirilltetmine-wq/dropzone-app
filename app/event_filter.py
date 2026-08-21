from PyQt6.QtCore import Qt, QPoint, QTimer, QEvent, QRect
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QPixmap
from PyQt6.QtWidgets import QWidget, QFrame, QLabel
from core.theme import *
from core.utils import _get_cached_pixmap
from gui.detach import DetachableSection


class EventFilterMixin:
    def eventFilter(self, obj, event):

        if hasattr(self, 'tab_btns') and len(self.tab_btns) >= 2:

            if obj in self.tab_btns and event.type() == QEvent.Type.MouseButtonPress:

                if event.button() == Qt.MouseButton.LeftButton:

                    self._tab_drag_active_idx = self.tab_btns.index(obj)

                    self._tab_drag_start_pos = event.globalPosition().toPoint()

                    self._tab_drag_preview_shown = False

            if event.type() == QEvent.Type.MouseMove and self._tab_drag_active_idx >= 0:

                if event.buttons() & Qt.MouseButton.LeftButton and self._tab_drag_start_pos is not None:

                    pos = event.globalPosition().toPoint()

                    dist = (pos - self._tab_drag_start_pos).manhattanLength()

                    if dist > 20:

                        tab_bar_global = QRect(self.tab_bar.mapToGlobal(QPoint(0, 0)), self.tab_bar.size())

                        tab_bar_global.adjust(0, -10, 0, 10)

                        if not tab_bar_global.contains(pos):

                            if not self._tab_drag_preview_shown:

                                section = self.stack.widget(self._tab_drag_active_idx)

                                if isinstance(section, DetachableSection) and not section.is_detached:

                                    self._show_tab_drag_preview(section, pos)

                                    self._tab_drag_preview_shown = True

                                    self.setCursor(Qt.CursorShape.ClosedHandCursor)

                            elif self._tab_drag_preview is not None:

                                self._tab_drag_preview.move(

                                    pos - QPoint(self._tab_drag_preview.width() // 2,

                                                 self._tab_drag_preview.height() // 2)

                                )

                        else:

                            if self._tab_drag_preview_shown:

                                self._tab_drag_preview_shown = False

                                self._hide_tab_drag_preview()

                    elif dist > 5:

                        self.setCursor(Qt.CursorShape.ClosedHandCursor)

                    return True

                self._tab_drag_active_idx = -1

                self._tab_drag_start_pos = None

                self._tab_drag_preview_shown = False

                self._hide_tab_drag_preview()

                self.setCursor(Qt.CursorShape.ArrowCursor)

            if event.type() == QEvent.Type.MouseButtonRelease and self._tab_drag_active_idx >= 0:

                if event.button() == Qt.MouseButton.LeftButton:

                    if self._tab_drag_preview_shown:

                        pos = event.globalPosition().toPoint()

                        section = self.stack.widget(self._tab_drag_active_idx)

                        if isinstance(section, DetachableSection) and not section.is_detached:

                            section._detach(pos)

                        self._hide_tab_drag_preview()

                        self._tab_drag_active_idx = -1

                        self._tab_drag_start_pos = None

                        self._tab_drag_preview_shown = False

                        self.setCursor(Qt.CursorShape.ArrowCursor)

                        return True

                    self._tab_drag_active_idx = -1

                    self._tab_drag_start_pos = None

        if hasattr(self, 'sub_nav_btns') and len(self.sub_nav_btns) >= 2:

            if obj in self.sub_nav_btns and event.type() == QEvent.Type.MouseButtonPress:

                if event.button() == Qt.MouseButton.LeftButton:

                    self._sub_drag_active_idx = self.sub_nav_btns.index(obj)

                    self._sub_drag_start_pos = event.globalPosition().toPoint()

                    self._sub_drag_preview_shown = False

            if event.type() == QEvent.Type.MouseMove and self._sub_drag_active_idx >= 0:

                if event.buttons() & Qt.MouseButton.LeftButton and self._sub_drag_start_pos is not None:

                    pos = event.globalPosition().toPoint()

                    dist = (pos - self._sub_drag_start_pos).manhattanLength()

                    if dist > 20 and not self._sub_drag_preview_shown:

                        idx = self._sub_drag_active_idx

                        if idx < len(self._sub_sections):

                            section = self._sub_sections[idx]

                            if not section.is_detached:

                                self._show_sub_drag_preview(section, pos)

                                self._sub_drag_preview_shown = True

                                self.setCursor(Qt.CursorShape.ClosedHandCursor)

                    elif self._sub_drag_preview_shown and self._tab_drag_preview is not None:

                        self._tab_drag_preview.move(

                            pos - QPoint(self._tab_drag_preview.width() // 2,

                                         self._tab_drag_preview.height() // 2)

                        )

                    elif dist > 5:

                        self.setCursor(Qt.CursorShape.ClosedHandCursor)

                    return True

                self._sub_drag_active_idx = -1

                self._sub_drag_start_pos = None

                self._sub_drag_preview_shown = False

                self._hide_tab_drag_preview()

                self.setCursor(Qt.CursorShape.ArrowCursor)

            if event.type() == QEvent.Type.MouseButtonRelease and self._sub_drag_active_idx >= 0:

                if event.button() == Qt.MouseButton.LeftButton:

                    if self._sub_drag_preview_shown:

                        pos = event.globalPosition().toPoint()

                        idx = self._sub_drag_active_idx

                        if idx < len(self._sub_sections):

                            section = self._sub_sections[idx]

                            if not section.is_detached:

                                section._detach(pos)

                        self._hide_tab_drag_preview()

                        self._sub_drag_active_idx = -1

                        self._sub_drag_start_pos = None

                        self._sub_drag_preview_shown = False

                        self.setCursor(Qt.CursorShape.ArrowCursor)

                        return True

                    self._sub_drag_active_idx = -1

                    self._sub_drag_start_pos = None

        if hasattr(self, 'main_sub_nav_btns') and len(self.main_sub_nav_btns) >= 2:

            if obj in self.main_sub_nav_btns and event.type() == QEvent.Type.MouseButtonPress:

                if event.button() == Qt.MouseButton.LeftButton:

                    self._main_sub_drag_active_idx = self.main_sub_nav_btns.index(obj)

                    self._main_sub_drag_start_pos = event.globalPosition().toPoint()

                    self._main_sub_drag_preview_shown = False

            if event.type() == QEvent.Type.MouseMove and self._main_sub_drag_active_idx >= 0:

                if event.buttons() & Qt.MouseButton.LeftButton and self._main_sub_drag_start_pos is not None:

                    pos = event.globalPosition().toPoint()

                    dist = (pos - self._main_sub_drag_start_pos).manhattanLength()

                    if dist > 20 and not self._main_sub_drag_preview_shown:

                        idx = self._main_sub_drag_active_idx

                        if idx < len(self._main_sub_sections):

                            section = self._main_sub_sections[idx]

                            if not section.is_detached:

                                self._show_main_sub_drag_preview(section, pos)

                                self._main_sub_drag_preview_shown = True

                                self.setCursor(Qt.CursorShape.ClosedHandCursor)

                    elif self._main_sub_drag_preview_shown and self._tab_drag_preview is not None:

                        self._tab_drag_preview.move(

                            pos - QPoint(self._tab_drag_preview.width() // 2,

                                         self._tab_drag_preview.height() // 2)

                        )

                    elif dist > 5:

                        self.setCursor(Qt.CursorShape.ClosedHandCursor)

                    return True

                self._main_sub_drag_active_idx = -1

                self._main_sub_drag_start_pos = None

                self._main_sub_drag_preview_shown = False

                self._hide_tab_drag_preview()

                self.setCursor(Qt.CursorShape.ArrowCursor)

            if event.type() == QEvent.Type.MouseButtonRelease and self._main_sub_drag_active_idx >= 0:

                if event.button() == Qt.MouseButton.LeftButton:

                    if self._main_sub_drag_preview_shown:

                        pos = event.globalPosition().toPoint()

                        idx = self._main_sub_drag_active_idx

                        if idx < len(self._main_sub_sections):

                            section = self._main_sub_sections[idx]

                            if not section.is_detached:

                                section._detach(pos)

                        self._hide_tab_drag_preview()

                        self._main_sub_drag_active_idx = -1

                        self._main_sub_drag_start_pos = None

                        self._main_sub_drag_preview_shown = False

                        self.setCursor(Qt.CursorShape.ArrowCursor)

                        return True

                    self._main_sub_drag_active_idx = -1

                    self._main_sub_drag_start_pos = None

        if event.type() == QEvent.Type.MouseMove:

            global_pos = event.globalPosition().toPoint()

            local_pos = self.mapFromGlobal(global_pos)

            if self._resizing and self._resize_edge is not None:

                delta = global_pos - self._resize_last_global

                self._resize_last_global = global_pos

                geom = self.geometry()

                x, y, w, h = geom.x(), geom.y(), geom.width(), geom.height()

                if 'left' in self._resize_edge:

                    new_x = x + delta.x()

                    new_w = w - delta.x()

                    if new_w >= self.minimumWidth():

                        x = new_x

                        w = new_w

                if 'right' in self._resize_edge:

                    new_w = w + delta.x()

                    if new_w >= self.minimumWidth():

                        w = new_w

                if 'top' in self._resize_edge:

                    new_y = y + delta.y()

                    new_h = h - delta.y()

                    if new_h >= self.minimumHeight():

                        y = new_y

                        h = new_h

                if 'bottom' in self._resize_edge:

                    new_h = h + delta.y()

                    if new_h >= self.minimumHeight():

                        h = new_h

                self.setGeometry(x, y, w, h)

                return True

            if self.rect().contains(local_pos) and not self.isMaximized():

                edges = self._get_resize_edge(local_pos)

                self._set_resize_cursor(edges)

            elif not self._is_over_detached_window(obj):

                self.setCursor(Qt.CursorShape.ArrowCursor)

            return False

        elif event.type() == QEvent.Type.MouseButtonPress:

            if event.button() == Qt.MouseButton.LeftButton and not self.isMaximized():

                global_pos = event.globalPosition().toPoint()

                local_pos = self.mapFromGlobal(global_pos)

                if self.rect().contains(local_pos):

                    edges = self._get_resize_edge(local_pos)

                    if edges:

                        self._resizing = True

                        self._resize_edge = edges

                        self._resize_start_global = global_pos

                        self._resize_start_rect = self.geometry()

                        self._resize_last_global = global_pos

                        return True

            return False

        elif event.type() == QEvent.Type.MouseButtonRelease:

            if event.button() == Qt.MouseButton.LeftButton and self._resizing and not self.isMaximized():

                self._resizing = False

                self._resize_edge = None

                self._resize_start_global = None

                self._resize_start_rect = None

                self._resize_last_global = None

                self.setCursor(Qt.CursorShape.ArrowCursor)

                return True

            return False

        if not hasattr(self, 'tab_btns') or len(self.tab_btns) < 2:

            return False

        if not hasattr(self, 'sub_nav') or not hasattr(self, '_sub_nav_hover_timer'):

            return False

        if obj is self.tab_btns[0]:

            if event.type() == event.Type.Enter:

                self._show_main_sub_nav()

            elif event.type() == event.Type.Leave:

                self._main_sub_nav_hover_timer.start(150)

            elif event.type() == event.Type.Wheel:

                if self.stack.currentIndex() == 0:

                    self._do_main_wheel_switch(event.angleDelta().y())

                    return True

        elif obj is self.tab_btns[1]:

            if event.type() == event.Type.Enter:

                self._show_sub_nav()

            elif event.type() == event.Type.Leave:

                self._sub_nav_hover_timer.start(150)

            elif event.type() == event.Type.Wheel:

                if self.stack.currentIndex() == 1:

                    self._do_wheel_switch(event.angleDelta().y())

                    return True

        elif obj is self.sub_nav:

            if event.type() == event.Type.Enter:

                self._sub_nav_hover_timer.stop()

                self._show_sub_nav()

            elif event.type() == event.Type.Leave:

                self._sub_nav_hover_timer.start(150)

        elif obj is getattr(self, 'main_sub_nav', None):

            if event.type() == event.Type.Enter:

                self._main_sub_nav_hover_timer.stop()

                self._show_main_sub_nav()

            elif event.type() == event.Type.Leave:

                self._main_sub_nav_hover_timer.start(150)

        elif obj is getattr(self, '_case_overlay', None):

            if event.type() == event.Type.Resize:

                self._resize_case_image()

        return False