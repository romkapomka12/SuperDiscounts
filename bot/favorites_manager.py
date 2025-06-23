import json
import os
from typing import List, Dict, Any

FILE_FAVORITES = "users_favorites.json"

def load_favorites(user_id: int) -> List[Dict[str, Any]]:
    if not os.path.exists(FILE_FAVORITES):
        return []

    with open(FILE_FAVORITES, "r", encoding="utf-8") as file:
        try:
            all_data = json.load(file)
        except json.JSONDecodeError:
            return []

    return all_data.get(str(user_id), [])



def save_favorites(user_id: int, favorites: List[Dict[str, Any]]):
    all_data = {}

    if os.path.exists(FILE_FAVORITES):
        with open(FILE_FAVORITES, "r", encoding="utf-8") as file:
            try:
                all_data = json.load(file)
            except json.JSONDecodeError:
                all_data = {}

    all_data[str(user_id)] = favorites

    with open(FILE_FAVORITES, "w", encoding="utf-8") as file:
        json.dump(all_data, file, ensure_ascii=False, indent=2)
