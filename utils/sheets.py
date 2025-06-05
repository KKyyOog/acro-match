import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from utils.logging_util import log_exception

print("✅ sheets.py loaded")

SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

gc = None

def _init_gc():
    global gc
    if gc is not None:
        return gc

    print("🔐 Initializing Google Credentials")
    cred_json = os.getenv("GOOGLE_CREDENTIALS")
    if not cred_json:
        raise RuntimeError("GOOGLE_CREDENTIALS not set")

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(cred_json), SCOPES)
    gc = gspread.authorize(credentials)
    return gc

def get_sheet(sheet_name):
    client = _init_gc()
    try:
        spreadsheet = client.open_by_key(os.getenv("SPREADSHEET_ID"))
        return spreadsheet.worksheet(sheet_name)
    except Exception as e:
        log_exception(e, context=f"シート取得失敗: {sheet_name}")
        raise

def update_sheet_headers_for_alb(sheet, new_headers):
    sheet.resize(rows=1)  # ヘッダーだけ残す
    sheet.insert_row(new_headers, index=1)

def update_sheet_headers_for_classroom(sheet, new_headers):
    sheet.resize(rows=1)
    sheet.insert_row(new_headers, index=1)

def get_webhook_id_from_liff_id(sheet, liff_id):
    try:
        records = sheet.get_all_records()
        for record in records:
            if str(record.get("LIFF ID")) == str(liff_id):
                return record.get("webhook ID")
    except Exception as e:
        log_exception(e, context="LIFF ID 検索中にエラー")
    return None