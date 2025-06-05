# utils/sheets.py

import gspread
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from utils.logging_util import log_exception

load_dotenv()

def get_google_credentials():
    try:
        credentials_json = os.getenv("GOOGLE_CREDENTIALS")
        credentials_path = os.getenv("GOOGLE_CREDENTIAL_PATH")

        if credentials_json:
            info = json.loads(credentials_json)
        elif credentials_path and os.path.exists(credentials_path):
            with open(credentials_path, "r", encoding="utf-8") as f:
                info = json.load(f)
        else:
            raise ValueError("Google認証情報が見つかりません")

        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
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

# 以下の関数はそのまま、またはエラーハンドリング追加して移植
# - load_settings
# - add_user_id_mapping_if_new
# - update_birthday_if_exists
# - update_liff_id_in_user_map
# - update_sheet_headers_for_alb
# - update_sheet_headers_for_classroom
# - get_webhook_id_from_liff_id
# - save_settings

# 変更点は主に認証取得の柔軟性と log_exception の徹底活用