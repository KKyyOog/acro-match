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

def update_birthday_if_exists(liff_id, birthday, sheet_name="ユーザー情報"):
    sheet = get_sheet(sheet_name)
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):
        if row.get("LIFF ID") == liff_id:
            col_index = list(row.keys()).index("誕生日") + 1
            sheet.update_cell(idx, col_index, birthday)
            return True
    return False

def append_row_if_new_user(name, birthday, liff_id, webhook_id=None, timestamp=None, sheet_name="ユーザー情報"):
    sheet = get_sheet(sheet_name)
    records = sheet.get_all_records()

    for idx, row in enumerate(records, start=2):
        if row.get("LIFF ID") == liff_id:
            updated = False
            if not row.get("名前") and name:
                name_col = list(row.keys()).index("名前") + 1
                sheet.update_cell(idx, name_col, name)
                updated = True
            if not row.get("誕生日") and birthday:
                bday_col = list(row.keys()).index("誕生日") + 1
                sheet.update_cell(idx, bday_col, birthday)
                updated = True
            if webhook_id and not row.get("Webhook ID"):
                hook_col = list(row.keys()).index("Webhook ID") + 1
                sheet.update_cell(idx, hook_col, webhook_id)
                updated = True
            if timestamp and "登録日時" in row and not row.get("登録日時"):
                time_col = list(row.keys()).index("登録日時") + 1
                sheet.update_cell(idx, time_col, timestamp)
                updated = True
            return not updated

    headers = sheet.row_values(1)
    new_row_dict = {
        "名前": name,
        "誕生日": birthday,
        "Webhook ID": webhook_id or "",
        "LIFF ID": liff_id,
        "登録日時": timestamp or ""
    }
    row = [new_row_dict.get(h, "") for h in headers]
    sheet.append_row(row)
    return True

def update_liff_id_by_name_and_birthday4(nickname, birthday4, liff_id, sheet_name="ユーザー情報"):
    sheet = get_sheet(sheet_name)
    records = sheet.get_all_records()
    for idx, row in enumerate(records, start=2):
        if row.get("名前") == nickname:
            full_birthday = row.get("誕生日", "")
            digits = ''.join(filter(str.isdigit, full_birthday))
            if len(digits) >= 4 and digits[-4:] == str(birthday4):
                col_index = list(row.keys()).index("LIFF ID") + 1
                sheet.update_cell(idx, col_index, liff_id)
                return True
    return False

def update_liff_id_by_name_birthday(name, birthday, liff_id, sheet_name="ユーザー情報"):
    sheet = get_sheet(sheet_name)
    records = sheet.get_all_records()

    for idx, row in enumerate(records, start=2):
        if row.get("名前") == name and row.get("誕生日") == birthday:
            col_index = list(row.keys()).index("LIFF ID") + 1
            sheet.update_cell(idx, col_index, liff_id)
            return True
    return False
