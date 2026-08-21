import threading

import time

import random

import re

from PyQt6.QtWidgets import (

    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,

    QFrame, QLineEdit, QScrollArea, QSizePolicy,

    QGraphicsDropShadowEffect, QDialog,

)

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QPoint, QSize

from PyQt6.QtGui import QFont, QIcon

from core.theme import (

    BG_COLOR, CARD_COLOR, TEXT_MAIN, TEXT_SEC, BORDER_COLOR,

    ACCENT_LIME, FONT_FAMILY, CARD_LIGHT,

    KRESTIK_PATH,

    ACCENT_CYAN, DANGER_COLOR, SUCCESS_COLOR, GLOBAL_RADIUS,

    CIRCLE_ACTIVE_PATH, CIRCLE_DISABLED_PATH,

    RECYCLE_BIN_PATH, RECYCLE_BIN_ACTIVE_PATH,

    get_stylesheet,

)

from core.config import ConfigManager

from ui_kit import ModernDialog, show_info

from ui_kit import (
    RoundedButton, GlowButton,
    RoundedLineEdit, ToggleSwitch, HoverIconButton,
)

from ui_kit.ui_kit_pages import LotteryTabTemplate
from gui.chat import ChatManager, PlatformInfo, PLATFORM_REGISTRY, ChatSidebar
from gui.chat.platform_registry import PLATFORM_RED, PLATFORM_PURPLE

