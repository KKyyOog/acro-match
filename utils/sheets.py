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

def update_sheet_headers_for_alb(sheet, settings):
    headers = [
        settings.get("form_label_name", "ニックネーム"),
        settings.get("form_label_birthday4", "誕生日4桁"),
        settings.get("form_label_alb_experience", "経験"),
        settings.get("form_label_alb_handslevel", "補助レベル"),
        settings.get("form_label_area", "エリア"),
        settings.get("form_label_available", "稼働可能日・時間"),
        settings.get("form_label_reachtime", "連絡可能時間帯"),
        "LIFF ID"
    ]
    existing_headers = sheet.row_values(1)
    if existing_headers != headers:
        if not existing_headers: sheet.resize(rows=1)  # データ消さないように安全に調整
        sheet.insert_row(headers, index=1)

def update_sheet_headers_for_classroom(sheet, settings):
    headers = [
        settings.get("form_label_classroom_name", "教室名"),
        settings.get("form_label_classroom_location", "場所"),
        settings.get("form_label_classroom_date", "開催日"),
        settings.get("form_label_classroom_experience", "希望する経験"),
        settings.get("form_label_classroom_support_level", "補助レベル"),
        settings.get("form_label_classroom_notes", "補足・備考"),
        "LIFF ID"
    ]
    existing_headers = sheet.row_values(1)
    if existing_headers != headers:
        if not existing_headers: sheet.resize(rows=1)  # データ消さないように安全に調整
        sheet.insert_row(headers, index=1)

    custom_fields = settings.get("custom_fields_classroom", [])
    for field in custom_fields:
        headers.append(field.get("label", field.get("name")))

    sheet.resize(rows=1)
    sheet.insert_row(headers, index=1)

def get_webhook_id_from_liff_id(sheet, liff_id):
    try:
        records = sheet.get_all_records()
        for record in records:
            if str(record.get("LIFF ID")) == str(liff_id):
                return record.get("webhook ID")
    except Exception as e:
        log_exception(e, context="LIFF ID 検索中にエラー")
    return None

def update_birthday_if_exists(liff_id, birthday, sheet_name="ユーザー情報"):
    sheet = get_sheet(sheet_name)
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):
        if row.get("LIFF ID") == liff_id:
            col_index = list(row.keys()).index("誕生日") + 1
            sheet.update_cell(idx, col_index, birthday)
            return True
    return False

def update_liff_id_in_user_map(name, last4, liff_id, sheet_name="ユーザー名マッピング"):
    sheet = get_sheet(sheet_name)
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):
        if row.get("名前") == name and str(row.get("誕生日下4桁")) == str(last4):
            col_index = list(row.keys()).index("LIFF ID") + 1
            sheet.update_cell(idx, col_index, liff_id)
            return True
    return False

def append_row_if_new_user(name, birthday, liff_id, webhook_id=None, sheet_name="ユーザー情報"):
    sheet = get_sheet(sheet_name)
    records = sheet.get_all_records()

    for row in records:
        if row.get("名前") == name and row.get("誕生日") == birthday and row.get("LIFF ID") == liff_id:
            return False  # Already exists

    headers = sheet.row_values(1)
    new_row_dict = {
        "名前": name,
        "誕生日": birthday,
        "LIFF ID": liff_id,
        "webhook ID": webhook_id or ""
    }
    row = [new_row_dict.get(h, "") for h in headers]
    sheet.append_row(row)
    return True

def update_liff_id_from_nickname_birthday(nickname, birthday4, liff_id, sheet_name="ユーザー情報"):
    sheet = get_sheet(sheet_name)
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):
        if row.get("名前") == nickname and str(row.get("誕生日下4桁")) == str(birthday4):
            col_index = list(row.keys()).index("LIFF ID") + 1
            sheet.update_cell(idx, col_index, liff_id)
            return True
    return False
