import gspread
import json
import os
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

### 設定ファイルの読み書き
def load_settings():
    default_settings = {
        # アルバイトフォーム用
        "title": "アルバイト登録",
        "button_color": "#00b900",
        "form_label_name": "ニックネーム",
        "form_label_area": "希望エリア",
        "form_label_available": "稼働可能日・時間",
        "form_label_alb_experience": "経験",

        # 教室フォーム用
        "classroom_title": "教室登録",
        "button_color": "#00b900",
        "form_label_classroom_name": "教室名",
        "form_label_classroom_location": "場所", 
        "form_label_classroom_date": "募集日時",
        "form_label_classroom_experience": "希望する経験",
        "form_label_classroom_handslevel": "補助レベル",
        "form_label_classroom_notes": "その他ご要望・自由記述",

        # カスタム項目
        "custom_fields": [],
        "custom_fields_classroom": []
    }
    try:
        with open("settings.json", "r", encoding="utf-8") as f:
            saved = json.load(f)

        # フォーム互換変換
        if "custom_fields_form" in saved:
            saved["custom_fields"] = saved["custom_fields_form"]

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

### Google Sheets アクセス
def get_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

### LIFF ID取得
def get_liff_id(context="default"):
    return {
        "classroom": os.getenv("LIFF_ID_classroom", ""),
        "alb": os.getenv("LIFF_ID_alb", ""),
        "recruit": os.getenv("LIFF_ID_recruit", ""),
    }.get(context, "")

### アルバイト登録シートのヘッダー更新
def update_sheet_headers_for_alb(sheet, settings):
    headers = [
        settings.get("form_label_name", "名前"),
        settings.get("form_label_alb_experience", "経験"),
        settings.get("form_label_alb_handslevel", "補助レベル"),
        settings.get("form_label_area", "希望エリア"),
        settings.get("form_label_available", "稼働可能日・時間"),
    ]
    for field in settings.get("custom_fields", []):
        headers.append(field.get("label", ""))
    headers.append("user_id")
    sheet.delete_rows(1)
    sheet.insert_row(headers, index=1)

### 教室登録シートのヘッダー更新
def update_sheet_headers_for_classroom(sheet, settings):
    headers = [
        settings.get("form_label_classroom_name", "教室名"),
        settings.get("form_label_classroom_location", "場所"),
        settings.get("form_label_classroom_date", "募集日時"),
        settings.get("form_label_classroom_experience", "希望する経験"),
        settings.get("form_label_classroom_handslevel", "補助レベル"),
        settings.get("form_label_classroom_notes", "その他ご要望・自由記述"),
    ]
    for field in settings.get("custom_fields_classroom", []):
        headers.append(field.get("label", ""))
    headers.append("user_id")
    sheet.delete_rows(1)
    sheet.insert_row(headers, index=1)

### 条件マッチング検索（教室 → アルバイト）
def find_matching_alb(sheet, area, experience_required, datetime_str):
    all_rows = sheet.get_all_records()
    matched = []
    for row in all_rows:
        area_match = area in row.get("希望エリア", "")
        date_match = datetime_str[:10] in row.get("稼働可能日・時間", "")
        handslevel = row.get("補助レベル", "")
        exp_match = experience_required in handslevel
        if area_match or date_match or exp_match:
            matched.append(row.get("user_id"))
    return matched
