import sys

import os

os.environ["QT_OPENGL"] = "software"

os.environ["QSG_RHI_BACKEND"] = "software"

os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.fonts=false"

from PyQt6.QtWidgets import QApplication

from PyQt6.QtCore import qInstallMessageHandler

from PyQt6.QtGui import QSurfaceFormat, QIcon

# Enable MSAA for smoother rendering
fmt = QSurfaceFormat()
fmt.setSamples(4)
QSurfaceFormat.setDefaultFormat(fmt)

from core.theme import APP_DIR, load_font_global

from gui.splash import SplashScreen

from app import ChatLotteryApp

def _qt_message_handler(mode, context, message):

    if "QPainter" in message or "Painter not active" in message:

        return

    if "font-variant-numeric" in message:

        return

    if "QSG" in message:

        return

    print(message, file=__import__('sys').stderr) if message else None

if __name__ == "__main__":

    qInstallMessageHandler(_qt_message_handler)

    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(str(APP_DIR / "resources" / "logo.ico")))

    load_font_global(app)

    splash = SplashScreen()

    if splash.exec() == 1:

        splash.close()

        window = ChatLotteryApp()

        window.show()

        sys.exit(app.exec())
