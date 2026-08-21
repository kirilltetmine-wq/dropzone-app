import json

from datetime import datetime

from pathlib import Path

from core.theme import APP_DATA_ROOT

DATA_DIR = APP_DATA_ROOT / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)

WHEELS_FILE = DATA_DIR / "wheels.json"

CASES_FILE = DATA_DIR / "cases.json"

LOGS_FILE = DATA_DIR / "history.json"

def load_json(file_path, default_value):

    if not file_path.exists():

        return default_value

    try:

        with file_path.open('r', encoding='utf-8') as f:

            return json.load(f)

    except Exception:

        return default_value

def save_json(file_path, data):

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open('w', encoding='utf-8') as f:

        json.dump(data, f, ensure_ascii=False, indent=4)

class Storage:

    @staticmethod

    def get_wheels():

        return load_json(WHEELS_FILE, {})

    @staticmethod

    def save_wheels(wheels):

        save_json(WHEELS_FILE, wheels)

    @staticmethod

    def get_cases():

        return load_json(CASES_FILE, {})

    @staticmethod

    def save_cases(cases):

        save_json(CASES_FILE, cases)

    @staticmethod

    def add_log(user, prize, wheel_name):

        logs = load_json(LOGS_FILE, [])

        logs.append({

            "user": user,

            "prize": str(prize),

            "wheel": str(wheel_name),

            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        })

        save_json(LOGS_FILE, logs)

    @staticmethod

    def get_logs():

        return load_json(LOGS_FILE, [])

    @staticmethod

    def clear_logs():

        save_json(LOGS_FILE, [])