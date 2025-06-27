import os
import json
import gspread
from typing import Optional
from oauth2client.service_account import ServiceAccountCredentials
from utils.logging_util import log_exception

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

def append_row_if_new_user(name, birthday, chat_liff_id="", app_liff_id="", timestamp=None, sheet_name="ユーザー情報"):
    sheet = get_sheet(sheet_name)
    records = sheet.get_all_records()

    for idx, row in enumerate(records, start=2):
        if row.get("チャット LIFF ID") == chat_liff_id or (name and birthday and row.get("名前") == name and row.get("誕生日") == birthday):
            updated = False
            if not row.get("名前") and name:
                col = list(row.keys()).index("名前") + 1
                sheet.update_cell(idx, col, name)
                updated = True
            if not row.get("誕生日") and birthday:
                col = list(row.keys()).index("誕生日") + 1
                sheet.update_cell(idx, col, birthday)
                updated = True
            if not row.get("チャット LIFF ID") and chat_liff_id:
                col = list(row.keys()).index("チャット LIFF ID") + 1
                sheet.update_cell(idx, col, chat_liff_id)
                updated = True
            if not row.get("アプリ LIFF ID") and app_liff_id:
                col = list(row.keys()).index("アプリ LIFF ID") + 1
                sheet.update_cell(idx, col, app_liff_id)
                updated = True
            if not row.get("登録日時") and timestamp:
                col = list(row.keys()).index("登録日時") + 1
                sheet.update_cell(idx, col, timestamp)
                updated = True
            return not updated

    headers = sheet.row_values(1)
    new_row = {
        "名前": name,
        "誕生日": birthday,
        "チャット LIFF ID": chat_liff_id,
        "アプリ LIFF ID": app_liff_id,
        "登録日時": timestamp or ""
    }
    sheet.append_row([new_row.get(h, "") for h in headers])
    return True

def update_app_liff_id_by_name_birthday(name, birthday, app_liff_id, sheet_name="ユーザー情報"):
    sheet = get_sheet(sheet_name)
    records = sheet.get_all_records()

    for idx, row in enumerate(records, start=2):
        if row.get("名前") == name and row.get("誕生日") == birthday:
            col = list(row.keys()).index("アプリ LIFF ID") + 1
            sheet.update_cell(idx, col, app_liff_id)
            return True
    return False

def update_liff_id_by_name_and_birthday4(nickname, birthday4, app_liff_id, sheet_name="ユーザー情報"):
    sheet = get_sheet(sheet_name)
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):
        if row.get("名前") == nickname:
            full_birthday = str(row.get("誕生日", ""))
            digits = ''.join(filter(str.isdigit, full_birthday))
            if len(digits) >= 4 and digits[-4:] == str(birthday4):
                col_index = list(row.keys()).index("アプリ LIFF ID") + 1
                sheet.update_cell(idx, col_index, app_liff_id)
                return True
    return False

def get_chat_liff_id_by_app_liff_id(app_liff_id: str, user_sheet_name: str = "ユーザー情報") -> Optional[str]:
    sheet = get_sheet(user_sheet_name)
    records = sheet.get_all_records()
    for row in records:
        if row.get("アプリ LIFF ID") == app_liff_id:
            return row.get("チャット LIFF ID")
    return None

def highlight_classroom_row(row_index: int, sheet_name: str = "教室登録シート"):
    sheet = get_sheet(sheet_name)
    # 行番号は1オリジンで、ヘッダーを含めて+2する（ヘッダー+row_index）
    row_num = row_index + 2
    last_col = len(sheet.row_values(1))  # ヘッダー行の列数取得

    cell_range = f"A{row_num}:{chr(64 + last_col)}{row_num}"
    sheet.format(cell_range, {
        "backgroundColor": {
            "red": 0.8,
            "green": 1.0,
            "blue": 0.8
        }
    })
