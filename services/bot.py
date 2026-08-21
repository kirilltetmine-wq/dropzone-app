import time
import socket
import threading
import random
import re as re_module
import requests

from googleapiclient.discovery import build

class YouTubeChatBot:

    POLL_INTERVAL = 5

    def __init__(self, credentials):

        self.youtube = build('youtube', 'v3', credentials=credentials)

        self.live_chat_id = None

        self.next_page_token = None

        self.participants = set()

        self.is_running = False

        self._message_queue = []

        self._queue_lock = threading.Lock()

        self._last_fetch_index = 0

        self._last_display_index = 0

        self._poll_running = False

        self._poll_thread = None

        self._poll_error = None

    def get_live_chat_id(self, video_id):

        try:

            response = self.youtube.videos().list(

                part='liveStreamingDetails,snippet',

                id=video_id

            ).execute()

            if not response['items']:

                return None, None, "Video not found."

            item = response['items'][0]
            title = item['snippet']['title']

            chat_id = item.get('liveStreamingDetails', {}).get('activeLiveChatId')

            if not chat_id:

                return None, title, "No active live chat on this video (stream ended or not a live stream)."

            self.live_chat_id = chat_id

            return chat_id, title, None

        except Exception as e:

            return None, None, str(e)

    def start_polling(self):

        if self._poll_running or not self.live_chat_id:

            return

        self._poll_running = True

        self._poll_error = None

        self.next_page_token = None

        self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)

        self._poll_thread.start()

    def stop_polling(self):

        self._poll_running = False

        if self._poll_thread:

            self._poll_thread = None

    def fetch_messages(self, keyword):

        if not self.live_chat_id:

            return [], "No active chat"

        try:

            request = self.youtube.liveChatMessages().list(

                liveChatId=self.live_chat_id,

                part='snippet,authorDetails',

                pageToken=self.next_page_token

            )

            response = request.execute()

            self.next_page_token = response.get('nextPageToken')

            new_participants = []

            total_msgs = len(response.get('items', []))

            with self._queue_lock:

                for item in response.get('items', []):

                    author_name = item['authorDetails']['displayName']

                    message_text = item['snippet']['displayMessage']

                    ch_id = item['authorDetails']['channelId']

                    is_mod = item['authorDetails'].get('isChatModerator', False)

                    self._message_queue.append({

                        'author': author_name,

                        'text': message_text,

                        'channel_id': ch_id,

                        'is_mod': is_mod,

                    })

                    if keyword.lower() in message_text.lower():

                        if author_name not in self.participants:

                            self.participants.add(author_name)

                            new_participants.append(author_name)

            self._last_fetch_index = len(self._message_queue)

            if total_msgs > 0:

                print(f"[YT] Fetched {total_msgs} messages, found {len(new_participants)} new participants for '{keyword}'")

            return new_participants, None

        except Exception as e:

            err_str = str(e)

            print(f"[YT] API ERROR: {err_str}")

            if 'quotaExceeded' in err_str:

                return [], "QUOTA_EXCEEDED"

            if 'liveChatNotFound' in err_str or 'liveChatDisabled' in err_str:

                return [], "CHAT_ENDED"

            if 'unauthorized' in err_str.lower() or 'invalid credentials' in err_str.lower() or '403' in err_str:

                return [], "AUTH_FAILED"

            return [], f"API_ERROR: {err_str}"

    def get_display_messages(self):

        with self._queue_lock:

            new_msgs = self._message_queue[self._last_display_index:]

            self._last_display_index = len(self._message_queue)

            self._trim_queue()

        return new_msgs

    def clear_participants(self):

        self.participants.clear()

    def send_message(self, message):

        if not self.live_chat_id:

            print("[YT] send_message: no live_chat_id")

            return False

        try:

            print(f"[YT] send_message: sending '{message[:50]}' to {self.live_chat_id}")

            self.youtube.liveChatMessages().insert(

                part='snippet',

                body={

                    'snippet': {

                        'liveChatId': self.live_chat_id,

                        'type': 'textMessageEvent',

                        'textMessageDetails': {

                            'messageText': message

                        }

                    }

                }

            ).execute()

            print("[YT] send_message: OK")

            return True

        except Exception as e:

            print(f"[YT] send_message FAILED: {e}")

            return False

    def ban_user(self, channel_id, duration_seconds=None):
        if not self.live_chat_id:
            return False
        try:
            body = {
                'snippet': {
                    'liveChatId': self.live_chat_id,
                    'bannedUserDetails': {'channelId': channel_id},
                    'type': 'temporary' if duration_seconds else 'permanent',
                }
            }
            if duration_seconds:
                body['snippet']['banDurationSeconds'] = str(duration_seconds)
            self.youtube.liveChatBans().insert(part='snippet', body=body).execute()
            return True
        except:
            return False

    def make_moderator(self, channel_id):
        if not self.live_chat_id:
            return False
        try:
            self.youtube.liveChatModerators().insert(
                part='snippet',
                body={
                    'snippet': {
                        'liveChatId': self.live_chat_id,
                        'channelId': channel_id,
                    }
                }
            ).execute()
            return True
        except:
            return False

    def _poll_loop(self):

        while self._poll_running:

            try:

                request = self.youtube.liveChatMessages().list(

                    liveChatId=self.live_chat_id,

                    part='snippet,authorDetails',

                    pageToken=self.next_page_token

                )

                response = request.execute()

                self.next_page_token = response.get('nextPageToken')

                with self._queue_lock:

                    for item in response.get('items', []):

                        self._message_queue.append({

                            'author': item['authorDetails']['displayName'],

                            'text': item['snippet']['displayMessage'],

                            'channel_id': item['authorDetails']['channelId'],

                            'is_mod': item['authorDetails'].get('isChatModerator', False),

                        })

                self._poll_error = None

                time.sleep(self.POLL_INTERVAL)

            except Exception as e:

                err_str = str(e)

                if 'quotaExceeded' in err_str:

                    self._poll_error = "QUOTA_EXCEEDED"

                    break

                if 'liveChatNotFound' in err_str or 'liveChatDisabled' in err_str:

                    self._poll_error = "CHAT_ENDED"

                    break

                if 'unauthorized' in err_str.lower() or 'invalid credentials' in err_str.lower():

                    self._poll_error = "AUTH_FAILED"

                    break

                self._poll_error = f"API_ERROR: {err_str}"

                time.sleep(10)

        self._poll_running = False

    def _trim_queue(self):

        if len(self._message_queue) > 5000:

            trim = min(self._last_fetch_index, self._last_display_index)

            if trim > 0:

                self._message_queue = self._message_queue[trim:]

                self._last_fetch_index -= trim

                self._last_display_index -= trim

