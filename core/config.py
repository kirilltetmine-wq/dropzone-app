import json

from core.theme import APP_DATA_ROOT

class ConfigManager:

    def __init__(self):

        self._app_dir = APP_DATA_ROOT

        self._config_dir = self._app_dir / 'config'

        self._lists_dir = self._app_dir / 'lists'

        self._wheels_dir = self._app_dir / 'wheels'

        self._logs_dir = self._app_dir / 'logs'

        self._auth_dir = self._app_dir / 'auth'

        self._config_file = self._config_dir / 'settings.json'

        for d in [self._config_dir, self._lists_dir, self._wheels_dir, self._logs_dir, self._auth_dir]:

            d.mkdir(parents=True, exist_ok=True)

        self._defaults = {

            'general': {
                'always_on_top': False,
                'start_minimized': False,
                'transparency': 90,
                'auto_save_interval': 5,
                'confirm_before_delete': True,
                'tutorial_shown': False,
            },

            'appearance': {

                'dark_mode': True,

                'accent_color': '#CCFF00',

            },

            'api': {

                'auto_reconnect': True,

            },

            'lottery': {

                'default_keyword': '!join',

                'case_sensitive': False,

                'auto_delete_winners': True,

                'auto_wheel': False,

                'show_manual_add': True,

                'duplicate_check': True,

                'blacklist_enabled': False,

                'blacklist': [],

                'whitelist_enabled': False,

                'whitelist': [],

            },

            'wheels': {

                'show_add_sector': True,

                'show_equalize': True,

                'show_delete': True,

                'show_rename': True,

                'show_auto_color': True,

                'show_random_color': True,

                'show_general_color': True,

            },

            'logs': {

                'auto_clear_entries': 1000,

                'show_timestamps': True,

            },

            'youtube': {

                'bound_channel': '',

                'channel_name': '',

                'auto_track': False,

            },

            'twitch': {

                'oauth_token': '',

                'channel_name': '',

                'auto_track': False,

            },

            'chat': {

                'max_messages': 200,

                'show_timestamps': True,

                'show_badges': True,

                'show_platform_icons': True,

                'mod_default_timeout': 300,

            },

            'dice': {

                'animation_enabled': True,

                'auto_roll': False,

            },

            'notifications': {
                'system_notifications': True,
            },

        }

        self._settings = self._load()

        self.save()

    def _load(self):

        if self._config_file.exists():

            try:

                with open(self._config_file, 'r', encoding='utf-8') as f:

                    saved = json.load(f)

                merged = self._full_deep_copy(self._defaults)

                self._deep_merge(merged, saved)

                return merged

            except Exception:

                return self._full_deep_copy(self._defaults)

        return self._full_deep_copy(self._defaults)

    def _full_deep_copy(self, d):

        return json.loads(json.dumps(d))

    def _deep_merge(self, base, override):

        for key, value in override.items():

            if key in base and isinstance(base[key], dict) and isinstance(value, dict):

                self._deep_merge(base[key], value)

            else:

                base[key] = value

    def save(self):

        with open(self._config_file, 'w', encoding='utf-8') as f:

            json.dump(self._settings, f, ensure_ascii=False, indent=4)

    def get(self, section, key, default=None):

        val = self._settings.get(section, {}).get(key, default)

        if isinstance(val, str):

            val = val.strip("\\ '")

        return val

    def set(self, section, key, value):

        if section not in self._settings:

            self._settings[section] = {}

        self._settings[section][key] = value

        self.save()

    def get_section(self, section):

        return self._settings.get(section, {}).copy()

    def reset_all(self):

        self._settings = self._full_deep_copy(self._defaults)

        self.save()

    def add_blacklist_user(self, name):

        if name not in self._settings['lottery']['blacklist']:

            self._settings['lottery']['blacklist'].append(name)

            self.save()

    def remove_blacklist_user(self, name):

        self._settings['lottery']['blacklist'] = [n for n in self._settings['lottery']['blacklist'] if n != name]

        self.save()

    def add_whitelist_user(self, name):

        if name not in self._settings['lottery']['whitelist']:

            self._settings['lottery']['whitelist'].append(name)

            self.save()

    def remove_whitelist_user(self, name):

        self._settings['lottery']['whitelist'] = [n for n in self._settings['lottery']['whitelist'] if n != name]

        self.save()

    def export_data(self):

        return self._full_deep_copy(self._settings)

    def import_data(self, data):

        if isinstance(data, dict):

            self._settings = self._full_deep_copy(self._defaults)

            self._deep_merge(self._settings, data)

            self.save()

            return True

        return False
