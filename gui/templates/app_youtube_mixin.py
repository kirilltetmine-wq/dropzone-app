import pickle

import re

from PyQt6.QtCore import Qt, QTimer

from services.bot import YouTubeChatBot

from core.config import ConfigManager

from ui_kit import show_info

from core.theme import (
    CLIENT_SECRET_PATH, TOKEN_PATH,
    FONT_FAMILY, SUCCESS_COLOR, DANGER_COLOR, ACCENT_CYAN,
)

class YouTubeMixin:

    def run_oauth(self):

        if not CLIENT_SECRET_PATH.exists():

            show_info(self, "Error", "client_secret.json missing")

            return

        try:

            from google_auth_oauthlib.flow import InstalledAppFlow

            flow = InstalledAppFlow.from_client_secrets_file(

                str(CLIENT_SECRET_PATH),

                ["https://www.googleapis.com/auth/youtube.force-ssl"]

            )

            creds = flow.run_local_server(port=8080, timeout_seconds=120)

            TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
            with TOKEN_PATH.open("wb") as f:

                pickle.dump(creds, f)

            self.credentials = creds

            self.bot = YouTubeChatBot(creds)

            self._update_yt_status()
 
            try:
 
                resp = self.bot.youtube.channels().list(
 
                    part='snippet',
 
                    mine=True
 
                ).execute()
 
                if resp.get('items'):
 
                    channel = resp['items'][0]
 
                    channel_id = channel['id']
 
                    display_name = channel['snippet']['title']
 
                    self.config_mgr.set('youtube', 'bound_channel', channel_id)
 
                    self.config_mgr.set('youtube', 'channel_name', display_name)
 
                    self._set_channel_bound_ui(channel_id, display_name)
 
                    show_info(self, "Success", f"API Authorization Complete\n\nChannel '{display_name}' auto-bound.")
 
                else:
 
                    show_info(self, "Success", "API Authorization Complete\nNo channel found for this account.")
 
            except Exception:
 
                show_info(self, "Success", "API Authorization Complete\nCould not auto-bind channel — enter it manually.")
 
        except Exception as e:
            err_str = str(e)
            if 'Timeout' in err_str or 'timed out' in err_str.lower():
                show_info(self, "Timeout", "Authorization timed out. Please try again and complete the process in the browser.")
            elif 'access_denied' in err_str or 'cancelled' in err_str.lower():
                show_info(self, "Cancelled", "Authorization was cancelled.")
            else:
                show_info(self, "Error", f"Authorization failed: {err_str}")

    def _bind_youtube_channel(self):

        if not self.bot:

            show_info(self, "Error", "Authorize Google Account first")

            return

        raw = self._channel_entry.text().strip()

        if not raw:

            show_info(self, "Error", "Enter a channel URL, handle, or ID")

            return

        channel_id = self._resolve_channel_id(raw)

        if not channel_id:

            show_info(self, "Error", "Could not resolve channel. Check the URL / handle and try again.")

            return

        display_name = channel_id

        try:

            resp = self.bot.youtube.channels().list(

                part='snippet',

                id=channel_id

            ).execute()

            if resp.get('items'):

                display_name = resp['items'][0]['snippet']['title']

        except Exception:

            pass

        self.config_mgr.set('youtube', 'bound_channel', channel_id)

        self.config_mgr.set('youtube', 'channel_name', display_name)

        self._set_channel_bound_ui(channel_id, display_name)

        self._update_yt_status()

        # Auto-enable tracking after bind
        self.config_mgr.set('youtube', 'auto_track', True)
        if hasattr(self, '_auto_track_switch'):
            self._auto_track_switch.set_checked(True)
        self._start_monitor()

        show_info(self, "Channel Bound", f"Channel '{display_name}' has been bound successfully.")

    def _resolve_channel_id(self, raw):
        text = raw.strip()
        m = re.search(r'youtube\.com/(?:@|channel/|c/|user/)?([A-Za-z0-9_@-]+)', text)
        if m:
            text = m.group(1)
        if text.startswith('UC') and len(text) == 24:
            return text
        handle = text if text.startswith('@') else f'@{text}'
        try:
            resp = self.bot.youtube.channels().list(
                part='id',
                forHandle=handle
            ).execute()
            if resp.get('items'):
                return resp['items'][0]['id']
        except Exception:
            pass
        try:
            resp = self.bot.youtube.search().list(
                part='snippet',
                q=text.lstrip('@'),
                type='channel',
                maxResults=1
            ).execute()
            if resp.get('items'):
                return resp['items'][0]['snippet']['channelId']
        except Exception:
            pass
        return None

    def _update_yt_status(self):
        bot = getattr(self, 'bot', None)
        has_channel = bool(self.config_mgr.get('youtube', 'bound_channel', ''))
        connected = (bot is not None
                     and hasattr(bot, 'youtube')
                     and bot.youtube is not None
                     and has_channel)
        color = SUCCESS_COLOR if connected else DANGER_COLOR
        text = "CONNECTED" if connected else "DISCONNECTED"
        if hasattr(self, '_yt_status_dot'):
            self._yt_status_dot.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
        if hasattr(self, '_yt_status_text'):
            self._yt_status_text.setText(text)
            self._yt_status_text.setStyleSheet(
                f"color: {color}; font-size: 13px; font-weight: 700;"
                f" font-family: '{FONT_FAMILY}', 'Segoe UI', sans-serif;"
            )

    def _unbind_youtube_channel(self):

        self.config_mgr.set('youtube', 'bound_channel', '')

        self.config_mgr.set('youtube', 'channel_name', '')

        self.config_mgr.set('youtube', 'auto_track', False)

        self._channel_entry.setReadOnly(False)

        self._channel_entry.setText('')

        self._channel_status_label.setText('')

        self._bind_channel_btn.setVisible(True)

        self._unbind_channel_btn.setVisible(False)
        self._auto_track_switch.set_checked(False)
        self.credentials = None
        self.bot = None
        # Delete token file so it doesn't get loaded on next start
        if TOKEN_PATH.exists():
            TOKEN_PATH.unlink()
        self._update_yt_status()
        if hasattr(self, '_update_chat_status_labels'):
            self._update_chat_status_labels()

        self._stop_monitor()

        show_info(self, "Channel Unbound", "YouTube channel has been unbound.")

    def _on_auto_track_toggle(self, checked):

        self.config_mgr.set('youtube', 'auto_track', checked)

        if checked:

            self._start_monitor()

        else:

            self._stop_monitor()

    def _start_monitor(self):

        bound = self.config_mgr.get('youtube', 'bound_channel', '')

        if not bound:

            self._auto_track_switch.set_checked(False)

            show_info(self, "Info", "Bind a channel first before enabling auto-track.")

            return

        if not self.bot:

            show_info(self, "Error", "Authorize Google Account first")

            self._auto_track_switch.set_checked(False)

            return

        if self._monitor_running:

            return

        self._monitor_running = True

        self._monitored_streams.clear()

        self._monitor_timer = QTimer(self)

        self._monitor_timer.timeout.connect(self._check_live_streams)

        self._monitor_timer.start(60000)

        self._check_live_streams()

        self._channel_status_label.setText(

            f"{self._channel_status_label.text().replace(' (monitoring)', '')} (monitoring)"

        )

    def _stop_monitor(self):

        self._monitor_running = False

        if self._monitor_timer:

            self._monitor_timer.stop()

            self._monitor_timer.deleteLater()

            self._monitor_timer = None

        status_text = self._channel_status_label.text()

        if status_text:

            self._channel_status_label.setText(status_text.replace(' (monitoring)', ''))

    def _check_live_streams(self):

        channel_id = self.config_mgr.get('youtube', 'bound_channel', '')

        if not channel_id or not self.bot:

            return

        try:

            resp = self.bot.youtube.search().list(

                part='snippet',

                channelId=channel_id,

                type='video',

                eventType='live',

                order='date',

                maxResults=5

            ).execute()

            for item in resp.get('items', []):

                video_id = item['id']['videoId']

                if video_id not in self._monitored_streams:

                    self._monitored_streams.add(video_id)

                    title = item['snippet']['title']

                    self._on_new_live_stream(video_id, title)

        except Exception as e:

            pass

    def _on_new_live_stream(self, video_id, title):

        if not self.config_mgr.get('youtube', 'auto_track', False):

            return

        if getattr(self, 'bot', None) and getattr(self.bot, '_poll_running', False):

            return

        chat_id, title, err = self.bot.get_live_chat_id(video_id)

        if err:

            self._monitored_streams.discard(video_id)

            return

        self.bot.start_polling()

        # Mark as connected — update start_btn to STOP TRACKING
        self.is_connected = True
        if hasattr(self, 'start_btn'):
            self.start_btn.setText("STOP TRACKING")
            self.start_btn._style = "danger"
            self.start_btn.update_style()
        if hasattr(self, 'collect_btn'):
            self.collect_btn.setEnabled(True)
        if hasattr(self, 'status_label'):
            self.status_label.setText("CONNECTED")
            self.status_label.setStyleSheet(f"color: {ACCENT_CYAN}; font-weight: bold;")

        # Add to connected streams via chat_manager
        channel_name = self.config_mgr.get('youtube', 'channel_name', '') or self.config_mgr.get('youtube', 'bound_channel', '')
        if hasattr(self, 'chat_manager'):
            conn = self.chat_manager.add_connection("youtube", channel_name, self.bot, chat_id=chat_id)
            if hasattr(self, '_add_connection_ui'):
                self._add_connection_ui(conn)
            if hasattr(self, 'chat_widget'):
                self.chat_widget.set_chat_manager(self.chat_manager)
            if hasattr(self, '_update_chat_status_labels'):
                self._update_chat_status_labels()
            if hasattr(self, '_update_connections_status'):
                self._update_connections_status()

        show_info(self, "Auto-Track", f"New live stream detected!\n\n{title}\n\nAuto-connected to chat.")
