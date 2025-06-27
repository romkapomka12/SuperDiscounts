import json
import os
from config.config import FAVORITES_FILE_PATH


def get_favorites_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "users_favorites.json")


def load_favorites(user_id):
    try:
        if os.path.exists(FAVORITES_FILE_PATH):
            with open(FAVORITES_FILE_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data.get(str(user_id), [])
        return []
    except Exception as e:
        print(f"Помилка завантаження обраних: {e}")
        return []

def save_favorites(user_id, favorites):
    try:
        data = {}
        if os.path.exists(FAVORITES_FILE_PATH):
            with open(FAVORITES_FILE_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)

        data[str(user_id)] = favorites

        with open(FAVORITES_FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Помилка збереження обраних: {e}")
        raise
