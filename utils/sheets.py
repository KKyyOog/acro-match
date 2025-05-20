import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
load_dotenv()

def load_settings():
    default_settings = {
        "title": "アルバイト登録",
        "button_color": "#00b900",
        "form_label_name": "お名前",
        "form_label_area": "希望エリア",
        "form_label_available": "出勤可能日",
        "custom_fields": [],
        "classroom_title": "教室登録フォーム",
        "form_label_classroom_name": "教室名",
        "form_label_classroom_location": "場所",
        "form_label_classroom_date": "募集日時",
        "form_label_classroom_experience": "希望する経験"
    }
    try:
        with open("settings.json", "r", encoding="utf-8") as f:
            saved = json.load(f)
        return {**default_settings, **saved}
    except Exception as e:
        print(f"⚠️ load_settings error: {e}")
        return default_settings

def save_settings(data):
    try:
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ save_settings error: {e}")

def get_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

def find_matching_alb(sheet, area, experience_required, datetime_str):
    all_rows = sheet.get_all_records()
    matched = []
    for row in all_rows:
        area_match = area in row.get("area", "")
        date_match = datetime_str[:10] in row.get("available", "")
        gym_match = experience_required == "体操経験者" and row.get("gym") == "あり"
        cheer_match = experience_required == "チアリーディング可" and row.get("cheer") == "あり"
        fallback_match = experience_required == "補助可能"
        if area_match or date_match or gym_match or cheer_match or fallback_match:
            matched.append(row.get("user_id"))
    return matched

def get_liff_id(context="default"):
    return {
        "classroom": os.getenv("LIFF_ID_classroom", ""),
        "alb": os.getenv("LIFF_ID_alb", ""),
        "recruit": os.getenv("LIFF_ID_recruit", ""),
    }.get(context, "")

def update_sheet_headers_for_alb(sheet, settings):
    headers = [
        settings.get("form_label_name", "名前"),
        settings.get("form_label_alb_experience", "経験"),
        settings.get("form_label_area", "エリア"),
        settings.get("form_label_available", "出勤可能日・時間")
    ]

    # カスタム項目のラベルも追加
    for field in settings.get("custom_fields", []):
        headers.append(field.get("label", ""))

    headers.append("user_id")

    # 1行目を上書き
    sheet.delete_rows(1)  # 古いヘッダーを削除
    sheet.insert_row(headers, index=1)
