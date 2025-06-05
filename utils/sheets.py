import gspread
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from utils.logging_util import log_exception  # ✅ ログユーティリティ

load_dotenv()

def get_google_credentials():
    try:
        credentials_json = os.getenv("GOOGLE_CREDENTIALS")
        if not credentials_json:
            raise ValueError("GOOGLE_CREDENTIALS が設定されていません")
        info = json.loads(credentials_json)
        scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        return Credentials.from_service_account_info(info, scopes=scopes)
    except Exception as e:
        log_exception(e, context="Google認証取得")
        raise

def get_sheet(sheet_name: str):
    try:
        sheet_id = os.getenv("SPREADSHEET_ID")
        if not sheet_id:
            raise ValueError("SPREADSHEET_ID が環境変数に設定されていません。")
        creds = get_google_credentials()
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(sheet_id)
        return spreadsheet.worksheet(sheet_name)
    except Exception as e:
        log_exception(e, context=f"シート取得: {sheet_name}")
        raise

def load_settings():
    try:
        with open("settings.json", "r", encoding="utf-8") as f:
            saved = json.load(f)
        return saved
    except Exception as e:
        log_exception(e, context="settings.json 読み込み")
        return {}

def add_user_id_mapping_if_new(webhook_id: str, name: str):
    try:
        sheet = get_sheet("ユーザーIDマップ")
        values = sheet.get_all_values()
        webhook_ids = [row[1] for row in values[1:] if len(row) > 1]

        if webhook_id in webhook_ids:
            return

        sheet.append_row([name, webhook_id, "", "", datetime.now().strftime("%Y-%m-%d")])
    except Exception as e:
        log_exception(e, context="ユーザーIDマップ追加")

def update_birthday_if_exists(webhook_id: str, birthday: str) -> bool:
    try:
        sheet = get_sheet("ユーザーIDマップ")
        values = sheet.get_all_values()

        for i, row in enumerate(values[1:], start=2):
            if len(row) > 1 and row[1] == webhook_id:
                sheet.update_cell(i, 4, birthday)
                return True
        return False
    except Exception as e:
        log_exception(e, context="誕生日更新")
        return False

def update_liff_id_in_user_map(name: str, birthday4: str, liff_id: str) -> bool:
    try:
        sheet = get_sheet("ユーザーIDマップ")
        values = sheet.get_all_values()

        for i, row in enumerate(values[1:], start=2):
            if len(row) >= 4 and row[0] == name and row[3].endswith(birthday4):
                sheet.update_cell(i, 3, liff_id)
                return True
        return False
    except Exception as e:
        log_exception(e, context="LIFF ID更新")
        return False
