from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication

from services.bot import TwitchChatBot
from ui_kit import show_info
from core.theme import (
    ACCENT_CYAN, DANGER_COLOR, FONT_FAMILY, SUCCESS_COLOR, TWITCH_CLIENT_ID,
)


class TwitchMixin:
    """Twitch: OAuth (API) + anonymous (nickname) connection."""

    # ── status ──────────────────────────────────────────────

    def _update_twitch_status(self):
        bot = getattr(self, 'twitch_bot', None)
        connected = bot is not None and bot.is_connected()
        color = SUCCESS_COLOR if connected else DANGER_COLOR
        text = "CONNECTED" if connected else "DISCONNECTED"
        self._twitch_status_dot.setStyleSheet(f"""
            background-color: {color};
            border-radius: 4px;
        """)
        self._twitch_status_text.setText(text)
        self._twitch_status_text.setStyleSheet(
            f"color: {color}; font-size: 13px; font-weight: 700;"
            f" font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;"
        )

    # ── OAuth (API) ─────────────────────────────────────────

    def _twitch_oauth(self):
        cid = TWITCH_CLIENT_ID
        import requests as reqs
        import time as time_module

        try:
            resp = reqs.post("https://id.twitch.tv/oauth2/device", data={
                "client_id": cid,
                "scopes": "chat:read chat:edit"
            })
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            show_info(self, "Error", f"Failed to request device code: {e}")
            return

        device_code = data["device_code"]
        user_code = data["user_code"]
        verification_uri = data["verification_uri"]
        interval = data.get("interval", 5)
        expires_in = data.get("expires_in", 180)

        show_info(self, "TWITCH AUTHORIZATION",
                  f"1. Open the link in your browser\n"
                  f"2. Enter the code: {user_code}\n\n"
                  f"Link: {verification_uri}")
        QDesktopServices.openUrl(QUrl(verification_uri))

        timeout = expires_in
        waited = 0
        token = None
        while waited < timeout:
            try:
                poll_resp = reqs.post("https://id.twitch.tv/oauth2/token", data={
                    "client_id": cid,
                    "device_code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
                })
                poll_data = poll_resp.json()
                if "access_token" in poll_data:
                    token = poll_data["access_token"]
                    break
                elif poll_data.get("status") == 400 and "authorization_pending" in poll_data.get("message", ""):
                    pass
                elif poll_data.get("status") == 400 and "slow_down" in poll_data.get("message", ""):
                    interval += 1
            except Exception:
                pass
            for _ in range(int(interval / 0.2)):
                if waited >= timeout:
                    break
                QApplication.processEvents()
                time_module.sleep(0.2)
                waited += 0.2

        if not token:
            show_info(self, "Error", "Twitch authorization timed out or was cancelled")
            return

        self.config_mgr.set('twitch', 'oauth_token', token)

        username = ""
        try:
            validate_resp = reqs.get("https://id.twitch.tv/oauth2/validate",
                                     headers={"Authorization": f"Bearer {token}"})
            if validate_resp.status_code == 200:
                validate_data = validate_resp.json()
                username = validate_data.get("login", "")
                if username:
                    self.config_mgr.set('twitch', 'channel_name', username)
                    self._twitch_channel_entry.setText(username)
                    self._twitch_channel_entry.setReadOnly(True)
                    self._twitch_bind_btn.setVisible(False)
                    self._twitch_unbind_btn.setVisible(True)
                    self._twitch_status_label.setText(f"Bound: {username}")
                    self._twitch_status_label.setStyleSheet(
                        f"color: {SUCCESS_COLOR}; font-size: 12px;"
                        f" font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;"
                    )
        except Exception:
            pass

        self._update_twitch_status()
        if username:
            show_info(self, "Twitch Authorized",
                      f"Twitch OAuth token obtained successfully.\nChannel '{username}' auto-bound.")
        else:
            show_info(self, "Twitch Authorized", "Twitch OAuth token obtained successfully.")

    # ── bind / unbind channel (API mode) ────────────────────

    def _bind_twitch_channel(self):
        channel = self._twitch_channel_entry.text().strip().lower()
        if not channel:
            show_info(self, "Error", "Enter a Twitch channel name")
            return
        channel = channel.lstrip('#').strip()
        self._twitch_channel_entry.setText(channel)
        # Connect immediately — handles config save, UI setup, and chat connection
        self._connect_twitch(silent=True)

    def _unbind_twitch_channel(self):
        self._disconnect_twitch_bot()
        self.config_mgr.set('twitch', 'channel_name', '')
        self.config_mgr.set('twitch', 'auto_track', False)
        self._twitch_channel_entry.setReadOnly(False)
        self._twitch_channel_entry.setText('')
        self._update_twitch_status()
        self._twitch_bind_btn.setVisible(True)
        self._twitch_unbind_btn.setVisible(False)
        self._twitch_auto_track_switch.set_checked(False)
        self._stop_twitch_monitor()
        self._twitch_status_label.setText("")
        show_info(self, "Twitch Channel Unbound", "Twitch channel has been unbound.")

    # ── quick connect (nickname) ────────────────────────────

    def _connect_twitch(self, silent=False):
        """Connect by channel name — uses OAuth token if available, else anonymous."""
        channel = self._twitch_channel_entry.text().strip().lower()
        if not channel:
            show_info(self, "Error", "Enter a Twitch channel name")
            return
        channel = channel.lstrip('#').strip()
        self.config_mgr.set('twitch', 'channel_name', channel)
        self._twitch_channel_entry.setText(channel)

        self._disconnect_twitch_bot()

        cid = TWITCH_CLIENT_ID
        token = self.config_mgr.get('twitch', 'oauth_token', '') or None
        self.twitch_bot = TwitchChatBot(cid, token, channel)
        ok, err = self.twitch_bot.connect()
        if not ok:
            show_info(self, "Error", f"Failed to connect: {err}")
            self.twitch_bot = None
            self._update_twitch_status()
            return

        if hasattr(self, 'chat_manager'):
            conn = self.chat_manager.add_connection("twitch", channel, self.twitch_bot)
            if hasattr(self, '_add_connection_ui'):
                self._add_connection_ui(conn)
            if hasattr(self, 'chat_widget'):
                self.chat_widget.set_chat_manager(self.chat_manager)
            if hasattr(self, '_update_connections_status'):
                self._update_connections_status()

        self._twitch_channel_entry.setReadOnly(True)
        self._update_twitch_status()
        self._activate_twitch_platform(channel)
        if hasattr(self, '_twitch_status_label'):
            self._twitch_status_label.setText(f"Bound: {channel}")
            self._twitch_status_label.setStyleSheet(
                f"color: {SUCCESS_COLOR}; font-size: 12px;"
                f" font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;"
            )
        if hasattr(self, '_update_chat_status_labels'):
            self._update_chat_status_labels()
        if not silent:
            mode = "OAuth" if token else "anonymous"
            show_info(self, "Twitch Connected", f"Connected to twitch.tv/{channel} ({mode})")

    def _disconnect_twitch_bot(self):
        bot = getattr(self, 'twitch_bot', None)
        if bot:
            bot.disconnect()
            self.twitch_bot = None
        if hasattr(self, 'chat_widget'):
            self.chat_widget.set_twitch_bot(None)
        if hasattr(self, '_update_chat_status_labels'):
            self._update_chat_status_labels()

    # ── auto-track (API mode, requires OAuth) ───────────────

    def _on_twitch_auto_track(self, checked):
        self.config_mgr.set('twitch', 'auto_track', checked)
        if checked:
            self._start_twitch_monitor()
        else:
            self._stop_twitch_monitor()

    def _start_twitch_monitor(self):
        channel = self.config_mgr.get('twitch', 'channel_name', '')
        if not channel:
            self._twitch_auto_track_switch.set_checked(False)
            show_info(self, "Info", "Bind a Twitch channel first before enabling auto-track.")
            return
        cid = TWITCH_CLIENT_ID
        token = self.config_mgr.get('twitch', 'oauth_token', '')
        if not token:
            self._twitch_auto_track_switch.set_checked(False)
            show_info(self, "Error", "Authorize Twitch first (AUTHORIZE TWITCH button)")
            return
        if hasattr(self, '_twitch_monitor_running') and self._twitch_monitor_running:
            return
        self._twitch_monitor_running = True
        self._twitch_monitored_streams = set()
        self._twitch_monitor_timer = QTimer(self)
        self._twitch_monitor_timer.timeout.connect(self._check_twitch_streams)
        self._twitch_monitor_timer.start(60000)
        self._check_twitch_streams()

    def _stop_twitch_monitor(self):
        self._twitch_monitor_running = False
        if hasattr(self, '_twitch_monitor_timer') and self._twitch_monitor_timer:
            self._twitch_monitor_timer.stop()
            self._twitch_monitor_timer.deleteLater()
            self._twitch_monitor_timer = None

    def _check_twitch_streams(self):
        channel = self.config_mgr.get('twitch', 'channel_name', '')
        cid = TWITCH_CLIENT_ID
        token = self.config_mgr.get('twitch', 'oauth_token', '')
        if not channel or not token:
            return
        try:
            import requests
            headers = {
                "Client-ID": cid,
                "Authorization": f"Bearer {token}"
            }
            url = f"https://api.twitch.tv/helix/streams?user_login={channel}"
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            if data.get('data'):
                stream = data['data'][0]
                stream_id = stream.get('id', '')
                if stream_id not in self._twitch_monitored_streams:
                    self._twitch_monitored_streams.add(stream_id)
                    title = stream.get('title', '')
                    self._on_new_twitch_stream(title)
        except:
            pass

    def _on_new_twitch_stream(self, title):
        channel = self.config_mgr.get('twitch', 'channel_name', '')
        if getattr(self, 'twitch_bot', None) and self.twitch_bot.is_connected():
            return
        cid = TWITCH_CLIENT_ID
        token = self.config_mgr.get('twitch', 'oauth_token', '')
        self.twitch_bot = TwitchChatBot(cid, token, channel)
        ok, err = self.twitch_bot.connect()
        if not ok:
            return

        # Activate platform state (is_connected, _current_platform, status_label, collect_btn)
        self._activate_twitch_platform(channel)

        # Add to connected streams via chat_manager
        if hasattr(self, 'chat_manager'):
            conn = self.chat_manager.add_connection("twitch", channel, self.twitch_bot)
            if hasattr(self, '_add_connection_ui'):
                self._add_connection_ui(conn)
            if hasattr(self, 'chat_widget'):
                self.chat_widget.set_chat_manager(self.chat_manager)
            if hasattr(self, '_update_chat_status_labels'):
                self._update_chat_status_labels()
            if hasattr(self, '_update_connections_status'):
                self._update_connections_status()

        show_info(self, "Twitch Auto-Track", f"Live stream detected!\n\n{title}\n\nAuto-connected to {channel}.")

    def _activate_twitch_platform(self, channel):
        self.is_connected = True
        self.is_collecting = False
        self._current_platform = "twitch"
        if hasattr(self, 'start_btn'):
            self.start_btn.setText("STOP TRACKING")
            self.start_btn._style = "danger"
            self.start_btn.update_style()
        if hasattr(self, 'collect_btn'):
            self.collect_btn.setEnabled(True)
        if hasattr(self, 'status_label'):
            self.status_label.setText("CONNECTED")
            self.status_label.setStyleSheet(f"color: {ACCENT_CYAN}; font-weight: bold;")