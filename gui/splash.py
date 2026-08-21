import random

from PyQt6.QtCore import Qt, QTimer, QSize, QEvent

from PyQt6.QtGui import QPixmap, QIcon

from PyQt6.QtWidgets import (

    QDialog, QFrame, QWidget, QVBoxLayout, QLabel, QPushButton,

)

from core.theme import (

    APP_DIR, BG_COLOR, CARD_COLOR, BORDER_COLOR, ACCENT_LIME, TEXT_MAIN, TEXT_SEC, FONT_FAMILY

)

class SplashScreen(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)

        self.setWindowIcon(QIcon(str(APP_DIR / "resources" / "logo.ico")))

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setFixedSize(520, 420)

        self._drag_start = None

        self._welcome_active = False

        self._skipped = False

        card = QFrame(self)

        card.setObjectName("splashCard")

        card.setGeometry(0, 0, 520, 420)

        card.setStyleSheet(f"""
            QFrame#splashCard {{
                background-color: {CARD_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 30px;
            }}
        """)

        self._card = card

        card.installEventFilter(self)

        self.loading_widget = QWidget(card)

        self.loading_widget.setGeometry(0, 0, 520, 420)

        self.loading_widget.setStyleSheet("background: transparent;")

        loading_layout = QVBoxLayout(self.loading_widget)

        loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        loading_layout.setSpacing(20)

        logo = QLabel()

        logo.setPixmap(QPixmap(str(APP_DIR / "resources" / "logo.png")).scaled(

            120, 120, Qt.AspectRatioMode.KeepAspectRatio,

            Qt.TransformationMode.SmoothTransformation

        ))

        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo.setStyleSheet("background: transparent;")

        loading_layout.addWidget(logo)

        progress_container = QFrame()

        progress_container.setFixedSize(280, 4)

        progress_container.setStyleSheet(f"""

            background-color: {BORDER_COLOR}; border-radius: 2px; border: none;

        """)

        self.progress_fill = QFrame(progress_container)

        self.progress_fill.setFixedSize(0, 4)

        self.progress_fill.setStyleSheet(f"""

            background-color: {ACCENT_LIME}; border-radius: 2px; border: none;

        """)

        loading_layout.addWidget(progress_container, alignment=Qt.AlignmentFlag.AlignCenter)

        self.loading_status = QLabel("Loading...")

        self.loading_status.setStyleSheet(f"""

            color: {TEXT_SEC}; font-size: 12px; letter-spacing: 1px;

            background: transparent; text-transform: uppercase;

        """)

        self.loading_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        loading_layout.addWidget(self.loading_status)

        version = QLabel("release 1.0.0")

        version.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; opacity: 0.4; background: transparent;")

        version.setAlignment(Qt.AlignmentFlag.AlignCenter)

        loading_layout.addWidget(version)

        self.welcome_widget = QWidget(card)

        self.welcome_widget.setGeometry(0, 0, 520, 420)

        self.welcome_widget.setStyleSheet("background: transparent;")

        self.welcome_widget.hide()

        welcome_layout = QVBoxLayout(self.welcome_widget)

        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_layout.setSpacing(10)

        welcome_logo = QLabel()

        welcome_logo.setPixmap(QPixmap(str(APP_DIR / "resources" / "logo.png")).scaled(

            100, 100, Qt.AspectRatioMode.KeepAspectRatio,

            Qt.TransformationMode.SmoothTransformation

        ))

        welcome_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_logo.setStyleSheet("background: transparent;")

        welcome_layout.addWidget(welcome_logo)

        self.typewriter_label = QLabel()

        self.typewriter_label.setStyleSheet(f"""

            color: {ACCENT_LIME}; font-size: 36px; font-weight: 900;

            background: transparent; letter-spacing: -1px;

        """)

        self.typewriter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.typewriter_label.setFixedHeight(50)

        welcome_layout.addWidget(self.typewriter_label)

        self.subtitle_label = QLabel()

        self.subtitle_label.setStyleSheet(f"""

            color: {TEXT_SEC}; font-size: 14px; background: transparent;

            letter-spacing: 0.3px;

        """)

        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.subtitle_label.setWordWrap(True)

        self.subtitle_label.setFixedWidth(460)

        self.subtitle_label.setFixedHeight(50)

        welcome_layout.addWidget(self.subtitle_label)

        self.start_btn = QPushButton("START")

        self.start_btn.setFixedSize(200, 52)

        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_LIME}; color: {BG_COLOR};
                border: none; border-radius: 26px;
                font-size: 15px; font-weight: 700;
                letter-spacing: 1.5px; text-transform: uppercase;
            }}
            QPushButton:hover {{
                background: transparent; color: {ACCENT_LIME};
                border: 2px solid {ACCENT_LIME};
            }}
        """)

        self.start_btn.clicked.connect(self.accept)

        self.start_btn.setVisible(False)

        welcome_layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        skip = QLabel("press ENTER to skip")

        skip.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; background: transparent;")

        skip.setAlignment(Qt.AlignmentFlag.AlignCenter)

        skip.setFixedHeight(20)

        welcome_layout.addWidget(skip)

        self._loading_steps = [

            (15, "Initializing..."),

            (35, "Loading modules..."),

            (55, "Connecting services..."),

            (75, "Preparing interface..."),

            (90, "Almost ready..."),

            (100, "Ready."),

        ]

        self._step_idx = 0

        QTimer.singleShot(300, self._next_loading_step)

    def _next_loading_step(self):

        if self._step_idx >= len(self._loading_steps):

            QTimer.singleShot(400, self._show_welcome)

            return

        pct, text = self._loading_steps[self._step_idx]

        w = int(280 * pct / 100)

        self.progress_fill.setFixedWidth(w)

        self.loading_status.setText(text)

        self._step_idx += 1

        delay = 150 + random.randint(0, 100)

        QTimer.singleShot(delay, self._next_loading_step)

    def _show_welcome(self):

        self.loading_widget.hide()

        self.welcome_widget.show()

        self._welcome_active = True

        QTimer.singleShot(300, self._type_title)

    def _type_title(self):

        text = "Dropzone?"

        self._typewriter_text = text

        self._typewriter_idx = 0

        self._typewriter_timer = QTimer(self)

        self._typewriter_timer.timeout.connect(self._type_title_char)

        self._typewriter_timer.start(100 + random.randint(0, 50))

    def _type_title_char(self):

        if self._typewriter_idx < len(self._typewriter_text):

            shown = self._typewriter_text[:self._typewriter_idx + 1]

            self.typewriter_label.setText(shown + "▎")

            self._typewriter_idx += 1

        else:

            self.typewriter_label.setText(self._typewriter_text)

            self._typewriter_timer.stop()

            QTimer.singleShot(500, self._type_subtitle)

    def _type_subtitle(self):

        text = "Yea, Dropzone — the best APP for giveaways on any stream!"

        self._subtitle_text = text

        self._subtitle_idx = 0

        self._subtitle_timer = QTimer(self)

        self._subtitle_timer.timeout.connect(self._type_subtitle_char)

        self._subtitle_timer.start(30 + random.randint(0, 10))

    def _type_subtitle_char(self):

        if self._subtitle_idx < len(self._subtitle_text):

            shown = self._subtitle_text[:self._subtitle_idx + 1]

            self.subtitle_label.setText(shown + "▎")

            self._subtitle_idx += 1

        else:

            self.subtitle_label.setText(self._subtitle_text)

            self._subtitle_timer.stop()

            self.start_btn.setVisible(True)

    def keyPressEvent(self, event):

        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:

            self._skip_to_end()

        super().keyPressEvent(event)

    def _skip_to_end(self):
        if self._skipped:
            return

        self._skipped = True

        # Stop all timers
        if hasattr(self, '_typewriter_timer') and self._typewriter_timer.isActive():
            self._typewriter_timer.stop()

        if hasattr(self, '_subtitle_timer') and self._subtitle_timer.isActive():
            self._subtitle_timer.stop()

        # Accept immediately — open the app
        self.accept()

    def eventFilter(self, obj, event):

        if event.type() == QEvent.Type.MouseButtonPress:

            if event.button() == Qt.MouseButton.LeftButton:

                if obj is not self.start_btn:

                    self._drag_start = event.globalPosition().toPoint()

                    return True

        elif event.type() == QEvent.Type.MouseMove:

            if self._drag_start and event.buttons() & Qt.MouseButton.LeftButton:

                delta = event.globalPosition().toPoint() - self._drag_start

                self._drag_start = event.globalPosition().toPoint()

                self.move(self.pos() + delta)

                return True

        elif event.type() == QEvent.Type.MouseButtonRelease:

            if event.button() == Qt.MouseButton.LeftButton:

                self._drag_start = None

                return True

        return super().eventFilter(obj, event)
