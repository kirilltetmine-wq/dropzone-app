from PyQt6.QtCore import Qt, QSize, QEvent

from PyQt6.QtGui import QIcon

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from core.theme import (

    BG_COLOR, CARD_COLOR, TEXT_MAIN, BORDER_COLOR, DANGER_COLOR,

    MINUS_PATH, KVADRAT_PATH, KRESTIK_PATH,

    KRESTIK_WHITE_PATH

)

class TitleBar(QFrame):

    def __init__(self, parent):

        super().__init__(parent)

        self._parent = parent

        self.setFixedHeight(38)

        self.setStyleSheet(f"""

            QFrame {{

                background-color: {BG_COLOR};

                border-bottom: 1px solid {BORDER_COLOR};

            }}

        """)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(16, 0, 0, 0)

        layout.setSpacing(0)

        title = QLabel("Dropzone")

        title.setStyleSheet(f"""

            QLabel {{

                color: {TEXT_MAIN};

                font-size: 13px;

                font-weight: 700;

                background: transparent;

                padding: 0;

            }}

        """)

        layout.addWidget(title)

        layout.addStretch()

        btn_base = f"""

            #titleMinBtn, #titleMaxBtn, #titleCloseBtn {{

                background: transparent;

                border: none;

                border-radius: 0;

                padding: 0;

            }}

            #titleMinBtn:hover, #titleMaxBtn:hover {{

                background: {CARD_COLOR};

            }}

        """

        self.min_btn = QPushButton()

        self.min_btn.setObjectName("titleMinBtn")

        self.min_btn.setIcon(QIcon(str(MINUS_PATH)))

        self.min_btn.setIconSize(QSize(16, 16))

        self.min_btn.setFixedSize(46, 38)

        self.min_btn.setStyleSheet(btn_base)

        self.min_btn.clicked.connect(self._parent.showMinimized)

        self.min_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        layout.addWidget(self.min_btn)

        self.max_btn = QPushButton()

        self.max_btn.setObjectName("titleMaxBtn")

        self.max_btn.setIcon(QIcon(str(KVADRAT_PATH)))

        self.max_btn.setIconSize(QSize(16, 16))

        self.max_btn.setFixedSize(46, 38)

        self.max_btn.setStyleSheet(btn_base)

        self.max_btn.clicked.connect(self._toggle_maximize)

        self.max_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        layout.addWidget(self.max_btn)

        self.close_btn = QPushButton()

        self.close_btn.setObjectName("titleCloseBtn")

        self.close_btn.setIcon(QIcon(str(KRESTIK_PATH)))

        self.close_btn.setIconSize(QSize(16, 16))

        self.close_btn.setFixedSize(46, 38)

        self.close_btn.setStyleSheet(f"""

            #titleCloseBtn {{

                background: transparent;

                border: none;

                border-radius: 0;

                padding: 0;

            }}

            #titleCloseBtn:hover {{

                background: {DANGER_COLOR};

            }}

        """)

        self.close_btn.clicked.connect(self._parent.close)

        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.close_btn.installEventFilter(self)

        layout.addWidget(self.close_btn)

    def _toggle_maximize(self):

        if self._parent.isMaximized():

            self._parent.showNormal()

        else:

            self._parent.showMaximized()

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self._drag_pos = event.globalPosition().toPoint()

            self._drag_start = self._parent.pos()

            event.accept()

    def mouseMoveEvent(self, event):

        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_pos'):

            delta = event.globalPosition().toPoint() - self._drag_pos

            self._parent.move(self._drag_start + delta)

            event.accept()

    def mouseDoubleClickEvent(self, event):

        self._toggle_maximize()

    def eventFilter(self, obj, event):

        if obj is self.close_btn:

            if event.type() == QEvent.Type.Enter:

                self.close_btn.setIcon(QIcon(str(KRESTIK_WHITE_PATH)))

            elif event.type() == QEvent.Type.Leave:

                self.close_btn.setIcon(QIcon(str(KRESTIK_PATH)))

        return super().eventFilter(obj, event)