class TwitchChatBot:

    HOST = "irc.chat.twitch.tv"
    PORT = 6667

    def __init__(self, client_id, oauth_token, channel_name):
        self.client_id = client_id
        self.oauth_token = oauth_token  # None = anonymous (read-only)
        self.channel_name = channel_name.lower().lstrip('#')
        self.sock = None
        self.participants = set()
        self.is_running = False
        self._read_thread = None
        self._buffer = ""
        self._message_queue = []
        self._queue_lock = threading.Lock()

    def connect(self):
        try:
            self.sock = socket.socket()
            self.sock.settimeout(10)
            self.sock.connect((self.HOST, self.PORT))

            if self.oauth_token:
                self._send(f"PASS oauth:{self.oauth_token}")
                self._send(f"NICK {self.channel_name}")
            else:
                # Anonymous read-only access via justinfan
                anon_nick = f"justinfan{random.randint(10000, 99999)}"
                self._send("PASS SCHMOOPIIE")
                self._send(f"NICK {anon_nick}")

            self._send(f"JOIN #{self.channel_name}")

            resp = self._recv(timeout=3)
            if "Login authentication failed" in resp:
                return False, "Twitch auth failed — check OAuth token"

            self.is_running = True
            self._read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self._read_thread.start()
            return True, None

        except Exception as e:
            return False, str(e)

    def disconnect(self):

        self.is_running = False

        if self.sock:

            try:

                self._send("QUIT")

                self.sock.close()

            except:

                pass

            self.sock = None

    def is_connected(self):

        return self.sock is not None and self.is_running

    def fetch_messages(self, keyword):

        new_participants = []

        messages = []

        with self._queue_lock:

            messages = self._message_queue.copy()

            self._message_queue.clear()

        for msg in messages:

            author = msg.get('author', '')

            text = msg.get('text', '')

            if keyword.lower() in text.lower():

                if author not in self.participants:

                    self.participants.add(author)

                    new_participants.append(author)

        return new_participants, None

    def send_message(self, message):

        if self.sock and self.is_running:

            try:

                self._send(f"PRIVMSG #{self.channel_name} :{message}")

                return True

            except:

                return False

        return False

    def ban_user(self, user_login):
        return self._send(f"PRIVMSG #{self.channel_name} :/ban {user_login}")

    def timeout_user(self, user_login, duration_seconds=300):
        return self._send(f"PRIVMSG #{self.channel_name} :/timeout {user_login} {duration_seconds}")

    def delete_message(self, msg_id):
        return self._send(f"PRIVMSG #{self.channel_name} :/delete {msg_id}")

    def make_moderator(self, user_login):
        return self._send(f"PRIVMSG #{self.channel_name} :/mod {user_login}")

    def clear_participants(self):

        self.participants.clear()

    def get_stream_status(self):

        if not self.client_id or not self.oauth_token:

            return False, "", 0

        try:

            headers = {

                "Client-ID": self.client_id,

                "Authorization": f"Bearer {self.oauth_token}"

            }

            url = f"https://api.twitch.tv/helix/streams?user_login={self.channel_name}"

            resp = requests.get(url, headers=headers, timeout=10)

            data = resp.json()

            if data.get('data'):

                stream = data['data'][0]

                return True, stream.get('title', ''), stream.get('viewer_count', 0)

            return False, "", 0

        except:

            return False, "", 0

    def _send(self, msg):

        if self.sock:

            self.sock.send(f"{msg}\r\n".encode('utf-8'))

    def _recv(self, timeout=3):

        if not self.sock:

            return ""

        self.sock.settimeout(timeout)

        try:

            data = self.sock.recv(4096).decode('utf-8', errors='ignore')

            return data

        except socket.timeout:

            return ""

        except:

            return ""

    def _read_loop(self):

        while self.is_running:

            try:

                self.sock.settimeout(1)

                data = self.sock.recv(4096).decode('utf-8', errors='ignore')

                if not data:

                    break

                self._buffer += data

                lines = self._buffer.split('\r\n')

                self._buffer = lines.pop()

                for line in lines:

                    self._process_line(line)

            except socket.timeout:

                continue

            except:

                break

        self.is_running = False

    def _process_line(self, line):

        if line.startswith("PING"):

            self._send(f"PONG {line[5:]}")

            return

        is_mod = False
        user_id = ""
        msg_id = ""

        msg_line = line

        if line.startswith('@'):

            tag_end = line.index(' ')

            tags_str = line[1:tag_end]

            msg_line = line[tag_end+1:]

            for tag in tags_str.split(';'):

                if '=' in tag:

                    k, v = tag.split('=', 1)

                    if k == 'mod' and v == '1':
                        is_mod = True
                    elif k == 'id':
                        msg_id = v
                    elif k == 'user-id':
                        user_id = v

        match = re_module.match(r':(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :(.*)', msg_line)

        if match:

            author = match.group(1)

            text = match.group(2)

            with self._queue_lock:

                self._message_queue.append({'author': author, 'text': text, 'is_mod': is_mod, 'user_id': user_id, 'msg_id': msg_id})
