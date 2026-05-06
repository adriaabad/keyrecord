import json
import os

DATA_FILE = "data/stats.json"


def ensure_data_folder():
    os.makedirs("data", exist_ok=True)


def get_empty_stats():
    return {
        "keyboard": {},
        "mouse": {}
    }


def load_stats():
    ensure_data_folder()

    if not os.path.exists(DATA_FILE):
        return get_empty_stats()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return get_empty_stats()


def save_stats(stats):
    ensure_data_folder()

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(stats, file, indent=4, ensure_ascii=False)