class LotteryMixin:

    def _setup_lottery_tab(self, page=None):

        # Используем готовый шаблон из UI Kit
        if page is None:
            self.lottery_page = LotteryTabTemplate()
            page = self.lottery_page
            template = page
        elif isinstance(page, LotteryTabTemplate):
            template = page
        else:
            # page — существующий контейнер, вставляем шаблон в него
            template = LotteryTabTemplate()
            layout = page.layout()
            if layout is None:
                layout = QVBoxLayout(page)
                layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(template)

        # Копируем ссылки на виджеты (для обратной совместимости)
        self.video_url_entry = template.video_url_entry
        self.keyword_entry = template.keyword_entry
        self.keyword_entry.textChanged.connect(self._on_keyword_changed)
        
        # Очищаем поле ввода ссылки при старте, так как забинженные каналы
        # должны подгружаться автоматически через chat_manager
        self.video_url_entry.clear()
        
        # Устанавливаем начальное значение keyword
        self._keyword_updating = False
        kw_default = self.config_mgr.get("lottery", "default_keyword", "!join")
        self.keyword_entry.setText(kw_default)
        self.start_btn = template.start_btn
        self.collect_btn = template.collect_btn
        self.pick_winner_btn = template.pick_winner_btn
        self.clear_btn = template.clear_btn
        self.manual_add_entry = template.manual_add_entry
        self.manual_add_row = template.manual_add_row
        self.auto_gray_toggle = template.auto_gray_toggle
        self.auto_wheel_toggle = template.auto_wheel_toggle
        self.auto_wheel_toggle.set_checked(self.config_mgr.get("lottery", "auto_wheel", False))
        self.status_label = template.status_label
        self.participants_container = template.participants_container
        self.connections_container = template.connections_container
        self.connections_layout = template.connections_layout
        self.chat_manager = ChatManager()
        self.stream_connections = self.chat_manager  # Alias for backward compat

        # Подключаем сигналы
        self.start_btn.clicked.connect(self.toggle_collection)
        self.collect_btn.clicked.connect(self.toggle_collecting)
        self.pick_winner_btn.clicked.connect(self.pick_winner)
        self.clear_btn.clicked.connect(self.clear_participants_list)
        self.manual_add_entry.returnPressed.connect(self._manual_add_user)
        self.add_user_btn = template.add_user_btn
        self.add_user_btn.clicked.connect(self._manual_add_user)
        self.auto_gray_toggle.toggled.connect(self._on_auto_gray_toggle)
        self.auto_wheel_toggle.toggled.connect(
            lambda v: self.config_mgr.set("lottery", "auto_wheel", v)
        )
        self.video_url_entry.returnPressed.connect(self._on_lottery_url_entered)

        self.participants_layout = QVBoxLayout(self.participants_container)
        self.participants_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.participant_widgets = {}

    def toggle_collection(self):
        """Start/stop tracking all connected streams."""

        if not self.is_connected:
            # START TRACKING
            if not self.chat_manager.has_connections():
                show_info(self, "Error", "Add a stream URL / channel name first and press Enter")
                return

            self.is_connected = True
            self.start_btn.setText("STOP TRACKING")
            self.start_btn._style = "danger"
            self.start_btn.update_style()
            self.collect_btn.setEnabled(True)
            self._update_connections_status()

        else:
            # STOP TRACKING
            self.is_connected = False
            self.is_collecting = False

            # Disconnect all session bots
            self.chat_manager.clear_all()
            self._clear_connections_ui()

            self.start_btn.setText("START TRACKING")
            self.start_btn._style = "ghost"
            self.start_btn.update_style()
            self.collect_btn.setEnabled(False)
            self.collect_btn.setText("START COLLECTING")
            self.collect_btn._style = "outline"
            self.collect_btn.update_style()
            self.status_label.setText("STANDBY")
            self.status_label.setStyleSheet(f"color: {TEXT_SEC}; font-weight: bold;")

            # Also clear config-based bots
            if self.twitch_bot:
                self.twitch_bot.disconnect()
                self.twitch_bot = None
            if self.bot:
                self.bot.stop_polling()
            # Removed self.bot.clear_participants() and self.clear_participants_list() from here


    def toggle_collecting(self):

        if not self.is_connected:
            return

        active_bot = self.twitch_bot if self._current_platform == "twitch" else self.bot
        has_active = active_bot and (self._current_platform != "youtube" or active_bot.live_chat_id)

        if not has_active and not self.chat_manager.has_connections():
            return

        if not self.is_collecting:

            self.is_collecting = True

            self.collect_btn.setText("STOP COLLECTING")

            self.collect_btn._style = "danger"

            self.collect_btn.update_style()

            self.status_label.setText("COLLECTING")

            self.status_label.setStyleSheet(f"color: {SUCCESS_COLOR}; font-weight: bold;")

            # Clear all bots
            if active_bot:
                active_bot.clear_participants()
            for conn in self.chat_manager.connections:
                if conn.bot:
                    conn.bot.clear_participants()

            self.clear_participants_list()

            if self.config_mgr.get("lottery", "whitelist_enabled", False):
                for name in self.config_mgr.get("lottery", "whitelist", []):
                    if name not in self.participant_widgets:
                        self.add_participant_widget(name)
                    if active_bot:
                        active_bot.participants.add(name)

            threading.Thread(target=self.collection_loop, daemon=True).start()

        else:

            self.is_collecting = False

            self.collect_btn.setText("START COLLECTING")

            self.collect_btn._style = "outline"

            self.collect_btn.update_style()

            self.status_label.setText("CONNECTED")

            self.status_label.setStyleSheet(f"color: {ACCENT_CYAN}; font-weight: bold;")

    def collection_loop(self):

        fatal_errors = {"QUOTA_EXCEEDED", "CHAT_ENDED", "AUTH_FAILED"}

        consecutive_errors = 0

        # Collect from all active chat_manager connections only
        all_bots = []
        for conn in self.chat_manager.connections:
            bot = conn.bot
            if bot:
                all_bots.append(bot)

        if not all_bots:
            return

        while self.is_collecting:

            keyword = self.keyword_entry.text()

            print(f"[COLLECT] Polling {len(all_bots)} bot(s) with keyword='{keyword}'...")

            any_ok = False
            for bot in all_bots:
                new_names, error = bot.fetch_messages(keyword)
                if error:
                    consecutive_errors += 1
                    if error in fatal_errors:
                        self._add_participant_signal.error_occurred.emit(error)
                        break
                    elif consecutive_errors >= 3:
                        self._add_participant_signal.error_occurred.emit(error)
                        break
                    else:
                        self._add_participant_signal.error_occurred.emit(error)
                else:
                    consecutive_errors = 0
                    any_ok = True
                    for name in new_names:
                        self._add_participant_signal.add_participant.emit(name)

            if not any_ok and consecutive_errors >= 3:
                break
            time.sleep(15)

        if self.is_collecting:

            self._add_participant_signal.error_occurred.emit("SELF_STOP")

    def _on_tracking_error(self, error_code):

        if error_code == "SELF_STOP":

            return

        self.is_collecting = False

        self.collect_btn.setText("START COLLECTING")

        self.collect_btn._style = "outline"

        self.collect_btn.update_style()

        messages = {

            "QUOTA_EXCEEDED": "QUOTA EXCEEDED — API limit reached. Try again tomorrow or increase quota in Google Cloud Console.",

            "CHAT_ENDED": "CHAT ENDED — The live stream has ended or chat is no longer available.",

            "AUTH_FAILED": "AUTH FAILED — Token expired. Re-authorize in CONFIG tab.",

        }

        msg = messages.get(error_code, f"ERROR: {error_code}")

        self.status_label.setText(msg)

        self.status_label.setStyleSheet(f"color: {DANGER_COLOR}; font-weight: bold;")

    def _on_auto_gray_toggle(self, checked):

        self.auto_gray_winners = checked

    def _on_keyword_changed(self, text):
        self.clear_participants_list()
        self._load_whitelist_participants()

    def _sync_keyword(self, text, from_lottery=True):
        if getattr(self, '_keyword_updating', False):
            return
        self._keyword_updating = True
        self.config_mgr.set("lottery", "default_keyword", text)
        if from_lottery and hasattr(self, '_chat_keyword_entry'):
            self._chat_keyword_entry.setText(text)
        elif not from_lottery and hasattr(self, 'keyword_entry'):
            self.keyword_entry.setText(text)
        self._keyword_updating = False

    def _load_whitelist_participants(self):

        if self.config_mgr.get("lottery", "whitelist_enabled", False):

            for name in self.config_mgr.get("lottery", "whitelist", []):

                if name not in self.participant_widgets:

                    self.add_participant_widget(name)

    def clear_participants_list(self):

        for w in self.participant_widgets.values():

            w.deleteLater()

        self.participant_widgets.clear()

        self.participants_data.clear()

    def add_participant_widget(self, name, skip_whitelist=False):

        if self.config_mgr.get("lottery", "blacklist_enabled", False):

            if name in self.config_mgr.get("lottery", "blacklist", []):

                return

        if not skip_whitelist and self.config_mgr.get("lottery", "whitelist_enabled", False):

            if name not in self.config_mgr.get("lottery", "whitelist", []):

                return

        if name not in self.participant_widgets:

            w = QFrame()

            w.setObjectName("cardDark")

            w.setFixedHeight(45)

            w_layout = QHBoxLayout(w)

            w_layout.setContentsMargins(20, 0, 20, 0)

            toggle_btn = QPushButton()

            toggle_btn.setFixedSize(28, 28)

            toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)

            icon_active = QIcon(str(CIRCLE_ACTIVE_PATH))

            toggle_btn.setIcon(icon_active)

            toggle_btn.setIconSize(toggle_btn.size())

            toggle_btn.setStyleSheet("""

                QPushButton {

                    background-color: transparent;

                    border: none;

                    padding: 0;

                }

            """)

            toggle_btn.clicked.connect(lambda checked, n=name: self._toggle_participant(n))

            w_layout.addWidget(toggle_btn)

            lbl = QLabel(name)

            lbl.setStyleSheet("color: white; font-size: 14px;")

            w_layout.addWidget(lbl, 1)

            del_btn = HoverIconButton(RECYCLE_BIN_PATH, RECYCLE_BIN_ACTIVE_PATH)

            del_btn.setFixedSize(28, 28)

            del_btn.setIconSize(del_btn.size())

            del_btn.setCursor(Qt.CursorShape.PointingHandCursor)

            del_btn.setStyleSheet("""

                QPushButton {

                    background-color: transparent;

                    border: none;

                    padding: 0;

                }

                QPushButton:hover {

                    background-color: rgba(255, 59, 48, 20);

                    border-radius: 14px;

                }

            """)

            del_btn.clicked.connect(lambda checked, n=name: self._delete_participant(n))

            w_layout.addWidget(del_btn)

            self.participants_layout.addWidget(w)

            self.participant_widgets[name] = w

            self.participants_data[name] = {"active": True, "widget": w, "toggle_btn": toggle_btn, "label": lbl, "del_btn": del_btn}

    def _manual_add_user(self):

        text = self.manual_add_entry.text().strip()

        if not text:

            return

        name = text.lstrip("@").strip()

        if not name:

            return

        if self.config_mgr.get("lottery", "blacklist_enabled", False):

            bl = self.config_mgr.get("lottery", "blacklist", [])

            if name in bl:

                return

        if self.bot:

            self.bot.participants.add(name)

        if name not in self.participant_widgets:

            self.add_participant_widget(name, skip_whitelist=True)

        print(f"[MANUAL] Added user: {name}")

        self.manual_add_entry.clear()

    def _toggle_participant(self, name):

        if name not in self.participants_data:

            return

        data = self.participants_data[name]

        data["active"] = not data["active"]

        if data["active"]:

            icon = QIcon(str(CIRCLE_ACTIVE_PATH))

            data["toggle_btn"].setIcon(icon)

            data["toggle_btn"].setIconSize(data["toggle_btn"].size())

            data["label"].setStyleSheet("color: white;")

        else:

            icon = QIcon(str(CIRCLE_DISABLED_PATH))

            data["toggle_btn"].setIcon(icon)

            data["toggle_btn"].setIconSize(data["toggle_btn"].size())

            data["label"].setStyleSheet(f"color: {TEXT_SEC};")

    def _delete_participant(self, name):

        if name not in self.participants_data:

            return

        dialog = ModernDialog(self, "DELETE PARTICIPANT", f"Remove '{name}' from the list?")

        if dialog.exec() == QDialog.DialogCode.Accepted:

            if self.bot and name in self.bot.participants:

                self.bot.participants.discard(name)

            data = self.participants_data.pop(name, None)

            if data:

                data["widget"].deleteLater()

            self.participant_widgets.pop(name, None)

    def extract_video_id(self, url):

        if len(url) == 11:

            return url

        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)

        return match.group(1) if match else None

    def pick_winner(self):

        if not self.bot:

            show_info(self, "Error", "Setup API first")

            return

        if self.is_collecting:

            self.is_collecting = False

            self.collect_btn.setText("START COLLECTING")

            self.collect_btn._style = "outline"

            self.collect_btn.update_style()

        active_names = [n for n, d in self.participants_data.items() if d["active"]]

        if not active_names:

            show_info(self, "Warning", "No active participants found!")

            return

        winner = random.choice(active_names)

        if self.auto_gray_winners:

            self._toggle_participant(winner)

        self.status_label.setText("WINNER PICKED")

        self.status_label.setStyleSheet(f"color: {ACCENT_LIME}; font-weight: bold;")

        dialog = ModernDialog(self, "LOTTERY", f"WINNER SELECTED: {winner.upper()}!\n\nSpin the wheel for a prize?")

        if dialog.exec() != QDialog.DialogCode.Accepted:

            return

        self._current_winner = winner

        if hasattr(self, 'winner_entry'):

            self.winner_entry.setText(winner)

        self._show_confirm_prize_btn(False)

        self._switch_tab_by_index(1)

        if self.config_mgr.get("lottery", "auto_wheel", False):

            show_info(self, "SPINNING", f"Auto-spinning wheel for {winner.upper()}!")

            self.start_spin()

        else:

            show_info(self, "SPIN", f"Spin any wheel for {winner.upper()}!")

    def _on_lottery_url_entered(self):
        """Detect YouTube URL or Twitch channel name and connect accordingly."""
        text = self.video_url_entry.text().strip()
        if not text:
            return

        import re as _re

        is_twitch = bool(_re.search(r'twitch\.tv', text, _re.IGNORECASE))
        is_youtube = bool(_re.search(r'youtube\.com|youtu\.be', text, _re.IGNORECASE))
        is_video_id = bool(_re.match(r'^[A-Za-z0-9_-]{11}$', text))

        if is_twitch:
            # Extract channel name from Twitch URL
            m = _re.search(r'twitch\.tv/([a-zA-Z0-9_]+)', text)
            channel = m.group(1).lower() if m else text
            self._add_twitch_connection(channel)
        elif is_youtube:
            self._add_youtube_connection(text)
        elif is_video_id:
            self._add_youtube_connection(text)
        else:
            # Plain name without URL → treat as Twitch channel
            channel = _re.sub(r'[@#]', '', text).strip().lower()
            self._add_twitch_connection(channel)
        self.video_url_entry.setText("")

    def _add_twitch_connection(self, channel):
        """Add a session-only Twitch connection."""
        from services.bot import TwitchChatBot
        from core.theme import TWITCH_CLIENT_ID
        cid = TWITCH_CLIENT_ID
        token = self.config_mgr.get('twitch', 'oauth_token', '') or None
        bot = TwitchChatBot(cid, token, channel)
        ok, err = bot.connect()
        if not ok:
            show_info(self, "Error", f"Failed to connect to {channel}: {err}")
            return
        conn = self.chat_manager.add_connection("twitch", channel, bot)
        self._add_connection_ui(conn)
        if hasattr(self, 'chat_widget'):
            self.chat_widget.set_chat_manager(self.chat_manager)
        if hasattr(self, '_update_twitch_status'):
            self._update_twitch_status()
        if hasattr(self, '_update_chat_status_labels'):
            self._update_chat_status_labels()

    def _add_youtube_connection(self, url):
        """Add a session-only YouTube connection — creates a dedicated bot per stream."""
        video_id = self.extract_video_id(url) if hasattr(self, 'extract_video_id') else None
        if not video_id and hasattr(self, 'bot') and self.bot:
            from core.utils import extract_video_id as ext_id
            video_id = ext_id(url)
        if not video_id:
            show_info(self, "Error", "Invalid YouTube URL")
            return
        if not hasattr(self, 'bot') or not self.bot:
            show_info(self, "Error", "YouTube API not authorized. Use CONFIG tab first.")
            return

        # Create a dedicated bot for this stream
        from services.bot import YouTubeChatBot
        yt_bot = YouTubeChatBot(self.credentials)
        chat_id, title, err = yt_bot.get_live_chat_id(video_id)
        if err:
            show_info(self, "Error", err)
            return
        yt_bot.live_chat_id = chat_id
        yt_bot.start_polling()

        conn = self.chat_manager.add_connection("youtube", title or video_id, yt_bot, chat_id=chat_id)
        self._add_connection_ui(conn)
        if hasattr(self, 'chat_widget'):
            self.chat_widget.set_chat_manager(self.chat_manager)

    def _add_connection_ui(self, conn):
        """Add a UI row for a chat connection — matches participant row style."""
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        row.setFixedHeight(45)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(20, 0, 20, 0)
        row_layout.setSpacing(8)

        # Number badge (circle)
        number_badge = QLabel(str(conn.number))
        number_badge.setFixedSize(28, 28)
        number_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_color = PLATFORM_RED if conn.platform == "youtube" else PLATFORM_PURPLE if conn.platform == "twitch" else "#8E8E93"
        number_badge.setStyleSheet(f"""
            background-color: {badge_color};
            color: #FFFFFF;
            font-size: 12px;
            font-weight: 800;
            border-radius: 14px;
        """)
        row_layout.addWidget(number_badge)

        # Platform icon
        icon_lbl = QLabel()
        icon_path = conn.platform_info.icon_path
        from PyQt6.QtGui import QPixmap
        if icon_path.exists():
            pix = QPixmap(str(icon_path))
            icon_lbl.setPixmap(pix.scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation))
        icon_lbl.setFixedSize(18, 18)
        row_layout.addWidget(icon_lbl)

        # Channel name (same font style as participants)
        name_lbl = QLabel(conn.channel)
        name_lbl.setStyleSheet(f"color: white; font-size: 14px;")
        row_layout.addWidget(name_lbl, 1)

        # Recycle bin button (same size as participants)
        remove_btn = HoverIconButton(RECYCLE_BIN_PATH, RECYCLE_BIN_ACTIVE_PATH)
        remove_btn.setFixedSize(28, 28)
        remove_btn.setIconSize(remove_btn.size())
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0;
            }
            QPushButton:hover {
                background-color: rgba(255, 59, 48, 20);
                border-radius: 14px;
            }
        """)
        remove_btn.clicked.connect(lambda checked, c=conn: self._remove_connection_ui(c.connection_id))
        row_layout.addWidget(remove_btn)

        conn.ui_row = row
        self.connections_layout.addWidget(row)
        self._update_connections_status()

    def _remove_connection_ui(self, connection_id):
        """Disconnect and remove a stream connection."""
        conn = self.chat_manager.get_connection(connection_id)
        if conn:
            if conn.platform == "twitch" and conn.bot:
                conn.bot.disconnect()
            self.chat_manager.remove_connection(connection_id)
            ui_row = getattr(conn, 'ui_row', None)
            if ui_row:
                self.connections_layout.removeWidget(ui_row)
                ui_row.deleteLater()
        if not self.chat_manager.has_connections():
            self.collect_btn.setEnabled(False)
        if hasattr(self, '_update_twitch_status'):
            self._update_twitch_status()
        if hasattr(self, '_update_chat_status_labels'):
            self._update_chat_status_labels()
        self._update_connections_status()

    def _clear_connections_ui(self):
        """Clear all connection UI rows."""
        while self.connections_layout.count():
            item = self.connections_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _update_connections_status(self):
        """Update status label — just 'CONNECTED' without channel names."""
        if not self.chat_manager.has_connections():
            if self.is_connected:
                self.status_label.setText("CONNECTED")
            else:
                self.status_label.setText("STANDBY")
            return
        self.status_label.setText("CONNECTED")
        self.status_label.setStyleSheet(f"color: {ACCENT_CYAN}; font-weight: bold;")

