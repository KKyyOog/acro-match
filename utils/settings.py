# utils/settings.py
import json
import os

SETTINGS_PATH = "settings.json"

def load_settings():
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print("⚠️ 設定読み込み失敗:", e)
    return {}
